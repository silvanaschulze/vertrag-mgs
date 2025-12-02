"""
Pytest Configuration and Shared Fixtures
Konfiguration und gemeinsame Fixtures für Pytest

DE: Zentrale Konfiguration für alle Tests.
PT: Configuração central para todos os testes.
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao PYTHONPATH para todos os testes
# Backend-Verzeichnis zum PYTHONPATH für alle Tests hinzufügen
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Define o backend anyio para testes assíncronos
    Definiert anyio-Backend für asynchrone Tests
    """
    return "asyncio"


@pytest.fixture
async def test_engine():
    """
    Cria engine de banco de dados in-memory para testes
    Erstellt In-Memory-Datenbankengine für Tests
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    await engine.dispose()


@pytest.fixture
async def test_session(test_engine):
    """
    Cria sessão de banco de dados para testes
    Erstellt Datenbanksitzung für Tests
    """
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
