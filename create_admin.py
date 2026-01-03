#!/home/sschulze/projects/vertrag-mgs/.venv/bin/python
# type: ignore
"""
Script para criar usuário admin de teste
Skript zum Erstellen eines Admin-Testbenutzers
"""
import asyncio
import sys
import os
from pathlib import Path

# Mudar para o diretório backend (onde o contracts.db está)
backend_dir = Path(__file__).parent / 'backend'
os.chdir(backend_dir)

# Adiciona o diretório backend ao path
sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.models.user import User, UserRole, AccessLevel
from app.utils.security import get_password_hash


async def create_admin_user():
    """Cria usuário admin de teste / Erstellt Admin-Testbenutzer"""
    
    async with SessionLocal() as db:
        # Verificar se já existe
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.email == 'admin@test.com')
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("❌ Usuário admin@test.com já existe!")
            print("✅ Pode fazer login com: admin@test.com / admin123")
            return
        
        # Criar novo admin
        admin = User(
            email='admin@test.com',
            name='System Admin',
            password_hash=get_password_hash('admin123'),
            role=UserRole.SYSTEM_ADMIN,
            access_level=AccessLevel.LEVEL_6,
            is_active=True
        )
        
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        print("✅ Usuário criado com sucesso!")
        print("=" * 50)
        print(f"Email:    admin@test.com")
        print(f"Senha:    admin123")
        print(f"Role:     {admin.role}")
        print(f"Level:    {admin.access_level}")
        print("=" * 50)
        print("\n🚀 Agora você pode fazer login em: http://localhost:5173/login")


if __name__ == '__main__':
    try:
        asyncio.run(create_admin_user())
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        import traceback
        traceback.print_exc()
