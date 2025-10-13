# app/routers/users.py
"""
 Benutzer-Router 
Endpoints da API para operações de gerenciamento de usuários
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserRole
from app.services.user_service import UserService
from app.core.security import get_current_user, get_current_active_user
from app.models.user import User

# Router-Instanz erstellen 
router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={
        404: {"description": " Benutzer nicht gefunden"},
        403: {"description": "Unzureichende Berechtigung"},
        401: {"description": "Authentifizierung erforderlich"}
    }
)
@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Alle Benutzer abrufen.
    Erfordert Authentifizierung.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können alle Benutzer auflisten"
        )
    users = await UserService(db).get_users(skip=skip, limit=limit)
    return users    

@router.get("/{user_id}", response_model=UserResponse)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Einen Benutzer nach ID abrufen.
    Erfordert Authentifizierung.
    """
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sie können nur Ihr eigenes Profil anzeigen"
        )

    user = await UserService(db).get_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=" Benutzer nicht gefunden")
    return user 

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Einen neuen Benutzer erstellen.
    Erfordert Authentifizierung.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können Benutzer erstellen"
        )
    
    db_user = await UserService(db).get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="E-Mail bereits registriert")
    new_user = await UserService(db).create_user(user=user)
    return new_user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Einen vorhandenen Benutzer aktualisieren.
    Erfordert Authentifizierung.
    """
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sie können nur Ihr eigenes Profil aktualisieren"
        )
    
    db_user = await UserService(db).get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=" Benutzer nicht gefunden")
    updated_user = await UserService(db).update_user(user_id=user_id, user=user)
    return updated_user 

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Einen Benutzer löschen.
    Erfordert Authentifizierung.
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sie können Ihr eigenes Konto nicht löschen"
        )
    db_user = await UserService(db).get_user(user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail=" Benutzer nicht gefunden")
    await UserService(db).delete_user(user_id=user_id)
    return None     

@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Mein Profil abrufen 
    Gibt die Daten des aktuell angemeldeten Benutzers zurück
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Mein Profil aktualisieren 
    Aktualisiert die Daten des aktuell angemeldeten Benutzers
    """
    updated_user = await UserService(db).update_user(
        user_id=current_user.id, 
        user=user
    )
    return updated_user


@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Benutzer aktivieren 
    Erfordert Admin-Berechtigung 
    """
    # Nur Administratoren können Benutzer aktivieren
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können Benutzer aktivieren"
        )
    
    db_user = await UserService(db).get_user_by_id(user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer nicht gefunden"
        )
    
    await UserService(db).activate_user(user_id)
    updated_user = await UserService(db).get_user_by_id(user_id)
    return updated_user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Benutzer deaktivieren
    Erfordert Admin-Berechtigung 
    """
    # Nur Administratoren können Benutzer deaktivieren
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können Benutzer deaktivieren"
        )
    
    # Verhindern dass sich ein Admin selbst deaktiviert
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sie können Ihr eigenes Konto nicht deaktivieren"
        )
    
    db_user = await UserService(db).get_user_by_id(user_id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benutzer nicht gefunden"
        )
    
    await UserService(db).deactivate_user(user_id)
    updated_user = await UserService(db).get_user_by_id(user_id)
    return updated_user

@router.get("/search/", response_model=List[UserResponse])
async def search_users(
    query: str,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Benutzer suchen 
    Erfordert Admin-Berechtigung 
    """
    # Nur Administratoren können Benutzer suchen
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Nur Administratoren können Benutzer suchen"
        )
    
    users = await UserService(db).search_users(query=query, skip=skip, limit=limit)
    return users

