# app/services/user.py
"""
Geschäftslogik für Benutzeroperationen
"""

from typing import Optional, List
from typing import cast
from sqlalchemy import select, update, delete, or_, func
from sqlalchemy.ext.asyncio import AsyncSession


from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.security import get_password_hash, verify_password

class UserService:
    """Benutzerservice-Klasse """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Neuen Benutzer erstellen 
        """
        # Prüfen ob Benutzer bereits existiert
        existing_user: Optional[User] = None
        if user_data.username:
            existing_user = await self.get_user_by_username(user_data.username)
        if existing_user:
            raise ValueError("Username already exists - Benutzername bereits vorhanden - Nome de usuário já existe")
        
        # Prüfen ob E-Mail bereits existiert
        existing_email = await self.get_user_by_email(user_data.email)
        if existing_email:
            raise ValueError("Email already exists - E-Mail bereits vorhanden - E-mail já existe")
        
        # Benutzer erstellen / Criar usuário
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            name=getattr(user_data, "name", None) or getattr(user_data, "full_name", None),
            password_hash=hashed_password,
            role=user_data.role,
            is_active=user_data.is_active,
            is_superuser=user_data.is_superuser
        )
        
        self.db.add(db_user)
        await self.db.flush()      # pega PK sem precisar commitar
        await self.db.refresh(db_user)
        await self.db.commit()
        return db_user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Benutzer nach ID abrufen 
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """
        Benutzer nach ID abrufen (Alias für get_user_by_id)
        """
        return await self.get_user_by_id(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Benutzer nach Benutzername abrufen
        """
        """result = await self.db.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()"""

        if not username:
            return None
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Benutzer nach E-Mail abrufen 
        """
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
       Benutzer authentifizieren 
        """
        user = await self.get_user_by_username(username)
        if not user:
            return None
        
        hashed = cast(str, getattr(user, "password_hash"))
        if not verify_password(password, hashed):  # ← Corrigir: hashed_password para password_hash
            return None
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """
        Benutzer aktualisieren 
        """
        # Bestehenden Benutzer abrufen
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Felder aktualisieren / Atualizar campos
        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))  # ← Corrigir: hashed_password para password_hash
        
        await self.db.execute(
            update(User).where(User.id == user_id).values(**update_data)
        )
        await self.db.commit()
        
        # Aktualisierten Benutzer zurückgeben
        return await self.get_user_by_id(user_id)
    
    async def delete_user(self, user_id: int) -> bool:
        """
         Benutzer löschen 
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True
    
    async def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Benutzerliste abrufen 
        """
        result = await self.db.execute(
            select(User).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
       
    
    async def activate_user(self, user_id: int) -> bool:
        """
        Benutzer aktivieren 
        """
        await self.db.execute(
            update(User).where(User.id == user_id).values(is_active=True)
        )
        await self.db.commit()
        return True
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Benutzer deaktivieren 
        """
        await self.db.execute(
            update(User).where(User.id == user_id).values(is_active=False)
        )
        await self.db.commit()
        return True

    async def search_users(self, query: str, skip: int = 0, limit: int = 100) -> List[User]:
        """
       Benutzer nach Name, E-Mail oder Benutzername suchen 
        
        """
        # Suche in Benutzername, E-Mail und vollständigem Namen
      
        pattern = f"%{query}%"
        stmt = (
            select(User)
            .where(or_(User.username.ilike(pattern), User.email.ilike(pattern), User.name.ilike(pattern)))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())