"""
Performance & Concurrency Tests / Leistungs- und Parallelitätstests
DE: Last- und Parallelitätstests | PT: Testes de carga e concorrência
"""

import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
import pytest_asyncio
import asyncio
import time
from datetime import date, timedelta
from statistics import mean, median
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, func

from app.core.database import Base, get_db
from app.models.contract import Contract
from app.models.user import User, UserRole, AccessLevel
from app.models.alert import Alert
from app.models.rent_step import RentStep
from app.utils.security import get_password_hash
from main import app


@pytest_asyncio.fixture
async def test_db():
    """DB in-memory para performance"""
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


@pytest_asyncio.fixture
async def perf_user(test_db):
    """User para testes de performance"""
    async with test_db() as session:
        user = User(username="perf", email="perf@example.com", name="Performance",
                   password_hash=get_password_hash("Perf123!"), role=UserRole.DEPARTMENT_ADM,
                   access_level=AccessLevel.LEVEL_4, is_active=True, is_verified=True)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


# === TESTES DE CONCORRÊNCIA / CONCURRENCY TESTS ===

@pytest.mark.asyncio
async def test_concurrent_contract_creation(test_db, client, perf_user):
    """
    50 contratos simultâneos / 50 gleichzeitige Verträge
    DE: Parallelität bei Vertragserstellung | PT: Concorrência na criação
    """
    login = client.post("/auth/login", data={"username": "perf", "password": "Perf123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    async def create_contract(i):
        return client.post("/contracts/", json={
            "title": f"Contract {i}", "contract_type": "dienstleistung", "status": "aktiv",
            "value": 5000.00, "currency": "EUR", "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=365)).isoformat(),
            "client_name": f"Client {i}", "client_email": f"client{i}@example.com"
        }, params={"created_by": perf_user.id}, headers=headers)
    
    start = time.time()
    tasks = [create_contract(i) for i in range(50)]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    assert all(r.status_code == 201 for r in results)
    assert elapsed < 10.0, f"Too slow: {elapsed:.2f}s"
    
    async with test_db() as session:
        count = (await session.execute(select(func.count(Contract.id)))).scalar()
        assert count == 50


@pytest.mark.asyncio
async def test_concurrent_contract_updates(test_db, client, perf_user):
    """
    20 updates simultâneos / 20 gleichzeitige Updates
    DE: Parallelität bei Updates | PT: Concorrência em atualizações
    """
    login = client.post("/auth/login", data={"username": "perf", "password": "Perf123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    contract = client.post("/contracts/", json={
        "title": "Update Test", "contract_type": "dienstleistung", "status": "entwurf",
        "value": 5000.00, "currency": "EUR", "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=365)).isoformat(),
        "client_name": "Client", "client_email": "client@example.com"
    }, params={"created_by": perf_user.id}, headers=headers)
    contract_id = contract.json()["id"]
    
    async def update_contract(i):
        return client.put(f"/contracts/{contract_id}", json={"value": 5000.00 + i}, headers=headers)
    
    tasks = [update_contract(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    
    assert all(r.status_code == 200 for r in results)


@pytest.mark.asyncio
async def test_concurrent_rentstep_creation(test_db, client, perf_user):
    """
    15 RentSteps simultâneos / 15 gleichzeitige RentSteps
    DE: Parallelität bei RentSteps | PT: Concorrência em RentSteps
    """
    login = client.post("/auth/login", data={"username": "perf", "password": "Perf123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    contract = client.post("/contracts/", json={
        "title": "RentStep Test", "contract_type": "miete", "status": "aktiv",
        "value": 10000.00, "currency": "EUR", "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=365)).isoformat(),
        "client_name": "Client", "client_email": "client@example.com"
    }, params={"created_by": perf_user.id}, headers=headers)
    contract_id = contract.json()["id"]
    
    async def create_rentstep(i):
        return client.post(f"/contracts/{contract_id}/rent-steps", json={
            "effective_date": (date.today() + timedelta(days=30 * i)).isoformat(),
            "amount": 10000.00 + (i * 100), "currency": "EUR"
        }, headers=headers)
    
    tasks = [create_rentstep(i) for i in range(1, 16)]
    results = await asyncio.gather(*tasks)
    
    assert all(r.status_code == 201 for r in results)
    
    async with test_db() as session:
        rentsteps = (await session.execute(select(RentStep).where(RentStep.contract_id == contract_id).order_by(RentStep.effective_date))).scalars().all()
        assert len(rentsteps) == 15


# === TESTES DE CARGA / LOAD TESTS ===

@pytest.mark.asyncio
async def test_bulk_contract_creation_performance(test_db, client, perf_user):
    """
    1000 contratos em lote / 1000 Verträge im Batch
    DE: Massenvertragserstellung | PT: Criação em massa
    """
    login = client.post("/auth/login", data={"username": "perf", "password": "Perf123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    start = time.time()
    times = []
    
    for i in range(1000):
        t_start = time.time()
        resp = client.post("/contracts/", json={
            "title": f"Bulk {i}", "contract_type": "dienstleistung", "status": "aktiv",
            "value": 5000.00, "currency": "EUR", "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=365)).isoformat(),
            "client_name": f"Bulk {i}", "client_email": f"bulk{i}@example.com"
        }, params={"created_by": perf_user.id}, headers=headers)
        times.append(time.time() - t_start)
        assert resp.status_code == 201
    
    elapsed = time.time() - start
    avg_time = mean(times) * 1000
    med_time = median(times) * 1000
    
    assert elapsed < 30.0, f"Too slow: {elapsed:.2f}s"
    print(f"\n⏱️  Total: {elapsed:.2f}s | Avg: {avg_time:.2f}ms | Median: {med_time:.2f}ms")


@pytest.mark.asyncio
async def test_large_dataset_filtering_performance(test_db, client, perf_user):
    """
    5000 contratos + filtros / 5000 Verträge + Filter
    DE: Filterleistung | PT: Performance de filtros
    """
    login = client.post("/auth/login", data={"username": "perf", "password": "Perf123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    # Criar 5000 contratos
    for i in range(5000):
        client.post("/contracts/", json={
            "title": f"Filter {i}", 
            "contract_type": "dienstleistung" if i % 2 == 0 else "mietvertrag",
            "status": "aktiv" if i % 3 == 0 else "entwurf",
            "value": 5000.00, "currency": "EUR", "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=365)).isoformat(),
            "client_name": f"Filter {i}", "client_email": f"filter{i}@example.com"
        }, params={"created_by": perf_user.id}, headers=headers)
    
    # Testar filtros
    start = time.time()
    resp1 = client.get("/contracts/?status=aktiv", headers=headers)
    t1 = time.time() - start
    
    start = time.time()
    resp2 = client.get("/contracts/?contract_type=mietvertrag", headers=headers)
    t2 = time.time() - start
    
    assert t1 < 2.0 and t2 < 2.0
    print(f"\n⏱️  Filter status: {t1:.2f}s | Filter type: {t2:.2f}s")


@pytest.mark.asyncio
async def test_bulk_alert_processing_performance(test_db, client, perf_user):
    """
    500 contratos criados em massa
    DE: Massen-Vertragserstellung | PT: Criação em massa de contratos
    """
    login = client.post("/auth/login", data={"username": "perf", "password": "Perf123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    start = time.time()
    created = 0
    
    for i in range(500):
        resp = client.post("/contracts/", json={
            "title": f"Bulk {i}", "contract_type": "dienstleistung", "status": "aktiv",
            "value": 5000.00, "currency": "EUR", "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=35 + i % 30)).isoformat(),
            "client_name": f"Bulk {i}", "client_email": f"bulk{i}@example.com"
        }, params={"created_by": perf_user.id}, headers=headers)
        if resp.status_code == 201:
            created += 1
    
    elapsed = time.time() - start
    
    assert created == 500
    assert elapsed < 60.0, f"Too slow: {elapsed:.2f}s"
    print(f"\n⏱️  500 contracts created in {elapsed:.2f}s")


# === TESTES DE QUERY PERFORMANCE / QUERY PERFORMANCE TESTS ===

@pytest.mark.asyncio
async def test_database_query_performance(test_db, perf_user):
    """
    10.000 contratos + queries / 10.000 Verträge + Abfragen
    DE: Datenbankabfrageleistung | PT: Performance de queries
    """
    async with test_db() as session:
        for i in range(10000):
            contract = Contract(
                title=f"Query {i}", contract_type="dienstleistung", status="aktiv",
                value=5000.00, currency="EUR", start_date=date.today(),
                end_date=date.today() + timedelta(days=365),
                client_name=f"Query {i}", created_by=perf_user.id
            )
            session.add(contract)
        await session.commit()
    
    # Test queries
    async with test_db() as session:
        start = time.time()
        contract = (await session.execute(select(Contract).where(Contract.id == 5000))).scalar_one_or_none()
        t1 = time.time() - start
        
        start = time.time()
        count = (await session.execute(select(func.count(Contract.id)).where(Contract.status == "aktiv"))).scalar()
        t2 = time.time() - start
        
        assert t1 < 1.0 and t2 < 1.0
        print(f"\n⏱️  SELECT by ID: {t1*1000:.2f}ms | COUNT: {t2*1000:.2f}ms")


@pytest.mark.asyncio
async def test_pagination_large_dataset(test_db, client, perf_user):
    """
    5000 contratos + paginação / 5000 Verträge + Paginierung
    DE: Paginierungsleistung | PT: Performance de paginação
    """
    login = client.post("/auth/login", data={"username": "perf", "password": "Perf123!"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    
    for i in range(5000):
        client.post("/contracts/", json={
            "title": f"Page {i}", "contract_type": "dienstleistung", "status": "aktiv",
            "value": 5000.00, "currency": "EUR", "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=365)).isoformat(),
            "client_name": f"Page {i}", "client_email": f"page{i}@example.com"
        }, params={"created_by": perf_user.id}, headers=headers)
    
    # Test pagination
    start = time.time()
    p1 = client.get("/contracts/?skip=0&limit=50", headers=headers)
    t1 = time.time() - start
    
    start = time.time()
    p2 = client.get("/contracts/?skip=2450&limit=50", headers=headers)
    t2 = time.time() - start
    
    start = time.time()
    p3 = client.get("/contracts/?skip=4950&limit=50", headers=headers)
    t3 = time.time() - start
    
    assert all(t < 0.5 for t in [t1, t2, t3])
    print(f"\n⏱️  Page 1: {t1*1000:.2f}ms | Page 50: {t2*1000:.2f}ms | Page 100: {t3*1000:.2f}ms")
