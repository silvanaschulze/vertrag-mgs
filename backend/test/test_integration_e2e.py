"""
E2E Integration Tests / End-to-End-Integrationstests
DE: Vollständige Workflows | PT: Fluxos completos
"""

import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
import pytest_asyncio
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import Base, get_db
from app.models.contract import Contract
from app.models.user import User, UserRole, AccessLevel
from app.models.rent_step import RentStep
from app.utils.security import get_password_hash
from main import app


@pytest_asyncio.fixture
async def test_db():
    """DB in-memory"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    yield async_session
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.asyncio
async def test_complete_user_contract_workflow(test_db, client):
    """
    User → Login → Contract → RentStep
    DE: Kompletter Workflow | PT: Fluxo completo
    """
    async with test_db() as session:
        user = User(username="e2e", email="e2e@example.com", name="E2E",
                   password_hash=get_password_hash("E2E123!"), role=UserRole.DEPARTMENT_ADM,
                   access_level=AccessLevel.LEVEL_4, is_active=True, is_verified=True)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        user_id = user.id
    
    login = client.post("/auth/login", data={"username": "e2e", "password": "E2E123!"})
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    contract = client.post("/contracts/", json={
        "title": "E2E Contract", "contract_type": "dienstleistung", "status": "aktiv",
        "value": 5000.00, "currency": "EUR", "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=365)).isoformat(),
        "client_name": "E2E Client", "client_email": "e2e@client.com"
    }, params={"created_by": user_id}, headers=headers)
    assert contract.status_code == 201
    contract_id = contract.json()["id"]
    
    rs = client.post(f"/contracts/{contract_id}/rent-steps", json={
        "effective_date": (date.today() + timedelta(days=90)).isoformat(),
        "amount": 6000.00, "currency": "EUR"
    }, headers=headers)
    assert rs.status_code == 201
    
    async with test_db() as session:
        c = (await session.execute(select(Contract).where(Contract.id == contract_id))).scalar_one()
        assert c.title == "E2E Contract"
        rentsteps = (await session.execute(select(RentStep).where(RentStep.contract_id == contract_id))).scalars().all()
        assert len(rentsteps) == 1


@pytest.mark.asyncio
async def test_contract_lifecycle_with_updates(test_db, client):
    """
    DRAFT → ACTIVE → 3 RentSteps → DELETE
    DE: Lebenszyklus | PT: Ciclo de vida
    """
    async with test_db() as session:
        user = User(username="lifecycle", email="lifecycle@example.com", name="Lifecycle",
                   password_hash=get_password_hash("Life123!"), role=UserRole.DEPARTMENT_ADM,
                   access_level=AccessLevel.LEVEL_4, is_active=True, is_verified=True)
        session.add(user)
        await session.commit()
        user_id = user.id
    
    login = client.post("/auth/login", data={"username": "lifecycle", "password": "Life123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    contract = client.post("/contracts/", json={
        "title": "Lifecycle", "contract_type": "miete", "status": "entwurf",
        "value": 10000.00, "currency": "EUR", "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=365)).isoformat(),
        "client_name": "Client", "client_email": "client@example.com"
    }, params={"created_by": user_id}, headers=headers)
    assert contract.status_code == 201
    contract_id = contract.json()["id"]
    
    update = client.put(f"/contracts/{contract_id}", json={"status": "aktiv"}, headers=headers)
    assert update.json()["status"] == "aktiv"
    
    for days, amt in [(90, 11000), (180, 12000), (270, 13000)]:
        client.post(f"/contracts/{contract_id}/rent-steps", json={
            "effective_date": (date.today() + timedelta(days=days)).isoformat(),
            "amount": amt, "currency": "EUR"
        }, headers=headers)
    
    async with test_db() as session:
        rentsteps = (await session.execute(select(RentStep).where(RentStep.contract_id == contract_id))).scalars().all()
        assert len(rentsteps) == 3
    
    client.delete(f"/contracts/{contract_id}", headers=headers)
    
    async with test_db() as session:
        assert (await session.execute(select(Contract).where(Contract.id == contract_id))).scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_multi_user_collaboration(test_db, client):
    """
    STAFF cria → ADMIN aprova
    DE: Zusammenarbeit | PT: Colaboração
    """
    async with test_db() as session:
        staff = User(username="staff", email="staff@example.com", name="Staff",
                    password_hash=get_password_hash("Staff123!"), role=UserRole.STAFF,
                    access_level=AccessLevel.LEVEL_2, is_active=True, is_verified=True)
        admin = User(username="admin", email="admin@example.com", name="Admin",
                    password_hash=get_password_hash("Admin123!"), role=UserRole.DEPARTMENT_ADM,
                    access_level=AccessLevel.LEVEL_4, is_active=True, is_verified=True)
        session.add_all([staff, admin])
        await session.commit()
        staff_id = staff.id
    
    staff_login = client.post("/auth/login", data={"username": "staff", "password": "Staff123!"})
    staff_h = {"Authorization": f"Bearer {staff_login.json()['access_token']}"}
    
    contract = client.post("/contracts/", json={
        "title": "Collab", "contract_type": "dienstleistung", "status": "entwurf",
        "value": 8000.00, "currency": "EUR", "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=60)).isoformat(),
        "client_name": "Client", "client_email": "client@example.com"
    }, params={"created_by": staff_id}, headers=staff_h)
    assert contract.status_code == 201
    contract_id = contract.json()["id"]
    
    admin_login = client.post("/auth/login", data={"username": "admin", "password": "Admin123!"})
    admin_h = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    
    approve = client.put(f"/contracts/{contract_id}", json={"status": "aktiv"}, headers=admin_h)
    assert approve.json()["status"] == "aktiv"


@pytest.mark.asyncio
async def test_contract_deletion_cascade(test_db, client):
    """
    Contract + RentSteps → DELETE → Cascade
    DE: Kaskadenlöschung | PT: Delete em cascata
    """
    async with test_db() as session:
        user = User(username="del", email="del@example.com", name="Delete",
                   password_hash=get_password_hash("Del123!"), role=UserRole.DEPARTMENT_ADM,
                   access_level=AccessLevel.LEVEL_4, is_active=True, is_verified=True)
        session.add(user)
        await session.commit()
        user_id = user.id
    
    login = client.post("/auth/login", data={"username": "del", "password": "Del123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    contract = client.post("/contracts/", json={
        "title": "Delete Test", "contract_type": "miete", "status": "aktiv",
        "value": 7500.00, "currency": "EUR",
        "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=365)).isoformat(),
        "client_name": "Client", "client_email": "client@example.com"
    }, params={"created_by": user_id}, headers=headers)
    contract_id = contract.json()["id"]
    
    for i in range(3):
        client.post(f"/contracts/{contract_id}/rent-steps", json={
            "effective_date": (date.today() + timedelta(days=90 * (i+1))).isoformat(),
            "amount": 8000 + (i * 500), "currency": "EUR"
        }, headers=headers)
    
    async with test_db() as session:
        rentsteps = (await session.execute(select(RentStep).where(RentStep.contract_id == contract_id))).scalars().all()
        assert len(rentsteps) == 3
    
    client.delete(f"/contracts/{contract_id}", headers=headers)
    
    async with test_db() as session:
        assert (await session.execute(select(Contract).where(Contract.id == contract_id))).scalar_one_or_none() is None
        rentsteps = (await session.execute(select(RentStep).where(RentStep.contract_id == contract_id))).scalars().all()
        assert len(rentsteps) == 0

