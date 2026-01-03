#!/home/sschulze/projects/vertrag-mgs/.venv/bin/python
# type: ignore
"""Verifica as tabelas do banco de dados"""
import asyncio
import sys
import os
from pathlib import Path

backend_dir = Path(__file__).parent / 'backend'
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

from sqlalchemy import inspect, text
from app.core.database import engine


async def check_database():
    """Verifica estrutura do banco"""
    
    async with engine.connect() as conn:
        # Listar tabelas
        def get_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names()
        
        tables = await conn.run_sync(get_tables)
        
        print("\n📊 TABELAS NO BANCO DE DADOS:")
        print("=" * 60)
        if not tables:
            print("⚠️  Nenhuma tabela encontrada!")
        else:
            for table in tables:
                print(f"  ✓ {table}")
        
        # Contar usuários se a tabela existir
        if 'users' in tables:
            result = await conn.execute(text("SELECT COUNT(*) FROM users"))
            count = result.scalar()
            print("\n👥 USUÁRIOS:")
            print("=" * 60)
            print(f"  Total: {count} usuário(s)")
            
            if count > 0:
                result = await conn.execute(text("SELECT email, name, role FROM users"))
                users = result.fetchall()
                print("\n  Lista de usuários:")
                for user in users:
                    print(f"    • {user[0]} - {user[1]} ({user[2]})")
        
        print("\n" + "=" * 60)


if __name__ == '__main__':
    asyncio.run(check_database())
