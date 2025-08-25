# Contract Management System (MVP)

A system for managing contracts with automatic renewal alerts, draft generation, and organized PDF storage.

A system for managing contracts with automatic renewal alerts, template-based draft generation (docxtpl), and organized PDF storage.

## MVP Features
- Contract CRUD (title, counterparty, type, value, start/end dates, department, renewal responsible/email)
- Automatic email alert 30 days before expiration (APScheduler)
- Document storage on filesystem (PDFs, drafts)
- Draft generation using docxtpl (.docx)
- Basic audit events (who did what, when)
- Daily backups (DB dump + files)

## Tech Stack
- **Backend:** Python (FastAPI, SQLAlchemy 2.0, Alembic, APScheduler)
- **Database:** MySQL 8
- **Templates:** docxtpl
- **Frontend:** React + Vite (later)
- **Dev/Deploy:** Docker Compose
- **Utilities:** Adminer (DB GUI), Mailpit (SMTP testing)

## Dev bootstrap
1. Create and use `dev` branch
2. `docker compose up` to start MySQL, Adminer, Mailpit
3. Implement backend API + migrations
4. Add React + Vite frontend (consume API)