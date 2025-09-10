"""
Schemas-Paket für das Vertragsverwaltungssystem

Dieses Modul enthält alle Pydantic-Schemas für die Validierung und Serialisierung von Daten.
Schemas definieren die Struktur der Daten, die an die API gesendet und von ihr empfangen werden können.
"""

# Alle Schemas hier importieren für einfachen Zugriff

from .token import (
    Token, 
    TokenData, 
    RefreshTokenRequest, 
    LoginRequest, 
    LoginResponse
)

__all__ = [
    # Token-Schemas
    "Token",
    "TokenData", 
    "RefreshTokenRequest",
    "LoginRequest",
    "LoginResponse"
]

