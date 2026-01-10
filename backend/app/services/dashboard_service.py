"""
Dashboard Service - Dashboard-Dienst
Business logic for dashboard statistics
Geschäftslogik für Dashboard-Statistiken

Este serviço filtra estatísticas baseado no role e access_level do usuário,
respeitando as novas regras de permissão onde System Admin (Level 6) NÃO
tem acesso a contratos/relatórios, apenas dados técnicos.

Dieser Service filtert Statistiken basierend auf der Rolle und Zugriffsstufe
des Benutzers und respektiert die neuen Berechtigungsregeln, bei denen
System Admin (Level 6) KEINEN Zugriff auf Verträge/Berichte hat, nur auf
technische Daten.
"""

import os
from datetime import datetime, timedelta, date
from typing import Dict, Optional
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole, AccessLevel
from app.models.contract import Contract, ContractStatus
from app.models.alert import Alert, AlertStatus
from app.schemas.dashboard import DashboardStats


class DashboardService:
    """
    Serviço de estatísticas do dashboard
    Dashboard-Statistikdienst
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa o serviço com uma sessão de banco de dados
        Initialisiert den Service mit einer Datenbanksitzung
        
        Args:
            db: SQLAlchemy async session
        """
        self.db = db
    
    async def get_stats_by_role(self, user: User) -> DashboardStats:
        """
        Retorna estatísticas filtradas pelo role do usuário
        Gibt Statistiken gefiltert nach Benutzerrolle zurück
        
        Lógica / Logik:
        - Level 6 (SYSTEM_ADMIN): APENAS dados técnicos (sem contratos)
        - Level 5 (DIRECTOR): Todas estatísticas da empresa
        - Level 4 (DEPARTMENT_ADM): Estatísticas completas do departamento
        - Level 3 (DEPARTMENT_USER): Estatísticas do departamento sem valores
        - Level 2 (TEAM): Estatísticas do time
        - Level 1 (STAFF): Apenas contratos próprios
        
        Args:
            user: Objeto User com role e access_level
            
        Returns:
            DashboardStats com campos preenchidos conforme permissões
        """
        # Level 6: SYSTEM_ADMIN - apenas dados técnicos
        if user.access_level >= AccessLevel.LEVEL_6:
            return await self._get_system_admin_stats(user)
        
        # Level 5: DIRECTOR - tudo da empresa
        elif user.access_level >= AccessLevel.LEVEL_5:
            return await self._get_director_stats(user)
        
        # Level 4: DEPARTMENT_ADM - departamento completo
        elif user.access_level >= AccessLevel.LEVEL_4:
            return await self._get_department_adm_stats(user)
        
        # Level 3: DEPARTMENT_USER - departamento sem valores
        elif user.access_level >= AccessLevel.LEVEL_3:
            return await self._get_department_user_stats(user)
        
        # Level 2: TEAM - time
        elif user.access_level >= AccessLevel.LEVEL_2:
            return await self._get_team_stats(user)
        
        # Level 1: STAFF - apenas próprios
        else:
            return await self._get_staff_stats(user)
    
    # =========================================================================
    # MÉTODOS PRIVADOS POR ROLE / PRIVATE METHODS BY ROLE
    # =========================================================================
    
    async def _get_system_admin_stats(self, user: User) -> DashboardStats:
        """
        Estatísticas para SYSTEM_ADMIN (Level 6)
        APENAS dados técnicos, SEM contratos/relatórios
        
        Statistiken für SYSTEM_ADMIN (Level 6)
        NUR technische Daten, KEINE Verträge/Berichte
        """
        # Total de usuários no sistema
        total_users_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_deleted == False)
        )
        total_users = total_users_result.scalar() or 0
        
        # Usuários ativos (últimos 30 dias)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_users_result = await self.db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.is_deleted == False,
                    User.last_login >= thirty_days_ago
                )
            )
        )
        active_sessions = active_users_result.scalar() or 0
        
        # Tamanho do banco de dados (SQLite)
        db_size_mb = 0.0
        try:
            db_path = "backend/contracts.db"
            if os.path.exists(db_path):
                db_size_mb = os.path.getsize(db_path) / (1024 * 1024)  # Bytes para MB
        except Exception:
            pass
        
        # Uso de disco (diretório uploads)
        disk_usage_mb = 0.0
        try:
            upload_dir = "uploads"
            if os.path.exists(upload_dir):
                total_size = 0
                for dirpath, dirnames, filenames in os.walk(upload_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        if os.path.exists(filepath):
                            total_size += os.path.getsize(filepath)
                disk_usage_mb = total_size / (1024 * 1024)
        except Exception:
            pass
        
        # Data do último backup (simulado - implementar lógica real)
        last_backup = "N/A"
        
        # Uptime (simulado - implementar lógica real de uptime)
        uptime_days = 0
        
        return DashboardStats(
            # SEM estatísticas de contratos para System Admin
            total_contracts=None,
            active_contracts=None,
            expiring_30_days=None,
            expiring_90_days=None,
            monthly_value=None,
            
            # SEM alertas/aprovações
            total_alerts=None,
            unread_alerts=None,
            pending_approvals=None,
            
            # Dados técnicos
            total_users=total_users,
            last_backup=last_backup,
            disk_usage_mb=round(disk_usage_mb, 2),
            total_database_size_mb=round(db_size_mb, 2),
            active_sessions=active_sessions,
            uptime_days=uptime_days,
            
            # Metadata
            user_role=user.role.value,
            user_access_level=user.access_level
        )
    
    async def _get_director_stats(self, user: User) -> DashboardStats:
        """
        Estatísticas para DIRECTOR (Level 5)
        Todos contratos da empresa + relatórios completos
        
        Statistiken für DIRECTOR (Level 5)
        Alle Verträge des Unternehmens + vollständige Berichte
        """
        # Total de contratos
        total_result = await self.db.execute(
            select(func.count(Contract.id))
        )
        total_contracts = total_result.scalar() or 0
        
        # Contratos ativos
        active_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                Contract.status == ContractStatus.ACTIVE
            )
        )
        active_contracts = active_result.scalar() or 0
        
        # Expirando em 30 dias
        today = date.today()
        thirty_days = today + timedelta(days=30)
        exp30_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(
                    Contract.end_date.isnot(None),
                    Contract.end_date <= thirty_days,
                    Contract.end_date >= today,
                    Contract.status == ContractStatus.ACTIVE
                )
            )
        )
        expiring_30_days = exp30_result.scalar() or 0
        
        # Expirando em 90 dias
        ninety_days = today + timedelta(days=90)
        exp90_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(
                    Contract.end_date.isnot(None),
                    Contract.end_date <= ninety_days,
                    Contract.end_date >= today,
                    Contract.status == ContractStatus.ACTIVE
                )
            )
        )
        expiring_90_days = exp90_result.scalar() or 0
        
        # Valor mensal total
        value_result = await self.db.execute(
            select(func.sum(Contract.value)).where(
                Contract.status == ContractStatus.ACTIVE
            )
        )
        monthly_value = float(value_result.scalar() or 0.0)
        
        # Alertas
        alerts_result = await self.db.execute(
            select(func.count(Alert.id))
        )
        total_alerts = alerts_result.scalar() or 0
        
        unread_result = await self.db.execute(
            select(func.count(Alert.id)).where(
                Alert.status == AlertStatus.PENDING
            )
        )
        unread_alerts = unread_result.scalar() or 0
        
        # Aprovações pendentes (simulado - implementar quando houver tabela)
        pending_approvals = 0
        
        # Total de usuários
        users_result = await self.db.execute(
            select(func.count(User.id)).where(User.is_deleted == False)
        )
        total_users = users_result.scalar() or 0
        
        # Contratos por departamento
        dept_result = await self.db.execute(
            select(Contract.department, func.count(Contract.id))
            .where(Contract.department.isnot(None))
            .group_by(Contract.department)
        )
        contracts_by_department = {dept: count for dept, count in dept_result.all()}
        
        # Contratos por status
        status_result = await self.db.execute(
            select(Contract.status, func.count(Contract.id))
            .group_by(Contract.status)
        )
        contracts_by_status = {status.value: count for status, count in status_result.all()}
        
        # Contratos por tipo
        type_result = await self.db.execute(
            select(Contract.contract_type, func.count(Contract.id))
            .group_by(Contract.contract_type)
        )
        contracts_by_type = {ctype.value: count for ctype, count in type_result.all()}
        
        return DashboardStats(
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            expiring_30_days=expiring_30_days,
            expiring_90_days=expiring_90_days,
            monthly_value=monthly_value,
            total_alerts=total_alerts,
            unread_alerts=unread_alerts,
            pending_approvals=pending_approvals,
            total_users=total_users,
            contracts_by_department=contracts_by_department,
            contracts_by_status=contracts_by_status,
            contracts_by_type=contracts_by_type,
            user_role=user.role.value,
            user_access_level=user.access_level
        )
    
    async def _get_department_adm_stats(self, user: User) -> DashboardStats:
        """
        Estatísticas para DEPARTMENT_ADM (Level 4)
        Contratos do departamento + valores financeiros
        
        Statistiken für DEPARTMENT_ADM (Level 4)
        Verträge der Abteilung + Finanzwerte
        """
        dept_filter = Contract.department == user.department
        
        # Total de contratos do departamento
        total_result = await self.db.execute(
            select(func.count(Contract.id)).where(dept_filter)
        )
        total_contracts = total_result.scalar() or 0
        
        # Contratos ativos
        active_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(dept_filter, Contract.status == ContractStatus.ACTIVE)
            )
        )
        active_contracts = active_result.scalar() or 0
        
        # Expirando em 30 dias
        today = date.today()
        thirty_days = today + timedelta(days=30)
        exp30_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(
                    dept_filter,
                    Contract.end_date.isnot(None),
                    Contract.end_date <= thirty_days,
                    Contract.end_date >= today,
                    Contract.status == ContractStatus.ACTIVE
                )
            )
        )
        expiring_30_days = exp30_result.scalar() or 0
        
        # Expirando em 90 dias
        ninety_days = today + timedelta(days=90)
        exp90_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(
                    dept_filter,
                    Contract.end_date.isnot(None),
                    Contract.end_date <= ninety_days,
                    Contract.end_date >= today,
                    Contract.status == ContractStatus.ACTIVE
                )
            )
        )
        expiring_90_days = exp90_result.scalar() or 0
        
        # Valor mensal (PODE ver valores financeiros)
        value_result = await self.db.execute(
            select(func.sum(Contract.value)).where(
                and_(dept_filter, Contract.status == ContractStatus.ACTIVE)
            )
        )
        monthly_value = float(value_result.scalar() or 0.0)
        
        # Alertas do departamento
        alerts_subq = select(Contract.id).where(dept_filter).scalar_subquery()
        alerts_result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.contract_id.in_(alerts_subq))
        )
        total_alerts = alerts_result.scalar() or 0
        
        unread_result = await self.db.execute(
            select(func.count(Alert.id)).where(
                and_(
                    Alert.contract_id.in_(alerts_subq),
                    Alert.status == AlertStatus.PENDING
                )
            )
        )
        unread_alerts = unread_result.scalar() or 0
        
        # Aprovações pendentes
        pending_approvals = 0
        
        # Usuários do departamento
        dept_users_result = await self.db.execute(
            select(func.count(User.id)).where(
                and_(
                    User.department == user.department,
                    User.is_deleted == False
                )
            )
        )
        department_users = dept_users_result.scalar() or 0
        
        return DashboardStats(
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            expiring_30_days=expiring_30_days,
            expiring_90_days=expiring_90_days,
            monthly_value=monthly_value,
            total_alerts=total_alerts,
            unread_alerts=unread_alerts,
            pending_approvals=pending_approvals,
            department_name=user.department,
            department_users=department_users,
            user_role=user.role.value,
            user_access_level=user.access_level
        )
    
    async def _get_department_user_stats(self, user: User) -> DashboardStats:
        """
        Estatísticas para DEPARTMENT_USER (Level 3)
        Contratos do departamento SEM valores financeiros
        
        Statistiken für DEPARTMENT_USER (Level 3)
        Verträge der Abteilung OHNE Finanzwerte
        """
        dept_filter = Contract.department == user.department
        
        # Total de contratos do departamento
        total_result = await self.db.execute(
            select(func.count(Contract.id)).where(dept_filter)
        )
        total_contracts = total_result.scalar() or 0
        
        # Contratos ativos
        active_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(dept_filter, Contract.status == ContractStatus.ACTIVE)
            )
        )
        active_contracts = active_result.scalar() or 0
        
        # Expirando em 30 dias
        today = date.today()
        thirty_days = today + timedelta(days=30)
        exp30_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(
                    dept_filter,
                    Contract.end_date.isnot(None),
                    Contract.end_date <= thirty_days,
                    Contract.end_date >= today,
                    Contract.status == ContractStatus.ACTIVE
                )
            )
        )
        expiring_30_days = exp30_result.scalar() or 0
        
        # Expirando em 90 dias
        ninety_days = today + timedelta(days=90)
        exp90_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(
                    dept_filter,
                    Contract.end_date.isnot(None),
                    Contract.end_date <= ninety_days,
                    Contract.end_date >= today,
                    Contract.status == ContractStatus.ACTIVE
                )
            )
        )
        expiring_90_days = exp90_result.scalar() or 0
        
        # NÃO retorna valores financeiros (monthly_value = None)
        
        # Alertas
        alerts_subq = select(Contract.id).where(dept_filter).scalar_subquery()
        alerts_result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.contract_id.in_(alerts_subq))
        )
        total_alerts = alerts_result.scalar() or 0
        
        unread_result = await self.db.execute(
            select(func.count(Alert.id)).where(
                and_(
                    Alert.contract_id.in_(alerts_subq),
                    Alert.status == AlertStatus.PENDING
                )
            )
        )
        unread_alerts = unread_result.scalar() or 0
        
        # Aprovações pendentes
        pending_approvals = 0
        
        return DashboardStats(
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            expiring_30_days=expiring_30_days,
            expiring_90_days=expiring_90_days,
            monthly_value=None,  # SEM valores financeiros
            total_alerts=total_alerts,
            unread_alerts=unread_alerts,
            pending_approvals=pending_approvals,
            department_name=user.department,
            user_role=user.role.value,
            user_access_level=user.access_level
        )
    
    async def _get_team_stats(self, user: User) -> DashboardStats:
        """
        Estatísticas para TEAM (Level 2)
        Contratos do time, SEM relatórios
        
        Statistiken für TEAM (Level 2)
        Verträge des Teams, KEINE Berichte
        """
        team_filter = Contract.team == user.team
        
        # Total de contratos do time
        total_result = await self.db.execute(
            select(func.count(Contract.id)).where(team_filter)
        )
        total_contracts = total_result.scalar() or 0
        
        # Contratos ativos
        active_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(team_filter, Contract.status == ContractStatus.ACTIVE)
            )
        )
        active_contracts = active_result.scalar() or 0
        
        # Expirando em 30 dias
        today = date.today()
        thirty_days = today + timedelta(days=30)
        exp30_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(
                    team_filter,
                    Contract.end_date.isnot(None),
                    Contract.end_date <= thirty_days,
                    Contract.end_date >= today,
                    Contract.status == ContractStatus.ACTIVE
                )
            )
        )
        expiring_30_days = exp30_result.scalar() or 0
        
        # Alertas do time
        alerts_subq = select(Contract.id).where(team_filter).scalar_subquery()
        alerts_result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.contract_id.in_(alerts_subq))
        )
        total_alerts = alerts_result.scalar() or 0
        
        unread_result = await self.db.execute(
            select(func.count(Alert.id)).where(
                and_(
                    Alert.contract_id.in_(alerts_subq),
                    Alert.status == AlertStatus.PENDING
                )
            )
        )
        unread_alerts = unread_result.scalar() or 0
        
        return DashboardStats(
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            expiring_30_days=expiring_30_days,
            expiring_90_days=None,  # Não mostra 90 dias para simplificar
            monthly_value=None,  # SEM valores financeiros
            total_alerts=total_alerts,
            unread_alerts=unread_alerts,
            pending_approvals=None,  # Level 2 não aprova
            team_name=user.team,
            department_name=user.department,
            user_role=user.role.value,
            user_access_level=user.access_level
        )
    
    async def _get_staff_stats(self, user: User) -> DashboardStats:
        """
        Estatísticas para STAFF (Level 1)
        APENAS contratos próprios
        
        Statistiken für STAFF (Level 1)
        NUR eigene Verträge
        """
        # Filtro: apenas contratos onde é responsável
        own_filter = or_(
            Contract.created_by == user.id,
            Contract.responsible_user_id == user.id
        )
        
        # Total de contratos próprios
        total_result = await self.db.execute(
            select(func.count(Contract.id)).where(own_filter)
        )
        total_contracts = total_result.scalar() or 0
        
        # Contratos ativos
        active_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(own_filter, Contract.status == ContractStatus.ACTIVE)
            )
        )
        active_contracts = active_result.scalar() or 0
        
        # Expirando em 30 dias
        today = date.today()
        thirty_days = today + timedelta(days=30)
        exp30_result = await self.db.execute(
            select(func.count(Contract.id)).where(
                and_(
                    own_filter,
                    Contract.end_date.isnot(None),
                    Contract.end_date <= thirty_days,
                    Contract.end_date >= today,
                    Contract.status == ContractStatus.ACTIVE
                )
            )
        )
        expiring_30_days = exp30_result.scalar() or 0
        
        # Alertas próprios
        alerts_subq = select(Contract.id).where(own_filter).scalar_subquery()
        alerts_result = await self.db.execute(
            select(func.count(Alert.id)).where(Alert.contract_id.in_(alerts_subq))
        )
        total_alerts = alerts_result.scalar() or 0
        
        unread_result = await self.db.execute(
            select(func.count(Alert.id)).where(
                and_(
                    Alert.contract_id.in_(alerts_subq),
                    Alert.status == AlertStatus.PENDING
                )
            )
        )
        unread_alerts = unread_result.scalar() or 0
        
        return DashboardStats(
            total_contracts=total_contracts,
            active_contracts=active_contracts,
            expiring_30_days=expiring_30_days,
            expiring_90_days=None,
            monthly_value=None,
            total_alerts=total_alerts,
            unread_alerts=unread_alerts,
            pending_approvals=None,
            user_role=user.role.value,
            user_access_level=user.access_level
        )
