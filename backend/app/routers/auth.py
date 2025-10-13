"""Autentifizierungs - Router.
Behandelt Endpunkte für die Benutzeranmeldung, Token-Generierung und Token-Validierung.
"""

from datetime import timedelta, datetime, timezone
from typing import Any, Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt  
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports - Lokale Importe
from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.token import Token
from backend.app.services.user_service import UserService


# Router-Konfiguration
# Router configuration 
router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={
        404: {"description": "Not found - Nicht gefunden"},
        401: {"description": "Unauthorized - Nicht autorisiert"},
        403: {"description": "Forbidden - Verboten"}
    }
)

# Sicherheitskonfiguration

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT-Einstellungen

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token de acesso expira em 30 minutos
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Token de refresh expira em 7 dias

# Hilfsfunktionen 
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """ Passwort verifizieren """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Passwort hashen """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Zugriffstoken erstellen """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Aktualisierungstoken erstellen """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db)
) -> User:
    """ Aktuellen authentifizierten Benutzer abrufen"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials - Anmeldedaten konnten nicht validiert werden",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Benutzer aus Datenbank abrufen
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Aktuellen aktiven Benutzer abrufen"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user - Inaktiver Benutzer"
        )
    return current_user

# Authentifizierungs-Endpunkte - Endpoints de autenticação

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Anmelde-Endpunkt -
    Benutzer authentifizieren und Zugriffstoken zurückgeben

    """
    # Benutzerservice abrufen
    user_service = UserService(db)
    
    # Benutzer authentifizieren
    user = await user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password - Falscher Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user - Inaktiver Benutzer"
        )
    
    # Zugriffstoken erstellen
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user - Neuen Benutzer registrieren - 
    Neues Benutzerkonto erstellen
    """
    # Benutzerservice abrufen
    user_service = UserService(db)
    
    try:
        # Benutzer erstellen
        user = await user_service.create_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Abmelde-Endpunkt 
    Benutzer abmelden (in einer echten App würde man den Token sperren)
    """
    return {"message": "Successfully logged out - Erfolgreich abgemeldet - Logout realizado com sucesso"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Aktuelle Benutzerinformationen abrufen 
    Aktuelle authentifizierte Benutzerinformationen zurückgeben
    """
    return current_user




