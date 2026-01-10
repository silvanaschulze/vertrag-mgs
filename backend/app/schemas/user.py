"""
Benutzer-Schemas für das Vertragsverwaltungssystem

Dieses Modul enthält Pydantic-Schemas für die Validierung und Serialisierung von Benutzerdaten.
Verschiedene Schemas werden für verschiedene Operationen verwendet (erstellen, aktualisieren, antworten).
"""

from datetime import datetime
from typing import Optional
from enum import Enum, IntEnum
from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator, ConfigDict

# Zugriffsstufen Enumeration / Enumeração de níveis de acesso
class AccessLevel(IntEnum):
    """Zugriffsstufen für hierarchische Berechtigungen.
    Níveis de acesso para permissões hierárquicas.
    """
    LEVEL_1 = 1  # Basis (Colaborador) - Nur verantwortliche Verträge, keine Genehmigungen / Básico - Apenas contratos onde é responsável, não aprova
    LEVEL_2 = 2  # Team - Alle Verträge des Teams, kann erstellen/bearbeiten, keine Reports / Time - Todos contratos do time, pode criar/editar, sem relatórios
    LEVEL_3 = 3  # Department User - Alle Verträge des Bereichs, kann genehmigen, Reports ohne Werte / Dept User - Todos contratos do depto, pode aprovar, relatórios sem valores
    LEVEL_4 = 4  # Department Admin - Volle Bereichsrechte, Reports mit Werten / Dept Admin - Direitos completos do depto, relatórios com valores
    LEVEL_5 = 5  # Geschäftsführung - Unternehmensweiter Zugriff, alle Reports / Diretoria - Acesso em toda empresa, todos relatórios
    LEVEL_6 = 6  # System Admin - NUR technische Rechte (Configs, Logs, Backups), KEINE Verträge/Reports / Admin Sistema - APENAS direitos técnicos, SEM contratos/relatórios

# Benutzer-Rollen Enumeration
class UserRole(str, Enum):
    """Systemrollen für Benutzer.
    Papéis técnicos do sistema.
    """
    SYSTEM_ADMIN = "system_admin"        # TI / Admin técnico
    DIRECTOR = "director"                # Geschäftsführung / Diretoria
    DEPARTMENT_USER = "department_user"  # Leiter mit eingeschränkten Funktionen
    DEPARTMENT_ADM = "department_adm"    # Leiter mit Admin-Funktionen
    TEAM_LEAD = "team_lead"              # Teamleiter / Líder de time
    STAFF = "staff"                      # Mitarbeiter / Colaborador
    READ_ONLY = "read_only"              # Nur Lesezugriff / Somente leitura
    

# Basis-Schema mit gemeinsamen Feldern
class UserBase(BaseModel):
    """Basis-Schema mit gemeinsamen Benutzerfeldern / Schema base com campos comuns de usuário"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Benutzername / Nome de usuário")
    email: EmailStr = Field(..., description="Benutzer-E-Mail-Adresse / Endereço de e-mail do usuário")
    name: str = Field(..., min_length=2, max_length=100, description="Vollständiger Name des Benutzers / Nome completo do usuário")
    department: Optional[str] = Field(None, max_length=100, description="Bereich / Departamento")
    team: Optional[str] = Field(None, max_length=100, description="Team / Time")
    role: UserRole = Field(default=UserRole.STAFF, description="Benutzerrolle / Função do usuário")
    access_level: int = Field(default=AccessLevel.LEVEL_1, ge=1, le=6, description="Zugriffsstufe (1-6) / Nível de acesso (1-6)")

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
        """Validar que apenas SYSTEM_ADMIN ou DIRECTOR podem ser superuser.
        Validar que apenas SYSTEM_ADMIN ou DIRECTOR podem ser superusuários.
        """
        data = info.data or {}
        if v and data.get("role") not in [UserRole.SYSTEM_ADMIN, UserRole.DIRECTOR]:
            raise ValueError("Nur SYSTEM_ADMIN oder DIRECTOR können Superuser sein / Apenas SYSTEM_ADMIN ou DIRECTOR podem ser superusuários")
        return v

# Schema für die Aktualisierung von Benutzerdaten
class UserUpdate(BaseModel):
    """Schema für die Aktualisierung von Benutzerdaten / Schema para atualização de dados de usuário"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Benutzername / Nome de usuário")
    email: Optional[EmailStr] = Field(None, description="Benutzer-E-Mail-Adresse / Endereço de e-mail do usuário")
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Vollständiger Name des Benutzers / Nome completo do usuário")
    department: Optional[str] = Field(None, max_length=100, description="Bereich / Departamento")
    team: Optional[str] = Field(None, max_length=100, description="Team / Time")
    role: Optional[UserRole] = Field(None, description="Benutzerrolle / Função do usuário")
    access_level: Optional[int] = Field(None, ge=1, le=6, description="Zugriffsstufe (1-6) / Nível de acesso (1-6)")
    password: Optional[str] = Field(None, min_length=8, description="Benutzerpasswort / Senha do usuário")

# Schema für Benutzerdaten in der Datenbank (enthält gehashtes Passwort)
class UserInDB(UserBase):
    """Schema für Benutzerdaten wie in der Datenbank gespeichert"""
    id: int = Field(..., description="Eindeutiger Benutzerbezeichner")
    password_hash: str = Field(..., description="Gehashtes Passwort")
    created_at: datetime = Field(..., description="Zeitstempel der Benutzererstellung")
    updated_at: Optional[datetime] = Field(None, description="Zeitstempel der letzten Aktualisierung")
    
    model_config = ConfigDict(from_attributes=True)

# Schema für API-Antworten (schließt sensible Daten aus)
class UserResponse(UserBase):
    """Schema für Benutzerdaten in API-Antworten"""
    id: int = Field(..., description="Eindeutiger Benutzerbezeichner")
    created_at: datetime = Field(..., description="Zeitstempel der Benutzererstellung")
    updated_at: Optional[datetime] = Field(None, description="Zeitstempel der letzten Aktualisierung")
    
    model_config = ConfigDict(from_attributes=True)

# Administrator-spezifische Schemas
class UserAdminCreate(UserCreate):
    """Schema für Administrator zum Erstellen von Benutzern"""
    role: UserRole = Field(default=UserRole.STAFF, description="Benutzerrolle (Administrator kann jede Rolle setzen)")
    model_config = ConfigDict(from_attributes=True)

class UserAdminUpdate(UserUpdate):
    """Schema für Administrator zum Aktualisieren von Benutzern"""
    role: Optional[UserRole] = Field(None, description="Benutzerrolle (Administrator kann Rollen ändern)")
    is_active: Optional[bool] = Field(None, description="Aktiver Benutzerstatus")

class UserAdminResponse(UserResponse):
    """Schema für Administrator zum Anzeigen von Benutzerdetails"""
    is_active: bool = Field(..., description="Aktiver Benutzerstatus")
    last_login: Optional[datetime] = Field(None, description="Zeitstempel der letzten Anmeldung")
