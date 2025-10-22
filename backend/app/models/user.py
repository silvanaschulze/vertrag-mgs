"""User Model - Benutzermodell"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

import enum
from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from .contract import Contract



from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles enumeration
    Benutzerrollen Aufzählung
    """
    USER = "user"
    MANAGER = "manager" 
    ADMIN = "admin"

class User(Base):
    """User model
    Benutzermodell
    """
    __tablename__ = "users"

    #Prämärschlüssel
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
   
    #Grundlegende Benutzerinformationen / Informações básicas do usuário
    username: Mapped[Optional[str]] = mapped_column(String(50), unique=True, index=True, nullable=True)  # ← ADICIONAR CAMPO USERNAME
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.USER, nullable=False)


    #Authentifizierungsinformationen
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    verification_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reset_token_expiration: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    
    #Zusätzliche Informationen
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    position: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    #Audit Felder
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # ForeignKey zu User.id kann hinzugefügt werden
    updated_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # ForeignKey zu User.id kann hinzugefügt werden
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # ForeignKey zu User.id kann hinzu
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv6 kompatibel
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    preferences: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON String für Benutzerpräferenzen

    #Beziehungen
    
    contracts: Mapped[list["Contract"]] = relationship("Contract", back_populates="creator") 
    
    """String Darstellung des Benutzers"""
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', name='{self.name}', role='{self.role.value}')>"   
    """Überprüft ob der Benutzer Admin ist """
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
    """Überprüft ob der Benutzer Manager ist """
    def is_manager(self) -> bool:
        return self.role == UserRole.MANAGER
    """Überprüft ob der Benutzer regulärer Benutzer ist """
    def is_user(self) -> bool:
        return self.role == UserRole.USER
    """Aktualisiert das letzte Login Datum und die IP Adresse"""
    def update_last_login(self, ip_address: Optional[str] = None):
        self.last_login = datetime.now(timezone.utc)
        if ip_address:
            self.last_login_ip = ip_address
    """Erhöht die Anzahl der fehlgeschlagenen Login Versuche"""
    def increment_failed_logins(self):
        self.failed_login_attempts += 1
    """Setzt die Anzahl der fehlgeschlagenen Login Versuche zurück"""
    def reset_failed_logins(self):
        self.failed_login_attempts = 0  
    """Markiert den Benutzer als gelöscht"""
    def mark_as_deleted(self, deleted_by: Optional[int] = None):
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)  # ← CORRIGIDO
        if deleted_by:
            self.deleted_by = deleted_by

    # Hilfsfunktionen für das User-Modell



def create_user(db, email: str, name: str, password_hash: str, role: UserRole = UserRole.USER, username: Optional[str] = None) -> User:
    """ Neuen Benutzer in der Datenbank erstellen
    Criar novo usuário no banco de dados
   """
    import warnings
    warnings.warn(
        "create_user(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )

    new_user = User(
        username=username,
        email=email,
        name=name,
        password_hash=password_hash,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def delete_user(db, user: User, deleted_by: Optional[int] = None):
    """Benutzer aus der Datenbank löschen (soft delete)
    """
    import warnings
    warnings.warn(
        "delete_user(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )
    user.mark_as_deleted(deleted_by)
    db.commit()


def update_user(db, user: User, **kwargs) -> User:
    """Benutzerinformationen aktualisieren
    """
    import warnings
    warnings.warn(
        "update_user(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def verify_user(db, user: User):
    """Benutzer verifizieren
    """
    import warnings
    warnings.warn(
        "verify_user(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db, user: User, new_password_hash: str):
    """Benutzerpasswort zurücksetzen
    """
    import warnings
    warnings.warn(
        "reset_user_password(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )
    user.password_hash = new_password_hash
    user.reset_token = None
    user.reset_token_expiration = None
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db, email: str) -> Optional[User]:
    """Benutzer anhand der E-Mail abrufen (ignoriert gelöschte Benutzer)"""
    import warnings
    warnings.warn(
        "get_user_by_email(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )
    return db.query(User).filter(User.email == email, User.is_deleted == False).first()


def authenticate_user(db, email: str, password_hash: str) -> Optional[User]:
    """Benutzer authentifizieren
    """
    import warnings
    warnings.warn(
        "authenticate_user(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )
    user = get_user_by_email(db, email)
    if user and user.password_hash == password_hash and user.is_active and not user.is_deleted:
        user.reset_failed_logins()
        db.commit()
        db.refresh(user)
        return user
    elif user:
        user.increment_failed_logins()
        db.commit()
        db.refresh(user)
    return None


def get_users_by_role(db, role: UserRole) -> list[User]:
    """Benutzer anhand ihrer Rolle abrufen
    """
    import warnings
    warnings.warn(
        "get_users_by_role(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )
    return db.query(User).filter(User.role == role, User.is_deleted == False).all()


def search_users(db, query: str) -> list[User]:
    """Benutzer anhand von Name, E-Mail oder Benutzername durchsuchen
    Buscar usuários por nome, e-mail ou nome de usuário
    """
    import warnings
    warnings.warn(
        "search_users(db, ...) is synchronous helper for scripts/tests. Use app.services.user_service.UserService for async code.",
        DeprecationWarning,
        stacklevel=2,
    )
    return db.query(User).filter(
        (User.name.ilike(f"%{query}%")) | 
        (User.email.ilike(f"%{query}%")) | 
        (User.username.ilike(f"%{query}%")),
        User.is_deleted == False
    ).all()