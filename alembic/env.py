import asyncio
import sys
import os
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection

from alembic import context

# Ensure project root is on sys.path so `app` imports resolve
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging if available.
cfg_fname = getattr(config, "config_file_name", None)
if cfg_fname:
    try:
        fileConfig(cfg_fname)
    except Exception:
        # best-effort logging configuration; do not fail migrations if logging setup fails
        pass

import importlib

def _dynamic_import(module_name: str):
    try:
        return importlib.import_module(module_name)
    except Exception:
        return None

# Try a few module paths so Alembic can run with different PYTHONPATH layouts
db_mod = _dynamic_import("app.core.database") or _dynamic_import("backend.app.core.database")
cfg_mod = _dynamic_import("app.core.config") or _dynamic_import("backend.app.core.config")

if not db_mod or not cfg_mod:
    raise RuntimeError(
        "Cannot import project modules for Alembic env (tried 'app.core.*' and 'backend.app.core.*'). "
        "Run Alembic with the project root on PYTHONPATH, e.g. `PYTHONPATH=backend alembic ...`"
    )

Base = getattr(db_mod, "Base")
settings = getattr(cfg_mod, "settings")


target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url") or settings.SQLALCHEMY_DATABASE_URI
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    connectable = create_async_engine(settings.SQLALCHEMY_DATABASE_URI)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def run_migrations_online() -> None:
    try:
        asyncio.run(run_async_migrations())
    except Exception:
        # fallback for synchronous engines
        from sqlalchemy import create_engine

        url = config.get_main_option("sqlalchemy.url") or getattr(settings, "SQLALCHEMY_DATABASE_URI", None)
        if not url:
            raise RuntimeError("No SQLAlchemy URL configured for alembic offline/online fallback")

        engine = create_engine(url)
        with engine.connect() as connection:
            do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
