
"""
Alert Router – Benachrichtigungs-Router
Router de Alertas – Endpoints para gerenciamento de alertas

DE: FastAPI-Router für Alert-Verwaltung (Liste, Details, Reprocessing).
PT: Router FastAPI para gerenciamento de alertas (listagem, detalhes, reprocessamento).
"""
from typing import List, Optional, cast
from datetime import datetime, timezone


from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import OperationalError
from sqlalchemy import select, and_, desc, func
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.alert import Alert, AlertType, AlertStatus, AlertResponse, AlertListResponse
from app.schemas.alert_with_contract import AlertWithContractInfo
from app.schemas.alert_with_contract import AlertWithContractInfo, AlertWithContractListResponse
from app.models.contract import Contract
from app.services.notification_service import NotificationService



# Router instance / Instância do router
router = APIRouter(
    prefix="/alerts",
    tags=["alerts"],
    responses={
        404: {"description": "Alert not found / Alerta não encontrado"},
        500: {"description": "Internal server error / Erro interno do servidor"}
    }
)

from app.schemas.alert import AlertUpdate  # type: ignore # Certifique-se de ter esse schema

@router.put("/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Atualiza um alerta existente.
    Aktualisiert eine bestehende Benachrichtigung.

    Args / Argumentos:
        alert_id: ID do alerta / Alert-ID
        alert_update: Dados para atualização / Aktualisierungsdaten

    Returns / Retorna:
        AlertResponse: Alerta atualizado / Aktualisierte Benachrichtigung

    Raises / Levanta:
        HTTPException 404: Alerta não encontrado / Alert nicht gefunden
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found / Alerta não encontrado")

    # Atualiza os campos permitidos
    if alert_update.responsible_user_id is not None:
        alert.responsible_user_id = alert_update.responsible_user_id # type: ignore
    if alert_update.scheduled_for is not None:
        alert.scheduled_for = alert_update.scheduled_for
    if alert_update.status is not None:
        alert.status = alert_update.status

    await db.commit()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)

# Deletar alerta / Alerta löschen
@router.delete("/{alert_id}", status_code=204)
async def delete_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """
    Remove um alerta do banco de dados (hard delete).
    Löscht einen Alert aus der Datenbank (Hard Delete).
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found / Alerta não encontrado")
    await db.delete(alert)
    await db.commit()
    return

# Rejeitar alerta / Alert ablehnen
@router.post("/{alert_id}/reject", response_model=AlertResponse)
async def reject_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """
    Rejeita um alerta (marca como REJECTED).
    Lehnt einen Alert ab (als REJECTED markieren).
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found / Alerta não encontrado")
    alert.status = AlertStatus.REJECTED
    await db.commit()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)


# Aprovar alerta / Alerta genehmigen
@router.post("/{alert_id}/approve", response_model=AlertResponse)
async def approve_alert(alert_id: int, db: AsyncSession = Depends(get_db)):
    """
    Aprova um alerta (marca como enviado).
    Genehmigt einen Alert (als gesendet markieren).
    """
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found / Alerta não encontrado")
    alert.status = AlertStatus.SENT
    alert.sent_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)



@router.get("/", response_model=AlertWithContractListResponse)
async def list_alerts(
    page: int = Query(1, ge=1, description="Page number / Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page / Itens por página"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status / Filtrar por status"),
    alert_type: Optional[AlertType] = Query(None, description="Filter by alert type / Filtrar por tipo de alerta"),
    contract_id: Optional[int] = Query(None, description="Filter by contract ID / Filtrar por ID do contrato"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista alertas com informações do contrato (company_name, created_by_name, responsible_user_name).
    """
    try:
            # Join com Contract, User (criador) e User (responsável)
            from app.models.user import User
            from sqlalchemy.orm import aliased
            UserResponsible = aliased(User)
            query = (
                select(
                    Alert,
                    Contract.company_name,
                    User.name.label("created_by_name"),
                    UserResponsible.name.label("responsible_user_name")
                )
                .join(Contract, Alert.contract_id == Contract.id)
                .join(User, Contract.created_by == User.id)
                .outerjoin(UserResponsible, Contract.responsible_user_id == UserResponsible.id)
            )

            filters = []
            if status is not None:
                filters.append(Alert.status == status)
            if alert_type is not None:
                filters.append(Alert.alert_type == alert_type)
            if contract_id is not None:
                filters.append(Alert.contract_id == contract_id)
            if filters:
                query = query.where(and_(*filters))

            query = query.order_by(desc(Alert.created_at))

            # Paginação
            try:
                count_result = await db.execute(select(func.count()).select_from(query.subquery()))
                total = int(count_result.scalar_one())
            except OperationalError:
                return AlertWithContractListResponse(total=0, alerts=[], page=page, per_page=per_page)
            start_idx = (page - 1) * per_page
            query = query.limit(per_page).offset(start_idx)
            result = await db.execute(query)
            rows = result.all()

            alert_responses = []
            for alert, company_name, created_by_name, responsible_user_name in rows:
                alert_responses.append(
                    AlertWithContractInfo.model_validate({
                        **alert.__dict__,
                        "company_name": company_name,
                        "created_by_name": created_by_name,
                        "responsible_user_name": responsible_user_name
                    })
                )

            return AlertWithContractListResponse(
                total=total,
                alerts=alert_responses,
                page=page,
                per_page=per_page
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listing alerts / Erro ao listar alertas: {str(e)}"
        )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Obtém detalhes de um alerta específico.
    Ruft Details einer bestimmten Benachrichtigung ab.
    
    Args / Argumentos:
        alert_id: ID do alerta / Alert-ID
        
    Returns / Retorna:
        AlertResponse: Detalhes do alerta / Alert-Details
    """
    try:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()

        if alert is None:
            raise HTTPException(
                status_code=404,
                detail="Alert not found / Alerta não encontrado"
            )

        return AlertResponse.model_validate(alert)

    except HTTPException:
        raise
    except OperationalError:
        # DB not initialized -> treat as not found
        raise HTTPException(status_code=404, detail="Alert not found / Alerta não encontrado")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting alert / Erro ao obter alerta: {str(e)}"
        )


@router.post("/{alert_id}/reprocess", response_model=AlertResponse)
async def reprocess_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Reprocessa um alerta (útil para alertas com status FAILED).
    Reprozessiert eine Benachrichtigung (nützlich für FAILED-Status).
    
    Args / Argumentos:
        alert_id: ID do alerta / Alert-ID
        
    Returns / Retorna:
        AlertResponse: Alerta reprocessado / Reprozessierte Benachrichtigung
    """
    try:
        # Verificar se o alerta existe / Prüfen ob Alert existiert
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        alert = result.scalar_one_or_none()
        
        if alert is None:
            raise HTTPException(
                status_code=404,
                detail="Alert not found / Alerta não encontrado"
            )
        
        # Reprocessar usando o serviço / Mit Service reprozessieren
        notification_service = NotificationService(db)
        reprocessed_alert = await notification_service.reprocess_alert(alert_id)
        
        if reprocessed_alert is None:
            raise HTTPException(
                status_code=400,
                detail="Could not reprocess alert / Não foi possível reprocessar o alerta"
            )
        
        return reprocessed_alert
        
    except HTTPException:
        raise
    except OperationalError:
        # DB not initialized -> treat as not found
        raise HTTPException(status_code=404, detail="Alert not found / Alerta não encontrado")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error reprocessing alert / Erro ao reprocessar alerta: {str(e)}"
        )



@router.get("/contract/{contract_id}", response_model=List[AlertWithContractInfo])
async def get_contract_alerts(
    contract_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os alertas de um contrato específico, incluindo dados do contrato.
    """
    try:
        # Verificar se o contrato existe
        contract_result = await db.execute(select(Contract).where(Contract.id == contract_id))
        contract = contract_result.scalar_one_or_none()
        if contract is None:
            raise HTTPException(status_code=404, detail="Contract not found / Contrato não encontrado")

        # Buscar alertas do contrato com join para dados extras
        result = await db.execute(
            select(Alert, Contract.company_name, Contract.created_by, Contract.created_by_name, Contract.responsible_user_name) # type: ignore
            .join(Contract, Alert.contract_id == Contract.id)
            .where(Alert.contract_id == contract_id)
            .order_by(desc(Alert.created_at))
        )
        rows = result.all()

        alert_responses = []
        for alert, company_name, created_by, created_by_name, responsible_user_name in rows:
            alert_responses.append(
                AlertWithContractInfo.model_validate({
                    **alert.__dict__,
                    "company_name": company_name,
                    "created_by_name": created_by_name,
                    "responsible_user_name": responsible_user_name
                })
            )
        return alert_responses

    except HTTPException:
        raise
    except OperationalError:
        raise HTTPException(status_code=404, detail="Contract not found / Contrato não encontrado")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting contract alerts / Erro ao obter alertas do contrato: {str(e)}"
        )


@router.get("/stats/summary")
async def get_alerts_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Retorna estatísticas resumidas dos alertas.
    Gibt zusammenfassende Alert-Statistiken zurück.
    
    Returns / Retorna:
        dict: Estatísticas dos alertas / Alert-Statistiken
    """
    try:
        # Contar por status usando consultas COUNT() / Nach Status zählen mit COUNT()
        status_counts = {}
        for status in AlertStatus:
            count_result = await db.execute(select(func.count()).select_from(Alert).where(Alert.status == status))
            count = int(count_result.scalar_one() or 0)
            status_counts[cast(str, status.value)] = count

        # Contar por tipo usando COUNT()
        type_counts = {}
        for alert_type in AlertType:
            count_result = await db.execute(select(func.count()).select_from(Alert).where(Alert.alert_type == alert_type))
            count = int(count_result.scalar_one() or 0)
            type_counts[cast(str, alert_type.value)] = count

        # Total de alertas usando COUNT()
        total_result = await db.execute(select(func.count()).select_from(Alert))
        total_alerts = int(total_result.scalar_one() or 0)

        return {
            "total_alerts": total_alerts,
            "by_status": status_counts,
            "by_type": type_counts,
            "generated_at": datetime.utcnow().isoformat()
        }

    except OperationalError:
        # DB not initialized: retornar resumo vazio
        return {
            "total_alerts": 0,
            "by_status": {},
            "by_type": {},
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting alerts summary / Erro ao obter resumo dos alertas: {str(e)}"
        )


@router.post("/manual", response_model=AlertResponse)
async def create_manual_alert(
    contract_id: int = Query(..., description="Vertrags-ID für den Alert / ID do contrato para o alerta"),
    scheduled_for: datetime = Query(..., description="Geplante Sendezeit / Horário agendado para envio"),
    recipient: Optional[str] = Query(None, description="E-Mail-Empfänger (optional, Standard: Vertragsbesitzer) / Destinatário do email (opcional, padrão: proprietário do contrato)"),
    subject: Optional[str] = Query(None, description="E-Mail-Betreff (optional) / Assunto do email (opcional)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Erstellt einen benutzerdefinierten Alert für einen Vertrag.
    Cria um alerta personalizado para um contrato.
    
    Diese Funktion ermöglicht es Benutzern, benutzerdefinierte Alerts für beliebige Daten zu erstellen.
    Der Alert wird vom Hintergrund-Scheduler zur geplanten Zeit verarbeitet.
    
    Esta função permite aos usuários criar alertas personalizados para datas específicas.
    O alerta será processado pelo scheduler em background no horário agendado.
    
    Args / Argumentos:
        contract_id: ID des Vertrags / ID do contrato
        scheduled_for: Geplante Zeit für den Versand / Horário agendado para envio
        recipient: E-Mail-Empfänger (optional) / Destinatário do email (opcional)  
        subject: E-Mail-Betreff (optional) / Assunto do email (opcional)
        
    Returns / Retorna:
        AlertResponse: Erstellter Alert / Alerta criado
        
    Raises / Levanta:
        HTTPException 404: Vertrag nicht gefunden / Contrato não encontrado
        HTTPException 400: Ungültige Daten / Dados inválidos
    """
    # Vertrag prüfen / Verificar contrato
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found / Contrato não encontrado")

    alert = Alert(
        contract_id=contract_id,
        alert_type=AlertType.BENUTZERDEFINIERT,
        scheduled_for=scheduled_for,
        recipient=recipient,
        subject=subject,
        status=AlertStatus.PENDING
    )
    db.add(alert)
    await db.commit()
    await db.refresh(alert)
    return AlertResponse.model_validate(alert)


@router.post("/process-all")
async def process_all_alerts(db: AsyncSession = Depends(get_db)):
    """
    Processa todos os alertas pendentes para todos os contratos.
    Verarbeitet alle ausstehenden Benachrichtigungen für alle Verträge.
    
    Útil para processar alertas manualmente sem esperar o scheduler.
    Nützlich zum manuellen Verarbeiten von Benachrichtigungen ohne auf den Scheduler zu warten.
    
    Returns / Retorna:
        dict: Resultado do processamento / Verarbeitungsergebnis
    """
    try:
        notification_service = NotificationService(db)
        result = await notification_service.process_due_alerts()
        
        return {
            "success": True,
            "total_processed": getattr(result, "total", 0),
            "message": f"Processados {getattr(result, 'total', 0)} alertas / {getattr(result, 'total', 0)} Benachrichtigungen verarbeitet"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar alertas / Fehler beim Verarbeiten von Benachrichtigungen: {str(e)}"
        )
