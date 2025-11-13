# Technische Dokumentation - Vertragsverwaltungssystem
# Documentação Técnica - Sistema de Gerenciamento de Contratos

## Inhaltsverzeichnis / Índice

1. [Projektübersicht / Visão Geral do Projeto](#projektübersicht--visão-geral-do-projeto)
2. [Systemarchitektur / Arquitetura do Sistema](#systemarchitektur--arquitetura-do-sistema)
3. [Verzeichnisstruktur / Estrutura de Diretórios](#verzeichnisstruktur--estrutura-de-diretórios)
4. [Datenmodelle / Modelos de Dados](#datenmodelle--modelos-de-dados)
5. [API-Endpunkte / API Endpoints](#api-endpunkte--api-endpoints)
6. [Services und Geschäftslogik / Serviços e Lógica de Negócio](#services-und-geschäftslogik--serviços-e-lógica-de-negócio)
7. [Konfiguration und Deployment / Configuração e Deploy](#konfiguration-und-deployment--configuração-e-deploy)
8. [Tests / Testes](#tests--testes)
9. [Entwicklung / Desenvolvimento](#entwicklung--desenvolvimento)

---

## Projektübersicht / Visão Geral do Projeto

### Beschreibung / Descrição
**Deutsch:** Vertragsverwaltungssystem mit automatischen Ablaufbenachrichtigungen, entwickelt in Python mit FastAPI, SQLAlchemy und E-Mail-Benachrichtigungssystem.

**Português:** Sistema de gerenciamento de contratos com notificações automáticas de vencimento, desenvolvido em Python com FastAPI, SQLAlchemy e sistema de alertas por e-mail.

### Hauptfunktionen / Funcionalidades Principais
- **Vertrags-CRUD / CRUD de Contratos**
- **Automatische Benachrichtigungen / Notificações Automáticas** (T-60, T-30, T-10, T-1)
- **Dokumentenerstellung / Geração de Documentos** (DOCX → PDF)
- **Benutzerverwaltung / Gerenciamento de Usuários**
- **Berechtigungssystem / Sistema de Permissões**
- **Berichte und Statistiken / Relatórios e Estatísticas**

-- **Darstellung und Verwaltung von Miet- / Pachtverträgen / Representação e gestão de contratos de arrendamento**
-- **Mietstaffelung / Escalonamentos de aluguel (RentStep)**
-- **Erfassung von Verträgen mit vordefinierten zukünftigen Anpassungen / Registro de contratos com reajustes futuros já definidos**

### Technologie-Stack / Stack Tecnológico
- **Backend:** Python 3.11+ / FastAPI / SQLAlchemy 2.0
- **Datenbank:** SQLite (Entwicklung) / MySQL (Produktion)
- **Authentifizierung:** JWT (python-jose)
- **Dokumente:** docxtpl / LibreOffice
- **E-Mail:** SMTP
- **Tests:** pytest / asyncio
 - **Migrationen:** Alembic

---

## Systemarchitektur / Arquitetura do Sistema

### Architekturmuster / Padrão Arquitetural
Das System folgt einer **modularen Schichtenarchitektur** mit klarer Trennung der Verantwortlichkeiten:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Layer     │    │  Service Layer  │    │  Data Layer     │
│   (Routers)     │◄──►│   (Services)     │◄──►│   (Models)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Schemas       │    │   Utils         │    │   Database      │
│   (Validation)  │    │   (Helpers)     │    │   (SQLAlchemy)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Hauptkomponenten / Componentes Principais

Hinweis: Die modulare Schichtenarchitektur wurde bewusst so gestaltet, dass neue persistente Entitäten (z. B. `RentStep` für Mietstaffelungen) sauber in die bestehende Struktur integriert werden können. Router, Services und Models bleiben getrennt, wodurch Erweiterungen testbar und wartbar sind.


#### 1. **API Layer (API-Schicht)**
- **Routers:** REST-API-Endpunkte
- **Schemas:** Datenvalidierung und -serialisierung
- **Middleware:** CORS, Authentifizierung, Logging

#### 2. **Service Layer (Service-Schicht)**
- **UserService:** Benutzerverwaltung
- **ContractService:** Vertragsgeschäftslogik
- **NotificationService:** Benachrichtigungssystem
- **AuthService:** Authentifizierung und Autorisierung

#### 3. **Data Layer (Daten-Schicht)**
- **Models:** Datenbankentitäten
- **Database:** Konfiguration und Sitzungen
- **Migrations:** Schema-Versionskontrolle

---

## Verzeichnisstruktur / Estrutura de Diretórios

```
vertrag-mgs/
├── backend/                          # Backend der Anwendung
│   ├── app/                         # Hauptanwendungscode
│   │   ├── core/                    # Zentrale Konfigurationen
│   │   │   ├── config.py           # Anwendungskonfiguration
│   │   │   ├── database.py         # Datenbankkonfiguration
│   │   │   ├── security.py         # Sicherheit und JWT
│   │   │   └── permissions.py      # Berechtigungssystem
│   │   ├── models/                  # Datenmodelle (SQLAlchemy)
│   │   │   ├── user.py             # Benutzermodell
│   │   │   ├── contract.py         # Vertragsmodell
│   │   │   ├── alert.py            # Alertmodell
│   │   │   ├── rent_step.py        # Mietstaffelung / RentStep (neu)
│   │   │   └── permission.py       # Berechtigungsmodell
│   │   ├── schemas/                 # Pydantic-Schemas
│   │   │   ├── user.py             # Benutzerschemas
│   │   │   ├── contract.py         # Vertragsschemas
│   │   │   ├── token.py            # Authentifizierungsschemas
│   │   │   ├── extracted_contract.py # Extraktionsschemas
│   │   │   └── permissions.py      # Berechtigungsschemas
│   │   ├── routers/                 # API-Endpunkte
│   │   │   ├── auth.py             # Authentifizierung
│   │   │   ├── contracts.py        # Verträge
│   │   │   ├── contracts_import.py  # PDF-Import
│   │   │   ├── users.py            # Benutzer
│   │   │   ├── alerts.py           # Benachrichtigungen
│   │   │   └── rent_steps.py       # Mietstaffelung Endpoints (neu)
│   │   ├── services/               # Geschäftslogik
│   │   │   ├── user_service.py     # Benutzerservice
│   │   │   ├── contract_service.py # Vertragsservice
│   │   │   ├── notification_service.py # Benachrichtigungsservice
│   │   │   ├── auth_service.py     # Authentifizierungsservice
│   │   │   ├── pdf_reader.py       # PDF-Leser
│   │   │   └── pdf_reader_pkg/     # PDF-Verarbeitungspaket
│   │   │       ├── analysis.py     # Vertragsanalyse
│   │   │       ├── dates.py        # Datumsextraktion
│   │   │       ├── extractors.py  # Extraktoren
│   │   │       ├── financials.py  # Finanzdaten
│   │   │       ├── ocr.py         # OCR
│   │   │       ├── parsers.py     # Parser
│   │   │       ├── service.py     # Hauptservice
│   │   │       └── validate.py    # Validierung
│   │   ├── utils/                  # Hilfsprogramme
│   │   │   ├── security.py         # Sicherheit und Hash
│   │   │   ├── email.py            # E-Mail-Versand
│   │   │   └── document_generator.py # Dokumentenerstellung
│   │   └── __init__.py
│   ├── tests/                      # Tests (Plural)
│   │   ├── test_complete.py        # Integrationstests
│   │   ├── test_integration_db.py  # Datenbanktests
│   │   ├── test_alerts.py          # Alerttests
│   │   ├── test_local.py           # Lokale Tests
│   │   └── test_utils.py           # Hilfsprogramm-Tests
│   ├── main.py                     # Anwendungseinstiegspunkt
│   ├── Dockerfile                  # Docker-Container
│   └── requirements.txt            # Abhängigkeiten
├── alembic/                        # Datenbankmigrationen
│   ├── versions/                   # Migrationsversionen
│   │   ├── 0002_add_rent_steps.py  # Migration für RentStep (neu)
│   └── env.py                      # Alembic-Konfiguration
├── alembic.ini                     # Alembic-Konfiguration
├── requirements.txt                # Hauptabhängigkeiten
└── README.md                       # Projektdokumentation
```

---

## Datenmodelle / Modelos de Dados

### 1. **User (Benutzer / Usuário)**

```python
class User(Base):
    __tablename__ = "users"
    
    # Hauptfelder / Campos principais
    id: int                          # Eindeutige ID
    username: str                    # Benutzername
    email: str                       # E-Mail
    name: str                        # Vollständiger Name
    role: UserRole                   # Rolle (USER, MANAGER, ADMIN)
    password_hash: str               # Passwort-Hash
    
    # Audit-Felder / Campos de auditoria
    created_at: datetime             # Erstellungsdatum
    updated_at: datetime             # Aktualisierungsdatum
    last_login: datetime             # Letzter Login
    is_active: bool                  # Aktiver Status
    is_deleted: bool                 # Soft Delete
```

**Benutzerrollen / Funções de Usuário:**
- `USER`: Normaler Benutzer - kann eigene Verträge anzeigen und erstellen
- `MANAGER`: Manager - kann Teamverträge verwalten
- `ADMIN`: Administrator - vollständiger Systemzugang

### 2. **Contract (Vertrag / Contrato)**

```python
class Contract(Base):
    __tablename__ = "contracts"
    
    # Hauptfelder / Campos principais
    id: int                          # Eindeutige ID
    title: str                       # Vertragstitel
    description: str                 # Beschreibung
    contract_type: ContractType      # Typ (SERVICE, PRODUCT, etc.)
    status: ContractStatus           # Status (DRAFT, ACTIVE, EXPIRED)
    
    # Finanzfelder / Campos financeiros
    value: Decimal                   # Vertragswert
    currency: str                    # Währung (EUR, USD, etc.)
    
    # Daten / Datas
    start_date: date                 # Startdatum
    end_date: date                   # Enddatum
    renewal_date: date               # Verlängerungsdatum
    
    # Kunde / Cliente
    client_name: str                 # Kundenname
    client_email: str                # Kunden-E-Mail
    client_phone: str                # Kundentelefon
    client_address: str              # Kundenadresse
    
    # Audit / Auditoria
    created_by: int                  # ID des erstellen Benutzers
    created_at: datetime             # Erstellungsdatum
    updated_at: datetime             # Aktualisierungsdatum
```

**Vertragsstatus / Status do Contrato:**
- `DRAFT`: Entwurf
- `ACTIVE`: Aktiv
- `EXPIRED`: Abgelaufen
- `TERMINATED`: Beendet
- `PENDING_APPROVAL`: Wartet auf Genehmigung

### Mietstaffelung / RentStep (neu)

```python
class RentStep(Base):
  __tablename__ = "rent_steps"

  # Kernfelder / Campos principais
  id: int                  # Primärschlüssel
  contract_id: int         # FK -> contracts.id
  effective_date: date     # Datum, ab dem die Anpassung gilt
  amount: Decimal          # Neuer Betrag (numeric(12,2))
  currency: str | None     # Währung (optional)
  note: str | None         # Freitext
  created_by: int | None   # ID des Erstellers
  created_at: datetime     # Erstellungszeitpunkt (server default)

  # DB-Constraints / Regras de BD
  # UNIQUE(contract_id, effective_date) verhindert doppelte Einträge für dasselbe Datum
```

Kurzbeschreibung / Descrição curta:
- Speichert geplante Miet-/Pachtanpassungen für Verträge.
- Validierungen: `effective_date >= contract.start_date` (Service-Level) und `amount >= 0`.
- Persistenz: Neue Tabelle `rent_steps` mit Unique-Constraint `(contract_id, effective_date)`.


### 3. **Alert (Benachrichtigung / Alerta)**

```python
class Alert(Base):
    __tablename__ = "alerts"
    
    # Hauptfelder / Campos principais
    id: int                          # Eindeutige ID
    contract_id: int                 # Vertrags-ID
    alert_type: AlertType            # Typ (T-60, T-30, T-10, T-1)
    status: AlertStatus              # Status (PENDING, SENT, FAILED)
    
    # Terminierung / Agendamento
    scheduled_for: datetime           # Geplante Zeit
    sent_at: datetime                # Versandzeit
    
    # E-Mail / E-mail
    recipient: str                   # Empfänger
    subject: str                     # Betreff
    error: str                       # Fehler (falls vorhanden)
```

**Alert-Typen / Tipos de Alerta:**
- `T_MINUS_60`: 60 Tage vor Ablauf
- `T_MINUS_30`: 30 Tage vor Ablauf
- `T_MINUS_10`: 10 Tage vor Ablauf
- `T_MINUS_1`: 1 Tag vor Ablauf

**Scheduling-System / Sistema de Agendamento:**
- **Hintergrund-Scheduler:** Verarbeitet Benachrichtigungen automatisch alle 6 Stunden
- **Deduplizierung:** Verhindert doppelte Benachrichtigungen
- **Neuverarbeitung:** Ermöglicht Neuverarbeitung fehlgeschlagener Alerts
- **Konfigurierbar:** Alert-Fenster können angepasst werden (D-90, D-60, D-30, D-10, D-1)

### **Hintergrund-Scheduler in main.py / Background Scheduler no main.py**

**🔄 Automatisches Scheduling-System**

Das System implementiert einen robusten **Hintergrund-Scheduler** in `main.py` mit `asyncio`:

**📋 Implementierung im Lifespan:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Verwaltet den Anwendungslebenszyklus / Manages application lifecycle"""
    global scheduler_task
    
    # Startup / Inicialização
    logger.info("Anwendung wird gestartet / Starting application")
    scheduler_task = asyncio.create_task(background_scheduler())
    logger.info("Hintergrund-Scheduler gestartet / Background scheduler started")
    
    yield
    
    # Shutdown / Finalização
    logger.info("Anwendung wird beendet / Shutting down application")
    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        logger.info("Hintergrund-Scheduler gestoppt / Background scheduler stopped")
```

**⏰ Verarbeitungsfrequenz:**
```python
async def background_scheduler() -> None:
    """Hintergrund-Task für periodische Alert-Verarbeitung"""
    while True:
        try:
            await process_contract_alerts()
            # 6 Stunden warten vor nächster Verarbeitung
            await asyncio.sleep(6 * 60 * 60)  # 6 Stunden in Sekunden
        except Exception as e:
            logger.error(f"Fehler im Hintergrund-Scheduler: {e}")
            # 1 Stunde warten bei Fehler
            await asyncio.sleep(60 * 60)  # 1 Stunde in Sekunden
```

**🔧 Scheduler-Eigenschaften:**
- **Frequenz:** Alle 6 Stunden (21.600 Sekunden)
- **Resilient:** Funktioniert auch bei Fehlern weiter
- **Fallback:** 1 Stunde Wartezeit bei Fehlern
- **Logging:** Detaillierte Logs auf DE/PT
- **Graceful Shutdown:** Korrekte Beendigung beim App-Stop

**📊 Alert-Verarbeitung:**
```python
async def process_contract_alerts() -> None:
    """Verarbeitet ablaufende Vertragsbenachrichtigungen"""
    try:
        logger.info("Vertrags-Alert-Verarbeitung gestartet")
        
        async with SessionLocal() as db:
            notification_service = NotificationService(db)
            result = await notification_service.process_due_alerts()
            
            logger.info(f"{result.total} Vertragsbenachrichtigungen verarbeitet")
    except Exception as e:
        logger.error(f"Fehler bei Alert-Verarbeitung: {e}")
```

**🎯 Monitoring-Endpunkte:**
- **`GET /scheduler/status`:** Scheduler-Status
- **`POST /scheduler/trigger-alerts`:** Manuelle Verarbeitung auslösen

---

## API-Endpunkte / API Endpoints

### **Authentifizierung / Autenticação**

#### `POST /auth/login`
**Beschreibung:** Benutzeranmeldung (JWT)
**Body:**
```json
{
  "username": "string",
  "password": "string"
}
```
**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### `POST /auth/register`
**Beschreibung:** Neue Benutzerregistrierung
**Body:**
```json
{
  "username": "string",
  "email": "string",
  "name": "string",
  "password": "string",
  "role": "user"
}
```

#### `GET /auth/me`
**Beschreibung:** Informationen des angemeldeten Benutzers
**Headers:** `Authorization: Bearer <token>`

### **Vertragsimport / Importação de Contratos**

#### `POST /contracts/import/pdf`
**Beschreibung:** Vertrag aus PDF mit intelligenter Extraktion importieren
**Body (multipart/form-data):**
- `file`: PDF-Datei
- `extraction_method`: Extraktionsmethode (combined, pdfplumber, pypdf2, pymupdf)
- `language`: Sprache für OCR (de)
- `include_ocr`: OCR einschließen (true/false)

**Response:**
```json
{
  "success": true,
  "extracted_data": {
    "title": "string",
    "client_name": "string",
    "value": "1000.00",
    "currency": "EUR",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "confidence_level": "hoch"
  },
  "processing_time": 2.5,
  "file_size": 1024000
}
```

#### `POST /contracts/import/upload`
**Beschreibung:** Vertragsupload mit Metadaten
**Body (multipart/form-data):**
- `file`: PDF-Datei
- `title`: Vertragstitel (optional)
- `client_name`: Kundenname (optional)
- `contract_type`: Vertragstyp (optional)

#### `GET /contracts/import/status`
**Beschreibung:** Status des Import-Systems
**Response:**
```json
{
  "status": "online",
  "upload_directory": "uploads/contracts",
  "max_file_size": 10485760,
  "allowed_extensions": [".pdf"],
  "files_in_upload_dir": 5
}
```

### **Verträge / Contratos**

#### `GET /contracts/`
**Beschreibung:** Verträge mit Filtern und Paginierung auflisten
**Query Parameter:**
- `page`: Seitennummer (Standard: 1)
- `per_page`: Elemente pro Seite (Standard: 10, max: 100)
- `status`: Filter nach Status
- `contract_type`: Filter nach Typ
- `search`: Suche nach Titel/Beschreibung
- `sort_by`: Feld für Sortierung
- `sort_order`: Reihenfolge (asc/desc)

#### `POST /contracts/`
**Beschreibung:** Neuen Vertrag erstellen
**Body:**
```json
{
  "title": "string",
  "description": "string",
  "contract_type": "service",
  "value": 1000.00,
  "currency": "EUR",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "client_name": "string",
  "client_email": "string"
}
```

#### `GET /contracts/{contract_id}`
**Beschreibung:** Vertrag nach ID abrufen

#### `PUT /contracts/{contract_id}`
**Beschreibung:** Vertrag aktualisieren

#### `DELETE /contracts/{contract_id}`
**Beschreibung:** Vertrag löschen

#### `GET /contracts/stats`
**Beschreibung:** Vertragsstatistiken

#### `GET /contracts/expiring`
**Beschreibung:** Verträge kurz vor Ablauf
**Query Parameter:**
- `days`: Tage bis Ablauf (Standard: 30)

#### `GET /contracts/{contract_id}/document`
**Beschreibung:** Vertragsdokument generieren
**Query Parameter:**
- `format`: Format (pdf/docx, Standard: pdf)

### Mietstaffelung - RentStep Endpoints / Endpoints Mietstaffelung

Die API stellt CRUD-Endpunkte für Mietstaffelungen (RentSteps) bereit. Schreiboperationen sind auf MANAGER/ADMIN beschränkt.

- `GET /contracts/{contract_id}/rent-steps`
  - Listet alle Mietstaffelungen für einen Vertrag (aufsteigend nach `effective_date`).

- `POST /contracts/{contract_id}/rent-steps`
  - Erstellt eine neue RentStep (Berechtigung: MANAGER/ADMIN).
  - Body (JSON):
    ```json
    {
      "effective_date": "2026-01-01",
      "amount": 1500.00,
      "currency": "EUR",
      "note": "Jährliche Anpassung"
    }
    ```

- `GET /contracts/{contract_id}/rent-steps/{id}`
  - Holt Details einer spezifischen Mietstaffelung.

- `PUT /contracts/{contract_id}/rent-steps/{id}`
  - Aktualisiert eine Mietstaffelung (Berechtigung: MANAGER/ADMIN).

- `DELETE /contracts/{contract_id}/rent-steps/{id}`
  - Löscht eine Mietstaffelung (Berechtigung: MANAGER/ADMIN).


### **Benutzer / Usuários**

#### `GET /users/`
**Beschreibung:** Benutzer auflisten (nur ADMIN)

#### `POST /users/`
**Beschreibung:** Benutzer erstellen (nur ADMIN)

#### `GET /users/{user_id}`
**Beschreibung:** Benutzer nach ID abrufen

#### `PUT /users/{user_id}`
**Beschreibung:** Benutzer aktualisieren

#### `DELETE /users/{user_id}`
**Beschreibung:** Benutzer löschen

#### `PATCH /users/{user_id}/activate`
**Beschreibung:** Benutzer aktivieren (nur ADMIN)

#### `PATCH /users/{user_id}/deactivate`
**Beschreibung:** Benutzer deaktivieren (nur ADMIN)

### **Benachrichtigungen / Alertas**

#### `GET /alerts/`
**Beschreibung:** Benachrichtigungen mit Filtern auflisten
**Query Parameter:**
- `page`: Seitennummer
- `per_page`: Elemente pro Seite
- `status`: Filter nach Status
- `alert_type`: Filter nach Typ
- `contract_id`: Filter nach Vertrag

#### `GET /alerts/{alert_id}`
**Beschreibung:** Benachrichtigung nach ID abrufen

#### `POST /alerts/{alert_id}/reprocess`
**Beschreibung:** Benachrichtigung neu verarbeiten

#### `GET /alerts/contract/{contract_id}`
**Beschreibung:** Benachrichtigungen eines bestimmten Vertrags

#### `GET /alerts/stats/summary`
**Beschreibung:** Benachrichtigungsstatistiken

---

## Services und Geschäftslogik / Serviços e Lógica de Negócio

### **UserService**

**Verantwortlichkeiten / Responsabilidades:**
- Benutzererstellung, -aktualisierung und -löschung
- Authentifizierung und Passwortverifikation
- Rollen- und Berechtigungsverwaltung
- Benutzersuche und -auflistung

**Hauptmethoden / Métodos Principais:**
```python
async def create_user(user_data: UserCreate) -> User
async def get_user_by_id(user_id: int) -> Optional[User]
async def get_user_by_email(email: str) -> Optional[User]
async def authenticate_user(username: str, password: str) -> Optional[User]
async def update_user(user_id: int, user_data: UserUpdate) -> Optional[User]
async def delete_user(user_id: int) -> bool
async def activate_user(user_id: int) -> bool
async def deactivate_user(user_id: int) -> bool
```

### **ContractService**

**Verantwortlichkeiten / Responsabilidades:**
- Vollständiges Vertrags-CRUD
- Filter, Suche und Paginierung
- Statistikberechnung
- Statusverwaltung

**Hauptmethoden / Métodos Principais:**
```python
async def create_contract(contract_data: ContractCreate, created_by: int) -> ContractResponse
async def get_contract(contract_id: int) -> Optional[ContractResponse]
async def update_contract(contract_id: int, update_data: ContractUpdate) -> Optional[ContractResponse]
async def delete_contract(contract_id: int) -> bool
async def list_contracts(skip: int, limit: int, filters: Dict, search: str) -> ContractListResponse
async def get_contract_stats() -> ContractStats
async def get_contracts_expiring_within(days: int) -> ContractListResponse
```

### **NotificationService**

**Verantwortlichkeiten / Responsabilidades:**
- Ablaufbenachrichtigungsverarbeitung
- Automatische zweisprachige E-Mails (DE/PT)
- Benachrichtigungsdeduplizierung
- Neuverarbeitung fehlgeschlagener Alerts
- Hintergrund-Scheduler (läuft alle 6 Stunden)

**Hauptmethoden / Métodos Principais:**
```python
async def process_due_alerts() -> AlertListResponse
async def reprocess_alert(alert_id: int) -> Optional[AlertResponse]
```

**Alert-Logik / Lógica de Alertas:**
1. Sucht aktive Verträge mit definiertem Enddatum
2. Berechnet verbleibende Tage bis Ablauf
3. Ordnet Alert-Typen zu (T-60, T-30, T-10, T-1)
4. Prüft, ob Alert bereits gesendet wurde (Deduplizierung)
5. Erstellt und sendet E-Mail mit zweisprachigem HTML-Template
6. Aktualisiert Alert-Status
7. Hintergrund-Scheduler verarbeitet automatisch

### **PDFReaderService**

**Verantwortlichkeiten / Responsabilidades:**
- PDF-Text-Extraktion (mehrere Methoden)
- Intelligente Vertragsanalyse
- Strukturierte Datenextraktion
- Dokumentvalidierung
- OCR bei Bedarf

**Hauptmethoden / Métodos Principais:**
```python
def extract_text_combined(pdf_path: str) -> Dict[str, Any]
def extract_text_with_pdfplumber(pdf_path: str) -> Dict[str, Any]
def extract_text_with_pypdf2(pdf_path: str) -> Dict[str, Any]
def extract_text_with_pymupdf(pdf_path: str) -> Dict[str, Any]
def extract_intelligent_data(text: str) -> Dict[str, Any]
def validate_pdf(pdf_path: str) -> Dict[str, Any]
```

**PDF-Verarbeitungspaket / Pacote de Processamento PDF:**

#### **Unterpaket pdf_reader_pkg/ - Spezialisierte Module**

**📁 Paketstruktur:**
```
app/services/pdf_reader_pkg/
├── __init__.py          # Wrapper mit Exports
├── service.py          # Hauptservice (Delegation)
├── extractors.py       # Text-Extraktoren (pdfplumber, pypdf2, pymupdf)
├── parsers.py          # Spezialisierte Parser (Titel, Kunde, E-Mail)
├── dates.py            # Datumsextraktion und -berechnung
├── financials.py       # Finanzdaten und Geldwerte
├── analysis.py         # Komplexitätsanalyse und Rechtsterminologie
├── ocr.py              # Optische Zeichenerkennung
└── validate.py         # PDF-Dokumentvalidierung
```

**🔧 Detaillierte Module:**

**1. `__init__.py` - Wrapper mit Exports**
```python
# Hauptexports des Pakets
__all__ = [
    "PDFReaderService", "get_pdf_reader_service",
    "extract_text_with_pdfplumber", "extract_text_with_pypdf2", 
    "extract_text_with_pymupdf", "extract_text_combined",
    "ocr_with_pytesseract", "validate_pdf",
    "extract_title", "extract_client_name", "extract_email",
    "extract_phone", "extract_address", "extract_description",
    "extract_money_values", "extract_financial_terms",
    "extract_dates", "calculate_notice_period",
    "analyze_contract_complexity", "extract_key_terms",
    "extract_legal_entities", "extract_advanced_context_data"
]
```

**2. `extractors.py` - Text-Extraktoren**
- **Mehrere Methoden:** pdfplumber, pypdf2, pymupdf
- **Kombinierte Extraktion:** Wählt bestes Ergebnis
- **Größenvalidierung:** 50MB-Limit
- **Metadaten:** Titel, Autor, Ersteller, Daten

**3. `parsers.py` - Spezialisierte Parser**
- **Titel:** Deutsche Muster (Vertrag über, Vereinbarung)
- **Kunde:** Rechtseinheiten (GmbH, AG, KG, OHG)
- **E-Mail:** Regex für gültige Adressen
- **Telefon:** Deutsche Muster (+49, lokale Formate)
- **Adresse:** Deutsche Adressmuster

**4. `dates.py` - Datumsextraktion**
- **Deutsche Muster:** DD.MM.YYYY, DD/MM/YYYY, DD-MM-YYYY
- **Klassifizierung:** Start, End, Renewal nach Kontext
- **Kündigungsfrist:** Erkennung von Kündigungsperioden
- **Confidence:** Vertrauensscore für jedes Datum

**5. `financials.py` - Finanzdaten**
- **Geldwerte:** EUR-Muster (€, EUR)
- **Zahlungsbedingungen:** Fristen in Tagen
- **Strafen:** Strafzahlung, Pönale
- **Währungen:** Automatische Erkennung (EUR Standard)

**6. `analysis.py` - Erweiterte Analyse**
- **Komplexität:** Score basierend auf komplexen Wörtern
- **Rechtsterminologie:** Kündigung, Verlängerung, Haftung
- **Rechtseinheiten:** GmbH, AG, KG, OHG, UG
- **Erweiterter Kontext:** Kombinierte Analyse aller Daten

**7. `ocr.py` - Optische Zeichenerkennung**
- **Pytesseract:** OCR mit mehrsprachiger Unterstützung
- **Confidence:** OCR-Vertrauensscore
- **Sprachen:** Deutsch (deu), Portugiesisch (por)
- **Fallback:** Wenn Textextraktion fehlschlägt

**8. `validate.py` - PDF-Validierung**
- **Format:** PDF-Header-Überprüfung
- **Größe:** Leere Datei-Validierung
- **Integrität:** Datei-Lese-Test
- **Nachrichten:** Zweisprachig (DE/PT)

### **Confidence-Score-System / Sistema de Confidence Scores**

**🎯 Confidence Scores für extrahierte Felder**

Das System verwendet ein ausgeklügeltes **Confidence-Score-System** (0.0 - 1.0) zur Bewertung der Qualität extrahierter Daten:

**📊 Vertrauensstufen:**
```python
class ConfidenceLevel(str, Enum):
    HIGH = "hoch"           # > 80% (0.8+)
    MEDIUM = "mittel"       # 50-80% (0.5-0.8)
    LOW = "niedrig"         # < 50% (0.0-0.5)
    UNKNOWN = "unbekannt"   # Nicht extrahiert (0.0)
```

**🔍 Felder mit Confidence Scores:**
- **Titel:** `title_confidence` (0.0-1.0)
- **Kunde:** `client_name_confidence` (0.0-1.0)
- **E-Mail:** `client_email_confidence` (0.0-1.0)
- **Telefon:** `client_phone_confidence` (0.0-1.0)
- **Adresse:** `client_address_confidence` (0.0-1.0)
- **Wert:** `value_confidence` (0.0-1.0)
- **Währung:** `currency_confidence` (0.0-1.0)
- **Startdatum:** `start_date_confidence` (0.0-1.0)
- **Enddatum:** `end_date_confidence` (0.0-1.0)
- **Verlängerungsdatum:** `renewal_date_confidence` (0.0-1.0)
- **Bedingungen:** `terms_and_conditions_confidence` (0.0-1.0)
- **Beschreibung:** `description_confidence` (0.0-1.0)
- **Rohtext:** `raw_text_confidence` (0.0-1.0)

**📈 Automatische Berechnung:**
```python
@validator('overall_confidence', always=True)
def calculate_overall_confidence(cls, v, values):
    """Berechnet Gesamtscore basierend auf allen Feldern"""
    confidence_fields = [
        'title_confidence', 'client_name_confidence', 
        'client_email_confidence', 'value_confidence',
        'start_date_confidence', 'end_date_confidence'
    ]
    scores = [values.get(field, 0.0) for field in confidence_fields]
    non_zero_scores = [score for score in scores if score > 0]
    return sum(non_zero_scores) / len(non_zero_scores) if non_zero_scores else 0.0
```

**🎯 Analysemethoden:**
- **`get_high_confidence_fields()`:** Felder mit Confidence > 0.8
- **`get_medium_confidence_fields()`:** Felder mit Confidence 0.5-0.8
- **`get_low_confidence_fields()`:** Felder mit Confidence < 0.5
- **`get_extraction_summary()`:** Vollständiger Extraktionsüberblick

### **Komplexitätsanalyse und Rechtsterminologie / Análise de Complexidade e Termos Legais**

**🔍 Vertragskomplexitätsanalyse**

Das System führt erweiterte Komplexitätsanalysen zur Vertragsklassifizierung durch:

**📊 Komplexitätsmetriken:**
```python
def analyze_contract_complexity(text: str) -> Dict[str, Any]:
    return {
        'word_count': word_count,                    # Anzahl Wörter
        'sentence_count': sentence_count,            # Anzahl Sätze
        'paragraph_count': paragraph_count,          # Anzahl Absätze
        'avg_sentence_length': avg_sentence_length,  # Durchschnittliche Satzlänge
        'complex_word_ratio': complex_word_ratio,    # Anteil komplexer Wörter
        'complexity_score': complexity_score,        # Gesamtscore (0.0-1.0)
        'complexity_level': 'high'|'medium'|'low'     # Komplexitätsstufe
    }
```

**⚖️ Erkannte deutsche Rechtsterminologie:**

**Kündigungsterminologie:**
- `kündigung`, `kündigungsfrist`, `kündigbar`
- `beendigung`, `auflösung`, `terminierung`

**Verlängerungsterminologie:**
- `verlängerung`, `automatische verlängerung`
- `erneuerung`, `fortsetzung`

**Finanzielle Begriffe:**
- `leistung`, `vergütung`, `zahlung`, `entgelt`
- `rechnung`, `fällig`, `fälligkeit`

**Haftungsterminologie:**
- `haftung`, `haftungsausschluss`, `gewährleistung`
- `garantie`, `versicherung`

**Streitbeilegungsterminologie:**
- `streitbeilegung`, `schiedsgericht`, `gerichtsstand`
- `anwendbares recht`, `rechtsprechung`

**🏢 Deutsche Rechtseinheiten:**

**Erkennungsmuster:**
```python
ENTITY_PATTERNS = [
    r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:GmbH|GmbH & Co\. KG)\b',
    r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:AG|Aktiengesellschaft)\b',
    r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:KG|Kommanditgesellschaft)\b',
    r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:OHG|Offene Handelsgesellschaft)\b',
    r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:UG|Unternehmergesellschaft)\b',
]
```

**Einheitstypen:**
- **GmbH:** Gesellschaft mit beschränkter Haftung
- **AG:** Aktiengesellschaft
- **KG:** Kommanditgesellschaft
- **OHG:** Offene Handelsgesellschaft
- **UG:** Unternehmergesellschaft

**📈 Erweiterte Kontextanalyse:**
```python
def extract_advanced_context_data(text: str) -> Dict[str, Any]:
    return {
        'notice_period': calculate_notice_period(text),      # Kündigungsperiode
        'contract_complexity': analyze_contract_complexity(text),  # Komplexität
        'key_terms': extract_key_terms(text),                # Rechtsterminologie
        'legal_entities': extract_legal_entities(text),      # Rechtseinheiten
        'financial_terms': extract_financial_terms(text)     # Finanzbegriffe
    }
```

### **E-Mail-Templates / Templates de E-mail**

Das System enthält zweisprachige HTML-Templates (Deutsch/Portugiesisch) für Ablaufbenachrichtigungen:

**Eigenschaften / Características:**
- **Responsives Design:** Passt sich verschiedenen Geräten an
- **Zweisprachig:** Vollständige DE/PT-Unterstützung
- **Personalisierung:** Farben und Stile basierend auf Dringlichkeit
- **Vollständige Informationen:** Vertragsdaten, Kunde, Werte, Daten
- **Barrierefreiheit:** Semantische Struktur und angemessener Kontrast

**Template-Typen / Tipos de Template:**
- **T-60:** Orange Farben, niedrige Dringlichkeit
- **T-30:** Orange Farben, niedrige Dringlichkeit  
- **T-10:** Rote Farben, hohe Dringlichkeit
- **T-1:** Rote Farben, hohe Dringlichkeit

### **Dokumentenerstellung / Geração de Documentos**

**Generierungsablauf / Fluxo de Geração:**
1. **DOCX-Template:** Verwendet docxtpl für Word-Template-Rendering
2. **PDF-Konvertierung:** LibreOffice (soffice) konvertiert DOCX zu PDF
3. **Fallback:** Gibt DOCX zurück, wenn Konvertierung fehlschlägt
4. **Threading:** I/O-Operationen in Threads, um Event-Loop nicht zu blockieren

**Verfügbare Methoden / Métodos Disponíveis:**
```python
def render_docx_bytes(template_path: str, data: Dict[str, Any]) -> bytes
def _convert_docx_bytes_to_pdf_bytes(docx_bytes: bytes) -> bytes
def generate_contract_pdf(template_path: str, data: Dict[str, Any]) -> bytes
def generate_report_pdf(data: Dict[str, Any], report_type: str) -> bytes
```

---

## Konfiguration und Deployment / Configuração e Deploy

### **Anwendungskonfiguration / Configuração da Aplicação**

#### Umgebungsvariablen / Variáveis de Ambiente

```bash
# Datenbank / Database
SQLALCHEMY_DATABASE_URI=sqlite+aiosqlite:///./contracts.db

# Sicherheit / Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]

# SMTP / E-Mail
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-password
SMTP_USE_TLS=true

# Upload / Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIR=uploads
```

### **Docker / Container**

#### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System-Abhängigkeiten / System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten / Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode / Application code
COPY . .

# Verzeichnisse erstellen / Create directories
RUN mkdir -p /app/files

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

#### Docker Compose (Optionales Beispiel / Exemplo Opcional)
```yaml
# Hinweis: Dies ist ein nicht übernommenes Beispiel im aktuellen Projekt
# Nota: Este é um exemplo não adotado no projeto atual
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - SQLALCHEMY_DATABASE_URI=mysql+aiomysql://user:password@db:3306/contracts
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: contracts
      MYSQL_USER: user
      MYSQL_PASSWORD: password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

**Aktuelle Konfiguration / Configuração Atual:**
- **Entwicklung:** SQLite (sqlite+aiosqlite:///./contracts.db)
- **Produktion:** MySQL/PostgreSQL konfigurierbar
- **Docker:** Dockerfile vorhanden, Docker Compose nicht übernommen
- **Datenbank:** Konfiguration über Umgebungsvariablen

### **Migrationen / Migrações**

#### Alembic-Befehle / Comandos do Alembic
```bash
# Neue Migration erstellen / Criar nova migração
alembic revision --autogenerate -m "beschreibung"

# Migrationen anwenden / Aplicar migrações
alembic upgrade head

# Migration rückgängig machen / Reverter migração
alembic downgrade -1

# Historie anzeigen / Ver histórico
alembic history
```

---

## Tests / Testes

### **Teststruktur / Estrutura de Testes**

```
backend/tests/
├── test_complete.py          # Vollständige Integrationstests
├── test_integration_db.py    # Datenbanktests
├── test_local.py            # Lokale Tests
├── test_utils.py            # Hilfsprogramm-Tests
└── test_alerts.py           # Alert-Tests (455 Zeilen)
```

### **Testarten / Tipos de Teste**

#### 1. **Unit-Tests / Testes Unitários**
- Testen isolierte Funktionen
- Mock externer Abhängigkeiten
- Geschäftslogik-Validierung

#### 2. **Integration-Tests / Testes de Integração**
- Testen Komponenteninteraktion
- In-Memory-Datenbank
- Vollständige APIs

#### 3. **System-Tests / Testes de Sistema**
- Testen vollständige Abläufe
- Reale Nutzungsszenarien
- End-to-End-Validierung

### **Tests ausführen / Executando Testes**

```bash
# Alle Tests / Todos os testes
pytest

# Spezifische Tests / Testes específicos
pytest backend/tests/test_complete.py

# Mit Coverage / Com cobertura
pytest --cov=app

# Asynchrone Tests / Testes assíncronos
pytest -v backend/tests/test_integration_db.py

# Alert-Tests / Testes de alertas
pytest backend/tests/test_alerts.py
```

### **Testkonfiguration / Configuração de Testes**

#### pytest.ini
```ini
[tool:pytest]
testpaths = backend/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
```

---

## Projektstatus / Status do Projeto

### **📊 Entwicklungsstufen-Status**

**✅ Abgeschlossene Stufen (1-8):**
1. **✅ Initialkonfiguration:** FastAPI, SQLAlchemy, Alembic
2. **✅ Datenmodelle:** User, Contract, Alert, Permission
3. **✅ Pydantic-Schemas:** Validierung und Serialisierung
4. **✅ JWT-Authentifizierung:** Login, Registrierung, Tokens
5. **✅ Berechtigungssystem:** RBAC (USER, MANAGER, ADMIN)
6. **✅ Vertrags-CRUD:** Erstellung, Auflistung, Bearbeitung, Löschung
7. **✅ Alert-System:** Hintergrund-Scheduler, Benachrichtigungen
8. **✅ Dokumentenerstellung:** DOCX → PDF mit LibreOffice

**✅ Abgeschlossene Stufe (9):**
9. **✅ PDF-Import:** Intelligente Extraktion, Confidence Scores

**⏳ Ausstehende Stufen (10-11, 14-15):**
10. **⏳ React-Frontend:** Benutzeroberfläche (ausstehend)
11. **⏳ Produktions-Deploy:** Serverkonfiguration (ausstehend)
14. **⏳ Erweiterte Berichte:** Dashboards und Analytics (ausstehend)
15. **⏳ Externe Integration:** Drittanbieter-APIs (ausstehend)

**🔄 In Bearbeitung (12):**
12. **🔄 Automatisierte Tests:** ~60% abgeschlossen
   - ✅ Grundlegende Unit-Tests
   - ✅ Modelltests
   - ✅ Alert-Tests (455 Zeilen)
   - ⏳ Vollständige Integrationstests
   - ⏳ Performance-Tests
   - ⏳ End-to-End-Tests

**📈 Gesamtfortschritt:**
- **Backend:** 95% abgeschlossen
- **API:** 100% funktional
- **Tests:** 60% implementiert
- **Frontend:** 0% (ausstehend)
- **Deploy:** 0% (ausstehend)

**🎯 Nächste Schritte:**
1. **Tests vervollständigen:** 90%+ Abdeckung
2. **Frontend entwickeln:** React + Vite
3. **Deploy konfigurieren:** Docker + Server
4. **Berichte implementieren:** Erweiterte Dashboards
5. **Optimierungen:** Performance und Skalierbarkeit

---

## Entwicklung / Desenvolvimento

### **Umgebung einrichten / Setup do Ambiente**

#### 1. **Voraussetzungen / Pré-requisitos**
```bash
# Python 3.11+
python --version

# Git
git --version

# Docker (optional / opcional)
docker --version
```

#### 2. **Installation / Instalação**
```bash
# Repository klonen / Clone do repositório
git clone <repository-url>
cd vertrag-mgs

# Virtuelle Umgebung / Ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder / ou
venv\Scripts\activate      # Windows

# Abhängigkeiten / Dependências
pip install -r requirements.txt
```

#### 3. **Datenbank einrichten / Configuração do Banco**
```bash
# Migrationen / Migrações
alembic upgrade head

# Testdaten / Dados de teste
python -m app.utils.seed_data
```

#### 4. **Anwendung starten / Executar Aplicação**
```bash
# Entwicklung / Desenvolvimento
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Produktion / Produção
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### **Codestruktur / Estrutura de Código**

#### **Konventionen / Convenções**

1. **Namensgebung / Nomenclatura**
   - Klassen: PascalCase (`UserService`)
   - Funktionen: snake_case (`get_user_by_id`)
   - Konstanten: UPPER_CASE (`MAX_FILE_SIZE`)

2. **Dokumentation / Documentação**
   - Docstrings auf Deutsch und Portugiesisch
   - Type hints obligatorisch
   - Erklärende Kommentare

3. **Imports / Importações**
   ```python
   # Standardbibliothek / Standard library
   import os
   from datetime import datetime
   
   # Drittanbieter / Third party
   from fastapi import FastAPI
   from sqlalchemy import Column
   
   # Lokal / Local
   from app.models.user import User
   from app.services.user_service import UserService
   ```

### **Entwicklungsablauf / Fluxo de Desenvolvimento**

#### 1. **Neue Funktion / Nova Funcionalidade**
```bash
# Branch erstellen / Criar branch
git checkout -b feature/neue-funktion

# Entwickeln / Desenvolver
# ... Code / Código ...

# Tests / Testes
pytest

# Commit / Commit
git add .
git commit -m "feat: fügt neue Funktion hinzu"

# Push / Push
git push origin feature/neue-funktion
```

#### 2. **Code-Review / Code Review**
- Tests prüfen / Verificar testes
- Dokumentation validieren / Validar documentação
- Performance prüfen / Verificar performance
- Integration testen / Testar integração

#### 3. **Deploy / Deployment**
```bash
# Build / Build
docker build -t contract-system .

# Deploy / Deploy
docker-compose up -d
```

### **Debugging / Fehlerbehebung**

#### **Logs / Protokolle**
```python
import logging

logger = logging.getLogger(__name__)

# Info / Info
logger.info("Operation erfolgreich durchgeführt")

# Warnung / Warning
logger.warning("Achtung: niedriger Wert erkannt")

# Fehler / Error
logger.error("Fehler bei Vertragsverarbeitung", exc_info=True)
```

#### **Tools / Ferramentas**
- **pdb**: Python-Debugger
- **ipdb**: Interaktiver Debugger
- **pytest --pdb**: Debug in Tests
- **FastAPI Debug**: Automatischer Debug-Modus

### **Performance / Leistung**

#### **Optimierungen / Otimizações**
1. **Datenbank / Database**
   - Angemessene Indizes / Índices apropriados
   - Optimierte Abfragen / Queries otimizadas
   - Verbindungspooling / Connection pooling

2. **Cache / Caching**
   - Redis für Sessions / Redis para sessões
   - Cache für häufige Abfragen / Cache para consultas frequentes

3. **Async / Asíncrono**
   - Asynchrone I/O-Operationen / Operações I/O assíncronas
   - Hintergrundaufgaben / Background tasks

---

## Fazit / Conclusão

Dieses Vertragsverwaltungssystem bietet eine vollständige und robuste Lösung für Unternehmen, die den Lebenszyklus ihrer Verträge kontrollieren müssen. Die modulare Architektur ermöglicht einfache Wartung und Erweiterung, während das automatische Alert-System sicherstellt, dass kein Ablauf übersehen wird.

**Hauptvorteile / Principais Vantagens:**
- ✅ Saubere und skalierbare Architektur
- ✅ Automatisches Alert-System
- ✅ Automatische Dokumentenerstellung
- ✅ Vollständige REST-API
- ✅ Umfassende Tests
- ✅ Zweisprachige Dokumentation
- ✅ Flexible Konfiguration

**Nächste Schritte / Próximos Passos:**
- React-Frontend-Implementierung
- Integration mit externen Systemen
- Erweiterte Berichte
- Webhook-API
- Automatisches Backup-System

---

*Automatisch generierte Dokumentation - Vertragsverwaltungssystem v1.0.0*
*Documentação gerada automaticamente - Sistema de Gerenciamento de Contratos v1.0.0*

---

## Mietstaffelung / RentStep (Erweiterung)

### Beschreibung / Descrição
Diese Erweiterung fügt ein neues Datenmodell `RentStep` hinzu, das zukünftige Miet- oder Pachtanpassungen für einen Vertrag speichert.

Die Erweiterung umfasst:
- DB-Tabelle `rent_steps` mit `contract_id`, `effective_date`, `amount`, `currency`, `note`, `created_by`, `created_at`.
- API-Endpoints zur Verwaltung (CRUD) der Mietstaffelungen unter `/contracts/{contract_id}/rent-steps`.
- Validierungen: `effective_date >= contract.start_date` (Standard) und `amount >= 0`.
- Datenbank-Constraint: Unique(contract_id, effective_date) zur Vermeidung doppelter Einträge.

### Datenmodell / Modelo de dados

```text
RentStep
 - id: int (PK)
 - contract_id: int (FK -> contracts.id)
 - effective_date: date
 - amount: numeric(12,2)
 - currency: varchar(3) (optional)
 - note: text (optional)
 - created_by: int (optional)
 - created_at: datetime (server default now)
```

### API Endpoints / Endpoints API

- `GET /contracts/{contract_id}/rent-steps` — Listet alle Mietstaffelungen eines Vertrags (aufsteigend nach Datum).
- `POST /contracts/{contract_id}/rent-steps` — Erstellt eine neue Mietstaffelung (nur MANAGER/ADMIN).
- `GET /contracts/{contract_id}/rent-steps/{id}` — Holt Details einer Mietstaffelung.
- `PUT /contracts/{contract_id}/rent-steps/{id}` — Aktualisiert eine Mietstaffelung (nur MANAGER/ADMIN).
- `DELETE /contracts/{contract_id}/rent-steps/{id}` — Löscht eine Mietstaffelung (nur MANAGER/ADMIN).

Beispiel-Request (POST):
```json
{
  "effective_date": "2026-01-01",
  "amount": 1500.00,
  "currency": "EUR",
  "note": "Jährliche Anpassung"
}
```

### Validierungsregeln / Regras de validação
- `effective_date` muss gleich oder nach `contract.start_date` liegen (Standardverhalten).
- `amount` muss >= 0 sein.
- DB-Constraint `UNIQUE(contract_id, effective_date)` verhindert doppelte Einträge.

### Migration / Migração
Eine Alembic-Migration `0002_add_rent_steps.py` wird erzeugt, die die Tabelle `rent_steps` erstellt und die unique constraint setzt. Anwenden mit:

```bash
alembic upgrade head
```

### Scheduler / Alerts (Hinweis)
Diese Erweiterung implementiert zunächst nur persistente Mietstaffelungen und CRUD-APIs (Option B). Die Integration mit dem Notification-Scheduler (automatische Alerts z. B. T-30 / T-7 vor `effective_date`) kann später als Option C ergänzt werden. Bei Integration wird empfohlen, Alerts mit Referenz auf `rent_step_id` zu erzeugen, um Deduplizierung zuverlässig zu gewährleisten.

### Tests
Unit- und Integrationstests prüfen:
- Erstellen und Auflisten von RentSteps
- Validierungsfehler (effective_date < start_date, amount < 0)
- DB-Constraint-Verletzung (Duplicate)

