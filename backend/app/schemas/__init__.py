"""
Schemas-Paket für das Vertragsverwaltungssystem

Dieses Modul enthält alle Pydantic-Schemas für die Validierung und Serialisierung von Daten.
Schemas definieren die Struktur der Daten, die an die API gesendet und von ihr empfangen werden können.
"""

# Alle Schemas hier importieren für einfachen Zugriff
from .user import (
    UserCreate, UserUpdate, UserResponse, UserInDB,
    UserRole, UserAdminCreate, UserAdminUpdate, UserAdminResponse
)
from .contract import ContractCreate, ContractUpdate, ContractResponse, ContractInDB, ContractListResponse, ContractStats
from .auth import Token, UserLogin, UserRegister

# Alle Schemas exportieren
__all__ = [
    # Benutzer-Schemas
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "UserInDB",
    "UserRole",
    "UserAdminCreate",
    "UserAdminUpdate", 
    "UserAdminResponse",
    
    # Vertrags-Schemas
    "ContractCreate",
    "ContractUpdate",
    "ContractResponse", 
    "ContractInDB",
    "ContractListResponse",
    "ContractStats",
    
    # Authentifizierungs-Schemas
    "Token",
    "UserLogin",
    "UserRegister"
]


