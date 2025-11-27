"""
Permission utilities for the Contract Management System
Utilitários de permissão para o Sistema de Gerenciamento de Contratos

This module contains permission functions for different user roles.
Este módulo contém funções de permissão para diferentes funções de usuário.
"""

# pyright: reportGeneralTypeIssues=false
# pylance: ignore=reportGeneralTypeIssues
# Note: Pylance warnings about ColumnElement are false positives when
# comparing loaded model instances (which have Python values, not SQL expressions)

from typing import Optional, Dict, Any
from app.models.user import User, UserRole, AccessLevel
from app.models.contract import Contract
from fastapi import HTTPException, status


# =============================================================================
# PERFIS PADRÃO / STANDARD PROFILES
# =============================================================================

PERFIS_PADRAO: Dict[str, Dict[str, Any]] = {
    "Geschäftsführung": {
        "role": UserRole.DIRECTOR,
        "access_level": AccessLevel.LEVEL_5,
        "department": "Geschäftsführung",
        "team": None,
        "description_de": "Geschäftsführung mit Zugriff auf alle Verträge und Reports",
    },
    "Leiter_Personal_Organization_Finanzen": {
        "role": UserRole.DEPARTMENT_ADM,
        "access_level": AccessLevel.LEVEL_4,
        "department": "Personal Organization und Finanzen",
        "team": None,
        "description_de": "Bereichsleiter mit vollen Admin-Rechten im Bereich Personal/Org/Finanzen",
        
    },
    "Leiter_Technischer_Bereich": {
        "role": UserRole.DEPARTMENT_USER,
        "access_level": AccessLevel.LEVEL_3,
        "department": "Technischer Bereich",
        "team": None,
        "description_de": "Bereichsleiter mit eingeschränkten Funktionen im Technischen Bereich",
       
    },
    "Leiter_IT_Datenschutz": {
        "role": UserRole.DEPARTMENT_ADM,
        "access_level": AccessLevel.LEVEL_4,
        "department": "IT und Datenschutz",
        "team": None,
        "description_de": "Bereichsleiter IT mit vollen Admin-Rechten",
       
    },
    "Systemadministrator_TI": {
        "role": UserRole.SYSTEM_ADMIN,
        "access_level": AccessLevel.LEVEL_6,
        "department": "IT und Datenschutz",
        "team": "Informationstechnologie",
        "description_de": "Technischer Systemadministrator mit Vollzugriff",
        
    },
    "Mitarbeiter_Team_PR": {
        "role": UserRole.STAFF,
        "access_level": AccessLevel.LEVEL_2,
        "department": "IT und Datenschutz",
        "team": "PR",
        "description_de": "Mitarbeiter im Team PR",
      
    },
    "Mitarbeiter_Team_Finanzen": {
        "role": UserRole.STAFF,
        "access_level": AccessLevel.LEVEL_2,
        "department": "Personal Organization und Finanzen",
        "team": "Finanzen und Rechnungswesen",
        "description_de": "Mitarbeiter im Team Finanzen",
        
    }
}


# =============================================================================
# FUNÇÕES DE VERIFICAÇÃO DE ROLES / ROLE CHECKING FUNCTIONS
# =============================================================================

def require_role(user: User, role: UserRole) -> None:
    """Erfordert eine bestimmte Rolle.
    Exigir função específica.
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        role: Erforderliche Rolle / Função necessária
    """
    if user.role != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions / Permissões insuficientes",
        )


def require_system_admin(user: User) -> None:
    """Erfordert SYSTEM_ADMIN Rolle.
    Exigir função SYSTEM_ADMIN.
    
    Args:
        user: Benutzerobjekt / Objeto usuário
    """
    if user.role != UserRole.SYSTEM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System Admin permissions required / Permissões de administrador do sistema necessárias",
        )


def require_director(user: User) -> None:
    """Erfordert DIRECTOR Rolle.
    Exigir função DIRECTOR.
    
    Args:
        user: Benutzerobjekt / Objeto usuário
    """
    if user.role != UserRole.DIRECTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Director permissions required / Permissões de diretor necessárias",
        )


def require_director_or_system_admin(user: User) -> None:
    """Erfordert DIRECTOR oder SYSTEM_ADMIN Rolle.
    Exigir função DIRECTOR ou SYSTEM_ADMIN.
    
    Args:
        user: Benutzerobjekt / Objeto usuário
    """
    if user.role not in [UserRole.DIRECTOR, UserRole.SYSTEM_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Director or System Admin permissions required / Permissões de diretor ou admin sistema necessárias",
        )


def require_min_access_level(user: User, min_level: int) -> None:
    """Erfordert eine Mindestzugriffsstufe.
    Exigir nível mínimo de acesso.
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        min_level: Mindestzugriffsstufe (1-6) / Nível mínimo (1-6)
    """
    if user.access_level < min_level:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access level {min_level} or higher required / Nível de acesso {min_level} ou superior necessário",
        )


# =============================================================================
# FUNÇÕES DE PERMISSÃO DE CONTRATOS / CONTRACT PERMISSION FUNCTIONS
# =============================================================================

def can_view_contract(user: User, contract: Contract) -> bool:
    """Prüft, ob der Benutzer den Vertrag sehen darf.
    Verifica se o usuário pode visualizar o contrato.
    
    Logik / Lógica:
    - SYSTEM_ADMIN (Level 6): Alles / Tudo
    - DIRECTOR (Level 5): Alles / Tudo
    - DEPARTMENT_ADM (Level 4): Alle Verträge des eigenen Bereichs / Todos contratos do próprio departamento
    - DEPARTMENT_USER (Level 3): Alle Verträge des eigenen Bereichs / Todos contratos do próprio departamento
    - TEAM_LEAD (Level 2): Verträge des eigenen Teams / Contratos do próprio time
    - STAFF (Level 2): Verträge des eigenen Teams oder eigene / Contratos do próprio time ou próprios
    - STAFF (Level 1): Nur eigene Verträge / Apenas contratos próprios
    - READ_ONLY: Je nach Level / Conforme o nível
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        contract: Vertragsobjekt / Objeto contrato
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # Level 6: SYSTEM_ADMIN - sieht alles
    if user.access_level >= AccessLevel.LEVEL_6:
        return True
    
    # Level 5: DIRECTOR - sieht alles
    if user.access_level >= AccessLevel.LEVEL_5:
        return True
    
    # Level 4: DEPARTMENT_ADM - sieht alle Verträge des eigenen Bereichs
    if user.access_level >= AccessLevel.LEVEL_4:
        return contract.department == user.department
    
    # Level 3: DEPARTMENT_USER - sieht alle Verträge des eigenen Bereichs
    if user.access_level >= AccessLevel.LEVEL_3:
        return contract.department == user.department
    # Level 2: TEAM_LEAD oder STAFF - sieht Verträge des eigenen Teams
    if user.access_level >= AccessLevel.LEVEL_2:
        # Kann Team-Verträge sehen
        if contract.team is not None and user.team is not None and contract.team == user.team:
            return True
        # Kann eigene Verträge sehen
        if contract.created_by == user.id:
            return True
        if contract.responsible_user_id is not None and contract.responsible_user_id == user.id:
            return True
    # Level 1: Nur eigene Verträge
    is_creator = contract.created_by == user.id
    is_responsible = contract.responsible_user_id is not None and contract.responsible_user_id == user.id
    return bool(is_creator or is_responsible)


def can_edit_contract(user: User, contract: Contract) -> bool:
    """Prüft, ob der Benutzer den Vertrag bearbeiten darf.
    Verifica se o usuário pode editar o contrato.
    
    Logik / Lógica:
    - SYSTEM_ADMIN (Level 6): Alles / Tudo
    - DIRECTOR (Level 5): Alles / Tudo
    - DEPARTMENT_ADM (Level 4): Alle Verträge des eigenen Bereichs / Todos contratos do próprio departamento
    - DEPARTMENT_USER (Level 3): Alle Verträge des eigenen Bereichs / Todos contratos do próprio departamento
    - TEAM_LEAD: Verträge des eigenen Teams / Contratos do próprio time
    - STAFF: Nur eigene Verträge oder Team-Verträge (wenn Level 2) / Apenas próprios ou do time (se Level 2)
    - READ_ONLY: Nichts / Nada
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        contract: Vertragsobjekt / Objeto contrato
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # READ_ONLY kann nichts bearbeiten
    if user.role == UserRole.READ_ONLY:
        return False
    
    # Level 6: SYSTEM_ADMIN
    if user.access_level >= AccessLevel.LEVEL_6:
        return True
    
    # Level 5: DIRECTOR
    if user.access_level >= AccessLevel.LEVEL_5:
        return True
    
    # Level 4: DEPARTMENT_ADM - kann alle Verträge des Bereichs bearbeiten
    if user.access_level >= AccessLevel.LEVEL_4:
        return contract.department == user.department
    
    # Level 3: DEPARTMENT_USER - kann alle Verträge des Bereichs bearbeiten
    # TEAM_LEAD - kann Team-Verträge bearbeiten
    if user.role == UserRole.TEAM_LEAD:
        if contract.team is not None and user.team is not None and contract.team == user.team:
            return True
        # Kann eigene bearbeiten
        if contract.created_by == user.id:
            return True
    # STAFF Level 2 - kann Team-Verträge und eigene bearbeiten
    if user.role == UserRole.STAFF and user.access_level >= AccessLevel.LEVEL_2:
        if contract.team is not None and user.team is not None and contract.team == user.team:
            return True
        if contract.created_by == user.id:
            return True
    # STAFF Level 1 - nur eigene Verträge
    if user.role == UserRole.STAFF:
        if contract.created_by == user.id:
            return True
        if contract.responsible_user_id is not None and contract.responsible_user_id == user.id:
            return True
        return False
    
    return False


def can_delete_contract(user: User, contract: Contract) -> bool:
    """Prüft, ob der Benutzer den Vertrag löschen darf.
    Verifica se o usuário pode deletar o contrato.
    
    Logik / Lógica:
    - SYSTEM_ADMIN (Level 6): Alles / Tudo
    - DIRECTOR (Level 5): Alles / Tudo
    - DEPARTMENT_ADM (Level 4): Alle Verträge des eigenen Bereichs / Todos contratos do próprio departamento
    - DEPARTMENT_USER (Level 3): Keine Löschrechte / Sem direitos de exclusão
    - Andere: Keine Löschrechte / Outros: Sem direitos de exclusão
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        contract: Vertragsobjekt / Objeto contrato
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # Level 6: SYSTEM_ADMIN
    if user.access_level >= AccessLevel.LEVEL_6:
        return True
    
    # Level 5: DIRECTOR
    if user.access_level >= AccessLevel.LEVEL_5:
        return True
    
    # Level 4: DEPARTMENT_ADM - kann Verträge des eigenen Bereichs löschen
    if user.access_level >= AccessLevel.LEVEL_4 and user.role == UserRole.DEPARTMENT_ADM:
        return contract.department == user.department
    
    return False


def can_approve_contract(user: User, contract: Contract) -> bool:
    """Prüft, ob der Benutzer den Vertrag genehmigen darf.
    Verifica se o usuário pode aprovar o contrato.
    
    Logik / Lógica:
    - SYSTEM_ADMIN (Level 6): Alles / Tudo
    - DIRECTOR (Level 5): Alles (strategisch relevante) / Tudo (estratégicos)
    - DEPARTMENT_ADM (Level 4): Verträge des eigenen Bereichs / Contratos do próprio departamento
    - DEPARTMENT_USER (Level 3): Verträge des eigenen Bereichs / Contratos do próprio departamento
    - TEAM_LEAD: Verträge des eigenen Teams / Contratos do próprio time
    - Andere: Keine Genehmigungsrechte / Outros: Sem direitos de aprovação
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        contract: Vertragsobjekt / Objeto contrato
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # Level 6: SYSTEM_ADMIN
    if user.access_level >= AccessLevel.LEVEL_6:
        return True
    
    # Level 5: DIRECTOR - genehmigt strategisch relevante Verträge
    if user.access_level >= AccessLevel.LEVEL_5:
        return True
    
    # Level 4: DEPARTMENT_ADM - genehmigt Bereichsverträge
    if user.access_level >= AccessLevel.LEVEL_4 and user.role == UserRole.DEPARTMENT_ADM:
        return contract.department == user.department
    
    # Level 3: DEPARTMENT_USER - genehmigt Bereichsverträge
    if user.access_level >= AccessLevel.LEVEL_3 and user.role == UserRole.DEPARTMENT_USER:
        return contract.department == user.department
    
    # TEAM_LEAD - genehmigt Team-Verträge
    if user.role == UserRole.TEAM_LEAD:
        return contract.team is not None and user.team is not None and contract.team == user.team
    
    return False


# =============================================================================
# FUNÇÕES DE PERMISSÃO DE USUÁRIOS / USER PERMISSION FUNCTIONS
# =============================================================================

def can_manage_users(user: User, target_user: Optional[User] = None) -> bool:
    """Prüft, ob der Benutzer andere Benutzer verwalten darf.
    Verifica se o usuário pode gerenciar outros usuários.
    
    Logik / Lógica:
    - SYSTEM_ADMIN (Level 6): Alle Benutzer / Todos usuários
    - DIRECTOR (Level 5): Alle Benutzer / Todos usuários
    - DEPARTMENT_ADM (Level 4): Benutzer des eigenen Bereichs / Usuários do próprio departamento
    - DEPARTMENT_USER (Level 3): Benutzer des eigenen Bereichs (eingeschränkt) / Usuários do próprio departamento (restrito)
    - Andere: Keine Verwaltungsrechte / Outros: Sem direitos de gerenciamento
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        target_user: Zielbenutzer (optional) / Usuário alvo (opcional)
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # Level 6: SYSTEM_ADMIN - kann alle Benutzer verwalten
    if user.access_level >= AccessLevel.LEVEL_6:
        return True
    
    # Level 5: DIRECTOR - kann alle Benutzer verwalten
    if user.access_level >= AccessLevel.LEVEL_5:
        return True
    
    # Level 4: DEPARTMENT_ADM - kann Benutzer des eigenen Bereichs verwalten
    if user.access_level >= AccessLevel.LEVEL_4 and user.role == UserRole.DEPARTMENT_ADM:
        if target_user:
            return target_user.department == user.department
        return True  # Kann Benutzer im eigenen Bereich erstellen
    
    # Level 3: DEPARTMENT_USER - kann Benutzer des eigenen Bereichs verwalten (eingeschränkt)
    if user.access_level >= AccessLevel.LEVEL_3 and user.role == UserRole.DEPARTMENT_USER:
        if target_user:
            # Kann nur Benutzer mit Level <= 3 verwalten
            return target_user.department == user.department and target_user.access_level <= AccessLevel.LEVEL_3
        return True  # Kann Benutzer im eigenen Bereich erstellen
    
    return False


def can_set_user_role(user: User, target_role: UserRole, target_level: int) -> bool:
    """Prüft, ob der Benutzer eine bestimmte Rolle und Level vergeben darf.
    Verifica se o usuário pode definir uma função e nível específicos.
    
    Logik / Lógica:
    - SYSTEM_ADMIN (Level 6): Alle Rollen und Levels / Todas funções e níveis
    - DIRECTOR (Level 5): Alle Rollen bis Level 5 / Todas funções até nível 5
    - DEPARTMENT_ADM (Level 4): Rollen bis Level 4 / Funções até nível 4
    - DEPARTMENT_USER (Level 3): Rollen bis Level 3 / Funções até nível 3
    - Andere: Keine Rechte / Outros: Sem direitos
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        target_role: Zielrolle / Função alvo
        target_level: Ziellevel / Nível alvo
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # Level 6: SYSTEM_ADMIN - kann alles setzen
    if user.access_level >= AccessLevel.LEVEL_6:
        return True
    
    # Level 5: DIRECTOR - kann bis Level 5 setzen
    if user.access_level >= AccessLevel.LEVEL_5:
        return target_level <= AccessLevel.LEVEL_5
    
    # Level 4: DEPARTMENT_ADM - kann bis Level 4 setzen
    if user.access_level >= AccessLevel.LEVEL_4 and user.role == UserRole.DEPARTMENT_ADM:
        return target_level <= AccessLevel.LEVEL_4
    
    # Level 3: DEPARTMENT_USER - kann bis Level 3 setzen
    if user.access_level >= AccessLevel.LEVEL_3 and user.role == UserRole.DEPARTMENT_USER:
        return target_level <= AccessLevel.LEVEL_3
    
    return False


def can_access_reports(user: User, include_financials: bool = False) -> bool:
    """Prüft, ob der Benutzer auf Reports zugreifen darf.
    Verifica se o usuário pode acessar relatórios.
    
    Logik / Lógica:
    - SYSTEM_ADMIN (Level 6): Alle Reports / Todos relatórios
    - DIRECTOR (Level 5): Alle Reports / Todos relatórios
    - DEPARTMENT_ADM (Level 4): Vollständige Reports des Bereichs / Relatórios completos do departamento
    - DEPARTMENT_USER (Level 3): Eingeschränkte Reports (ohne Beträge) / Relatórios restritos (sem valores)
    - Andere: Keine Reports / Outros: Sem relatórios
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        include_financials: Ob Finanzinformationen enthalten sind / Se inclui informações financeiras
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # Level 6: SYSTEM_ADMIN
    if user.access_level >= AccessLevel.LEVEL_6:
        return True
    
    # Level 5: DIRECTOR
    if user.access_level >= AccessLevel.LEVEL_5:
        return True
    
    # Level 4: DEPARTMENT_ADM - volle Reports im Bereich
    if user.access_level >= AccessLevel.LEVEL_4 and user.role == UserRole.DEPARTMENT_ADM:
        return True
    
    # Level 3: DEPARTMENT_USER - eingeschränkte Reports (keine Beträge)
    if user.access_level >= AccessLevel.LEVEL_3 and user.role == UserRole.DEPARTMENT_USER:
        return not include_financials
    
    return False


# =============================================================================
# FUNÇÕES AUXILIARES DE COMPATIBILIDADE / COMPATIBILITY HELPER FUNCTIONS
# =============================================================================

def can_view_contracts(user: User) -> bool:
    """Prüft, ob der Benutzer Verträge sehen kann (allgemein).
    Verifica se o usuário pode visualizar contratos (geral).
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # Alle außer explizit deaktivierte Benutzer können Verträge sehen
    return user.is_active and not user.is_deleted


def can_create_contracts(user: User) -> bool:
    """Prüft, ob der Benutzer Verträge erstellen kann.
    Verifica se o usuário pode criar contratos.
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # READ_ONLY kann keine Verträge erstellen
    if user.role == UserRole.READ_ONLY:
        return False
    
    return user.is_active and not user.is_deleted


def can_upload_documents(user: User) -> bool:
    """Prüft, ob der Benutzer Dokumente hochladen kann.
    Verifica se o usuário pode fazer upload de documentos.
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        
    Returns:
        bool: True wenn erlaubt / True se permitido
    """
    # READ_ONLY kann keine Dokumente hochladen
    if user.role == UserRole.READ_ONLY:
        return False
    
    return user.is_active and not user.is_deleted


def require_view_original(user: User, owner_id: int) -> None:
    """Erlaubt Zugriff auf die Original-PDF eines Vertrags.
    Permite acesso ao PDF original de um contrato.
    
    Logik / Lógica:
    - SYSTEM_ADMIN, DIRECTOR: Alle Originale / Todos originais
    - DEPARTMENT_ADM, DEPARTMENT_USER: Originale des eigenen Bereichs / Originais do próprio departamento
    - Ersteller: Eigene Originale / Próprios originais
    
    Args:
        user: Benutzerobjekt / Objeto usuário
        owner_id: ID des Vertragserstellers / ID do criador do contrato
    """
    # Level 5+: DIRECTOR, SYSTEM_ADMIN
    if user.access_level >= AccessLevel.LEVEL_5:
        return
    
    # Level 3+: DEPARTMENT_USER, DEPARTMENT_ADM
    if user.access_level >= AccessLevel.LEVEL_3:
        return  # Bereichszugriff wird in der Hauptlogik geprüft
    
    # Eigene Verträge
    if user.id == owner_id:
        return
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Zugriff verweigert: Original-PDF darf nicht eingesehen werden / Acesso negado: PDF original não pode ser visualizado",
    )


# Manter funções antigas para compatibilidade com código existente (deprecated)
def require_admin(user: User) -> None:
    """DEPRECATED: Use require_system_admin() ou require_director() stattdessen.
    OBSOLETO: Use require_system_admin() ou require_director() no lugar.
    """
    require_director_or_system_admin(user)


def require_manager_or_admin(user: User) -> None:
    """DEPRECATED: Use require_min_access_level(user, 3) stattdessen.
    OBSOLETO: Use require_min_access_level(user, 3) no lugar.
    """
    require_min_access_level(user, AccessLevel.LEVEL_3)


def can_edit_contracts(user: User) -> bool:
    """DEPRECATED: Use can_edit_contract(user, contract) stattdessen.
    OBSOLETO: Use can_edit_contract(user, contract) no lugar.
    """
    return user.role != UserRole.READ_ONLY and user.is_active


def can_delete_contracts(user: User) -> bool:
    """DEPRECATED: Use can_delete_contract(user, contract) stattdessen.
    OBSOLETO: Use can_delete_contract(user, contract) no lugar.
    """
    return user.access_level >= AccessLevel.LEVEL_4


def can_delete_specific_contract(user: User, contract_owner_id: int) -> bool:
    """DEPRECATED: Use can_delete_contract(user, contract) stattdessen.
    OBSOLETO: Use can_delete_contract(user, contract) no lugar.
    """
    return user.access_level >= AccessLevel.LEVEL_4


def require_own_resource_or_admin(user: User, resource_owner_id: int) -> None:
    """DEPRECATED: Use específicas can_* Funktionen stattdessen.
    OBSOLETO: Use funções específicas can_* no lugar.
    """
    if user.access_level >= AccessLevel.LEVEL_5:
        return
    if user.id != resource_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources / Acesso negado: Você pode apenas acessar seus próprios recursos",
        )