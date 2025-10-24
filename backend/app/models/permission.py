"""
Berechtigungsmodell für das Vertragsverwaltungssystem
Modelo de permissão para o Sistema de Gerenciamento de Contratos

Dieses Modul definiert das Berechtigungsmodell für Benutzerrollen.
Este módulo define o modelo de permissão para funções de usuário.
"""

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Permission(Base):
    """
    Berechtigungsmodell / Modelo de permissão
    
    Definiert die verschiedenen Berechtigungen im System.
    Define as diferentes permissões no sistema.
    """
    __tablename__ = "permissions"
    
    # Primärschlüssel / Chave primária
    id = Column(Integer, primary_key=True, index=True)
    
    # Grundlegende Felder / Campos básicos
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Audit-Felder / Campos de auditoria
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    def __repr__(self) -> str:
        """
        String-Darstellung der Berechtigung / Representação em string da permissão
        """
        return f"<Permission(id={self.id}, name='{self.name}', active={self.is_active})>"
    
    def is_granted(self) -> bool:
        """
        Überprüft, ob die Berechtigung gewährt ist / Verifica se a permissão é concedida
        
        Returns / Retorna:
            bool: True wenn gewährt / True se concedida
        """
        return bool(self.is_active)