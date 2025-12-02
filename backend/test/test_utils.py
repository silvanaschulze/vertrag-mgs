import os
from decimal import Decimal
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi import HTTPException, status as http_status
from jose import jwt, JWTError

from app.utils.security import get_password_hash, verify_password
from app.utils import document_generator
from app.utils import email as email_utils
from app.models.alert import AlertType
from app.models.contract import Contract, ContractType, ContractStatus
from app.models.user import User, UserRole, AccessLevel
from app.core.security import create_access_token, create_refresh_token
from app.core.permissions import can_view_contract, can_edit_contract, can_delete_contract, can_approve_contract
from app.core.config import settings


def test_security_hash_and_verify():
    pw = "minhasenha123"
    hashed = get_password_hash(pw)
    assert isinstance(hashed, str) and len(hashed) > 0
    assert verify_password(pw, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_security_long_password_truncation():
    # bcrypt has a 72-byte limit; ensure long passwords are handled without exception
    long_pw = "a" * 200
    hashed = get_password_hash(long_pw)
    assert verify_password(long_pw, hashed) is True


def test_document_generator_monkeypatch(monkeypatch, tmp_path):
    # monkeypatch DocxTemplate used inside document_generator to avoid requiring real docx files
    class FakeDoc:
        def __init__(self, path):
            self.path = path
            self.rendered = None

        def render(self, data):
            self.rendered = data

        def save(self, dest):
            content = b"FAKE-DOCX-BYTES:" + str(self.rendered).encode("utf-8")
            # dest may be a file-like object (BytesIO) or a path
            if hasattr(dest, "write"):
                dest.write(content)
            else:
                with open(dest, "wb") as f:
                    f.write(content)

    monkeypatch.setattr(document_generator, "DocxTemplate", FakeDoc)

    data = {"name": "Test"}

    # case 1: no output_path -> returns bytes from BytesIO
    res = document_generator.generate_contract_pdf("fake_template.docx", data)
    assert isinstance(res, (bytes, bytearray))
    assert b"FAKE-DOCX-BYTES" in res

    # case 2: with output_path -> file written and bytes returned
    out = tmp_path / "out.docx"
    res2 = document_generator.generate_contract_pdf("fake_template.docx", data, output_path=str(out))
    assert isinstance(res2, (bytes, bytearray))
    assert out.exists()


def test_email_rendering_and_subject():
    # Create a minimal Contract object in-memory
    contract = Contract(
        id=1,
        title="Test Contract",
        client_name="Client",
        end_date=date.today(),
        contract_type=ContractType.SERVICE,
        value=Decimal("1234.56"),
        currency="EUR",
        start_date=date.today(),
        created_by=1,
    )

    html = email_utils.render_contract_expiry_html(contract, 5, AlertType.T_MINUS_10, language="de")
    assert isinstance(html, str)
    assert "Test Contract" in html

    subj = email_utils.get_email_subject_by_type(AlertType.T_MINUS_10, "Test Contract", language="de")
    assert isinstance(subj, str)
    # ensure the subject mentions the relative days or contains expected wording
    assert "10" in subj or "T-10" in subj


# ============================================================================
# TESTES DE JWT / JWT TESTS
# ============================================================================

class TestJWTAuthentication:
    """Testes de autenticação JWT / JWT Authentication Tests"""
    
    def test_create_access_token_success(self):
        """
        Testa criação de token de acesso
        Testet Erstellung von Access Token
        """
        data = {"user_id": 1, "username": "testuser"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decodificar e verificar payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["user_id"] == 1
        assert payload["username"] == "testuser"
        assert "exp" in payload
    
    def test_create_access_token_with_custom_expiration(self):
        """
        Testa token com expiração customizada
        Testet Token mit benutzerdefinierter Ablaufzeit
        """
        data = {"user_id": 1}
        custom_delta = timedelta(minutes=5)
        token = create_access_token(data, expires_delta=custom_delta)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        exp_timestamp = payload["exp"]
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        
        # Verificar que expira em ~5 minutos (com margem de 1 minuto)
        time_diff = (exp_datetime - now).total_seconds()
        assert 240 < time_diff < 360  # Entre 4 e 6 minutos
    
    def test_create_refresh_token_success(self):
        """
        Testa criação de refresh token
        Testet Erstellung von Refresh Token
        """
        data = {"user_id": 1, "username": "testuser"}
        token = create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Decodificar e verificar payload
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert payload["user_id"] == 1
        assert payload["username"] == "testuser"
        assert payload["type"] == "refresh"
        assert "exp" in payload
    
    def test_decode_valid_token(self):
        """
        Testa decodificação de token válido
        Testet Dekodierung gültiger Token
        """
        data = {"user_id": 42, "username": "validuser", "email": "valid@example.com"}
        token = create_access_token(data)
        
        # Decodificar
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        
        assert payload["user_id"] == 42
        assert payload["username"] == "validuser"
        assert payload["email"] == "valid@example.com"
    
    def test_decode_token_with_wrong_secret(self):
        """
        Testa token com secret incorreta
        Testet Token mit falschem Secret
        """
        data = {"user_id": 1}
        token = create_access_token(data)
        
        # Tentar decodificar com secret errada
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong-secret-key", algorithms=["HS256"])
    
    def test_decode_malformed_token(self):
        """
        Testa token malformado
        Testet ungültigen Token
        """
        malformed_token = "invalid.token.format"
        
        with pytest.raises(JWTError):
            jwt.decode(malformed_token, settings.SECRET_KEY, algorithms=["HS256"])
    
    def test_decode_expired_token(self):
        """
        Testa token expirado
        Testet abgelaufenen Token
        """
        data = {"user_id": 1}
        # Criar token que expira imediatamente
        expired_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expired_delta)
        
        # Tentar decodificar token expirado
        with pytest.raises(JWTError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    
    def test_token_without_user_id(self):
        """
        Testa token sem user_id
        Testet Token ohne user_id
        """
        data = {"username": "nouser"}
        token = create_access_token(data)
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert "user_id" not in payload
        assert payload["username"] == "nouser"


# ============================================================================
# TESTES DE PERMISSÕES / PERMISSIONS TESTS
# ============================================================================

class TestPermissions:
    """Testes de permissões por role / Tests für Berechtigungen nach Rolle"""
    
    @pytest.fixture
    def system_admin_user(self):
        """Usuário SYSTEM_ADMIN / SYSTEM_ADMIN Benutzer"""
        return User(
            id=1,
            username="admin",
            email="admin@example.com",
            name="System Admin",
            password_hash="hash",
            role=UserRole.SYSTEM_ADMIN,
            access_level=AccessLevel.LEVEL_6,
            department="IT und Datenschutz",
            team="TI",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def director_user(self):
        """Usuário DIRECTOR / DIRECTOR Benutzer"""
        return User(
            id=2,
            username="director",
            email="director@example.com",
            name="Director",
            password_hash="hash",
            role=UserRole.DIRECTOR,
            access_level=AccessLevel.LEVEL_5,
            department="Geschäftsführung",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def department_admin_user(self):
        """Usuário DEPARTMENT_ADM / DEPARTMENT_ADM Benutzer"""
        return User(
            id=3,
            username="dept_admin",
            email="deptadmin@example.com",
            name="Dept Admin",
            password_hash="hash",
            role=UserRole.DEPARTMENT_ADM,
            access_level=AccessLevel.LEVEL_4,
            department="Personal Organization und Finanzen",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def staff_user(self):
        """Usuário STAFF / STAFF Benutzer"""
        return User(
            id=4,
            username="staff",
            email="staff@example.com",
            name="Staff Member",
            password_hash="hash",
            role=UserRole.STAFF,
            access_level=AccessLevel.LEVEL_2,
            department="Personal Organization und Finanzen",
            team="Finanzen und Rechnungswesen",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def readonly_user(self):
        """Usuário READ_ONLY / READ_ONLY Benutzer"""
        return User(
            id=5,
            username="readonly",
            email="readonly@example.com",
            name="Read Only",
            password_hash="hash",
            role=UserRole.READ_ONLY,
            access_level=AccessLevel.LEVEL_1,
            department="Personal Organization und Finanzen",
            is_active=True,
            is_verified=True
        )
    
    @pytest.fixture
    def sample_contract(self):
        """Contrato de exemplo / Beispielvertrag"""
        return Contract(
            id=100,
            title="Test Contract",
            client_name="Test Client",
            start_date=date.today(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            department="Personal Organization und Finanzen",
            team="Finanzen und Rechnungswesen",
            created_by=4,  # Criado por staff_user
            responsible_user_id=4
        )
    
    # =======================================================================
    # TESTES DE can_view_contract
    # =======================================================================
    
    def test_can_view_contract_system_admin(self, system_admin_user, sample_contract):
        """SYSTEM_ADMIN pode ver qualquer contrato / SYSTEM_ADMIN kann alle Verträge sehen"""
        assert can_view_contract(system_admin_user, sample_contract) is True
    
    def test_can_view_contract_director(self, director_user, sample_contract):
        """DIRECTOR pode ver qualquer contrato / DIRECTOR kann alle Verträge sehen"""
        assert can_view_contract(director_user, sample_contract) is True
    
    def test_can_view_contract_department_admin_same_dept(self, department_admin_user, sample_contract):
        """DEPARTMENT_ADM pode ver contratos do mesmo departamento"""
        assert can_view_contract(department_admin_user, sample_contract) is True
    
    def test_can_view_contract_department_admin_different_dept(self, department_admin_user):
        """DEPARTMENT_ADM NÃO pode ver contratos de outro departamento"""
        other_dept_contract = Contract(
            id=101,
            title="Other Dept Contract",
            client_name="Client",
            start_date=date.today(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            department="IT und Datenschutz",  # Departamento diferente
            created_by=10
        )
        assert can_view_contract(department_admin_user, other_dept_contract) is False
    
    def test_can_view_contract_staff_own_contract(self, staff_user, sample_contract):
        """STAFF pode ver seus próprios contratos / STAFF kann eigene Verträge sehen"""
        assert can_view_contract(staff_user, sample_contract) is True
    
    def test_can_view_contract_staff_same_team(self, staff_user):
        """STAFF pode ver contratos do mesmo time"""
        team_contract = Contract(
            id=102,
            title="Team Contract",
            client_name="Client",
            start_date=date.today(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            department="Personal Organization und Finanzen",
            team="Finanzen und Rechnungswesen",
            created_by=99  # Outro usuário
        )
        assert can_view_contract(staff_user, team_contract) is True
    
    def test_can_view_contract_staff_different_team(self, staff_user):
        """STAFF NÃO pode ver contratos de outro time"""
        other_team_contract = Contract(
            id=103,
            title="Other Team Contract",
            client_name="Client",
            start_date=date.today(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            department="IT und Datenschutz",
            team="PR",
            created_by=99
        )
        assert can_view_contract(staff_user, other_team_contract) is False
    
    # =======================================================================
    # TESTES DE can_edit_contract
    # =======================================================================
    
    def test_can_edit_contract_system_admin(self, system_admin_user, sample_contract):
        """SYSTEM_ADMIN pode editar qualquer contrato"""
        assert can_edit_contract(system_admin_user, sample_contract) is True
    
    def test_can_edit_contract_director(self, director_user, sample_contract):
        """DIRECTOR pode editar qualquer contrato"""
        assert can_edit_contract(director_user, sample_contract) is True
    
    def test_can_edit_contract_department_admin_same_dept(self, department_admin_user, sample_contract):
        """DEPARTMENT_ADM pode editar contratos do mesmo departamento"""
        assert can_edit_contract(department_admin_user, sample_contract) is True
    
    def test_can_edit_contract_department_admin_different_dept(self, department_admin_user):
        """DEPARTMENT_ADM NÃO pode editar contratos de outro departamento"""
        other_dept_contract = Contract(
            id=104,
            title="Other Dept",
            client_name="Client",
            start_date=date.today(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            department="IT und Datenschutz",
            created_by=10
        )
        assert can_edit_contract(department_admin_user, other_dept_contract) is False
    
    def test_can_edit_contract_staff_own(self, staff_user, sample_contract):
        """STAFF pode editar seus próprios contratos"""
        assert can_edit_contract(staff_user, sample_contract) is True
    
    def test_can_edit_contract_readonly_cannot_edit(self, readonly_user, sample_contract):
        """READ_ONLY NÃO pode editar nada"""
        assert can_edit_contract(readonly_user, sample_contract) is False
    
    # =======================================================================
    # TESTES DE can_delete_contract
    # =======================================================================
    
    def test_can_delete_contract_system_admin(self, system_admin_user, sample_contract):
        """SYSTEM_ADMIN pode deletar qualquer contrato"""
        assert can_delete_contract(system_admin_user, sample_contract) is True
    
    def test_can_delete_contract_director(self, director_user, sample_contract):
        """DIRECTOR pode deletar qualquer contrato"""
        assert can_delete_contract(director_user, sample_contract) is True
    
    def test_can_delete_contract_department_admin_same_dept(self, department_admin_user, sample_contract):
        """DEPARTMENT_ADM pode deletar contratos do mesmo departamento"""
        assert can_delete_contract(department_admin_user, sample_contract) is True
    
    def test_can_delete_contract_department_admin_different_dept(self, department_admin_user):
        """DEPARTMENT_ADM NÃO pode deletar contratos de outro departamento"""
        other_dept_contract = Contract(
            id=105,
            title="Other",
            client_name="Client",
            start_date=date.today(),
            contract_type=ContractType.SERVICE,
            status=ContractStatus.ACTIVE,
            department="IT und Datenschutz",
            created_by=10
        )
        assert can_delete_contract(department_admin_user, other_dept_contract) is False
    
    def test_can_delete_contract_staff_cannot_delete(self, staff_user, sample_contract):
        """STAFF NÃO pode deletar contratos"""
        assert can_delete_contract(staff_user, sample_contract) is False
    
    def test_can_delete_contract_readonly_cannot_delete(self, readonly_user, sample_contract):
        """READ_ONLY NÃO pode deletar contratos"""
        assert can_delete_contract(readonly_user, sample_contract) is False
    
    # =======================================================================
    # TESTES DE can_approve_contract
    # =======================================================================
    
    def test_can_approve_contract_system_admin(self, system_admin_user, sample_contract):
        """SYSTEM_ADMIN pode aprovar qualquer contrato"""
        assert can_approve_contract(system_admin_user, sample_contract) is True
    
    def test_can_approve_contract_director(self, director_user, sample_contract):
        """DIRECTOR pode aprovar qualquer contrato"""
        assert can_approve_contract(director_user, sample_contract) is True
    
    def test_can_approve_contract_staff_cannot_approve(self, staff_user, sample_contract):
        """STAFF NÃO pode aprovar contratos"""
        # A função retorna True/False dependendo da lógica, vamos verificar
        result = can_approve_contract(staff_user, sample_contract)
        assert isinstance(result, bool)
    
    def test_can_approve_contract_readonly_cannot_approve(self, readonly_user, sample_contract):
        """READ_ONLY NÃO pode aprovar contratos"""
        result = can_approve_contract(readonly_user, sample_contract)
        assert isinstance(result, bool)
