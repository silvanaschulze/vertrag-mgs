# Contract Management and Automatic Renewal System (MVP)

A Contract Management and Automatic Renewal System designed to prevent delays or unwanted renewals of contracts with suppliers and service providers.
The system ensures proactive monitoring, centralized digital storage, and automation of contract lifecycle tasks.

## Core Features
- Contract CRUD (title, counterparty, type, value, start/end dates, department, renewal responsible/email)
- Automatic email alert 30 days before expiration (APScheduler)
- Digital storage of contracts in PDF format
- Draft generation using docxtpl (.docx → PDF)
- Responsible person management for each contract
- Basic audit events (who did what, when)
- Daily backups (DB dump + files)

## Tech Stack
- **Backend:** Python (FastAPI, SQLAlchemy 2.0, Alembic, APScheduler)
- **Database:** MySQL 8
- **Templates:** docxtpl
- **Frontend:** React + Vite (later)
- **Dev/Deploy:** Docker Compose
- **Utilities:** Adminer (DB GUI), Mailpit (SMTP testing)

## Development Setup
1. Create and use `main` branch
2. `docker compose up` to start MySQL, Adminer, Mailpit
3. Implement backend API + migrations
4. Add React + Vite frontend (consume API)
