"""
Health Check Endpoints - Vertrag MGS
Monitoramento e diagnóstico do sistema
System-Überwachung und Diagnose

DE: Endpunkte für Systemstatus, Datenbankverbindung und Service-Verfügbarkeit
PT: Endpoints para status do sistema, conexão com banco e disponibilidade do serviço
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
import os
import sys
from pathlib import Path

from app.core.database import get_db
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """
    Health Check básico / Einfacher Health Check
    
    Returns / Retorna:
    - Status: OK/ERROR
    - Timestamp
    - Versão Python
    - Uptime (se disponível)
    
    Use: Kubernetes liveness probe, load balancer checks, monitoring
    """
    return {
        "status": "OK",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }


@router.get("/db")
async def health_check_database(db: AsyncSession = Depends(get_db)):
    """
    Health Check do Banco de Dados / Datenbank Health Check
    
    Logik / Lógica:
    - Executa query simples para verificar conectividade
    - Führt einfache Abfrage aus, um die Konnektivität zu überprüfen
    
    Returns / Retorna:
    - Database: OK/ERROR
    - Response Time (ms)
    """
    try:
        start_time = datetime.utcnow()
        
        # Executa query simples / Führt einfache Abfrage aus
        result = await db.execute(text("SELECT 1"))
        row = result.scalar()
        
        end_time = datetime.utcnow()
        response_time_ms = (end_time - start_time).total_seconds() * 1000
        
        if row != 1:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Database query failed / Datenbankabfrage fehlgeschlagen"
            )
        
        return {
            "status": "OK",
            "database": "connected",
            "response_time_ms": round(response_time_ms, 2),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed / Datenbankverbindung fehlgeschlagen: {str(e)}"
        )


@router.get("/storage")
async def health_check_storage():
    """
    Health Check do Sistema de Arquivos / Dateisystem Health Check
    
    Verifica / Überprüft:
    - Diretório de uploads acessível / Upload-Verzeichnis zugänglich
    - Espaço em disco disponível / Verfügbarer Speicherplatz
    """
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        
        # Verificar se diretório existe e é acessível
        if not upload_dir.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Upload directory does not exist / Upload-Verzeichnis existiert nicht"
            )
        
        if not os.access(upload_dir, os.W_OK):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Upload directory not writable / Upload-Verzeichnis nicht beschreibbar"
            )
        
        # Verificar espaço em disco (Linux/Unix)
        stat = os.statvfs(upload_dir)
        free_space_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
        total_space_gb = (stat.f_blocks * stat.f_frsize) / (1024 ** 3)
        used_percent = ((total_space_gb - free_space_gb) / total_space_gb) * 100
        
        status_msg = "OK"
        if used_percent > 90:
            status_msg = "WARNING - Disk space critical"
        elif used_percent > 75:
            status_msg = "WARNING - Disk space low"
        
        return {
            "status": status_msg,
            "upload_directory": str(upload_dir),
            "writable": True,
            "disk_space": {
                "total_gb": round(total_space_gb, 2),
                "free_gb": round(free_space_gb, 2),
                "used_percent": round(used_percent, 2)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Storage check failed / Speicherüberprüfung fehlgeschlagen: {str(e)}"
        )


@router.get("/detailed")
async def health_check_detailed(db: AsyncSession = Depends(get_db)):
    """
    Health Check detalhado / Detaillierter Health Check
    
    Combina todas as verificações:
    - Sistema / System
    - Banco de dados / Datenbank
    - Armazenamento / Speicher
    
    Use: Monitoramento completo, troubleshooting
    """
    try:
        # Basic health
        basic = await health_check()
        
        # Database health
        try:
            db_health = await health_check_database(db)
            db_status = "OK"
        except Exception as e:
            db_health = {"error": str(e)}
            db_status = "ERROR"
        
        # Storage health
        try:
            storage_health = await health_check_storage()
            storage_status = "OK"
        except Exception as e:
            storage_health = {"error": str(e)}
            storage_status = "ERROR"
        
        # Overall status
        overall_status = "OK" if (db_status == "OK" and storage_status == "OK") else "DEGRADED"
        
        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": {
                "system": basic,
                "database": {
                    "status": db_status,
                    "details": db_health
                },
                "storage": {
                    "status": storage_status,
                    "details": storage_health
                }
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Detailed health check failed / Detaillierte Gesundheitsprüfung fehlgeschlagen: {str(e)}"
        )
