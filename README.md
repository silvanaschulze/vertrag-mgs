# Vertragsverwaltungssystem / Contract Management System

**Deutsch / Português / English**

Umfassendes Vertragsverwaltungssystem mit automatischen Benachrichtigungen, mehrstufigem Genehmigungsworkflow und intelligentem PDF-Management.

Comprehensive contract management system with automatic notifications, multi-level approval workflow, and intelligent PDF management.

Sistema abrangente de gerenciamento de contratos com notificações automáticas, fluxo de aprovação em vários níveis e gerenciamento inteligente de PDF.

---

## 🚀 Core Features

- **Contract Management** - Full CRUD, PDF upload/storage, intelligent extraction, document generation
- **Approval Workflow** - Multi-level (1-6), automatic & manual, full audit trail
- **Alert System** - Automatic (T-60, T-30, T-10, T-1) + manual scheduling
- **Permission System** - 7 roles, 6 access levels, RBAC, JWT authentication
- **Health Checks** - System, database, storage monitoring (production-ready)
- **Backup System** - Automatic daily backups with rotation (Linux & Windows)
- **Rent Step Management** - Future rent adjustments for lease contracts (Mietstaffelung)
- **Bilingual** - Full German/Portuguese support

---

## 🛠️ Tech Stack

**Backend:** FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, JWT  
**Database:** SQLite (dev), MySQL (prod)  
**PDF:** pdfplumber, PyPDF2, pytesseract (OCR)  
**Documents:** docxtpl, LibreOffice  
**Deployment:** Docker, Apache, systemd  
**Testing:** pytest, pytest-asyncio

---

## 🚀 Quick Start

### Development

```bash
# Clone and setup
git clone <repo-url>
cd vertrag-mgs
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# Configure
cp .env.example .env
# Edit .env with your settings

# Run migrations
cd backend
alembic upgrade head

# Start server
uvicorn main:app --reload --port 8000
```

**Access:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs

---

## 🐳 Production Deployment

### Linux/Ubuntu
```bash
sudo bash deploy-internal.sh
```
📖 **Full guide:** [deploy/README-PRODUCTION.md](deploy/README-PRODUCTION.md)

### Windows Server (Docker Engine)
```powershell
# See detailed guide
deploy/README-DOCKER-WINDOWS.md
```
📖 **Full guide:** [deploy/README-DOCKER-WINDOWS.md](deploy/README-DOCKER-WINDOWS.md)

**Features:** Apache reverse proxy (Linux), Docker Engine (Windows), automatic backups, health checks, systemd/Windows service

---

## 💾 Backup & Restore

**Linux:**
```bash
sudo bash scripts/backup-system.sh           # Manual backup
sudo bash scripts/setup-backup-cron.sh       # Schedule daily
sudo bash scripts/restore-system.sh <file>   # Restore
```

**Windows:**
```powershell
.\scripts\backup-windows.ps1                 # Manual backup
.\scripts\restore-windows.ps1 -BackupFile <file>  # Restore
```

Auto-scheduled daily at 2:00 AM • 30-day retention • SHA256 integrity checks

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **[Technische_Dokumentation.md](Technische_Dokumentation.md)** | Complete technical documentation (DE/PT) |
| **[PERMISSIONS_SYSTEM.md](docs/PERMISSIONS_SYSTEM.md)** | Permission system guide (DE/PT) |
| **[README-PRODUCTION.md](deploy/README-PRODUCTION.md)** | Linux deployment guide |
| **[README-DOCKER-WINDOWS.md](deploy/README-DOCKER-WINDOWS.md)** | Windows Docker deployment |
| **[API Docs](http://localhost:8000/docs)** | Interactive API documentation |

---

## 🔍 Database Migrations

1. `0001_initial.py` - Initial schema
2. `0002_add_rent_steps.py` - Rent step management
3. `0003_add_contract_pdf_fields.py` - PDF storage
4. `0004_add_pacht_contract_type.py` - PACHT type
5. `0005_add_access_level_team_and_new_roles.py` - Enhanced permissions
6. `0006_add_contract_approvals.py` - Approval workflow

```bash
alembic upgrade head        # Apply all
alembic current             # Show current
alembic history             # Show history
```

---

## 🧪 Testing

```bash
pytest                      # Run all tests
pytest --cov=app           # With coverage
pytest -v                  # Verbose
```

**Test files:** `test_alerts.py`, `test_contract.py`, `test_pdf_unit.py`, `test_integration_db.py`, `test_complete.py`, `test_users.py`, `test_utils.py`

---

## 🎯 Roadmap

### ✅ Completed
- Contract CRUD with PDF management
- Multi-level approval workflow
- Automatic alert system (T-60, T-30, T-10, T-1)
- Rent step management (Mietstaffelung)
- 7-role permission system
- Health check endpoints
- Backup system (Linux & Windows)
- Docker deployment (Linux & Windows)

### 🚧 In Progress
- React frontend
- Approval workflow UI
- Health metrics dashboard

### 📅 Planned
- External integrations (ERP, CRM)
- Advanced analytics
- Mobile app
- E-signature integration

---

**Version:** 1.5.0  
**Last Updated:** 28. Dezember 2025

---

**Made with ❤️ for contract management**


