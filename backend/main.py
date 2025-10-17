"""
Contract Management System - FastAPI Hauptanwendung
Sistema de Gerenciamento de Contratos - Aplicação Principal FastAPI
Erstellt: 2024 / Criado: 2024

Diese Datei enthält die Hauptanwendung für das Contract Management System.
Esta arquivo contém a aplicação principal para o Sistema de Gerenciamento de Contratos.
Sie konfiguriert FastAPI, Middleware, Router und Scheduler.
Ela configura FastAPI, middleware, roteadores e agendador.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth_router, contracts_router, users_router
from app.core.config import settings

# FastAPI-Anwendung erstellen / Criar aplicação FastAPI
app = FastAPI(
    title="Contract Management System",
    description="Ein System zur Verwaltung von Verträgen mit automatischen Benachrichtigungen / Um sistema para gerenciamento de contratos com notificações automáticas",
    version="1.0.0"
)



# CORS-Middleware konfigurieren / Configurar middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router registrieren / Registrar roteadores
app.include_router(auth_router)
app.include_router(contracts_router)
app.include_router(users_router)

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
    