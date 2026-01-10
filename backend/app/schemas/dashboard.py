"""
Dashboard Schemas - Dashboard-Schemas
Pydantic models for dashboard statistics and metrics
Modelos Pydantic para estatísticas e métricas do dashboard

Este módulo define os schemas para os dados estatísticos do dashboard,
filtrados por role e access_level do usuário.
Dieses Modul definiert die Schemas für die Dashboard-Statistikdaten,
gefiltert nach Rolle und Zugriffsstufe des Benutzers.
"""

from typing import Optional, Dict, List
from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """
    Estatísticas do dashboard filtradas por role do usuário
    Dashboard-Statistiken gefiltert nach Benutzerrolle
    
    Campos variam dependendo do access_level:
    - Level 6 (SYSTEM_ADMIN): Apenas estatísticas técnicas, sem contratos
    - Level 5 (DIRECTOR): Todas estatísticas da empresa
    - Level 4 (DEPARTMENT_ADM): Estatísticas completas do departamento
    - Level 3 (DEPARTMENT_USER): Estatísticas do departamento sem valores
    - Level 2 (TEAM): Estatísticas do time, sem relatórios
    - Level 1 (STAFF): Apenas contratos próprios
    """
    
    # =========================================================================
    # CONTRATOS - CONTRACT STATS (Levels 1-5, NÃO Level 6)
    # =========================================================================
    total_contracts: Optional[int] = Field(
        None, 
        description="Total de contratos visíveis / Gesamtzahl sichtbarer Verträge"
    )
    active_contracts: Optional[int] = Field(
        None,
        description="Contratos ativos / Aktive Verträge"
    )
    expiring_30_days: Optional[int] = Field(
        None,
        description="Contratos expirando em 30 dias / Verträge ablaufend in 30 Tagen"
    )
    expiring_90_days: Optional[int] = Field(
        None,
        description="Contratos expirando em 90 dias / Verträge ablaufend in 90 Tagen"
    )
    monthly_value: Optional[float] = Field(
        None,
        description="Valor mensal total (apenas Level 4+) / Monatlicher Gesamtwert (nur Level 4+)"
    )
    
    # =========================================================================
    # ALERTAS E APROVAÇÕES - ALERTS & APPROVALS (Levels 2-5)
    # =========================================================================
    total_alerts: Optional[int] = Field(
        None,
        description="Total de alertas / Gesamtzahl der Benachrichtigungen"
    )
    unread_alerts: Optional[int] = Field(
        None,
        description="Alertas não lidos / Ungelesene Benachrichtigungen"
    )
    pending_approvals: Optional[int] = Field(
        None,
        description="Aprovações pendentes / Ausstehende Genehmigungen"
    )
    
    # =========================================================================
    # ADMIN/DIRECTOR EXTRAS (Levels 5)
    # =========================================================================
    total_users: Optional[int] = Field(
        None,
        description="Total de usuários (apenas Director) / Gesamtzahl Benutzer (nur Director)"
    )
    contracts_by_department: Optional[Dict[str, int]] = Field(
        None,
        description="Contratos por departamento / Verträge nach Abteilung"
    )
    contracts_by_status: Optional[Dict[str, int]] = Field(
        None,
        description="Contratos por status / Verträge nach Status"
    )
    contracts_by_type: Optional[Dict[str, int]] = Field(
        None,
        description="Contratos por tipo / Verträge nach Typ"
    )
    
    # =========================================================================
    # SYSTEM ADMIN EXTRAS (Level 6) - Apenas técnico
    # =========================================================================
    last_backup: Optional[str] = Field(
        None,
        description="Data do último backup (apenas SYSTEM_ADMIN) / Datum des letzten Backups (nur SYSTEM_ADMIN)"
    )
    disk_usage_mb: Optional[float] = Field(
        None,
        description="Uso de disco em MB (apenas SYSTEM_ADMIN) / Festplattennutzung in MB (nur SYSTEM_ADMIN)"
    )
    total_database_size_mb: Optional[float] = Field(
        None,
        description="Tamanho total do banco de dados em MB / Gesamtgröße der Datenbank in MB"
    )
    active_sessions: Optional[int] = Field(
        None,
        description="Sessões ativas (apenas SYSTEM_ADMIN) / Aktive Sitzungen (nur SYSTEM_ADMIN)"
    )
    uptime_days: Optional[int] = Field(
        None,
        description="Dias de uptime do sistema / System-Betriebszeit in Tagen"
    )
    
    # =========================================================================
    # DEPARTMENT/TEAM SPECIFIC (Levels 2-4)
    # =========================================================================
    department_name: Optional[str] = Field(
        None,
        description="Nome do departamento / Abteilungsname"
    )
    team_name: Optional[str] = Field(
        None,
        description="Nome do time / Teamname"
    )
    team_contracts: Optional[int] = Field(
        None,
        description="Contratos do time / Team-Verträge"
    )
    department_users: Optional[int] = Field(
        None,
        description="Usuários do departamento / Benutzer der Abteilung"
    )
    
    # =========================================================================
    # METADATA
    # =========================================================================
    user_role: Optional[str] = Field(
        None,
        description="Role do usuário / Benutzerrolle"
    )
    user_access_level: Optional[int] = Field(
        None,
        description="Nível de acesso do usuário / Zugriffsstufe des Benutzers"
    )
    
    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "total_contracts": 42,
                "active_contracts": 35,
                "expiring_30_days": 5,
                "expiring_90_days": 12,
                "monthly_value": 125000.50,
                "total_alerts": 8,
                "unread_alerts": 3,
                "pending_approvals": 2,
                "department_name": "IT und Datenschutz",
                "team_name": "Infrastruktur",
                "user_role": "department_adm",
                "user_access_level": 4
            }
        }


class DashboardChartData(BaseModel):
    """
    Dados para gráficos do dashboard
    Daten für Dashboard-Diagramme
    """
    labels: List[str] = Field(
        ...,
        description="Rótulos do eixo X / X-Achsen-Beschriftungen"
    )
    values: List[int] = Field(
        ...,
        description="Valores do eixo Y / Y-Achsen-Werte"
    )
    chart_type: str = Field(
        ...,
        description="Tipo de gráfico (bar, line, pie) / Diagrammtyp"
    )
    title: str = Field(
        ...,
        description="Título do gráfico / Diagrammtitel"
    )
