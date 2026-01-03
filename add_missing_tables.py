#!/home/sschulze/projects/vertrag-mgs/.venv/bin/python
# type: ignore
"""
Cria apenas as tabelas faltantes (não apaga dados existentes)
Creates only missing tables (does not delete existing data)
"""
import asyncio
import sys
import os
from pathlib import Path

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


async def add_missing_tables():
    """Adiciona apenas tabelas que não existem"""
    
    print("🔍 Verificando banco de dados...")
    
    async with engine.begin() as conn:
        # Verificar tabelas existentes
        def check_tables(connection):
            inspector = inspect(connection)
            return set(inspector.get_table_names())
        
        existing = await conn.run_sync(check_tables)
        print(f"  Tabelas existentes: {', '.join(existing) if existing else 'nenhuma'}")
        
        # Criar apenas tabelas faltantes
        def create_missing(connection):
            # Pega os metadados de todas as tabelas definidas nos modelos
            all_tables = Base.metadata.tables
            
            # Cria apenas as que não existem
            for table_name, table in all_tables.items():
                if table_name not in existing:
                    print(f"  ➕ Criando tabela: {table_name}")
                    table.create(connection, checkfirst=True)
                else:
                    print(f"  ✓ Tabela já existe: {table_name}")
        
        await conn.run_sync(create_missing)
    
    print("\n✅ Banco de dados atualizado!")
    print("\nAgora execute: ./.venv/bin/python create_admin.py")


if __name__ == '__main__':
    try:
        asyncio.run(add_missing_tables())
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
