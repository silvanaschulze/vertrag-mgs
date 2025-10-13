"""
User Model - Benutzermodell 
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

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
    id = Column(Integer, primary_key=True, index=True)
   
    #Grundlegende Benutzerinformationen / Informações básicas do usuário
    username = Column(String(50), unique=True, index=True, nullable=True)  # ← ADICIONAR CAMPO USERNAME
    email = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)


    #Authentifizierungsinformationen
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expiration = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0)
    
    #Zusätzliche Informationen
    phone = Column(String(20), nullable=True)
    position = Column(String(100), nullable=True)

    #Audit Felder
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    created_by = Column(Integer, nullable=True)  # ForeignKey zu User.id kann hinzugefügt werden
    updated_by = Column(Integer, nullable=True)  # ForeignKey zu User.id kann hinzugefügt werden
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    deleted_by = Column(Integer, nullable=True)  # ForeignKey zu User.id kann hinzu
    is_deleted = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_login_ip = Column(String(45), nullable=True)  # IPv6 kompatibel
    notes = Column(String(500), nullable=True)
    preferences = Column(Text, nullable=True)  # JSON String für Benutzerpräferenzen

    #Beziehungen
    contracts = relationship("Contract", back_populates="creator")  
    files = relationship("File", back_populates="uploader")  
    notifications = relationship("Notification", back_populates="recipient")  
    activities = relationship("ActivityLog", back_populates="user")  
    responsible_contracts = relationship("Contract", back_populates="responsible") 

    
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

def get_user_by_id(db, user_id: int) -> Optional[User]:
    """ Benutzer anhand der ID aus der Datenbank abrufen
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db, email: str) -> Optional[User]:
    """Benutzer anhand der E-Mail aus der Datenbank abrufen
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db, username: str) -> Optional[User]:
    """Benutzer anhand des Benutzernamens aus der Datenbank abrufen
    Recuperar usuário por nome de usuário do banco de dados
    """
    return db.query(User).filter(User.username == username).first()


def get_active_users(db) -> List[User]:
    """Alle aktiven Benutzer aus der Datenbank abrufen
    """
    return db.query(User).filter(User.is_active == True, User.is_deleted == False).all()

def create_user(db, email: str, name: str, password_hash: str, role: UserRole = UserRole.USER, username: Optional[str] = None) -> User:
    """ Neuen Benutzer in der Datenbank erstellen
    Criar novo usuário no banco de dados
   """
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
    user.mark_as_deleted(deleted_by)
    db.commit()


def update_user(db, user: User, **kwargs) -> User:
    """Benutzerinformationen aktualisieren
    """
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


def verify_user(db, user: User):
    """Benutzer verifizieren
    """
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)
    return user


def reset_user_password(db, user: User, new_password_hash: str):
    """Benutzerpasswort zurücksetzen
    """
    user.password_hash = new_password_hash
    user.reset_token = None
    user.reset_token_expiration = None
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db, email: str, password_hash: str) -> Optional[User]:
    """Benutzer authentifizieren
    """
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


def get_users_by_role(db, role: UserRole) -> List[User]:
    """Benutzer anhand ihrer Rolle abrufen
    """
    return db.query(User).filter(User.role == role, User.is_deleted == False).all()


def search_users(db, query: str) -> List[User]:
    """Benutzer anhand von Name, E-Mail oder Benutzername durchsuchen
    Buscar usuários por nome, e-mail ou nome de usuário
    """
    return db.query(User).filter(
        (User.name.ilike(f"%{query}%")) | 
        (User.email.ilike(f"%{query}%")) | 
        (User.username.ilike(f"%{query}%")),
        User.is_deleted == False
    ).all()