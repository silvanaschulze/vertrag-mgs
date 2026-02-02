# Copilot Instructions for Vertrag-MGS

## Arquitetura Geral
- **Backend:** FastAPI (API REST principal), SQLAlchemy 2.0 (ORM), Alembic (migrações), Pydantic (validação), JWT (autenticação)
- **Frontend:** React + Vite (src/), comunicação via REST
- **Banco de Dados:** SQLite (dev), MySQL (prod)
- **PDF:** pdfplumber, PyPDF2, pytesseract (OCR)
- **Documentos:** docxtpl, LibreOffice
- **Deploy:** Docker, Apache (reverse proxy), systemd (Linux), Docker Engine (Windows)

## Fluxos e Workflows
- **Migrações:** Use `alembic upgrade head` para aplicar todas as migrações. Scripts em `alembic/versions/`.
- **Testes:** Execute `pytest` (ou `pytest --cov=app` para cobertura) a partir de `backend/`. Testes em `backend/test/`.
- **Backup/Restore:** Scripts em `scripts/` para Linux e Windows. Cron para backups automáticos.
- **Ambiente:** Use `.env` (baseie-se em `.env.example`).
- **Inicialização local:**
  1. `python3 -m venv .venv && source .venv/bin/activate`
  2. `pip install -r backend/requirements.txt`
  3. `cp .env.example .env` e edite
  4. `cd backend && alembic upgrade head`
  5. `uvicorn main:app --reload --port 8000`

## Convenções Específicas
- **Permissões:** RBAC com 7 papéis, 6 níveis de acesso. Veja `docs/PERMISSIONS_SYSTEM.md`.
- **Aprovação de Contratos:** Workflow multi-nível (1-6), automático/manual, rastreio completo. Veja migração `0006_add_contract_approvals.py`.
- **Alertas:** Notificações automáticas (T-60, T-30, T-10, T-1) e manuais.
- **Padrão de código:** Backend segue FastAPI + SQLAlchemy 2.0 (async), schemas Pydantic em `backend/app/schemas/`, modelos em `backend/app/models/`, rotas em `backend/app/routers/`, serviços em `backend/app/services/`.
- **PDFs:** Uploads em `uploads/contracts/`, templates em `uploads/templates/`.

## Integrações e Dependências
- **APIs externas:** Não há integrações externas diretas documentadas.
- **Dependências:** Veja `backend/requirements.txt` e `frontend/package.json`.
- **Documentação:**
  - [README.md](../README.md) (visão geral)
  - [Technische_Dokumentation.md](../Technische_Dokumentation.md) (detalhada)
  - [deploy/README-PRODUCTION.md](../deploy/README-PRODUCTION.md) (deploy Linux)
  - [deploy/README-DOCKER-WINDOWS.md](../deploy/README-DOCKER-WINDOWS.md) (deploy Windows)

## Exemplos de Comandos
- **Migração:** `alembic upgrade head`
- **Testes:** `pytest --cov=app`
- **Backup manual:** `sudo bash scripts/backup-system.sh`
- **Restore:** `sudo bash scripts/restore-system.sh <file>`
- **Start dev server:** `uvicorn main:app --reload --port 8000`

## Observações
- Sempre consulte os scripts de deploy e backup antes de alterar fluxos críticos.
- Siga a estrutura de pastas do backend para novos módulos (core/models/routers/schemas/services/utils).
- Use os exemplos de testes em `backend/test/` para novos testes.
