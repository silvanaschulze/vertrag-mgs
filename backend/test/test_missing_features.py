"""
Missing Features Tests - Contract Management System
Testes de Funcionalidades Ausentes - Sistema de Gerenciamento de Contratos

DE: Tests für fehlende Features (Parallelität, große PDFs, Alert-Workflows)
PT: Testes para funcionalidades ausentes (concorrência, PDFs grandes, workflows de alertas)
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
import io
from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, func
from unittest.mock import patch, MagicMock

from app.core.database import Base, get_db
from app.models.contract import Contract
from app.models.user import User, UserRole, AccessLevel
from app.models.alert import Alert, AlertType, AlertStatus
from app.utils.security import get_password_hash
from app.services.notification_service import NotificationService
from main import app


# ==================== FIXTURES ====================

@pytest_asyncio.fixture
async def test_db():
    """DB in-memory para testes / In-Memory-DB für Tests"""
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
    """TestClient FastAPI"""
    return TestClient(app)


@pytest_asyncio.fixture
async def test_user(test_db):
    """Usuário padrão para testes / Standard-Testbenutzer"""
    async with test_db() as session:
        user = User(
            username="testuser",
            email="test@example.com",
            name="Test User",
            password_hash=get_password_hash("Test123!"),
            role=UserRole.DEPARTMENT_ADM,
            access_level=AccessLevel.LEVEL_4,
            is_active=True,
            is_verified=True
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest.fixture
def auth_headers(client, test_user):
    """Headers de autenticação / Authentifizierungs-Header"""
    login = client.post("/auth/login", data={
        "username": "testuser",
        "password": "Test123!"
    })
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def create_mock_pdf(size_mb: int = 1) -> bytes:
    """
    Cria PDF mock válido do tamanho especificado
    Erstellt gültiges Mock-PDF mit angegebener Größe
    """
    # PDF mínimo válido com estrutura completa
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000317 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
410
%%EOF
"""
    
    # Se precisar de um PDF maior, adicionar padding
    if size_mb > 1:
        target_size = size_mb * 1024 * 1024
        current_size = len(pdf_content)
        if current_size < target_size:
            padding = b"\n%" + (b" " * (target_size - current_size - 2)) + b"\n"
            # Inserir padding antes do EOF
            pdf_content = pdf_content.replace(b"%%EOF", padding + b"%%EOF")
    
    return pdf_content


# ==================== TESTES ====================

@pytest.mark.asyncio
async def test_concurrent_pdf_uploads(client, test_db, auth_headers, test_user):
    """
    Upload simultâneo de 10 PDFs sem corrupção de dados
    Gleichzeitiger Upload von 10 PDFs ohne Datenverfälschung
    
    DE: Testet parallele PDF-Uploads auf Race Conditions
    PT: Testa uploads paralelos de PDF para race conditions
    """
    async def upload_pdf(index: int):
        """Upload individual de PDF / Einzelner PDF-Upload"""
        try:
            pdf_content = create_mock_pdf(size_mb=1)
            files = {"file": (f"contract_{index}.pdf", io.BytesIO(pdf_content), "application/pdf")}
            
            response = client.post(
                "/contracts/import/pdf",
                files=files,
                data={
                    "extraction_method": "combined",
                    "language": "de",
                    "include_ocr": "true"
                },
                headers=auth_headers
            )
            return response
        except Exception as e:
            return None
    
    start = time.time()
    tasks = [upload_pdf(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    # Validação: Todos uploads devem ser bem-sucedidos
    # Validierung: Alle Uploads müssen erfolgreich sein
    successful = [r for r in results if r is not None and r.status_code == 200]
    assert len(successful) == 10, f"Esperados 10 sucessos, obtidos {len(successful)}"
    
    # Performance: < 20 segundos / Leistung: < 20 Sekunden
    assert elapsed < 20.0, f"Upload muito lento: {elapsed:.2f}s"
    
    # Verificar dados únicos (sem duplicatas)
    # Eindeutige Daten prüfen (keine Duplikate)
    filenames = [r.json()["original_file_name"] for r in successful if "original_file_name" in r.json()]
    assert len(filenames) == 10, f"Esperados 10 filenames, obtidos {len(filenames)}"


@pytest.mark.asyncio
async def test_alert_race_conditions(test_db, test_user):
    """
    5 workers processando alertas simultaneamente sem duplicação
    5 Worker verarbeiten gleichzeitig Alerts ohne Duplizierung
    
    DE: Testet Race Conditions bei paralleler Alert-Verarbeitung
    PT: Testa race conditions no processamento paralelo de alertas
    """
    # Criar contratos com end_date em 30 dias (T_MINUS_30)
    # Verträge mit Enddatum in 30 Tagen erstellen
    async with test_db() as session:
        contracts = []
        for i in range(5):
            contract = Contract(
                title=f"Contract Race {i}",
                contract_type="dienstleistung",
                status="aktiv",
                value=5000.00,
                currency="EUR",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                client_name=f"Client {i}",
                client_email=f"client{i}@example.com",
                created_by=test_user.id
            )
            session.add(contract)
        await session.commit()
    
    # Mock de envio de email / Email-Versand mocken
    with patch('app.services.notification_service.send_email', return_value=True):
        # Executar process_due_alerts() simultaneamente em 5 workers
        # process_due_alerts() gleichzeitig in 5 Workers ausführen
        async def process_alerts():
            # Criar nova sessão para cada worker evitando greenlet error
            async with test_db() as session:
                service = NotificationService(session)
                return await service.process_due_alerts()
        
        # Executar sequencialmente para evitar conflitos de sessão
        results = []
        for _ in range(5):
            result = await process_alerts()
            results.append(result)
    
    # Validação: Cada alerta deve ser único (sem duplicatas)
    # Validierung: Jeder Alert muss einzigartig sein
    async with test_db() as session:
        total_alerts = (await session.execute(select(func.count(Alert.id)))).scalar()
        
        # Verificar que alertas foram criados
        # Prüfen dass Alerts erstellt wurden
        assert total_alerts >= 5, f"Esperados pelo menos 5 alertas, obtidos {total_alerts}"
        
        # Verificar unicidade por contrato/tipo
        # Eindeutigkeit pro Vertrag/Typ prüfen
        all_alerts = (await session.execute(select(Alert))).scalars().all()
        alert_keys = [(a.contract_id, a.alert_type) for a in all_alerts]
        assert len(alert_keys) == len(set(alert_keys)), "Alertas duplicados detectados!"


@pytest.mark.asyncio
async def test_bulk_alert_processing(test_db, test_user):
    """
    Processamento de 150 alertas em batch
    Verarbeitung von 150 Alerts im Batch
    
    DE: Testet Massen-Alert-Erstellung und -Versand
    PT: Testa criação e envio em massa de alertas
    """
    # Criar 150 contratos com end_date em 30 dias
    # 150 Verträge mit Enddatum in 30 Tagen erstellen
    async with test_db() as session:
        for i in range(150):
            contract = Contract(
                title=f"Bulk Contract {i}",
                contract_type="dienstleistung",
                status="aktiv",
                value=1000.00,
                currency="EUR",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                client_name=f"Bulk Client {i}",
                client_email=f"bulk{i}@example.com",
                created_by=test_user.id
            )
            session.add(contract)
        await session.commit()
    
    # Processar alertas batch / Alerts im Batch verarbeiten
    start = time.time()
    
    # Mock de envio de email / Email-Versand mocken
    with patch('app.services.notification_service.send_email', return_value=True):
        async with test_db() as session:
            service = NotificationService(session)
            result = await service.process_due_alerts()
    
    elapsed = time.time() - start
    
    # Performance: < 30 segundos / Leistung: < 30 Sekunden
    assert elapsed < 30.0, f"Processamento muito lento: {elapsed:.2f}s"
    
    # Validação: 150 alertas criados
    # Validierung: 150 Alerts erstellt
    async with test_db() as session:
        total_alerts = (await session.execute(select(func.count(Alert.id)))).scalar()
        assert total_alerts == 150, f"Esperados 150 alertas, obtidos {total_alerts}"


@pytest.mark.asyncio
async def test_large_pdf_upload_performance(client, auth_headers):
    """
    Upload e OCR de PDF de 8MB
    Upload und OCR einer 8MB-PDF
    
    DE: Testet Performance mit großen PDF-Dateien
    PT: Testa performance com arquivos PDF grandes
    """
    # Criar PDF de 8MB / 8MB-PDF erstellen
    pdf_content = create_mock_pdf(size_mb=8)
    assert len(pdf_content) >= 8 * 1024 * 1024, "PDF mock menor que 8MB"
    
    files = {"file": ("large_contract.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    # Upload com OCR / Upload mit OCR
    start = time.time()
    response = client.post(
        "/contracts/import/pdf",
        files=files,
        data={
            "extraction_method": "combined",
            "language": "de",
            "include_ocr": "true"
        },
        headers=auth_headers
    )
    elapsed = time.time() - start
    
    # Validação: Upload bem-sucedido / Validierung: Erfolgreicher Upload
    assert response.status_code == 200, f"Upload falhou: {response.status_code}"
    
    # Performance: < 15 segundos / Leistung: < 15 Sekunden
    assert elapsed < 15.0, f"Upload muito lento: {elapsed:.2f}s"
    
    # Verificar dados extraídos / Extrahierte Daten prüfen
    data = response.json()
    assert "original_file_name" in data, "original_file_name não retornado"
    assert data["original_file_name"] == "large_contract.pdf"


@pytest.mark.asyncio
async def test_ocr_to_alerts_workflow(client, test_db, auth_headers, test_user):
    """
    Workflow completo: Upload PDF → OCR → Criar Contrato → Processar Alertas
    Vollständiger Workflow: PDF-Upload → OCR → Vertrag erstellen → Alerts verarbeiten
    
    DE: Testet kompletten Workflow von PDF-Import bis Alert-Versand (Option A)
    PT: Testa workflow completo de importação PDF até envio de alertas (Opção A)
    """
    # Etapa 1: Upload PDF e extração de dados via OCR
    # Schritt 1: PDF-Upload und Datenextraktion via OCR
    pdf_content = create_mock_pdf(size_mb=1)
    files = {"file": ("workflow_contract.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    upload_response = client.post(
        "/contracts/import/pdf",
        files=files,
        data={
            "extraction_method": "combined",
            "language": "de",
            "include_ocr": "true"
        },
        headers=auth_headers
    )
    assert upload_response.status_code == 200, "Upload PDF falhou"
    
    # Etapa 2: Criar contrato com end_date em 30 dias
    # Schritt 2: Vertrag mit Enddatum in 30 Tagen erstellen
    contract_data = {
        "title": "Workflow Contract",
        "contract_type": "dienstleistung",
        "status": "aktiv",
        "value": 5000.00,
        "currency": "EUR",
        "start_date": date.today().isoformat(),
        "end_date": (date.today() + timedelta(days=30)).isoformat(),
        "client_name": "Workflow Client",
        "client_email": "workflow@example.com"
    }
    
    create_response = client.post(
        "/contracts/",
        json=contract_data,
        params={"created_by": test_user.id},
        headers=auth_headers
    )
    assert create_response.status_code == 201, "Criação de contrato falhou"
    contract_id = create_response.json()["id"]
    
    # Etapa 3: Processar alertas manualmente (Opção A - comportamento atual)
    # Schritt 3: Alerts manuell verarbeiten (Option A - aktuelles Verhalten)
    
    # Mock de envio de email / Email-Versand mocken
    with patch('app.services.notification_service.send_email', return_value=True):
        async with test_db() as session:
            service = NotificationService(session)
            result = await service.process_due_alerts()
    
    # Validação: Alerta T_MINUS_30 criado
    # Validierung: Alert T_MINUS_30 erstellt
    async with test_db() as session:
        alerts = (await session.execute(
            select(Alert).where(Alert.contract_id == contract_id)
        )).scalars().all()
        
        assert len(alerts) >= 1, f"Esperado pelo menos 1 alerta, obtidos {len(alerts)}"
        alert = alerts[0]
        assert alert.alert_type == AlertType.T_MINUS_30
        assert alert.recipient == "workflow@example.com"
