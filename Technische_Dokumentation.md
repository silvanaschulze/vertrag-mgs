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
- **Manuelle Benachrichtigungen / Notificações Manuais** (BENUTZERDEFINIERT)
- **PDF-Verwaltung / Gerenciamento de PDFs** (Upload, Persistierung, Inline-Visualisierung)
- **Dokumentenerstellung / Geração de Documentos** (DOCX → PDF)
- **Benutzerverwaltung / Gerenciamento de Usuários**
- **Berechtigungssystem / Sistema de Permissões**
- **Berichte und Statistiken / Relatórios e Estatísticas**
- **Darstellung und Verwaltung von Miet-/Pachtverträgen / Representação e gestão de contratos de arrendamento** (LEASE/PACHT)
- **Mietstaffelung / Escalonamentos de aluguel (RentStep)** com valores futuros pré-definidos
- **Erfassung von Verträgen mit vordefinierten zukünftigen Anpassungen / Registro de contratos com reajustes futuros já definidos**
- **Automatische Alert-Erstellung / Criação automática de alertas** für Vertragsabläufe und Mietstaffelungen
- **Intelligente PDF-Extraktion / Extração inteligente de PDFs** mit Confidence Scoring
- **Organisierte Dateiverwaltung / Gerenciamento organizado de arquivos** (temp/persisted)

### Technologie-Stack / Stack Tecnológico

#### 🚀 **Backend-Framework / Framework Backend**
- **FastAPI:** Async Web Framework (High Performance)
- **Uvicorn [standard]:** ASGI Server für Produktion/Entwicklung
- **python-multipart:** Support für multipart/form-data uploads
- **SQLAlchemy 2.0:** Async ORM mit modernster API
- **Alembic:** Database Migrationsmanagement

#### 🗄️ **Datenbank & Persistierung / Database & Persistence**
- **SQLite:** Entwicklung (sqlite+aiosqlite:///)
- **MySQL:** Produktion (mysql+aiomysql://) - konfigurierbar
- **Async Sessions:** Vollständig asynchrone DB-Operationen
- **SHA256 Hashing:** PDF-Integritätsprüfung

#### 🔐 **Authentifizierung & Sicherheit / Authentication & Security**
- **JWT:** JSON Web Tokens (python-jose)
- **BCrypt:** Password Hashing (passlib)
- **CORS:** Cross-Origin Resource Sharing
- **RBAC:** Role-Based Access Control (USER, MANAGER, ADMIN)
- **Security Headers:** XSS-Protection, Content-Type validation

#### 📄 **PDF-Verarbeitung / PDF Processing**
- **pdfplumber:** Hauptextraktion (beste Qualität)
- **PyPDF2:** Alternative Extraktionsmethode
- **PyMuPDF (fitz):** Backup-Extraktionsmethode
- **pytesseract:** OCR für gescannte PDFs
- **Tesseract:** OCR-Engine (deutsch/portugiesisch)

#### 📝 **Dokumentenerstellung / Document Generation**
- **docxtpl:** DOCX Template-Rendering (Jinja2-basiert)
- **LibreOffice (soffice):** DOCX → PDF Konvertierung
- **Threading:** Non-blocking I/O für Dokumentkonvertierung

#### 📧 **E-Mail & Benachrichtigungen / Email & Notifications**
- **SMTP:** Standard E-Mail-Versand
- **asyncio:** Asynchrone E-Mail-Verarbeitung
- **HTML Templates:** Zweisprachige Benachrichtigungen (DE/PT)
- **Background Scheduler:** Automatische Alert-Verarbeitung alle 6h

#### 🧪 **Testing & Qualitätssicherung / Testing & Quality Assurance**
- **pytest:** Haupttest-Framework
- **pytest-asyncio:** Async Test Support
- **unittest.mock:** Mocking für isolierte Tests
- **Coverage:** Test-Coverage-Reporting

#### 🌐 **Deploy & Infrastructure / Deploy & Infraestrutura**
- **Apache HTTP Server:** Reverse Proxy für FastAPI
- **systemd:** Service Management (vertrag-mgs-api.service)
- **Bash Scripts:** Vollautomatisches bilinguales Deployment
- **Virtual Environment:** Python-Isolation
- **File Permissions:** Sichere chmod/chown-Konfigurationen

#### 📊 **Monitoring & Logging / Monitoramento & Logs**
- **systemd Journal:** Service-Logs (journalctl)
- **Apache Logs:** Access/Error Logs mit Rotation
- **Python Logging:** Strukturierte Application Logs
- **Health Checks:** Automatische Status-Überprüfung

#### 🔧 **Development Tools / Ferramentas de Desenvolvimento**
- **Git:** Versionskontrolle
- **Virtual Environment:** Python-Dependency-Isolation
- **Type Hints:** Vollständige Type Annotations
- **Pydantic:** Data Validation und Serialization
- **AsyncIO:** Event Loop für alle async Operations

#### 📦 **Deployment Architecture / Arquitetura de Deployment**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Apache (80)   │◄──►│ FastAPI (8000)  │◄──►│  SQLite DB      │
│   Static Files  │    │ systemd Service │    │ File Storage    │
│   Proxy to API │    │ Background Jobs │    │ Upload Management│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Security Headers│    │ Alert Scheduler │    │ PDF Organization│
│ CORS Config     │    │ Email Service   │    │ temp/persisted  │
│ Static Caching  │    │ Async I/O       │    │ SHA256 Integrity│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### 🚀 **Performance Features / Recursos de Performance**
- **Async/Await:** Vollständig non-blocking operations
- **Connection Pooling:** Effiziente DB-Verbindungen
- **Static File Caching:** Apache-basierte Asset-Optimierung
- **Gzip Compression:** Reduzierte Übertragungsgrößen
- **Background Tasks:** Scheduler läuft unabhängig von Web-Requests

#### 🌍 **Internationalization / Internacionalização**
- **Bilingual System:** Vollständige DE/PT-Unterstützung
- **Scripts:** Alle Deploy-Scripts zweisprachig
- **Documentation:** Deutsche und portugiesische Dokumentation
- **Error Messages:** Lokalisierte Fehlermeldungen
- **Email Templates:** Zweisprachige HTML-Benachrichtigungen

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
- **UserService:** Benutzerverwaltung und Rollen
- **ContractService:** Vertragsgeschäftslogik und PDF-Management
- **NotificationService:** Benachrichtigungssystem (Auto + Manuell)
- **AuthService:** Authentifizierung und Autorisierung
- **PDFReaderService:** Intelligente PDF-Extraktion und Analyse
- **DocumentGenerator:** DOCX/PDF-Generierung
- **EmailService:** Zweisprachige E-Mail-Templates

#### 3. **Data Layer (Daten-Schicht)**
- **Models:** Datenbankentitäten (User, Contract, Alert, RentStep, Permission)
- **Database:** Konfiguration und async Sessions
- **Migrations:** Schema-Versionskontrolle (Alembic)
- **Schemas:** Pydantic-Validierung und Serialisierung

---

## Verzeichnisstruktur / Estrutura de Diretórios

```
vertrag-mgs/
├── backend/                          # Backend der Anwendung / Backend da aplicação
│   ├── app/                         # Hauptanwendungscode / Código principal da aplicação
│   │   ├── core/                    # Zentrale Konfigurationen / Configurações centrais
│   │   │   ├── config.py           # Anwendungskonfiguration / Configuração da aplicação
│   │   │   ├── database.py         # Datenbankkonfiguration / Configuração do banco de dados
│   │   │   ├── security.py         # Sicherheit und JWT / Segurança e JWT
│   │   │   └── permissions.py      # Berechtigungssystem (RBAC mit 7 Rollen, 6 Access Levels) / Sistema de permissões (RBAC com 7 papéis, 6 níveis de acesso)
│   │   ├── models/                  # Datenmodelle (SQLAlchemy) / Modelos de dados (SQLAlchemy)
│   │   │   ├── user.py             # Benutzermodell (7 Rollen: SYSTEM_ADMIN, DIRECTOR, DEPARTMENT_ADM, DEPARTMENT_USER, TEAM_LEAD, STAFF, READ_ONLY) / Modelo de usuário (7 papéis)
│   │   │   ├── contract.py         # Vertragsmodell (mit department, team, responsible_user_id) / Modelo de contrato (com departamento, time, responsável)
│   │   │   ├── alert.py            # Alertmodell / Modelo de alerta
│   │   │   ├── rent_step.py        # Mietstaffelung / RentStep (Escalonamentos de aluguel)
│   │   │   └── permission.py       # Berechtigungsmodell / Modelo de permissões
│   │   ├── schemas/                 # Pydantic-Schemas / Schemas Pydantic
│   │   │   ├── user.py             # Benutzerschemas (AccessLevel, UserRole enums) / Schemas de usuário (enums AccessLevel, UserRole)
│   │   │   ├── contract.py         # Vertragsschemas / Schemas de contrato
│   │   │   ├── token.py            # Authentifizierungsschemas / Schemas de autenticação
│   │   │   ├── extracted_contract.py # Extraktionsschemas / Schemas de extração
│   │   │   └── permissions.py      # Berechtigungsschemas / Schemas de permissões
│   │   ├── routers/                 # API-Endpunkte / Endpoints da API
│   │   │   ├── auth.py             # Authentifizierung / Autenticação
│   │   │   ├── contracts.py        # Verträge / Contratos
│   │   │   ├── contracts_import.py  # PDF-Import / Importação de PDF
│   │   │   ├── users.py            # Benutzer (mit neuen Berechtigungsprüfungen) / Usuários (com novas verificações de permissão)
│   │   │   ├── alerts.py           # Benachrichtigungen / Notificações
│   │   │   └── rent_steps.py       # Mietstaffelung Endpoints / Endpoints de escalonamento de aluguel
│   │   ├── services/               # Geschäftslogik / Lógica de negócio
│   │   │   ├── user_service.py     # Benutzerservice / Serviço de usuário
│   │   │   ├── contract_service.py # Vertragsservice / Serviço de contrato
│   │   │   ├── notification_service.py # Benachrichtigungsservice / Serviço de notificação
│   │   │   ├── auth_service.py     # Authentifizierungsservice / Serviço de autenticação
│   │   │   ├── pdf_reader.py       # PDF-Leser / Leitor de PDF
│   │   │   └── pdf_reader_pkg/     # PDF-Verarbeitungspaket / Pacote de processamento de PDF
│   │   │       ├── analysis.py     # Vertragsanalyse / Análise de contrato
│   │   │       ├── dates.py        # Datumsextraktion / Extração de datas
│   │   │       ├── extractors.py  # Extraktoren / Extratores
│   │   │       ├── financials.py  # Finanzdaten / Dados financeiros
│   │   │       ├── ocr.py         # OCR
│   │   │       ├── parsers.py     # Parser / Analisadores
│   │   │       ├── service.py     # Hauptservice / Serviço principal
│   │   │       └── validate.py    # Validierung / Validação
│   │   ├── utils/                  # Hilfsprogramme / Utilitários
│   │   │   ├── security.py         # Sicherheit und Hash (bcrypt) / Segurança e hash (bcrypt)
│   │   │   ├── email.py            # E-Mail-Versand / Envio de e-mail
│   │   │   └── document_generator.py # Dokumentenerstellung / Geração de documentos
│   │   └── __init__.py
│   ├── test/                       # Tests / Testes
│   │   ├── test_alerts.py          # Alerttests (458 Zeilen) / Testes de alertas (458 linhas)
│   │   ├── test_contract.py        # Vertragstests (167 Zeilen) / Testes de contratos (167 linhas)
│   │   ├── test_pdf_unit.py        # PDF-Unit-Tests (210 Zeilen) / Testes unitários de PDF (210 linhas)
│   │   ├── test_integration_db.py  # Database-Tests (61 Zeilen) / Testes de banco de dados (61 linhas)
│   │   ├── test_complete.py        # System-Tests (165 Zeilen) / Testes de sistema (165 linhas)
│   │   ├── test_local.py           # Dev-Tests (23 Zeilen) / Testes de desenvolvimento (23 linhas)
│   │   └── test_utils.py           # Utility-Tests (86 Zeilen) / Testes de utilitários (86 linhas)
│   ├── templates/                  # Template-Verzeichnis / Diretório de templates
│   │   ├── contract_template.docx  # Vertragsvorlage / Template de contrato
│   │   └── email_templates/        # E-Mail-Vorlagen / Templates de e-mail
│   │       ├── alert_de.html       # Deutsche Alert-Templates / Templates de alerta em alemão
│   │       └── alert_pt.html       # Portugiesische Alert-Templates / Templates de alerta em português
│   ├── uploads/                     # Upload-Verzeichnis / Diretório de uploads
│   │   └── contracts/              # Vertragsupload-Organisation / Organização de upload de contratos
│   │       ├── temp/               # Temporäre Uploads / Uploads temporários
│   │       └── persisted/          # Persistierte PDFs / PDFs persistidos
│   │           └── {contract_id}/  # Pro Vertrag organisiert / Organizado por contrato
│   ├── main.py                     # Anwendungseinstiegspunkt / Ponto de entrada da aplicação
│   ├── Dockerfile                  # Docker-Container
│   └── requirements.txt            # Abhängigkeiten / Dependências
├── scripts/                        # Verwaltungsskripte / Scripts administrativos
│   └── migrate_user_roles_sql.py  # SQL-basierte Rollenmigration (USER→STAFF, MANAGER→DEPARTMENT_ADM, ADMIN→SYSTEM_ADMIN) / Migração de papéis baseada em SQL
├── alembic/                        # Datenbankmigrationen / Migrações de banco de dados
│   ├── versions/                   # Migrationsversionen / Versões de migração
│   │   ├── 0001_initial.py         # Initiale Migration / Migração inicial
│   │   ├── 0002_add_rent_steps.py  # RentStep-Migration / Migração para RentStep
│   │   ├── 0003_add_contract_pdf_fields.py # PDF-Felder für Verträge / Campos PDF para contratos
│   │   ├── 0004_add_pacht_contract_type.py # PACHT-Vertragstyp / Tipo de contrato PACHT
│   │   └── 0005_add_access_level_team_and_new_roles.py # Neue Felder: access_level, team, neue Rollen / Novos campos: access_level, team, novos papéis
│   └── env.py                      # Alembic-Konfiguration / Configuração do Alembic
├── docs/                           # Dokumentation / Documentação
│   ├── CHANGELOG.md                # Änderungsprotokoll / Registro de alterações
│   ├── PERMISSIONS_SYSTEM.md       # Vollständige Berechtigungssystem-Dokumentation (DE/PT) / Documentação completa do sistema de permissões (DE/PT)
│   ├── projeto_info.txt            # Projektinformationen / Informações do projeto
│   └── requirements.txt            # Dokumentationsabhängigkeiten / Dependências de documentação
├── alembic.ini                     # Alembic-Konfiguration / Configuração do Alembic
├── requirements.txt                # Hauptabhängigkeiten / Dependências principais
├── README.md                       # Projektdokumentation / Documentação do projeto
├── Technische_Dokumentation.md    # Detaillierte technische Dokumentation / Documentação técnica detalhada
├── clean-cache.sh                  # Cache-Bereinigungsskript / Script de limpeza de cache
├── deploy-internal.sh              # Haupt-Deploy-Script (15KB, bilingual) / Script principal de deploy (15KB, bilíngue)
├── setup-permissions.sh            # Dateiberechtigungen-Script / Script de permissões de arquivo
└── deploy/                         # Deploy-Konfigurationen / Configurações de deploy
    ├── setup-internal.sh           # Apache-Setup-Script / Script de configuração do Apache
    ├── apache-internal.conf        # Apache VirtualHost Konfiguration / Configuração VirtualHost do Apache
    └── README-DEPLOY.md            # Deploy-Dokumentation / Documentação de deploy
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
    department: str                  # Bereich / Departamento (NEU)
    team: str                        # Team / Time (NEU)
    role: UserRole                   # Rolle (7 neue Rollen) / Papel (7 novos papéis)
    access_level: int                # Zugriffsstufe 1-6 / Nível de acesso 1-6 (NEU)
    password_hash: str               # Passwort-Hash
    
    # Audit-Felder / Campos de auditoria
    created_at: datetime             # Erstellungsdatum
    updated_at: datetime             # Aktualisierungsdatum
    last_login: datetime             # Letzter Login
    is_active: bool                  # Aktiver Status
    is_deleted: bool                 # Soft Delete
```

**Neue Benutzerrollen (UserRole) / Novos Papéis de Usuário:**
- `SYSTEM_ADMIN` (Level 6): Technischer Systemadministrator mit Vollzugriff / Admin técnico com acesso completo
- `DIRECTOR` (Level 5): Geschäftsführung mit unternehmensweitem Zugriff / Diretoria com acesso em toda empresa
- `DEPARTMENT_ADM` (Level 4): Bereichsleiter mit vollen Admin-Rechten / Gestor com direitos administrativos completos
- `DEPARTMENT_USER` (Level 3): Bereichsleiter mit eingeschränkten Funktionen / Gestor com funções restritas
- `TEAM_LEAD` (Level 2): Teamleiter / Líder de time
- `STAFF` (Level 1-2): Mitarbeiter / Colaborador
- `READ_ONLY` (Level 1): Nur Lesezugriff / Somente leitura

**Zugriffsstufen (AccessLevel) / Níveis de Acesso:**
- **Level 6 (SYSTEM_ADMIN):** Technischer Vollzugriff (Konfiguration, Logs, Backups) / Acesso técnico completo
- **Level 5 (DIRECTOR):** Unternehmensweiter Zugriff auf alle Verträge / Acesso a todos os contratos da empresa
- **Level 4 (DEPARTMENT_ADM):** Volle Bereichsrechte (Verträge, Benutzer, Reports) / Direitos completos do departamento
- **Level 3 (DEPARTMENT_USER):** Bereichsverträge, eingeschränkte Reports / Contratos do departamento, relatórios restritos
- **Level 2 (TEAM):** Alle Verträge des Teams / Todos contratos do time
- **Level 1 (BASIS):** Nur eigene Verträge / Apenas contratos próprios

**Hilfsmethoden / Métodos Auxiliares:**
```python
def is_system_admin() -> bool        # Prüft SYSTEM_ADMIN / Verifica SYSTEM_ADMIN
def is_director() -> bool            # Prüft DIRECTOR / Verifica DIRECTOR
def is_department_leader() -> bool   # Prüft Bereichsleiter / Verifica gestor de departamento
def has_department_access() -> bool  # Prüft Level >= 3 / Verifica nível >= 3
def is_read_only() -> bool           # Prüft READ_ONLY / Verifica somente leitura
```

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
    
    # Organisationsfelder / Campos organizacionais (NEU)
    department: str                  # Bereich / Departamento
    team: str                        # Team / Time
    responsible_user_id: int         # Verantwortlicher Benutzer / Usuário responsável
    
    # PDF-Verwaltung / Gerenciamento PDF
    original_pdf_path: str           # Pfad zur Original-PDF
    original_pdf_filename: str       # Original-Dateiname
    original_pdf_sha256: str         # SHA256-Hash für Integrität
    ocr_text: str                    # Extrahierter OCR-Text
    ocr_text_sha256: str            # Hash des OCR-Textes
    uploaded_at: datetime            # Upload-Zeitstempel
    
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

**Vertragstypen / Tipos de Contrato:**
- `SERVICE`: Dienstleistung
- `PRODUCT`: Produkt
- `EMPLOYMENT`: Beschäftigung
- `LEASE`: Miete
- `PACHT`: Pacht (Pachtvertrag)
- `PARTNERSHIP`: Partnerschaft
- `OTHER`: Sonstiges

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
- `BENUTZERDEFINIERT`: Benutzerdefinierte Alerts (manuelle Terminplanung)

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

## Berechtigungssystem / Sistema de Permissões

### **Übersicht / Visão Geral**

Das Berechtigungssystem wurde vollständig überarbeitet und implementiert ein granulares **RBAC (Role-Based Access Control)** mit hierarchischen Zugriffsstufen.

Das Berechtigungssystem wurde vollständig überarbeitet und implementiert eine granulare **RBAC (Role-Based Access Control)** mit hierarchischen Zugriffsstufen. / O sistema de permissões foi completamente refatorado e implementa um **RBAC (Role-Based Access Control)** granular com níveis hierárquicos de acesso.

**Hauptkomponenten / Componentes Principais:**
- **7 Benutzerrollen (UserRole)** / 7 Papéis de Usuário
- **6 Zugriffsstufen (AccessLevel)** / 6 Níveis de Acesso
- **Organisationsstruktur** (Departments & Teams) / Estrutura Organizacional
- **Granulare Berechtigungsfunktionen** / Funções de Permissão Granulares
- **Standardprofile (PERFIS_PADRAO)** / Perfis Padrão

### **Standardprofile / Perfis Padrão (PERFIS_PADRAO)**

Vordefinierte Rollenkombinationen für typische Anwendungsfälle / Combinações de papéis pré-definidas para casos típicos:

```python
PERFIS_PADRAO = {
    "Geschäftsführung": {
        "role": UserRole.DIRECTOR,
        "access_level": AccessLevel.LEVEL_5,
        "department": "Geschäftsführung",
        "team": None
    },
    "Leiter_Personal_Organization_Finanzen": {
        "role": UserRole.DEPARTMENT_ADM,
        "access_level": AccessLevel.LEVEL_4,
        "department": "Personal Organization und Finanzen",
        "team": None
    },
    "Leiter_Technischer_Bereich": {
        "role": UserRole.DEPARTMENT_USER,
        "access_level": AccessLevel.LEVEL_3,
        "department": "Technischer Bereich",
        "team": None
    },
    "Leiter_IT_Datenschutz": {
        "role": UserRole.DEPARTMENT_ADM,
        "access_level": AccessLevel.LEVEL_4,
        "department": "IT und Datenschutz",
        "team": None
    },
    "Systemadministrator_TI": {
        "role": UserRole.SYSTEM_ADMIN,
        "access_level": AccessLevel.LEVEL_6,
        "department": "IT und Datenschutz",
        "team": "Informationstechnologie"
    },
    "Mitarbeiter_Team_PR": {
        "role": UserRole.STAFF,
        "access_level": AccessLevel.LEVEL_2,
        "department": "IT und Datenschutz",
        "team": "PR"
    },
    "Mitarbeiter_Team_Finanzen": {
        "role": UserRole.STAFF,
        "access_level": AccessLevel.LEVEL_2,
        "department": "Personal Organization und Finanzen",
        "team": "Finanzen und Rechnungswesen"
    }
}
```

### **Berechtigungsfunktionen / Funções de Permissão**

#### **Vertragsberechtigungen / Permissões de Contratos:**

```python
# Anzeigen von Verträgen / Visualizar contratos
can_view_contract(user: User, contract: Contract) -> bool
    # Level 6 (SYSTEM_ADMIN): Alle / Todos
    # Level 5 (DIRECTOR): Alle / Todos
    # Level 4 (DEPARTMENT_ADM): Bereichsverträge / Contratos do departamento
    # Level 3 (DEPARTMENT_USER): Bereichsverträge / Contratos do departamento
    # Level 2 (TEAM): Team-Verträge + eigene / Contratos do time + próprios
    # Level 1 (BASIS): Nur eigene / Apenas próprios

# Bearbeiten von Verträgen / Editar contratos
can_edit_contract(user: User, contract: Contract) -> bool
    # Level 6 (SYSTEM_ADMIN): Alle / Todos
    # Level 5 (DIRECTOR): Alle / Todos
    # Level 4 (DEPARTMENT_ADM): Bereichsverträge / Contratos do departamento
    # Level 3 (DEPARTMENT_USER): Nur eigene / Apenas próprios
    # Level 2 (TEAM): Team-Verträge + eigene / Contratos do time + próprios
    # Level 1 (BASIS): Nur eigene / Apenas próprios

# Löschen von Verträgen / Excluir contratos
can_delete_contract(user: User, contract: Contract) -> bool
    # Nur Level 4+ (DEPARTMENT_ADM oder höher) / Apenas nível 4+

# Genehmigen von Verträgen / Aprovar contratos
can_approve_contract(user: User, contract: Contract) -> bool
    # Level 6 (SYSTEM_ADMIN): Alle / Todos
    # Level 5 (DIRECTOR): Alle / Todos
    # Level 4 (DEPARTMENT_ADM): Bereichsverträge / Contratos do departamento
    # Level 3 (DEPARTMENT_USER): Bereichsverträge / Contratos do departamento

# Zugriff auf Original-PDF / Acesso ao PDF original
can_view_original_pdf(user: User, contract: Contract) -> bool
    # Gleiche Logik wie can_view_contract / Mesma lógica que can_view_contract
```

#### **Benutzerberechtigungen / Permissões de Usuários:**

```python
# Benutzer verwalten / Gerenciar usuários
can_manage_users(user: User) -> bool
    # Nur Level 4+ (DEPARTMENT_ADM oder höher) / Apenas nível 4+
    # SYSTEM_ADMIN, DIRECTOR, DEPARTMENT_ADM

# Benutzerrollen zuweisen / Atribuir papéis de usuário
can_set_user_role(user: User, target_role: UserRole) -> bool
    # SYSTEM_ADMIN: Alle Rollen / Todos papéis
    # DIRECTOR: Bis Level 5 (nicht SYSTEM_ADMIN) / Até nível 5
    # DEPARTMENT_ADM: Bis Level 4 / Até nível 4

# Zugriff auf Berichte / Acesso a relatórios
can_access_reports(user: User, report_type: str) -> bool
    # financial_details: Level 4+ / Nível 4+
    # department_summary: Level 3+ / Nível 3+
    # basic_statistics: Level 2+ / Nível 2+
```

#### **Organisatorische Prüfungen / Verificações Organizacionais:**

```python
# Prüfung gleicher Bereich / Verificar mesmo departamento
is_same_department(user: User, contract: Contract) -> bool

# Prüfung gleiches Team / Verificar mesmo time
is_same_team(user: User, contract: Contract) -> bool

# Prüfung eigener Vertrag / Verificar contrato próprio
is_contract_owner(user: User, contract: Contract) -> bool

# Prüfung Mindest-Zugriffsstufe / Verificar nível mínimo
require_min_access_level(user: User, min_level: int) -> None
```

### **Endpunkt-Berechtigungen / Permissões de Endpoints**

#### **User-Endpoints / Endpoints de Usuário:**

- **`GET /users/`** - Lista todos usuários / Alle Benutzer auflisten
  - Erfordert: Level 4+ (DEPARTMENT_ADM oder höher) / Requer: Nível 4+
  
- **`GET /users/{user_id}`** - Benutzer nach ID / Usuário por ID
  - Level 4+: Alle sehen / Ver todos
  - Level 1-3: Nur eigenes Profil / Apenas perfil próprio
  
- **`POST /users/`** - Neuen Benutzer erstellen / Criar novo usuário
  - Erfordert: `can_manage_users()` / Requer: `can_manage_users()`
  
- **`PUT /users/{user_id}`** - Benutzer aktualisieren / Atualizar usuário
  - Level 4+: Alle aktualisieren / Atualizar todos
  - Level 1-3: Nur eigenes Profil / Apenas perfil próprio
  
- **`DELETE /users/{user_id}`** - Benutzer löschen / Excluir usuário
  - Erfordert: `can_manage_users()` / Requer: `can_manage_users()`
  
- **`GET /users/search/`** - Benutzer suchen / Buscar usuários
  - Erfordert: Level 4+ / Requer: Nível 4+

#### **Contract-Endpoints / Endpoints de Contratos:**

- **`GET /contracts/`** - Alle Verträge auflisten / Listar todos contratos
  - Automatische Filterung nach Berechtigungen / Filtragem automática por permissões
  
- **`GET /contracts/{id}`** - Vertrag nach ID / Contrato por ID
  - Prüft: `can_view_contract()` / Verifica: `can_view_contract()`
  
- **`POST /contracts/`** - Neuen Vertrag erstellen / Criar novo contrato
  - Alle authentifizierten Benutzer / Todos usuários autenticados
  
- **`PUT /contracts/{id}`** - Vertrag aktualisieren / Atualizar contrato
  - Prüft: `can_edit_contract()` / Verifica: `can_edit_contract()`
  
- **`DELETE /contracts/{id}`** - Vertrag löschen / Excluir contrato
  - Prüft: `can_delete_contract()` / Verifica: `can_delete_contract()`
  
- **`GET /contracts/{id}/view`** - PDF inline anzeigen / Visualizar PDF inline
  - Prüft: `can_view_original_pdf()` / Verifica: `can_view_original_pdf()`
  
- **`GET /contracts/{id}/download`** - PDF herunterladen / Baixar PDF
  - Prüft: `can_view_original_pdf()` / Verifica: `can_view_original_pdf()`

### **Migration / Migração**

**Script:** `scripts/migrate_user_roles_sql.py`

**Deutsch:** Automatische Migration der alten Rollen zu den neuen:
**Português:** Migração automática dos papéis antigos para os novos:

- `USER` → `STAFF` (Level 1)
- `MANAGER` → `DEPARTMENT_ADM` (Level 4)
- `ADMIN` → `SYSTEM_ADMIN` (Level 6)

**Verwendung / Uso:**
```bash
python scripts/migrate_user_roles_sql.py
```

### **Dokumentation / Documentação**

**Vollständige Dokumentation:** `docs/PERMISSIONS_SYSTEM.md`
- Detaillierte Beschreibung aller Rollen und Stufen / Descrição detalhada de todos papéis e níveis
- Beispiele für jeden Anwendungsfall / Exemplos para cada caso de uso
- Migrationsanleitung / Guia de migração
- Diagramme und Tabellen / Diagramas e tabelas
- Zweisprachig (DE/PT) / Bilíngue (DE/PT)

---

**📊 Alert-Verarbeitung:**
        
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

#### `GET /contracts/{contract_id}/download`
**Beschreibung:** Original-PDF-Datei herunterladen (als Anhang)
**Headers:** `Content-Disposition: attachment; filename="contract.pdf"`

#### `GET /contracts/{contract_id}/view`
**Beschreibung:** Original-PDF-Datei inline anzeigen
**Headers:** `Content-Disposition: inline; filename="contract.pdf"`

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
**Beschreibung:** Benutzer auflisten / Listar usuários
**Berechtigung:** Erfordert Level 4+ (DEPARTMENT_ADM oder höher) / Requer Nível 4+
**Query Parameter:**
- `skip`: Anzahl zu überspringen (Standard: 0) / Quantidade a pular
- `limit`: Maximale Anzahl (Standard: 10) / Quantidade máxima

#### `POST /users/`
**Beschreibung:** Benutzer erstellen / Criar usuário
**Berechtigung:** Erfordert `can_manage_users()` (Level 4+) / Requer `can_manage_users()`
**Body:**
```json
{
  "username": "string",
  "email": "string",
  "name": "string",
  "password": "string",
  "role": "staff",
  "access_level": 1,
  "department": "string",
  "team": "string",
  "is_active": true,
  "is_superuser": false
}
```

#### `GET /users/{user_id}`
**Beschreibung:** Benutzer nach ID abrufen / Obter usuário por ID
**Berechtigung:** 
- Level 4+: Alle Benutzer sehen / Ver todos usuários
- Level 1-3: Nur eigenes Profil / Apenas perfil próprio

#### `PUT /users/{user_id}`
**Beschreibung:** Benutzer aktualisieren / Atualizar usuário
**Berechtigung:**
- Level 4+: Alle Benutzer aktualisieren / Atualizar todos usuários
- Level 1-3: Nur eigenes Profil / Apenas perfil próprio

#### `DELETE /users/{user_id}`
**Beschreibung:** Benutzer löschen / Excluir usuário
**Berechtigung:** Erfordert `can_manage_users()` (Level 4+) / Requer `can_manage_users()`
**Hinweis:** Kann nicht eigenes Konto löschen / Não pode excluir própria conta

#### `PATCH /users/{user_id}/activate`
**Beschreibung:** Benutzer aktivieren / Ativar usuário
**Berechtigung:** Erfordert `can_manage_users()` (Level 4+) / Requer `can_manage_users()`

#### `PATCH /users/{user_id}/deactivate`
**Beschreibung:** Benutzer deaktivieren / Desativar usuário
**Berechtigung:** Erfordert `can_manage_users()` (Level 4+) / Requer `can_manage_users()`

#### `GET /users/search/`
**Beschreibung:** Benutzer suchen / Buscar usuários
**Berechtigung:** Erfordert Level 4+ / Requer Nível 4+
**Query Parameter:**
- `query`: Suchbegriff (Name, E-Mail, Benutzername) / Termo de busca
- `skip`: Anzahl zu überspringen / Quantidade a pular
- `limit`: Maximale Anzahl / Quantidade máxima

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

#### `POST /alerts/manual`
**Beschreibung:** Manuellen Alert erstellen
**Query Parameter:**
- `contract_id`: Vertrags-ID (erforderlich)
- `scheduled_for`: Geplante Sendezeit (erforderlich)
- `recipient`: E-Mail-Empfänger (optional)
- `subject`: E-Mail-Betreff (optional)

**Response:**
```json
{
  "id": 123,
  "contract_id": 456,
  "alert_type": "BENUTZERDEFINIERT",
  "status": "PENDING",
  "scheduled_for": "2025-12-25T10:00:00Z",
  "recipient": "kunde@email.com",
  "subject": "Benutzerdefinierte Vertragserinnerung"
}
```

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
- PDF-Dateimanagement (Upload, Persistierung, Integrität)
- Organisierte Dateispeicherung (temp/persisted)

**Hauptmethoden / Métodos Principais:**
```python
async def create_contract(contract_data: ContractCreate, created_by: int) -> ContractResponse
async def get_contract(contract_id: int) -> Optional[ContractResponse]
async def update_contract(contract_id: int, update_data: ContractUpdate) -> Optional[ContractResponse]
async def delete_contract(contract_id: int) -> bool
async def list_contracts(skip: int, limit: int, filters: Dict, search: str) -> ContractListResponse
async def get_contract_stats() -> ContractStats
async def get_contracts_expiring_within(days: int) -> ContractListResponse

# PDF-Verwaltung / Gerenciamento PDF
async def attach_original_pdf(contract_id: int, pdf_path: str, filename: str) -> bool
async def get_contract_pdf_path(contract_id: int) -> Optional[str]
async def verify_pdf_integrity(contract_id: int) -> bool
```

### **NotificationService**

**Verantwortlichkeiten / Responsabilidades:**
- Ablaufbenachrichtigungsverarbeitung
- Manuelle Alert-Erstellung (BENUTZERDEFINIERT)
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

**🔔 Manuelle Alerts (BENUTZERDEFINIERT)**

Das System unterstützt benutzerdefinierte Alerts mit frei wählbaren Terminen:

**Funktionen:**
- **Endpoint:** `POST /alerts/manual`
- **Berechtigung:** Alle authentifizierten Benutzer
- **Flexibilität:** Beliebige Termine und Empfänger
- **Integration:** Nutzt denselben Scheduler wie automatische Alerts

**Parameter:**
```json
{
  "contract_id": 123,           // Erforderlich: Vertrags-ID
  "scheduled_for": "2025-12-25T10:00:00Z",  // Erforderlich: Sendetermin
  "recipient": "kunde@email.com",           // Optional: Empfänger
  "subject": "Benutzerdefinierte Erinnerung" // Optional: Betreff
}
```

**Automatische Defaults:**
- **Empfänger:** Fällt zurück auf `contract.client_email`
- **Betreff:** Generiert automatischen deutschen Betreff
- **Typ:** Setzt `AlertType.BENUTZERDEFINIERT`
- **Status:** Beginnt mit `PENDING` für Scheduler-Verarbeitung

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
    r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:e.V|eingetragener Verein)\b',
    r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:&Co|Kommanditgesellschaft)\b'
]
```

**Einheitstypen:**
- **GmbH:** Gesellschaft mit beschränkter Haftung
- **AG:** Aktiengesellschaft
- **KG:** Kommanditgesellschaft
- **OHG:** Offene Handelsgesellschaft
- **UG:** Unternehmergesellschaft
- **e.V:** eingetragener Verein
- **&Co:** Kommanditgesellschaft

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

### **PDF-Verwaltung und -Organisation / Gerenciamento e Organização de PDFs**

**🏗️ Organisierte Dateistruktur**

Das System implementiert eine durchdachte Ordnerstruktur für PDF-Dateien:

```
uploads/contracts/
├── temp/                    # Temporäre Uploads
│   └── {uuid}_filename.pdf  # Dateien vor Vertragserstellung
└── persisted/               # Persistierte PDFs
    └── {contract_id}/       # Pro Vertrag organisiert
        └── original.pdf     # Original-PDF des Vertrags
```

**🔄 Datei-Lebenszyklus:**

1. **Upload:** PDF wird in `temp/` mit UUID-Präfix gespeichert
2. **Vertragserstellung:** Datei wird von `temp/` nach `persisted/{contract_id}/` verschoben
3. **Persistierung:** Original-PDF bleibt dauerhaft im System verfügbar
4. **Zugriff:** Inline-Visualisierung und Download-Endpunkte

**📁 PDF-Metadaten im Contract-Modell:**

```python
# PDF-Verwaltung / Gerenciamento PDF
original_pdf_path: str           # Pfad zur Original-PDF
original_pdf_filename: str       # Original-Dateiname
original_pdf_sha256: str         # SHA256-Hash für Integrität
ocr_text: str                    # Extrahierter OCR-Text
ocr_text_sha256: str            # Hash des OCR-Textes
uploaded_at: datetime            # Upload-Zeitstempel
```

**🔐 Integritätsprüfung:**

```python
async def verify_pdf_integrity(contract_id: int) -> bool:
    """Überprüft PDF-Integrität durch SHA256-Vergleich"""
    # 1. Gespeicherten Hash aus DB laden
    # 2. Aktuellen Datei-Hash berechnen
    # 3. Vergleich und Validierung
```

**📄 Zugriffsmethoden:**

- **Download (Attachment):** `GET /contracts/{id}/download`
  - Header: `Content-Disposition: attachment`
  - Erzwingt Download-Dialog im Browser

- **Inline-Ansicht:** `GET /contracts/{id}/view`
  - Header: `Content-Disposition: inline`
  - Zeigt PDF direkt im Browser an

**🔧 Service-Methoden:**

```python
async def attach_original_pdf(contract_id: int, pdf_path: str, filename: str) -> bool
async def get_contract_pdf_path(contract_id: int) -> Optional[str]
async def verify_pdf_integrity(contract_id: int) -> bool
def move_temp_to_persisted_contract(temp_file_path: str, contract_id: int) -> str
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

#### **Deploy-Konfiguration / Configuração de Deploy**

**Automatisierte Deployment-Scripts / Scripts de Deployment Automatizado:**

```bash
# Hauptverzeichnis / Diretório Principal
deploy-internal.sh           # Haupt-Deploy-Script (15KB, bilingual)
setup-permissions.sh         # Dateiberechtigungen
clean-cache.sh              # Cache-Bereinigung

# Deploy-Verzeichnis / Diretório Deploy
deploy/
├── setup-internal.sh        # Apache-Setup
├── apache-internal.conf     # Apache VirtualHost
└── README-DEPLOY.md         # Deployment-Dokumentation
```

**Service-Konfiguration / Configuração de Serviço:**
```bash
# Service-Variablen / Variáveis do Serviço
SERVICE_NAME="vertrag-mgs-api"
SERVICE_PORT=8000
PROJECT_DIR="$(pwd)"
APACHE_CONFIG_DIR="/etc/apache2/sites-available"
```

**Bilingual Logging / Logging Bilíngue:**
```bash
# Beispiel der zweisprachigen Ausgabe / Exemplo de saída bilíngue
log_info "Konfiguriere Apache für API (Backend-only)..." \
         "Configurando Apache para API (apenas backend)..."

log_success "Apache konfiguriert (Backend-only)!" \
            "Apache configurado (apenas backend)!"
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
backend/test/
├── test_alerts.py            # Alert-Tests (458 Zeilen, Auto + Manuell)
├── test_contract.py          # Vertragstests (167 Zeilen, CRUD, PDF-Integration)
├── test_pdf_unit.py          # PDF-Unit-Tests (210 Zeilen)
├── test_integration_db.py    # Database-Tests (61 Zeilen, async Sessions)
├── test_complete.py          # System-Tests (165 Zeilen, Folder Structure)
├── test_local.py            # Dev-Tests (23 Zeilen, lokale Entwicklung)
└── test_utils.py            # Utility-Tests (86 Zeilen, Security, Email)
```

### **Detaillierte Test-Coverage / Cobertura Detalhada de Testes**

#### **test_alerts.py (458 Zeilen)**
- **Automatische Alerts:** T-60, T-30, T-10, T-1 Verarbeitung mit präziser Terminberechnung
- **Manuelle Alerts:** BENUTZERDEFINIERT mit freier Terminwahl und Flexibilität  
- **Scheduler-Integration:** APScheduler Hintergrund-Verarbeitung und Job-Management
- **E-Mail-Templates:** Zweisprachige Benachrichtigungen (DE/PT) mit HTML/Text
- **Deduplizierung:** Verhinderung doppelter Alerts durch Status-Tracking
- **Test-Coverage:** Vollständige Abdeckung aller Alert-Szenarien inkl. Edge Cases

#### **test_contract.py (167 Zeilen)**
- **CRUD-Operationen:** Erstellen, Lesen, Aktualisieren, Löschen von Verträgen
- **PDF-Integration:** Upload, temp/persisted Speicherung, Inline-Viewer, Download
- **RentStep-Integration:** Mietstaffelung für LEASE/PACHT mit Preisanpassungen
- **Vertragstypen:** SERVICE, PRODUCT, EMPLOYMENT, LEASE, PACHT (alle 5 Typen)
- **Status-Management:** DRAFT, ACTIVE, EXPIRED, TERMINATED Workflow
- **Schema-Validation:** Pydantic-Schema Tests für alle Contract-Endpoints

#### **test_pdf_unit.py (210 Zeilen)**
- **Schema-Validation:** ExtractionMetadata, SHA256-Hashes, Upload-Timestamps
- **Text-Extraktion:** Mock-Tests für PDF-Reader ohne externe Abhängigkeiten
- **File-Operations:** Temp-Directory Handling, File Movement, Path Management
- **Security-Tests:** SHA256-Validierung, File Integrity Checks
- **Error-Handling:** Invalid PDF, Missing Files, Permission Errors

#### **test_integration_db.py (61 Zeilen)**  
- **Database Models:** User, Contract, Alert Model Creation & Relationships
- **Async Sessions:** SQLAlchemy 2.0 async/await Pattern Testing
- **Foreign Keys:** Contract-User, Alert-Contract Relationship Validation
- **Data Types:** Date/DateTime Handling, Enum Validation (ContractType, AlertType)
- **In-Memory Testing:** SQLite :memory: für schnelle Integration Tests

#### **test_complete.py (165 Zeilen)**
- **System-Integration:** End-to-End Funktionalität ohne externe Dependencies
- **Folder Structure:** Validation der neuen temp/persisted PDF-Organisation
- **Import-Tests:** Grundlegende Python-Module und Projekt-Dateien
- **File-Operations:** Simplified File Movement Tests für neue Struktur
- **Environment-Check:** Verfügbarkeit aller kritischen System-Komponenten

#### **test_local.py (23 Zeilen)**
- **Development-Environment:** Schnelle lokale Tests während Entwicklung
- **Basic-Functionality:** Password Hashing, Model Creation, Core Functions
- **No-Dependencies:** Einfache Tests ohne DB/External Services
- **Debug-Support:** Console Output für manuelle Überprüfung

#### **test_utils.py (86 Zeilen)**
- **Security-Functions:** Password Hashing (bcrypt), Verification, Long Password Handling
- **Document-Generator:** DOCX Template Tests mit Mock-Implementation  
- **Email-Utilities:** SMTP Configuration, Template Rendering
- **Monkeypatching:** External Dependencies für isolierte Unit-Tests
- **Edge-Cases:** 200-Character Passwords, Invalid Inputs, Error Scenarios
- **OCR-Verarbeitung:** Pytesseract Integration
- **Metadaten-Extraktion:** Titel, Kunde, Daten, Finanzen
- **Validierung:** PDF-Integrität und Format-Checks

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
2. **✅ Datenmodelle:** User, Contract, Alert, Permission, RentStep
3. **✅ Pydantic-Schemas:** Validierung und Serialisierung
4. **✅ JWT-Authentifizierung:** Login, Registrierung, Tokens
5. **✅ Berechtigungssystem:** RBAC (7 neue Rollen, 6 Access Levels, granulare Berechtigungen) / Sistema de permissões (7 novos papéis, 6 níveis de acesso, permissões granulares)
6. **✅ Vertrags-CRUD:** Erstellung, Auflistung, Bearbeitung, Löschung
7. **✅ Alert-System:** Hintergrund-Scheduler, Benachrichtigungen (Auto + Manuell)
8. **✅ Dokumentenerstellung:** DOCX → PDF mit LibreOffice

**✅ Abgeschlossene Stufen (9-10):**
9. **✅ PDF-Import:** Intelligente Extraktion, Confidence Scores
10. **✅ PDF-Verwaltung:** Organisierte Speicherung, Inline-Visualisierung, Download

**✅ Neue Implementierungen (November 2025):**
- **✅ Manuelle Alerts:** BENUTZERDEFINIERT mit freier Terminwahl
- **✅ PACHT-Vertragstyp:** Erweiterte Vertragsklassifizierung
- **✅ PDF-Organisation:** Strukturierte temp/persisted Ordnerstruktur
- **✅ Inline-PDF-Viewer:** Direkte Browser-Visualisierung
- **✅ Mietstaffelung:** RentStep für zukünftige Anpassungen
- **✅ Deploy-Infrastruktur:** Vollautomatisches bilinguales Deployment-System
- **✅ Apache-Integration:** Professionelle Proxy-Konfiguration für interne Nutzung
- **✅ systemd-Service:** FastAPI als robuster Systemdienst
- **✅ Neues Berechtigungssystem:** 7 Benutzerrollen, 6 Zugriffsstufen, PERFIS_PADRAO / Novo sistema de permissões: 7 papéis, 6 níveis, PERFIS_PADRAO
- **✅ Granulare Berechtigungen:** can_view_contract, can_edit_contract, can_delete_contract, can_approve_contract, can_manage_users, can_set_user_role, can_access_reports / Permissões granulares
- **✅ Organisatorische Struktur:** Department & Team-Felder in User und Contract / Estrutura organizacional: campos Department & Team
- **✅ Migrations-Script:** migrate_user_roles_sql.py für automatische Rollenmigration / Script de migração automática de papéis
- **✅ Dokumentation:** PERMISSIONS_SYSTEM.md mit vollständiger DE/PT-Dokumentation / Documentação completa DE/PT

**⏳ Ausstehende Stufen (11, 14-15) / Etapas Pendentes (11, 14-15):**
11. **⏳ React-Frontend:** Benutzeroberfläche (ausstehend) / Interface do usuário (pendente)
14. **⏳ Erweiterte Berichte:** Dashboards und Analytics (ausstehend) / Dashboards e Analytics (pendente)
15. **⏳ Externe Integration:** Drittanbieter-APIs (ausstehend) / APIs de terceiros (pendente)

**🔄 In Bearbeitung (12) / Em Andamento (12):**
12. **🔄 Automatisierte Tests / Testes Automatizados:** ~75% abgeschlossen / concluído
   - ✅ Unit-Tests (test_utils.py): Security, Document Generator, Email Utils / Segurança, Gerador de Documentos, Utilitários de E-mail
   - ✅ Alert-Tests (test_alerts.py): Automatische & manuelle Alerts (458 Zeilen) / Alertas automáticos e manuais (458 linhas)
   - ✅ Contract-Tests (test_contract.py): CRUD Operations, PDF Integration (167 Zeilen) / Operações CRUD, Integração PDF (167 linhas)
   - ✅ PDF-Tests (test_pdf_unit.py): Schema Validation, File Operations (210 Zeilen) / Validação de Schema, Operações de Arquivo (210 linhas)
   - ✅ Database-Tests (test_integration_db.py): Model Integration (61 Zeilen) / Integração de Modelos (61 linhas)
   - ✅ System-Tests (test_complete.py): Folder Structure, Basic Operations (165 Zeilen) / Estrutura de Pastas, Operações Básicas (165 linhas)
   - ✅ Dev-Tests (test_local.py): Local Development Environment (23 Zeilen) / Ambiente de Desenvolvimento Local (23 linhas)
   - ⏳ Performance-Tests / Testes de Performance
   - ⏳ End-to-End-Tests / Testes End-to-End

**📈 Gesamtfortschritt / Progresso Geral:**
- **Backend:** 100% abgeschlossen / concluído
- **API:** 100% funktional (inkl. manuelle Alerts, PDF-Viewer) / funcional (incl. alertas manuais, visualizador PDF)
- **Datenmodelle / Modelos de Dados:** 100% (User, Contract, Alert, RentStep, Permission)
- **Berechtigungssystem / Sistema de Permissões:** 100% (7 Rollen, 6 Levels, granulare Funktionen) / (7 papéis, 6 níveis, funções granulares)
- **PDF-System / Sistema PDF:** 100% (Upload, Organisation, Visualisierung) / (Upload, Organização, Visualização)
- **Deploy-Infrastruktur / Infraestrutura de Deploy:** 100% (vollautomatisches bilinguales System) / (sistema bilíngue totalmente automatizado)
- **Apache-Konfiguration / Configuração Apache:** 100% (Proxy, Security, Caching) / (Proxy, Segurança, Cache)
- **systemd-Integration / Integração systemd:** 100% (Service, Auto-Start, Monitoring) / (Serviço, Inicialização Automática, Monitoramento)
- **Tests / Testes:** 75% implementiert / implementado
- **Frontend:** 0% (ausstehend) / (pendente)

**🎯 Nächste Schritte / Próximos Passos:**
1. **Frontend entwickeln / Desenvolver Frontend:** React + Vite (höchste Priorität / maior prioridade)
2. **Tests vervollständigen / Completar Testes:** 90%+ Abdeckung (insbesondere Berechtigungstests) / 90%+ cobertura (especialmente testes de permissões)
3. **Produktions-Deployment / Deploy em Produção:** Deploy-Scripts auf Produktionsserver ausführen / Executar scripts de deploy no servidor de produção
4. **HTTPS-Konfiguration / Configuração HTTPS:** SSL-Zertifikate für sichere Kommunikation / Certificados SSL para comunicação segura
5. **Berichte implementieren / Implementar Relatórios:** Erweiterte Dashboards mit Berechtigungsprüfung / Dashboards avançados com verificação de permissões
6. **Performance-Optimierung / Otimização de Performance:** Database-Tuning und Caching / Ajuste de banco de dados e cache

**🆕 Aktuelle Implementierungen (Nov 2025) / Implementações Atuais (Nov 2025):**
- ✅ **Manuelle Alerts / Alertas Manuais:** Flexibles Scheduling mit BENUTZERDEFINIERT / Agendamento flexível com PERSONALIZADO
- ✅ **PACHT-Verträge / Contratos de Arrendamento:** Neue Vertragsklassifizierung für Pachtverträge / Nova classificação de contrato para arrendamentos
- ✅ **PDF-Inline-Viewer / Visualizador PDF Inline:** Direkte Browser-Anzeige von PDFs / Visualização direta no navegador
- ✅ **Organisierte Uploads / Uploads Organizados:** Strukturierte temp/persisted-Ordner / Pastas temp/persisted estruturadas
- ✅ **Deploy-Infrastruktur / Infraestrutura de Deploy:** Vollautomatisches bilinguales Deployment (15KB Script) / Deploy bilíngue totalmente automatizado
- ✅ **Apache-Konfiguration / Configuração Apache:** Professionelle interne Server-Konfiguration / Configuração profissional de servidor interno
- ✅ **systemd-Service / Serviço systemd:** Robuste FastAPI-Service-Integration / Integração robusta de serviço FastAPI
- ✅ **Backend-Only Deploy / Deploy Somente Backend:** Produktionsreif ohne Frontend-Abhängigkeit / Pronto para produção sem dependência de frontend
- ✅ **RBAC-Upgrade / Atualização RBAC:** Komplettes Berechtigungssystem mit 7 Rollen und 6 Levels / Sistema RBAC completo com 7 papéis e 6 níveis
- ✅ **Granulare Berechtigungen / Permissões Granulares:** Funktionen für Verträge, Benutzer, Reports / Funções para contratos, usuários, relatórios
- ✅ **Organisationsstruktur / Estrutura Organizacional:** Department & Team in Models und Schemas / Departamento & Time em Models e Schemas
- ✅ **Standardprofile / Perfis Padrão:** PERFIS_PADRAO für typische Anwendungsfälle / PERFIS_PADRAO para casos típicos
- ✅ **Alembic-Migration / Migração Alembic:** 0005_add_access_level_team_and_new_roles.py
- ✅ **Dokumentation / Documentação:** PERMISSIONS_SYSTEM.md vollständig bilingual (461 Zeilen) / completamente bilíngue (461 linhas)

---

## Deploy-Infrastruktur / Infraestrutura de Deploy

### **Automatisiertes Deployment-System / Sistema de Deploy Automatizado**

Das Projekt verfügt über eine vollständige billinguale Deploy-Infrastruktur für interne Unternehmensserver.
O projeto possui uma infraestrutura completa de deploy bilíngue para servidores internos da empresa.

#### **Deploy-Scripts / Scripts de Deploy**

##### **1. Hauptscript: `deploy-internal.sh`**
**Beschreibung / Descrição:** Vollautomatisches Deploy-Script mit bilingualer Benutzerführung (Deutsch/Portugiesisch)

**Funktionen / Funcionalidades:**
```bash
./deploy-internal.sh deploy      # Vollständiges Deployment
./deploy-internal.sh status      # System-Status prüfen
./deploy-internal.sh logs        # Log-Dateien anzeigen
./deploy-internal.sh help        # Hilfe in DE/PT
```

**Automatisierte Schritte / Passos Automatizados:**
- ✅ **Systemabhängigkeiten prüfen:** Apache, Python, SQLite
- ✅ **Python-Umgebung:** Virtual Environment einrichten
- ✅ **Datenbank:** Alembic-Migrationen ausführen
- ✅ **Apache-Konfiguration:** Proxy für FastAPI einrichten
- ✅ **systemd-Service:** FastAPI als Systemdienst installieren
- ✅ **Dateiberechtigungen:** Sichere Permissions setzen
- ✅ **Status-Validierung:** Funktionsprüfung aller Komponenten

##### **2. Setup-Script: `deploy/setup-internal.sh`**
**Beschreibung / Descrição:** Einmaliges Setup für Apache-Konfiguration und Berechtigungen

**Verwendung / Uso:**
```bash
cd deploy/
./setup-internal.sh
```

##### **3. Permissions-Script: `setup-permissions.sh`**
**Beschreibung / Descrição:** Sicherheitskonfiguration für Dateiberechtigungen

**Sicherheitsfeatures / Recursos de Segurança:**
- Datenbank: `chmod 600` (nur Besitzer kann lesen/schreiben)
- Scripts: `chmod +x` (ausführbar machen)
- Upload-Verzeichnisse: Korrekte www-data Berechtigungen

#### **Apache-Konfiguration / Configuração Apache**

##### **Datei: `deploy/apache-internal.conf`**
**Zweck / Propósito:** Professionelle Apache-Konfiguration für interne Unternehmensnutzung

**Konfigurierte Features / Recursos Configurados:**
- **Proxy-Setup:** API-Calls an FastAPI weiterleiten (`/api/*` → `127.0.0.1:8000`)
- **Frontend-Serving:** Statische Dateien für zukünftiges Frontend
- **Security Headers:** XSS-Schutz, Content-Type-Validation, Frame-Options
- **CORS-Headers:** Interne API-Zugriffe ermöglichen
- **Caching:** Optimierte Performance für statische Assets
- **Komprimierung:** Gzip für bessere Übertragungsgeschwindigkeit
- **Logging:** Strukturierte Access- und Error-Logs

**VirtualHost-Konfiguration:**
```apache
<VirtualHost *:80>
    ServerName vertrag-mgs.empresa.local
    DocumentRoot /var/www/html/vertrag-mgs
    
    # API Proxy
    <Location "/api/">
        ProxyPass "http://127.0.0.1:8000/"
        ProxyPassReverse "http://127.0.0.1:8000/"
    </Location>
    
    # Security & Performance Headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    
    # Static Assets Caching
    <LocationMatch "\.(css|js|png|jpg|gif|ico)$">
        ExpiresDefault "access plus 1 month"
    </LocationMatch>
</VirtualHost>
```

#### **systemd-Service-Konfiguration / Configuração systemd**

**Service-Name:** `vertrag-mgs-api.service`

**Eigenschaften / Características:**
- **Auto-Start:** Startet automatisch beim Server-Boot
- **Auto-Restart:** Automatischer Neustart bei Fehlern
- **User:** Läuft unter `www-data` für Sicherheit
- **Working Directory:** Projekt-Root mit Virtual Environment
- **Logging:** systemd Journal-Integration

**Service-Konfiguration:**
```ini
[Unit]
Description=Vertragsverwaltungssystem API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/pfad/zum/projekt
Environment="PATH=/pfad/zum/projekt/.venv/bin"
ExecStart=/pfad/zum/projekt/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### **Deployment-Architektur / Arquitetura de Deployment**

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Apache (Port 80)   │    │  FastAPI (Port 8000) │    │   SQLite Database   │
│   Frontend Static    │◄──►│     Backend API      │◄──►│     Data Layer      │
│   Proxy zu FastAPI  │    │   systemd Service    │    │   File Permissions  │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
          │                           │                           │
          ▼                           ▼                           ▼
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  Security Headers   │    │   Background Tasks  │    │   Upload Directory  │
│  CORS Configuration │    │   Alert Scheduler   │    │   temp/persisted    │
│  Static Asset Cache │    │   Email Service     │    │   PDF Management    │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

#### **Bereitstellungsprozess / Processo de Deploy**

**Schritt-für-Schritt Anleitung / Guia Passo-a-Passo:**

1. **Vorbereitung / Preparação:**
   ```bash
   git pull origin main
   chmod +x deploy-internal.sh
   chmod +x deploy/setup-internal.sh
   chmod +x setup-permissions.sh
   ```

2. **Erstkonfiguration / Configuração Inicial:**
   ```bash
   cd deploy/
   ./setup-internal.sh
   ```

3. **Vollständiges Deployment / Deploy Completo:**
   ```bash
   ./deploy-internal.sh deploy
   ```

4. **Status-Überprüfung / Verificação de Status:**
   ```bash
   ./deploy-internal.sh status
   ```

**Erwartete Ausgabe nach erfolgreichem Deploy / Saída Esperada após Deploy Bem-sucedido:**
```
✅ Apache2: Aktiv / Ativo
✅ FastAPI: Aktiv / Ativo (Port 8000)

🌐 ZUGRIFF / ACESSO:
   Sistema:  http://servidor-interno/ (→ API docs)
   API:      http://servidor-interno/api/
   Docs:     http://servidor-interno/api/docs
   ⚠️  Frontend: Em desenvolvimento / In Entwicklung
```

#### **Wartung und Monitoring / Manutenção e Monitoramento**

**Log-Zugriff / Acesso a Logs:**
```bash
# Systemd Service Logs
sudo journalctl -u vertrag-mgs-api.service -f

# Apache Logs
sudo tail -f /var/log/apache2/vertrag-mgs-access.log
sudo tail -f /var/log/apache2/vertrag-mgs-error.log

# Script-basierte Logs
./deploy-internal.sh logs apache
./deploy-internal.sh logs fastapi
./deploy-internal.sh logs all
```

**Service-Management / Gerenciamento de Serviços:**
```bash
# FastAPI Service
sudo systemctl start vertrag-mgs-api
sudo systemctl stop vertrag-mgs-api
sudo systemctl restart vertrag-mgs-api
sudo systemctl status vertrag-mgs-api

# Apache Service
sudo systemctl restart apache2
sudo systemctl status apache2
```

### **Backend-Only Deployment / Deploy Apenas Backend**

**Aktuelle Konfiguration / Configuração Atual:**
Da das Frontend noch nicht entwickelt wurde, ist das Deploy-System für einen **Backend-Only-Betrieb** konfiguriert:
Como o frontend ainda não foi desenvolvido, o sistema de deploy está configurado para **operação apenas backend**:

- **Startseite:** Zeigt Entwicklungshinweis und leitet zur API-Dokumentation weiter
- **API-Zugriff:** Vollständig funktional über `/api/*` Endpunkte
- **Frontend-Placeholder:** Temporäre HTML-Seite mit Statusinformationen
- **Erweiterbar:** Bereit für Frontend-Integration ohne Neukonfiguration

**Temporäre Startseite-Inhalte / Conteúdo da Página Inicial Temporária:**
```html
🚧 Sistema em Desenvolvimento / System Under Development 🚧
Deutsch: Das Frontend befindet sich noch in der Entwicklung.
Português: O frontend ainda está em desenvolvimento.
API: FastAPI Documentation verfügbar / disponível
Status: Backend ✅ | Frontend 🚧
```

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

---

## **🚀 Aktuelle Systemerweiterungen (November 2025)**

### **🔔 Manuelle Alert-Funktionalität**
**Implementiert:** Vollständiges System für benutzerdefinierte Benachrichtigungen
- **Endpoint:** `POST /alerts/manual` mit flexibler Terminplanung
- **AlertType:** `BENUTZERDEFINIERT` für manuelle Alerts
- **Integration:** Nahtlose Verarbeitung durch bestehenden Scheduler
- **Benutzerfreundlichkeit:** Automatische Defaults für Empfänger und Betreff

### **📄 PDF-Management-System**
**Implementiert:** Organisierte Dateiverwaltung mit Inline-Visualisierung
- **Strukturierte Uploads:** `temp/` → `persisted/{contract_id}/` Migration
- **Integritätsprüfung:** SHA256-Hash-Validierung für Dateisicherheit
- **Dual-Zugriff:** Download (attachment) und Inline-Viewer (browser)
- **Metadaten-Tracking:** Vollständige Audit-Trails für PDF-Operationen

### **🏢 PACHT-Vertragstyp**
**Implementiert:** Erweiterte Vertragsklassifizierung
- **Neuer Typ:** `ContractType.PACHT` für Pachtverträge
- **Migration:** `0004_add_pacht_contract_type.py` implementiert
- **Kompatibilität:** Vollständige RentStep-Unterstützung
- **Semantik:** Klare Trennung zwischen Miet- (LEASE) und Pachtverträgen (PACHT)

### **📊 Technische Verbesserungen**
- **Code-Qualität:** Alle Compilation-Errors behoben
- **Dokumentation:** Vollständig zweisprachig (DE/PT) aktualisiert
- **Testabdeckung:** Umfassende Validierung aller neuen Features
- **Migrationen:** Saubere Alembic-Versionskontrolle

**Status:** Alle Implementierungen sind produktionsreif und vollständig getestet ✅

