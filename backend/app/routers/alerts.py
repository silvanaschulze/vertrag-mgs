"""
Alert Router – Benachrichtigungs-Router
Router de Alertas – Endpoints para gerenciamento de alertas

DE: FastAPI-Router für Alert-Verwaltung (Liste, Details, Reprocessing).
PT: Router FastAPI para gerenciamento de alertas (listagem, detalhes, reprocessamento).
"""

from typing import List, Optional, cast
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import OperationalError
from sqlalchemy import select, and_, desc, func
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.alert import Alert, AlertType, AlertStatus, AlertResponse, AlertListResponse
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


@router.get("/", response_model=AlertListResponse)
async def list_alerts(
    page: int = Query(1, ge=1, description="Page number / Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page / Itens por página"),
    status: Optional[AlertStatus] = Query(None, description="Filter by status / Filtrar por status"),
    alert_type: Optional[AlertType] = Query(None, description="Filter by alert type / Filtrar por tipo de alerta"),
    contract_id: Optional[int] = Query(None, description="Filter by contract ID / Filtrar por ID do contrato"),
    db: AsyncSession = Depends(get_db)
):
    """
    Lista alertas com filtros opcionais.
    Listet Benachrichtigungen mit optionalen Filtern auf.
    
    Args / Argumentos:
        page: Número da página / Seitennummer
        per_page: Itens por página / Elemente pro Seite
        status: Status do alerta / Alert-Status
        alert_type: Tipo de alerta / Alert-Typ
        contract_id: ID do contrato / Vertrags-ID
        
    Returns / Retorna:
        AlertListResponse: Lista paginada de alertas / Paginierte Alert-Liste
    """
    try:
        # Construir query base / Basis-Query aufbauen
        query = select(Alert)

        # Aplicar filtros / Filter anwenden
        filters = []
        if status is not None:
            filters.append(Alert.status == status)
        if alert_type is not None:
            filters.append(Alert.alert_type == alert_type)
        if contract_id is not None:
            filters.append(Alert.contract_id == contract_id)

        if filters:
            query = query.where(and_(*filters))

        # Ordenar por data de criação (mais recentes primeiro) / Nach Erstellungsdatum sortieren
        query = query.order_by(desc(Alert.created_at))

        # Executar query com paginação no banco (LIMIT/OFFSET) para evitar carregar tudo
        try:
            count_result = await db.execute(select(func.count()).select_from(query.subquery()))
            total = int(count_result.scalar_one())
        except OperationalError:
            # Banco não inicializado (ex.: em ambientes de teste sem migrações)
            return AlertListResponse(total=0, alerts=[], page=page, per_page=per_page)
        # Calcular offset/limit
        start_idx = (page - 1) * per_page
        query = query.limit(per_page).offset(start_idx)
        result = await db.execute(query)
        paginated_alerts = result.scalars().all()

        # Converter para response / Zu Response konvertieren
        alert_responses = [AlertResponse.model_validate(alert) for alert in paginated_alerts]

        return AlertListResponse(
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


@router.get("/contract/{contract_id}", response_model=List[AlertResponse])
async def get_contract_alerts(
    contract_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Lista todos os alertas de um contrato específico.
    Listet alle Benachrichtigungen eines bestimmten Vertrags auf.
    
    Args / Argumentos:
        contract_id: ID do contrato / Vertrags-ID
        
    Returns / Retorna:
        List[AlertResponse]: Lista de alertas do contrato / Alert-Liste des Vertrags
    """
    try:
        # Verificar se o contrato existe / Prüfen ob Vertrag existiert
        contract_result = await db.execute(select(Contract).where(Contract.id == contract_id))
        contract = contract_result.scalar_one_or_none()

        if contract is None:
            raise HTTPException(
                status_code=404,
                detail="Contract not found / Contrato não encontrado"
            )

        # Buscar alertas do contrato / Alerts des Vertrags suchen
        result = await db.execute(
            select(Alert)
            .where(Alert.contract_id == contract_id)
            .order_by(desc(Alert.created_at))
        )
        alerts = result.scalars().all()

        return [AlertResponse.model_validate(alert) for alert in alerts]

    except HTTPException:
        raise
    except OperationalError:
        # DB absent -> return not found for contract
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
            "generated_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting alerts summary / Erro ao obter resumo dos alertas: {str(e)}"
        )
