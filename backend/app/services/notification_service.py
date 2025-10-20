"""
Notification Service – Vertragswarnungen
Serviço de Notificações – Alertas de contrato

DE: Selektiert Verträge nahe am Ablauf (T-60/T-30/T-10/T-1), erstellt
    deduplizierte Benachrichtigungen (Alert) und versendet E-Mails HTML.
PT: Seleciona contratos próximos do vencimento (T-60/T-30/T-10/T-1), cria
    notificações deduplicadas (Alert) e envia e-mails HTML.

Design:
 - Funções puras de cálculo (dias restantes, tipo de alerta)
 - Acesso a dados encapsulado
 - Renderização de e-mail separada
 - Métodos públicos:
    * process_due_alerts
    * reprocess_alert
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone, date
from typing import Iterable, List, Optional, Tuple, cast

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contract import Contract, ContractStatus
from app.models.alert import Alert, AlertType, AlertStatus, AlertResponse, AlertListResponse
from app.utils.email import send_email, render_contract_expiry_html, get_email_subject_by_type


# ========= Helpers de Cálculo / Berechnungshelfer =========

ALERT_DAY_MARKS: Tuple[int, int, int, int] = (60, 30, 10, 1)


def calculate_days_until(date_value: Optional[date]) -> Optional[int]:
    """Retorna dias inteiros até uma data; None se não aplicável.
    Gibt ganze Tage bis zu einem Datum zurück; None wenn nicht anwendbar.
    """
    if date_value is None:
        return None
    today = datetime.now(timezone.utc).date()
    target = date_value
    return (target - today).days


def map_days_to_alert_type(days_until: Optional[int]) -> Optional[AlertType]:
    """Mapeia dias restantes para o tipo de alerta.
    Ordnet verbleibende Tage dem Alert-Typ zu.
    """
    if days_until is None:
        return None
    if days_until == 60:
        return AlertType.T_MINUS_60
    if days_until == 30:
        return AlertType.T_MINUS_30
    if days_until == 10:
        return AlertType.T_MINUS_10
    if days_until == 1:
        return AlertType.T_MINUS_1
    return None


def build_email_subject(contract: Contract, days_until: int, alert_type: AlertType) -> str:
    """Assunto de e-mail usando templates dedicados.
    E-Mail-Betreff mit dedizierten Templates.
    """
    title = cast(str, contract.title)
    return get_email_subject_by_type(alert_type, title, language="de")


def build_email_body_html(contract: Contract, days_until: int, alert_type: AlertType) -> str:
    """Corpo HTML usando templates dedicados.
    HTML-Körper mit dedizierten Templates.
    """
    return render_contract_expiry_html(contract, days_until, alert_type, language="de")


# ========= Serviço =========

class NotificationService:
    """Serviço responsável por criar e enviar alertas de expiração.
    Dienst zum Erstellen und Versenden von Ablauf-Benachrichtigungen.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def _get_active_contracts_with_end_date(self) -> List[Contract]:
        """Seleciona contratos ativos com `end_date` definido.
        Wählt aktive Verträge mit gesetztem `end_date` aus.
        """
        result = await self.db.execute(
            select(Contract).where(
                and_(
                    Contract.status == ContractStatus.ACTIVE,  # type: ignore
                    Contract.end_date.is_not(None),
                )
            )
        )
        return list(result.scalars().all())

    async def _find_existing_alert(self, contract_id: int, alert_type: AlertType) -> Optional[Alert]:
        result = await self.db.execute(
            select(Alert).where(
                and_(Alert.contract_id == contract_id, Alert.alert_type == alert_type)
            )
        )
        return result.scalar_one_or_none()

    async def _create_alert(
        self,
        contract_id: int,
        alert_type: AlertType,
        scheduled_for: datetime,
        recipient: Optional[str],
        subject: str,
    ) -> Alert:
        alert = Alert(
            contract_id=contract_id,
            alert_type=alert_type,
            status=AlertStatus.PENDING,
            scheduled_for=scheduled_for,
            recipient=recipient,
            subject=subject,
        )
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        return alert

    async def _send_alert_email(self, alert: Alert, contract: Contract, days_until: int) -> bool:
        subject = alert.subject or build_email_subject(contract, days_until, cast(AlertType, alert.alert_type))
        body_html = build_email_body_html(contract, days_until, cast(AlertType, alert.alert_type))
        recipient = cast(Optional[str], alert.recipient) or cast(Optional[str], contract.client_email)
        if not recipient:
            # Sem destinatário, marcar como falha informativa
            alert.mark_failed("No recipient available / Kein Empfänger verfügbar")
            await self.db.commit()
            return False
        success = send_email(recipient, cast(str, subject), body_html, is_html=True)
        if success:
            alert.mark_sent()
        else:
            alert.mark_failed("SMTP error / SMTP-Fehler")
        await self.db.commit()
        return success

    async def process_due_alerts(self) -> AlertListResponse:
        """Processa todos os alertas devidos hoje (T-60/30/10/1).
        Verarbeitet alle fälligen Alerts heute.
        """
        contracts = await self._get_active_contracts_with_end_date()
        created: List[AlertResponse] = []

        now = datetime.now(timezone.utc)

        for contract in contracts:
            # Calcular dias restantes e tipo de alerta
            end_date_value = cast(Optional[date], contract.end_date)
            if end_date_value is None:
                continue
            days_until = calculate_days_until(end_date_value)
            alert_type = map_days_to_alert_type(days_until)
            if alert_type is None or days_until is None:
                continue

            # Dedupe
            existing = await self._find_existing_alert(cast(int, contract.id), alert_type)
            if existing and cast(AlertStatus, existing.status) == AlertStatus.SENT:
                continue

            subject = build_email_subject(contract, days_until, alert_type)
            recipient = cast(Optional[str], contract.client_email)

            # Criar ou reutilizar
            if existing is None:
                alert = await self._create_alert(
                    contract_id=cast(int, contract.id),
                    alert_type=alert_type,
                    scheduled_for=now,
                    recipient=recipient,
                    subject=subject,
                )
            else:
                alert = existing

            # Enviar
            await self._send_alert_email(alert, contract, days_until)

            # Coletar resposta
            created.append(AlertResponse.model_validate(alert))

        return AlertListResponse(total=len(created), alerts=created, page=1, per_page=len(created) or 1)

    async def reprocess_alert(self, alert_id: int) -> Optional[AlertResponse]:
        """Reprocessa um alerta (útil para status FAILED).
        Reprozessiert eine Benachrichtigung (nützlich für FAILED).
        """
        result = await self.db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        if alert is None:
            return None

        result_c = await self.db.execute(select(Contract).where(Contract.id == alert.contract_id))
        contract = result_c.scalar_one_or_none()
        if contract is None:
            return None
        end_date_value = cast(Optional[date], contract.end_date)
        if end_date_value is None:
            return None
        days_until = calculate_days_until(end_date_value)
        if days_until is None:
            return None

        await self._send_alert_email(alert, contract, days_until)
        return AlertResponse.model_validate(alert)

