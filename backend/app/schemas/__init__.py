# app/schemas/__init__.py
"""
Schema-Paket 
"""

#  Nur existierende Schemas importieren - Importar apenas schemas existentes
from .token import (
    Token, 
    TokenData, 
    RefreshTokenRequest, 
    LoginRequest, 
    LoginResponse
)

# Alle verfügbaren Schemas exportieren 
__all__ = [
    # Token-Schemas
    "Token",
    "TokenData", 
    "RefreshTokenRequest",
    "LoginRequest",
    "LoginResponse"
]
