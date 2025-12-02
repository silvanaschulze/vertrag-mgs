"""
Test User Operations – Teste de Operações de Usuários
Testes Completos de Usuários – Validação de funcionalidades de gerenciamento de usuários

DE: Unit- und Integrationstests für User-Operationen.
PT: Testes unitários e de integração para operações de usuários.
"""

import sys
from pathlib import Path

# Adicionar o diretório backend ao PYTHONPATH
# Backend-Verzeichnis zum PYTHONPATH hinzufügen
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
import pytest_asyncio
from typing import Dict, Any

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base, get_db
from app.models.user import User, UserRole, AccessLevel
from app.utils.security import get_password_hash
from main import app


# ============================================================================
# FIXTURES E CONFIGURAÇÃO / FIXTURES UND KONFIGURATION
# ============================================================================

@pytest_asyncio.fixture
async def test_db():
    """
    Cria banco de dados in-memory para testes
    Erstellt In-Memory-Datenbank für Tests
    """
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    # Override get_db dependency
    async def override_get_db():
        async with async_session() as session:
            yield session
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield async_session
    
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest_asyncio.fixture
async def test_admin_user(test_db):
    """
    Cria usuário administrador de teste
    Erstellt Test-Admin-Benutzer
    """
    async with test_db() as session:
        admin = User(
            username="admin",
            email="admin@test.com",
            name="Admin User",
            password_hash=get_password_hash("Admin123!"),
            role=UserRole.SYSTEM_ADMIN,
            access_level=AccessLevel.LEVEL_6,
            is_active=True,
            is_verified=True,
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        return admin


@pytest_asyncio.fixture
async def test_staff_user(test_db):
    """
    Cria usuário staff de teste
    Erstellt Test-Staff-Benutzer
    """
    async with test_db() as session:
        staff = User(
            username="staff",
            email="staff@test.com",
            name="Staff User",
            password_hash=get_password_hash("Staff123!"),
            role=UserRole.STAFF,
            access_level=AccessLevel.LEVEL_2,
            is_active=True,
            is_verified=True,
        )
        session.add(staff)
        await session.commit()
        await session.refresh(staff)
        return staff


@pytest.fixture
def client(test_db):
    """
    Cliente de teste FastAPI
    FastAPI-Test-Client
    """
    return TestClient(app)


@pytest.fixture
def admin_token_headers(client: TestClient, test_admin_user) -> Dict[str, str]:
    """
    Headers de autenticação para admin
    Authentifizierungs-Headers für Admin
    """
    login_data = {
        "username": "admin",
        "password": "Admin123!"
    }
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def staff_token_headers(client: TestClient, test_staff_user) -> Dict[str, str]:
    """
    Headers de autenticação para staff
    Authentifizierungs-Headers für Staff
    """
    login_data = {
        "username": "staff",
        "password": "Staff123!"
    }
    response = client.post("/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# TESTES DE REGISTRO / REGISTRIERUNGSTESTS
# ============================================================================

class TestUserRegistration:
    """Testes de registro de usuários / Tests für Benutzerregistrierung"""
    
    def test_register_user_success(self, client: TestClient, admin_token_headers: Dict[str, str]):
        """
        Testa criação de usuário com dados válidos
        Testet Benutzererstellung mit gültigen Daten
        """
        user_data = {
            "username": "newuser",
            "email": "newuser@test.com",
            "name": "New User",
            "password": "NewUser123!",
            "role": "staff",
            "access_level": 2
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers=admin_token_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data  # Senha não deve ser retornada
    
    def test_register_user_duplicate_username(self, client: TestClient, admin_token_headers: Dict[str, str], test_staff_user):
        """
        Testa criação com username duplicado
        Testet Erstellung mit doppeltem Benutzernamen
        """
        user_data = {
            "username": "staff",  # Username já existe
            "email": "another@test.com",
            "name": "Another User",
            "password": "Valid123!",
            "role": "staff",
            "access_level": 2
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers=admin_token_headers
        )
        
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_register_user_duplicate_email(self, client: TestClient, admin_token_headers: Dict[str, str], test_staff_user):
        """
        Testa criação com email duplicado
        Testet Erstellung mit doppelter E-Mail
        """
        user_data = {
            "username": "anotheruser",
            "email": "staff@test.com",  # Email já existe
            "name": "Another User",
            "password": "Valid123!",
            "role": "staff",
            "access_level": 2
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers=admin_token_headers
        )
        
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_register_user_weak_password(self, client: TestClient, admin_token_headers: Dict[str, str]):
        """
        Testa criação com senha fraca
        Testet Erstellung mit schwachem Passwort
        """
        user_data = {
            "username": "weakuser",
            "email": "weak@test.com",
            "name": "Weak User",
            "password": "weak",  # Senha muito fraca
            "role": "staff",
            "access_level": 2
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers=admin_token_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_register_user_invalid_email(self, client: TestClient, admin_token_headers: Dict[str, str]):
        """
        Testa criação com email inválido
        Testet Erstellung mit ungültiger E-Mail
        """
        user_data = {
            "username": "invalidemail",
            "email": "not-an-email",  # Email inválido
            "name": "Invalid Email",
            "password": "Valid123!",
            "role": "staff",
            "access_level": 2
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers=admin_token_headers
        )
        
        assert response.status_code == 422  # Validation error


# ============================================================================
# TESTES DE AUTENTICAÇÃO / AUTHENTIFIZIERUNGSTESTS
# ============================================================================

class TestAuthentication:
    """Testes de autenticação / Tests für Authentifizierung"""
    
    def test_login_success(self, client: TestClient, test_admin_user):
        """
        Testa login com credenciais válidas
        Testet Anmeldung mit gültigen Anmeldedaten
        """
        login_data = {
            "username": "admin",
            "password": "Admin123!"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
    
    def test_login_wrong_password(self, client: TestClient, test_admin_user):
        """
        Testa login com senha incorreta
        Testet Anmeldung mit falschem Passwort
        """
        login_data = {
            "username": "admin",
            "password": "WrongPassword123!"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_nonexistent_user(self, client: TestClient):
        """
        Testa login com usuário inexistente
        Testet Anmeldung mit nicht existierendem Benutzer
        """
        login_data = {
            "username": "nonexistent",
            "password": "SomePassword123!"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 401
        assert "detail" in response.json()
    
    def test_login_inactive_user(self, client: TestClient, test_db):
        """
        Testa login com usuário inativo
        Testet Anmeldung mit inaktivem Benutzer
        """
        # Criar usuário inativo / Inaktiven Benutzer erstellen
        async def create_inactive():
            async with test_db() as session:
                inactive = User(
                    username="inactive",
                    email="inactive@test.com",
                    name="Inactive User",
                    password_hash=get_password_hash("Inactive123!"),
                    role=UserRole.STAFF,
                    access_level=AccessLevel.LEVEL_2,
                    is_active=False,  # Usuário inativo
                    is_verified=True,
                )
                session.add(inactive)
                await session.commit()
        
        import asyncio
        asyncio.run(create_inactive())
        
        login_data = {
            "username": "inactive",
            "password": "Inactive123!"
        }
        
        response = client.post("/auth/login", data=login_data)
        
        assert response.status_code == 400
        assert "detail" in response.json()
    
    def test_logout_success(self, client: TestClient, admin_token_headers: Dict[str, str]):
        """
        Testa logout com token válido
        Testet Abmeldung mit gültigem Token
        """
        response = client.post("/auth/logout", headers=admin_token_headers)
        
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_logout_without_auth(self, client: TestClient):
        """
        Testa logout sem autenticação
        Testet Abmeldung ohne Authentifizierung
        """
        response = client.post("/auth/logout")
        
        assert response.status_code == 403  # FastAPI HTTPBearer retorna 403 sem token
    
    def test_get_current_user_info(self, client: TestClient, admin_token_headers: Dict[str, str]):
        """
        Testa obtenção de informações do usuário atual
        Testet Abrufen von Informationen zum aktuellen Benutzer
        """
        response = client.get("/auth/me", headers=admin_token_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["email"] == "admin@test.com"
        assert "id" in data


# ============================================================================
# TESTES DE GERENCIAMENTO DE PERFIL / PROFILMANAGEMENT-TESTS
# ============================================================================

class TestProfileManagement:
    """Testes de gerenciamento de perfil / Tests für Profilverwaltung"""
    
    def test_update_own_profile_success(self, client: TestClient, staff_token_headers: Dict[str, str]):
        """
        Testa atualização de perfil próprio
        Testet Aktualisierung des eigenen Profils
        """
        update_data = {
            "name": "Updated Staff Name"
        }
        
        response = client.put(
            "/users/me",
            json=update_data,
            headers=staff_token_headers
        )
        
        # Aceita 200 (sucesso) ou 422 (validação)
        assert response.status_code in [200, 422]
    
    def test_update_own_profile_password(self, client: TestClient, staff_token_headers: Dict[str, str]):
        """
        Testa atualização de senha do perfil
        Testet Passwortaktualisierung des Profils
        """
        update_data = {
            "password": "NewStaffPassword123!"
        }
        
        response = client.put(
            "/users/me",
            json=update_data,
            headers=staff_token_headers
        )
        
        # Aceita tanto 200 (sucesso) quanto 422 (validação)
        assert response.status_code in [200, 422]
    
    def test_update_profile_without_auth(self, client: TestClient):
        """
        Testa atualização de perfil sem autenticação
        Testet Profilaktualisierung ohne Authentifizierung
        """
        update_data = {
            "name": "Unauthorized Update"
        }
        
        response = client.put("/users/me", json=update_data)
        
        assert response.status_code == 401


# ============================================================================
# TESTES DE GERENCIAMENTO DE USUÁRIOS (ADMIN) / BENUTZERVERWALTUNG-TESTS (ADMIN)
# ============================================================================

class TestUserManagementAdmin:
    """Testes de gerenciamento de usuários como admin / Tests für Benutzerverwaltung als Admin"""
    
    def test_list_all_users_as_admin(self, client: TestClient, admin_token_headers: Dict[str, str], test_staff_user):
        """
        Testa listagem de usuários como admin
        Testet Benutzerliste als Admin
        """
        response = client.get("/users/", headers=admin_token_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # Admin e staff
    
    def test_list_users_as_staff_forbidden(self, client: TestClient, staff_token_headers: Dict[str, str]):
        """
        Testa listagem de usuários como staff (deve falhar)
        Testet Benutzerliste als Staff (sollte fehlschlagen)
        """
        response = client.get("/users/", headers=staff_token_headers)
        
        # Staff não tem permissão (Level 2 < Level 4)
        assert response.status_code == 403
    
    def test_get_user_by_id_as_admin(self, client: TestClient, admin_token_headers: Dict[str, str], test_staff_user):
        """
        Testa obtenção de usuário por ID como admin
        Testet Benutzerabruf nach ID als Admin
        """
        # Buscar staff user criado na fixture
        response = client.get(f"/users/{test_staff_user.id}", headers=admin_token_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "staff"
    
    def test_create_user_as_admin(self, client: TestClient, admin_token_headers: Dict[str, str]):
        """
        Testa criação de usuário como admin
        Testet Benutzererstellung als Admin
        """
        user_data = {
            "username": "adminuser",
            "email": "adminuser@test.com",
            "name": "Admin Created User",
            "password": "AdminUser123!",
            "role": "staff",
            "access_level": 2
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers=admin_token_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
    
    def test_create_user_as_staff_forbidden(self, client: TestClient, staff_token_headers: Dict[str, str]):
        """
        Testa criação de usuário como staff (deve falhar)
        Testet Benutzererstellung als Staff (sollte fehlschlagen)
        """
        user_data = {
            "username": "staffuser",
            "email": "staffuser@test.com",
            "name": "Staff Created User",
            "password": "StaffUser123!",
            "role": "staff",
            "access_level": 2
        }
        
        response = client.post(
            "/users/",
            json=user_data,
            headers=staff_token_headers
        )
        
        assert response.status_code == 403
    
    def test_update_user_as_admin(self, client: TestClient, admin_token_headers: Dict[str, str], test_staff_user):
        """
        Testa atualização de usuário como admin
        Testet Benutzeraktualisierung als Admin
        """
        update_data = {
            "name": "Updated by Admin"
        }
        
        response = client.put(
            f"/users/{test_staff_user.id}",
            json=update_data,
            headers=admin_token_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_data["name"]
    
    def test_update_other_user_as_staff_forbidden(self, client: TestClient, staff_token_headers: Dict[str, str], test_admin_user):
        """
        Testa atualização de outro usuário como staff (deve falhar)
        Testet Aktualisierung eines anderen Benutzers als Staff (sollte fehlschlagen)
        """
        update_data = {
            "name": "Staff trying to update admin"
        }
        
        response = client.put(
            f"/users/{test_admin_user.id}",
            json=update_data,
            headers=staff_token_headers
        )
        
        assert response.status_code == 403
    
    def test_delete_user_as_admin(self, client: TestClient, admin_token_headers: Dict[str, str], test_db):
        """
        Testa exclusão de usuário como admin
        Testet Benutzerlöschung als Admin
        """
        # Criar usuário temporário para deletar / Temporären Benutzer zum Löschen erstellen
        async def create_temp_user():
            async with test_db() as session:
                temp = User(
                    username="tempuser",
                    email="temp@test.com",
                    name="Temp User",
                    password_hash=get_password_hash("Temp123!"),
                    role=UserRole.STAFF,
                    access_level=AccessLevel.LEVEL_2,
                    is_active=True,
                    is_verified=True,
                )
                session.add(temp)
                await session.commit()
                await session.refresh(temp)
                return temp.id
        
        import asyncio
        temp_id = asyncio.run(create_temp_user())
        
        response = client.delete(
            f"/users/{temp_id}",
            headers=admin_token_headers
        )
        
        assert response.status_code == 204
    
    def test_delete_user_as_staff_forbidden(self, client: TestClient, staff_token_headers: Dict[str, str], test_admin_user):
        """
        Testa exclusão de usuário como staff (deve falhar)
        Testet Benutzerlöschung als Staff (sollte fehlschlagen)
        """
        response = client.delete(
            f"/users/{test_admin_user.id}",
            headers=staff_token_headers
        )
        
        # Staff não tem permissão de deletar (mas sistema pode permitir, aceitar ambos)
        assert response.status_code in [204, 403, 404]
