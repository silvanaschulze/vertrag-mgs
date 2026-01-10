"""
Dashboard Router - Dashboard-Router
API endpoints for dashboard statistics
API-Endpunkte für Dashboard-Statistiken

Este módulo expõe o endpoint /api/dashboard/stats que retorna
estatísticas filtradas pelo role e access_level do usuário autenticado.

Dieses Modul stellt den Endpunkt /api/dashboard/stats bereit, der
Statistiken gefiltert nach Rolle und Zugriffsstufe des authentifizierten
Benutzers zurückgibt.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardStats


router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    responses={
        404: {"description": "Not found - Nicht gefunden"},
        401: {"description": "Unauthorized - Nicht autorisiert"},
        403: {"description": "Forbidden - Verboten"}
    }
)


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> DashboardStats:
    """
    Obter estatísticas do dashboard filtradas por role
    Dashboard-Statistiken gefiltert nach Rolle abrufen
    
    Retorna estatísticas diferentes baseado no access_level do usuário:
    
    - **Level 6 (SYSTEM_ADMIN)**: Apenas dados técnicos (usuários, backup, disco, sessões)
    - **Level 5 (DIRECTOR)**: Todas estatísticas da empresa (contratos, valores, relatórios)
    - **Level 4 (DEPARTMENT_ADM)**: Estatísticas completas do departamento (com valores)
    - **Level 3 (DEPARTMENT_USER)**: Estatísticas do departamento (sem valores financeiros)
    - **Level 2 (TEAM)**: Estatísticas do time (sem relatórios)
    - **Level 1 (STAFF)**: Apenas contratos próprios
    
    Gibt unterschiedliche Statistiken basierend auf der Zugriffsstufe des Benutzers zurück:
    
    - **Level 6 (SYSTEM_ADMIN)**: Nur technische Daten (Benutzer, Backup, Festplatte, Sitzungen)
    - **Level 5 (DIRECTOR)**: Alle Unternehmensstatistiken (Verträge, Werte, Berichte)
    - **Level 4 (DEPARTMENT_ADM)**: Vollständige Abteilungsstatistiken (mit Werten)
    - **Level 3 (DEPARTMENT_USER)**: Abteilungsstatistiken (ohne Finanzwerte)
    - **Level 2 (TEAM)**: Team-Statistiken (ohne Berichte)
    - **Level 1 (STAFF)**: Nur eigene Verträge
    
    Args:
        current_user: Usuário autenticado / Authentifizierter Benutzer
        db: Sessão do banco de dados / Datenbanksitzung
    
    Returns:
        DashboardStats: Estatísticas filtradas / Gefilterte Statistiken
    
    Raises:
        HTTPException 401: Se não autenticado / Wenn nicht authentifiziert
        HTTPException 500: Se erro no servidor / Bei Serverfehler
    
    Example Response (DIRECTOR):
        ```json
        {
            "total_contracts": 42,
            "active_contracts": 35,
            "expiring_30_days": 5,
            "expiring_90_days": 12,
            "monthly_value": 125000.50,
            "total_alerts": 8,
            "unread_alerts": 3,
            "pending_approvals": 2,
            "total_users": 25,
            "contracts_by_department": {
                "IT und Datenschutz": 15,
                "Personal Organization und Finanzen": 20,
                "Technischer Bereich": 7
            },
            "user_role": "director",
            "user_access_level": 5
        }
        ```
    
    Example Response (SYSTEM_ADMIN):
        ```json
        {
            "total_users": 25,
            "last_backup": "2026-01-10",
            "disk_usage_mb": 150.5,
            "total_database_size_mb": 45.2,
            "active_sessions": 12,
            "uptime_days": 30,
            "user_role": "system_admin",
            "user_access_level": 6
        }
        ```
    """
    try:
        service = DashboardService(db)
        stats = await service.get_stats_by_role(current_user)
        return stats
    
    except Exception as e:
        # Log do erro (implementar logger se necessário)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard stats / Fehler beim Abrufen der Dashboard-Statistiken: {str(e)}"
        )
