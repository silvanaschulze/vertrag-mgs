"""
Alert Model – Benachrichtigungsmodell - Modelo de Alertas – Registro de notificações e estado de envio
DE: Dieses Modul definiert das SQLAlchemy-Modell für Benachrichtigungen
    (Vertragswarnungen wie T-60/T-30/T-10/T-1) inklusive Status.
PT: Este módulo define o modelo SQLAlchemy para notificações (alertas de
    contrato como T-60/T-30/T-10/T-1) incluindo status.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, func
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
from pydantic import BaseModel, Field, ConfigDict

if TYPE_CHECKING:
    from .contract import Contract

class AlertType(str, enum.Enum):
    """Alert-Typ verknüpft mit dem Ablaufzeitraum oder benutzerdefinierten Terminen.
    Tipo de alerta vinculado ao prazo de expiração ou datas personalizadas.
    """

    T_MINUS_60 = "T-60"
    T_MINUS_30 = "T-30"
    T_MINUS_10 = "T-10"
    T_MINUS_1 = "T-1"
    BENUTZERDEFINIERT = "BENUTZERDEFINIERT"  # Benutzerdefinierte Benachrichtigungen


class AlertStatus(str, enum.Enum):
    """Status de processamento/envio do alerta.
    Verarbeitungs-/Versandstatus der Benachrichtigung.
    """

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Alert(Base):
    """Modelo de alertas de contrato.
    Benachrichtigungsmodell für Verträge.
    """
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey("contracts.id"), nullable=False, index=True)
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType), nullable=False, index=True)
    status: Mapped[AlertStatus] = mapped_column(Enum(AlertStatus), default=AlertStatus.PENDING, nullable=False, index=True)

    # Programado para (data/hora do disparo pretendido) / Geplante Ausführung
    scheduled_for: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Registro de envio / Versandprotokoll
    # Registro de envio / Versandprotokoll
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    recipient: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    # Relacionamento com contrato / Beziehung zum Vertrag
    contract: Mapped["Contract"] = relationship("Contract", back_populates="alerts")

    def mark_sent(self, when: Optional[datetime] = None) -> None:
        """Marcar alerta como enviado.
        Benachrichtigung als gesendet markieren.
        """
        self.status = AlertStatus.SENT
        self.sent_at = when or datetime.now(timezone.utc)

    def mark_failed(self, message: str) -> None:
        """Marcar alerta como falhado e registrar erro.
        Benachrichtigung als fehlgeschlagen markieren und Fehler protokollieren.
        """
        self.status = AlertStatus.FAILED
        self.error = message

    def __repr__(self) -> str:
        return f"<Alert(id={self.id}, contract_id={self.contract_id}, type={self.alert_type.value}, status={self.status.value})>"


# =====================
# Pydantic Schemas (v2)
# =====================

class AlertBase(BaseModel):
    """Campos básicos do alerta / Grundlegende Alert-Felder"""

    contract_id: int = Field(..., description="ID do contrato / Vertrags-ID")
    alert_type: AlertType = Field(..., description="Tipo de alerta / Alert-Typ")
    status: AlertStatus = Field(AlertStatus.PENDING, description="Status do alerta / Benachrichtigungsstatus")
    scheduled_for: datetime = Field(..., description="Data/hora agendada / Geplante Ausführungszeit")
    recipient: Optional[str] = Field(None, description="Destinatário do e-mail / E-Mail-Empfänger")
    subject: Optional[str] = Field(None, description="Assunto do e-mail / E-Mail-Betreff")


class AlertCreate(BaseModel):
    """Payload para criação manual de alerta / Nutzlast für manuelle Alert-Erstellung"""

    contract_id: int
    alert_type: AlertType
    scheduled_for: datetime
    recipient: Optional[str] = None
    subject: Optional[str] = None


class AlertUpdate(BaseModel):
    """Campos atualizáveis / Aktualisierbare Felder"""

    status: Optional[AlertStatus] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    scheduled_for: Optional[datetime] = None


class AlertInDB(BaseModel):
    """Representação interna (from_attributes) / Interne Darstellung"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    contract_id: int
    alert_type: AlertType
    status: AlertStatus
    scheduled_for: datetime
    sent_at: Optional[datetime] = None
    recipient: Optional[str] = None
    subject: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AlertResponse(AlertInDB):
    """Resposta para uma única entidade / Antwort für eine einzelne Entität"""

    pass


class AlertListResponse(BaseModel):
    """Lista paginada de alertas / Paginierte Alert-Liste"""

    total: int
    alerts: list[AlertResponse]
    page: int = Field(1, ge=1)
    per_page: int = Field(10, ge=1, le=100)
