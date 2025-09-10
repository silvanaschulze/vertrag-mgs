# app/schemas/token.py
"""
Pydantic-Modelle für JWT-Tokens und Authentifizierungsantworten
"""

from typing import Optional
from pydantic import BaseModel, Field

class Token(BaseModel):
    """Token response model - Token-Antwortmodell """
    access_token: str = Field(..., description="Access token - Zugriffstoken - Token de acesso")
    token_type: str = Field(default="bearer", description="Token type - Token-Typ - Tipo de token")
    expires_in: int = Field(..., description="Expiration time in seconds - Ablaufzeit in Sekunden - Tempo de expiração em segundos")

class TokenData(BaseModel):
    """Token data model - Token-Datenmodell """
    username: Optional[str] = Field(None, description="Username - Benutzername - Nome de usuário")
    user_id: Optional[int] = Field(None, description="User ID - Benutzer-ID - ID do usuário")
    scopes: list[str] = Field(default_factory=list, description="Token scopes - Token-Bereiche - Escopos do token")

class RefreshTokenRequest(BaseModel):
    """Refresh token request model - Refresh-Token-Anfragemodell"""
    refresh_token: str = Field(..., description="Refresh token - Aktualisierungstoken - Token de atualização")

class LoginRequest(BaseModel):
    """Login request model - Anmeldeanfragemodell """
    username: str = Field(..., description="Username - Benutzername - Nome de usuário")
    password: str = Field(..., description="Password - Passwort - Senha")

class LoginResponse(BaseModel):
    """Login response model - Anmeldeantwortmodell """
    access_token: str = Field(..., description="Access token - Zugriffstoken - Token de acesso")
    refresh_token: str = Field(..., description="Refresh token - Aktualisierungstoken - Token de atualização")
    token_type: str = Field(default="bearer", description="Token type - Token-Typ - Tipo de token")
    expires_in: int = Field(..., description="Expiration time in seconds - Ablaufzeit in Sekunden - Tempo de expiração em segundos")
    user: dict = Field(..., description="User information - Benutzerinformationen - Informações do usuário")
