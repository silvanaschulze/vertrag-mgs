"""
Permission utilities for the Contract Management System
Utilitários de permissão para o Sistema de Gerenciamento de Contratos

This module contains permission functions for different user roles.
Este módulo contém funções de permissão para diferentes funções de usuário.
"""

from app.models.user import User, UserRole
from fastapi import HTTPException, status


def require_role(user: User, role: UserRole) -> None:
    """
    Require specific role / Exigir função específica
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        role (UserRole): Required role / Função necessária
    """
    if user.role != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions / Permissões insuficientes",
        )


def require_admin(user: User) -> None:
    """
    Require ADMIN role / Exigir função ADMIN
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
    """
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin permissions required / Permissões de administrador necessárias",
        )


def require_manager_or_admin(user: User) -> None:
    """
    Require MANAGER or ADMIN role / Exigir função MANAGER ou ADMIN
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
    """
    if user.role not in [UserRole.MANAGER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager or Admin permissions required / Permissões de gerente ou administrador necessárias",
        )


def require_own_resource_or_admin(user: User, resource_owner_id: int) -> None:
    """
    Require user to own resource or be ADMIN / Exigir que usuário seja dono do recurso ou seja ADMIN
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        resource_owner_id (int): ID of resource owner / ID do dono do recurso
    """
    if user.role != UserRole.ADMIN and user.id != resource_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources / Acesso negado: Você pode apenas acessar seus próprios recursos",
        )


def can_view_contracts(user: User) -> bool:
    """
    Check if user can view contracts / Verificar se usuário pode visualizar contratos
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        
    Returns / Retorna:
        bool: True if can view / True se pode visualizar
    """
    return user.role in [UserRole.USER, UserRole.MANAGER, UserRole.ADMIN]


def can_create_contracts(user: User) -> bool:
    """
    Check if user can create contracts / Verificar se usuário pode criar contratos
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        
    Returns / Retorna:
        bool: True if can create / True se pode criar
    """
    return user.role in [UserRole.USER, UserRole.MANAGER, UserRole.ADMIN]


def can_edit_contracts(user: User) -> bool:
    """
    Check if user can edit contracts / Verificar se usuário pode editar contratos
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        
    Returns / Retorna:
        bool: True if can edit / True se pode editar
    """
    return user.role in [UserRole.MANAGER, UserRole.ADMIN]


def can_delete_contracts(user: User) -> bool:
    """
    Check if user can delete contracts / Verificar se usuário pode deletar contratos
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        
    Returns / Retorna:
        bool: True if can delete / True se pode deletar
    """
    return user.role in [UserRole.ADMIN, UserRole.MANAGER]


def can_delete_specific_contract(user: User, contract_owner_id: int) -> bool:
    """
    Check if user can delete a specific contract / Verificar se usuário pode deletar um contrato específico
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        contract_owner_id (int): ID of contract owner / ID do dono do contrato
        
    Returns / Retorna:
        bool: True if can delete / True se pode deletar
    """
    # ADMINs can delete any contract / ADMINs podem deletar qualquer contrato
    if user.role == UserRole.ADMIN:
        return True
    
    # MANAGERs can only delete their own contracts / MANAGERs podem deletar apenas seus próprios contratos
    if user.role == UserRole.MANAGER:
        return user.id == contract_owner_id
    
    # USERs cannot delete contracts / USERs não podem deletar contratos
    return False



def can_manage_users(user: User) -> bool:
    """
    Check if user can manage users / Verificar se usuário pode gerenciar usuários
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        
    Returns / Retorna:
        bool: True if can manage / True se pode gerenciar
    """
    return user.role == UserRole.ADMIN


def can_upload_documents(user: User) -> bool:
    """
    Check if user can upload documents / Verificar se usuário pode fazer upload de documentos
    
    Args / Argumentos:
        user (User): User object / Objeto usuário
        
    Returns / Retorna:
        bool: True if can upload / True se pode fazer upload
    """
    return user.role in [UserRole.USER, UserRole.MANAGER, UserRole.ADMIN]


def require_view_original(user: User, owner_id: int) -> None:
    """
    Erlaubt Zugriff auf die Original-PDF eines Vertrags:
    - ADMIN und MANAGER dürfen alle Originale sehen
    - Der Ersteller (owner_id) darf sein eigenes Original sehen
    Ansonsten wird HTTP 403 ausgelöst.
    """
    if user.role == UserRole.ADMIN:
        return
    if user.role == UserRole.MANAGER:
        return
    if user.id == owner_id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Zugriff verweigert: Original-PDF darf nicht eingesehen werden",
    )