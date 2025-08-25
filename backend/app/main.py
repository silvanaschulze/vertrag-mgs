"""
Contract Management System - FastAPI Hauptanwendung
Erstellt: 2024

Diese Datei enthält die Hauptanwendung für das Contract Management System.
Sie konfiguriert FastAPI, Middleware, Router und Scheduler.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI-Anwendung erstellen
app = FastAPI(
    title="Contract Management System",
    description="Ein System zur Verwaltung von Verträgen mit automatischen Benachrichtigungen",
    version="1.0.0"
)

# CORS-Origins für Entwicklung
origins = [
    "http://localhost:5173", 
    "http://si-server.mshome.net:5173",
    "http://localhost:3000"  # ← Para React (futuro)
]

# CORS-Middleware konfigurieren
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """
    Root-Endpunkt für die API.
    """
    return {
        "message": "Contract Management System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    """
    Health-Check-Endpunkt für die Anwendung.
    """
    return {"ok": True, "status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    