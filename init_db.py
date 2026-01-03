#!/home/sschulze/projects/vertrag-mgs/.venv/bin/python
# type: ignore
"""
Inicializa o banco de dados e cria um usuário admin
Initialize database and create admin user
"""
import asyncio
import sys
import os
from pathlib import Path

# Mudar para o diretório backend
backend_dir = Path(__file__).parent / 'backend'
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect
from app.core.database import engine, Base
from app.models.user import User
from app.models.contract import Contract
from app.models.alert import Alert  
from app.models.rent_step import RentStep
from app.models.contract_approval import ContractApproval


async def init_database():
    """Cria todas as tabelas e usuário admin"""
    
    print("🔧 Iniciando banco de dados...")
    
    # Criar todas as tabelas
    async with engine.begin() as conn:
        # Verificar se as tabelas já existem
        def check_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()
        
        existing_tables = await conn.run_sync(check_tables)
        
        if existing_tables:
            print(f"⚠️  Tabelas existentes encontradas: {', '.join(existing_tables)}")
            response = input("Deseja recriar todas as tabelas? (ATENÇÃO: dados serão perdidos) [y/N]: ")
            if response.lower() == 'y':
                await conn.run_sync(Base.metadata.drop_all)
                print("🗑️  Tabelas antigas removidas")
        
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tabelas criadas com sucesso!")
    
    # Criar usuário admin
    from app.core.database import SessionLocal
    from app.models.user import UserRole, AccessLevel
    from app.utils.security import get_password_hash
    
    async with SessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.email == 'admin@test.com')
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print("ℹ️  Usuário admin@test.com já existe")
        else:
            admin = User(
                email='admin@test.com',
                name='System Admin',
                hashed_password=get_password_hash('admin123'),
                role=UserRole.SYSTEM_ADMIN,
                access_level=AccessLevel.SYSTEM,
                is_active=True,
                department_id=None,
                team_id=None
            )
            
            db.add(admin)
            await db.commit()
            await db.refresh(admin)
            
            print("✅ Usuário admin criado!")
    
    print("=" * 60)
    print("🎉 Banco de dados inicializado com sucesso!")
    print("=" * 60)
    print(f"📧 Email:    admin@test.com")
    print(f"🔑 Senha:    admin123")
    print(f"👤 Role:     SYSTEM_ADMIN")
    print(f"🔓 Level:    SYSTEM")
    print("=" * 60)
    print("\n🚀 Agora você pode fazer login em: http://localhost:5173/login")


if __name__ == '__main__':
    try:
        asyncio.run(init_database())
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
