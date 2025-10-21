"""
Test Alert System – Teste do Sistema de Alertas
Teste de Notificações – Validação de funcionalidades de alerta

DE: Unit- und Integrationstests für das Alert-System.
PT: Testes unitários e de integração para o sistema de alertas.
"""

import pytest
from datetime import datetime, date, timedelta, timezone
from typing import Optional, cast, Any
from unittest.mock import Mock, patch, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient

from app.models.alert import Alert, AlertType, AlertStatus
from app.models.contract import Contract, ContractStatus, ContractType
from app.services.notification_service import NotificationService
from app.utils.email import send_email
from main import app


class TestAlertModel:
    """Testes para o modelo Alert / Tests für das Alert-Modell"""
    
    def test_alert_creation(self):
        """Testa criação de alerta / Testet Alert-Erstellung"""
        alert = Alert(
            contract_id=1,
            alert_type=AlertType.T_MINUS_30,
            status=AlertStatus.PENDING,
            scheduled_for=datetime.now(timezone.utc)
        )
        
        # Usar cast para evitar erros do Pylance com ColumnElement
        assert cast(int, alert.contract_id) == 1
        assert cast(AlertType, alert.alert_type) == AlertType.T_MINUS_30
        assert cast(AlertStatus, alert.status) == AlertStatus.PENDING
        assert cast(Optional[datetime], alert.scheduled_for) is not None
    
    def test_alert_mark_sent(self):
        """Testa marcação de alerta como enviado / Testet Markierung als gesendet"""
        alert = Alert(
            contract_id=1,
            alert_type=AlertType.T_MINUS_30,
            status=AlertStatus.PENDING,
            scheduled_for=datetime.now(timezone.utc)
        )
        
        alert.mark_sent()
        
        # Usar cast para evitar erros do Pylance com ColumnElement
        assert cast(AlertStatus, alert.status) == AlertStatus.SENT
        assert cast(Optional[datetime], alert.sent_at) is not None
        assert cast(Optional[str], alert.error) is None
    
    def test_alert_mark_failed(self):
        """Testa marcação de alerta como falhado / Testet Markierung als fehlgeschlagen"""
        alert = Alert(
            contract_id=1,
            alert_type=AlertType.T_MINUS_30,
            status=AlertStatus.PENDING,
            scheduled_for=datetime.now(timezone.utc)
        )
        
        error_message = "SMTP connection failed"
        alert.mark_failed(error_message)
        
        # Usar cast para evitar erros do Pylance com ColumnElement
        assert cast(AlertStatus, alert.status) == AlertStatus.FAILED
        assert cast(Optional[str], alert.error) == error_message


class TestNotificationService:
    """Testes para o NotificationService / Tests für den NotificationService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock do banco de dados / Datenbank-Mock"""
        return Mock(spec=AsyncSession)
    
    @pytest.fixture
    def sample_contract(self):
        """Contrato de exemplo / Beispielvertrag"""
        return Contract(
            id=1,
            title="Test Contract",
            client_name="Test Client",
            client_email="test@example.com",
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            end_date=date.today() + timedelta(days=30),
            value=1000.00,
            currency="EUR"
        )
    
    def test_calculate_days_until(self):
        """Testa cálculo de dias restantes / Testet Berechnung verbleibender Tage"""
        from app.services.notification_service import calculate_days_until
        
        # Teste com data futura / Test mit zukünftigem Datum
        future_date = date.today() + timedelta(days=30)
        assert calculate_days_until(future_date) == 30
        
        # Teste com data passada / Test mit vergangenem Datum
        past_date = date.today() - timedelta(days=5)
        assert calculate_days_until(past_date) == -5
        
        # Teste com None / Test mit None
        assert calculate_days_until(None) is None
    
    def test_map_days_to_alert_type(self):
        """Testa mapeamento de dias para tipo de alerta / Testet Zuordnung von Tagen zu Alert-Typ"""
        from app.services.notification_service import map_days_to_alert_type
        
        assert map_days_to_alert_type(60) == AlertType.T_MINUS_60
        assert map_days_to_alert_type(30) == AlertType.T_MINUS_30
        assert map_days_to_alert_type(10) == AlertType.T_MINUS_10
        assert map_days_to_alert_type(1) == AlertType.T_MINUS_1
        assert map_days_to_alert_type(15) is None
        assert map_days_to_alert_type(None) is None
    
    @pytest.mark.asyncio
    async def test_process_due_alerts_happy_path(self, mock_db: Any, sample_contract: Contract):
        """Testa processamento de alertas - caminho feliz / Testet Alert-Verarbeitung - Happy Path"""
        # Mock do banco / Datenbank-Mock
        mock_db.execute.return_value.scalars.return_value.all.return_value = [sample_contract]
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        # Mock do envio de email / E-Mail-Versand-Mock
        with patch('app.services.notification_service.send_email', return_value=True):
            service = NotificationService(mock_db)
            result = await service.process_due_alerts()
            
            assert result.total >= 0
            assert isinstance(result.alerts, list)
    
    @pytest.mark.asyncio
    async def test_process_due_alerts_no_contracts(self, mock_db: Any):
        """Testa processamento sem contratos / Testet Verarbeitung ohne Verträge"""
        # Mock do banco vazio / Leerer Datenbank-Mock
        mock_db.execute.return_value.scalars.return_value.all.return_value = []
        
        service = NotificationService(mock_db)
        result = await service.process_due_alerts()
        
        assert result.total == 0
        assert result.alerts == []
    
    @pytest.mark.asyncio
    async def test_reprocess_alert_success(self, mock_db: Any, sample_contract: Contract):
        """Testa reprocessamento de alerta - sucesso / Testet Alert-Reprozessierung - Erfolg"""
        # Mock do alerta / Alert-Mock
        mock_alert = Alert(
            id=1,
            contract_id=1,
            alert_type=AlertType.T_MINUS_30,
            status=AlertStatus.FAILED,
            scheduled_for=datetime.now(timezone.utc)
        )
        
        # Mock do banco / Datenbank-Mock
        mock_db.execute.return_value.scalar_one_or_none.side_effect = [mock_alert, sample_contract]
        
        # Mock do envio de email / E-Mail-Versand-Mock
        with patch('app.services.notification_service.send_email', return_value=True):
            service = NotificationService(mock_db)
            result = await service.reprocess_alert(1)
            
            assert result is not None
            assert cast(int, result.id) == 1
    
    @pytest.mark.asyncio
    async def test_reprocess_alert_not_found(self, mock_db: Any):
        """Testa reprocessamento de alerta inexistente / Testet Reprozessierung nicht existierender Alerts"""
        # Mock do banco sem alerta / Datenbank-Mock ohne Alert
        mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        service = NotificationService(mock_db)
        result = await service.reprocess_alert(999)
        
        assert result is None


class TestAlertEndpoints:
    """Testes para endpoints de alertas / Tests für Alert-Endpoints"""
    
    @pytest.fixture
    def client(self):
        """Cliente de teste FastAPI / FastAPI-Test-Client"""
        return TestClient(app)
    
    @pytest.fixture
    def sample_alert_data(self):
        """Dados de alerta de exemplo / Beispiel-Alert-Daten"""
        return {
            "id": 1,
            "contract_id": 1,
            "alert_type": "T-30",
            "status": "pending",
            "scheduled_for": datetime.now(timezone.utc).isoformat(),
            "sent_at": None,
            "recipient": "test@example.com",
            "subject": "Test Alert",
            "error": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
    
    def test_list_alerts_endpoint(self, client: TestClient):
        """Testa endpoint de listagem de alertas / Testet Alert-Liste-Endpoint"""
        response = client.get("/alerts/")
        
        # Deve retornar 200 mesmo sem dados / Sollte 200 zurückgeben auch ohne Daten
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "alerts" in data
        assert "page" in data
        assert "per_page" in data
    
    def test_list_alerts_with_filters(self, client: TestClient):
        """Testa listagem com filtros / Testet Liste mit Filtern"""
        response = client.get("/alerts/?status=pending&alert_type=T-30")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
    
    def test_get_alert_not_found(self, client: TestClient):
        """Testa busca de alerta inexistente / Testet Suche nach nicht existierendem Alert"""
        response = client.get("/alerts/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_reprocess_alert_not_found(self, client: TestClient):
        """Testa reprocessamento de alerta inexistente / Testet Reprozessierung nicht existierender Alerts"""
        response = client.post("/alerts/999/reprocess")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_contract_alerts_not_found(self, client: TestClient):
        """Testa alertas de contrato inexistente / Testet Alerts nicht existierender Verträge"""
        response = client.get("/alerts/contract/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
    
    def test_get_alerts_summary(self, client: TestClient):
        """Testa endpoint de estatísticas / Testet Statistiken-Endpoint"""
        response = client.get("/alerts/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts" in data
        assert "by_status" in data
        assert "by_type" in data
        assert "generated_at" in data


class TestEmailIntegration:
    """Testes para integração de email / Tests für E-Mail-Integration"""
    
    @pytest.fixture
    def sample_contract(self):
        """Contrato de exemplo / Beispielvertrag"""
        return Contract(
            id=1,
            title="Test Contract",
            client_name="Test Client",
            client_email="test@example.com",
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            end_date=date.today() + timedelta(days=30),
            value=1000.00,
            currency="EUR"
        )
    
    def test_render_contract_expiry_html(self, sample_contract: Contract):
        """Testa renderização de HTML / Testet HTML-Rendering"""
        from app.utils.email import render_contract_expiry_html
        
        html = render_contract_expiry_html(
            contract=sample_contract,
            days_until=30,
            alert_type=AlertType.T_MINUS_30,
            language="de"
        )
        
        assert isinstance(html, str)
        assert "Test Contract" in html
        assert "30 Tage" in html
        assert "<html" in html
        assert "</html>" in html
    
    def test_get_email_subject_by_type(self):
        """Testa geração de assunto de email / Testet E-Mail-Betreff-Generierung"""
        from app.utils.email import get_email_subject_by_type
        
        subject = get_email_subject_by_type(
            alert_type=AlertType.T_MINUS_30,
            contract_title="Test Contract",
            language="de"
        )
        
        assert isinstance(subject, str)
        assert "30 Tagen" in subject
        assert "Test Contract" in subject
    
    @patch('app.utils.email.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp: MagicMock):
        """Testa envio de email - sucesso / Testet E-Mail-Versand - Erfolg"""
        # Mock do servidor SMTP / SMTP-Server-Mock
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        result = send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Test Body",
            is_html=False
        )
        
        assert result is True
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('app.utils.email.smtplib.SMTP')
    def test_send_email_failure(self, mock_smtp: MagicMock):
        """Testa envio de email - falha / Testet E-Mail-Versand - Fehler"""
        # Mock do servidor SMTP com erro / SMTP-Server-Mock mit Fehler
        mock_smtp.side_effect = Exception("SMTP connection failed")
        
        result = send_email(
            to="test@example.com",
            subject="Test Subject",
            body="Test Body",
            is_html=False
        )
        
        assert result is False


class TestAlertSystemIntegration:
    """Testes de integração do sistema de alertas / Integrationstests für Alert-System"""
    
    @pytest.mark.asyncio
    async def test_full_alert_workflow(self):
        """Testa fluxo completo de alertas / Testet vollständigen Alert-Workflow"""
        # Este teste seria executado com banco real em ambiente de teste
        pass
    
    def test_alert_type_enum_values(self):
        """Testa valores dos enums de tipo de alerta / Testet Alert-Typ-Enum-Werte"""
        assert AlertType.T_MINUS_60.value == "T-60"
        assert AlertType.T_MINUS_30.value == "T-30"
        assert AlertType.T_MINUS_10.value == "T-10"
        assert AlertType.T_MINUS_1.value == "T-1"
    
    def test_alert_status_enum_values(self):
        """Testa valores dos enums de status de alerta / Testet Alert-Status-Enum-Werte"""
        assert AlertStatus.PENDING.value == "pending"
        assert AlertStatus.SENT.value == "sent"
        assert AlertStatus.FAILED.value == "failed"


# ========= Testes de Performance / Performance-Tests =========

class TestAlertPerformance:
    """Testes de performance para alertas / Performance-Tests für Alerts"""
    
    def test_alert_creation_performance(self):
        """Testa performance de criação de alertas / Testet Alert-Erstellungs-Performance"""
        import time
        
        start_time = time.time()
        
        # Criar 100 alertas / 100 Alerts erstellen
        alerts = []
        for i in range(100):
            alert = Alert(
                contract_id=i,
                alert_type=AlertType.T_MINUS_30,
                status=AlertStatus.PENDING,
                scheduled_for=datetime.now(timezone.utc)
            )
            alerts.append(alert)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Deve ser rápido (< 1 segundo) / Sollte schnell sein (< 1 Sekunde)
        assert duration < 1.0
        assert len(alerts) == 100
    
    def test_html_rendering_performance(self):
        """Testa performance de renderização HTML / Testet HTML-Rendering-Performance"""
        from app.utils.email import render_contract_expiry_html
        
        contract = Contract(
            id=1,
            title="Performance Test Contract",
            client_name="Performance Test Client",
            client_email="perf@example.com",
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            end_date=date.today() + timedelta(days=30),
            value=1000.00,
            currency="EUR"
        )
        
        import time
        start_time = time.time()
        
        # Renderizar 50 vezes / 50 mal rendern
        for _ in range(50):
            html = render_contract_expiry_html(
                contract=contract,
                days_until=30,
                alert_type=AlertType.T_MINUS_30,
                language="de"
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Deve ser rápido (< 2 segundos) / Sollte schnell sein (< 2 Sekunden)
        assert duration < 2.0
        html = ""
        # Renderizar 50 vezes / 50 mal rendern
        for _ in range(50):
            html = render_contract_expiry_html(
            contract=contract,
            days_until=30,
            alert_type=AlertType.T_MINUS_30,
            language="de"
            )

        end_time = time.time()
        duration = end_time - start_time

        # Deve ser rápido (< 2 segundos) / Sollte schnell sein (< 2 Sekunden)
        assert duration < 2.0
        assert isinstance(html, str)


if __name__ == "__main__":
    # Executar testes básicos / Grundlegende Tests ausführen
    pytest.main([__file__, "-v"])

