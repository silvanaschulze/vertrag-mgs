"""
Benutzer-Schemas für das Vertragsverwaltungssystem

Dieses Modul enthält Pydantic-Schemas für die Validierung und Serialisierung von Benutzerdaten.
Verschiedene Schemas werden für verschiedene Operationen verwendet (erstellen, aktualisieren, antworten).
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

# Benutzer-Rollen Enumeration
class UserRole(str, Enum):
    """Benutzer-Rollen Enumeration"""
    USER = "user"           # Regulärer Benutzer - kann eigene Verträge einsehen
    MANAGER = "manager"     # Manager - kann Team-Verträge verwalten
    ADMIN = "admin"         # Administrator -  voller Systemzugriff
    

# Basis-Schema mit gemeinsamen Feldern
class UserBase(BaseModel):
    """Basis-Schema mit gemeinsamen Benutzerfeldern / Schema base com campos comuns de usuário"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Benutzername / Nome de usuário")
    email: EmailStr = Field(..., description="Benutzer-E-Mail-Adresse / Endereço de e-mail do usuário")
    name: str = Field(..., min_length=2, max_length=100, description="Vollständiger Name des Benutzers / Nome completo do usuário")
    role: UserRole = Field(default=UserRole.USER, description="Benutzerrolle / Função do usuário")

# Schema für die Erstellung eines neuen Benutzers
class UserCreate(UserBase):
    """Schema für die Erstellung eines neuen Benutzers"""
    password: str = Field(..., min_length=8, description="Benutzerpasswort (mindestens 8 Zeichen)")
    is_active: bool = Field(default=True, description="Benutzer ist aktiv / Usuário está ativo")
    is_superuser: bool = Field(default=False, description="Benutzer ist Superuser (nur für ADMIN) / Usuário é superusuário (apenas para ADMIN)")

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Passwortstärke validieren"""
        if len(v) < 8:
            raise ValueError('Das Passwort muss mindestens 8 Zeichen lang sein')
        if not any(c.isupper() for c in v):
            raise ValueError('Das Passwort muss mindestens einen Großbuchstaben enthalten')
        if not any(c.islower() for c in v):
            raise ValueError('Das Passwort muss mindestens einen Kleinbuchstaben enthalten')
        if not any(c.isdigit() for c in v):
            raise ValueError('Das Passwort muss mindestens eine Zahl enthalten')
        return v
    
@field_validator("is_superuser")
@classmethod
def validate_superuser(cls, v: bool, info: ValidationInfo) -> bool:
    """Validar que apenas ADMINs podem ser superuser"""
    data = info.data or {}
    if v and data.get("role") != UserRole.ADMIN:
        raise ValueError("Nur ADMINs können Superuser sein / Apenas ADMINs podem ser superusuários")
    return v

# Schema für die Aktualisierung von Benutzerdaten
class UserUpdate(BaseModel):
    """Schema für die Aktualisierung von Benutzerdaten / Schema para atualização de dados de usuário"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Benutzername / Nome de usuário")
    email: Optional[EmailStr] = Field(None, description="Benutzer-E-Mail-Adresse / Endereço de e-mail do usuário")
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Vollständiger Name des Benutzers / Nome completo do usuário")
    role: Optional[UserRole] = Field(None, description="Benutzerrolle / Função do usuário")
    password: Optional[str] = Field(None, min_length=8, description="Benutzerpasswort / Senha do usuário")

# Schema für Benutzerdaten in der Datenbank (enthält gehashtes Passwort)
class UserInDB(UserBase):
    """Schema für Benutzerdaten wie in der Datenbank gespeichert"""
    id: int = Field(..., description="Eindeutiger Benutzerbezeichner")
    password_hash: str = Field(..., description="Gehashtes Passwort")
    created_at: datetime = Field(..., description="Zeitstempel der Benutzererstellung")
    updated_at: Optional[datetime] = Field(None, description="Zeitstempel der letzten Aktualisierung")
    
    class Config:
        from_attributes = True  # Ermöglicht Konvertierung vom SQLAlchemy-Modell

# Schema für API-Antworten (schließt sensible Daten aus)
class UserResponse(UserBase):
    """Schema für Benutzerdaten in API-Antworten"""
    id: int = Field(..., description="Eindeutiger Benutzerbezeichner")
    created_at: datetime = Field(..., description="Zeitstempel der Benutzererstellung")
    updated_at: Optional[datetime] = Field(None, description="Zeitstempel der letzten Aktualisierung")
    
    class Config:
        from_attributes = True  # Ermöglicht Konvertierung vom SQLAlchemy-Modell

# Administrator-spezifische Schemas
class UserAdminCreate(UserCreate):
    """Schema für Administrator zum Erstellen von Benutzern"""
    role: UserRole = Field(default=UserRole.USER, description="Benutzerrolle (Administrator kann jede Rolle setzen)")
    class Config:
        from_attributes = True

class UserAdminUpdate(UserUpdate):
    """Schema für Administrator zum Aktualisieren von Benutzern"""
    role: Optional[UserRole] = Field(None, description="Benutzerrolle (Administrator kann Rollen ändern)")
    is_active: Optional[bool] = Field(None, description="Aktiver Benutzerstatus")

class UserAdminResponse(UserResponse):
    """Schema für Administrator zum Anzeigen von Benutzerdetails"""
    is_active: bool = Field(..., description="Aktiver Benutzerstatus")
    last_login: Optional[datetime] = Field(None, description="Zeitstempel der letzten Anmeldung")
