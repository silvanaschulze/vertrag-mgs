"""
Contract Management System - FastAPI Hauptanwendung
Sistema de Gerenciamento de Contratos - Aplicação Principal FastAPI
Erstellt: 2024 / Criado: 2024

Diese Datei enthält die Hauptanwendung für das Contract Management System.
Esta arquivo contém a aplicação principal para o Sistema de Gerenciamento de Contratos.
Sie konfiguriert FastAPI, Middleware, Router und Scheduler.
Ela configura FastAPI, middleware, roteadores e agendador.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.routers import auth_router, contracts_router, users_router, alerts_router, rent_steps_router
from app.routers.contracts_import import router as contracts_import_router
from app.routers.health import router as health_router
from app.routers.dashboard import router as dashboard_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.services.notification_service import NotificationService

# Configurar logging / Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler task / Tarefa global do scheduler
scheduler_task: asyncio.Task | None = None


async def process_contract_alerts() -> None:
    """
    Processa alertas de contratos vencendo.
    Verarbeitet Vertragsablauf-Benachrichtigungen.
    """
    try:
        logger.info("Starting contract alerts processing / Iniciando processamento de alertas de contratos")
        
        async with SessionLocal() as db:
            notification_service = NotificationService(db)
            result = await notification_service.process_due_alerts()
            
            logger.info(f"Processed {result.total} contract alerts / Processados {result.total} alertas de contratos")
           
            
    except Exception as e:
        logger.error(f"Error processing contract alerts / Erro ao processar alertas de contratos: {e}")

async def background_scheduler() -> None:
    """
    Background task para processar alertas periodicamente.
    Hintergrund-Task für periodische Benachrichtigungen.
    """
    while True:
        try:
            await process_contract_alerts()
            # Aguardar 6 horas antes do próximo processamento / Wait 6 hours before next processing
            await asyncio.sleep(6 * 60 * 60)  # 6 hours in seconds
        except Exception as e:
            logger.error(f"Error in background scheduler / Erro no scheduler em background: {e}")
            # Aguardar 1 hora em caso de erro / Wait 1 hour on error
            await asyncio.sleep(60 * 60)  # 1 hour in seconds



@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gerencia o ciclo de vida da aplicação / Manages application lifecycle.
    Inicia e para o scheduler automaticamente.
    """
    global scheduler_task
    
    # Startup / Inicialização
    logger.info("Starting application / Iniciando aplicação")
    
        # Iniciar task de background / Start background task
    scheduler_task = asyncio.create_task(background_scheduler())
    logger.info("Background scheduler started / Scheduler em background iniciado")
    
    yield
    
    # Shutdown / Finalização
    logger.info("Shutting down application / Finalizando aplicação")
    if scheduler_task:
        scheduler_task.cancel()
        try:
            await scheduler_task
        except asyncio.CancelledError:
            pass
        logger.info("Background scheduler stopped / Scheduler em background parado")


# FastAPI-Anwendung erstellen / Criar aplicação FastAPI
app = FastAPI(
    title="Contract Management System",
    description="Ein System zur Verwaltung von Verträgen mit automatischen Benachrichtigungen / Um sistema para gerenciamento de contratos com notificações automáticas",
    version="1.0.0",
    lifespan=lifespan
)



# CORS-Middleware konfigurieren / Configurar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
    expose_headers=["Content-Type", "Authorization"],
)

# Router registrieren / Registrar roteadores
app.include_router(health_router)  # Health checks sem autenticação
app.include_router(auth_router, prefix="/api")
app.include_router(contracts_router, prefix="/api")
app.include_router(contracts_import_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(rent_steps_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")  # Dashboard stats

@app.get("/")
def root():
    """
    Root-Endpunkt für die API / Endpoint raiz da API
    """
    return {
        "message": "Contract Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    """
    Health-Check-Endpunkt für die Anwendung / Endpoint de verificação de saúde da aplicação
    """
    return {"ok": True, "status": "healthy"}


@app.get("/scheduler/status")
def get_scheduler_status():
    """
    Status do scheduler / Scheduler-Status
    """
    global scheduler_task
    
    if not scheduler_task:
        return {
            "status": "not_initialized",
            "message": "Scheduler not initialized / Scheduler não inicializado"
        }
    
    
    return {
        "status": "running" if not scheduler_task.done() else "stopped",
        "task_name": "background_scheduler",
        "message": "Background task running every 6 hours / Tarefa em background executando a cada 6 horas"
    }


@app.post("/scheduler/trigger-alerts")
async def trigger_contract_alerts():
    """
    Dispara processamento manual de alertas / Manueller Auslöser für Benachrichtigungen
    """
    try:
        await process_contract_alerts()
        return {
            "success": True,
            "message": "Contract alerts processing triggered / Processamento de alertas disparado"
        }
    except Exception as e:
        logger.error(f"Error triggering alerts / Erro ao disparar alertas: {e}")
        return {
            "success": False,
            "message": f"Error triggering alerts / Erro ao disparar alertas: {str(e)}"
        }
    