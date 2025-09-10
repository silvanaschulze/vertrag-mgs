"""
Vertrags-Router Modul
Dieses Modul enthält alle API-Endpoints für die Verwaltung von Verträgen.
Funktionen :
- CRUD-Operationen für Verträge 
- Filterung und Paginierung 
- Statistiken und Berichte 
- Suche und Validierung 

"""
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session  

from app.core.database import get_db
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ContractStats,
)
from app.services.contract_service import ContractService

# Router für Contract-Endpoints
router = APIRouter(
    prefix="/contracts",
    tags=["contracts"],
    responses={
        404: {"description": "Vertrag nicht gefunden"},
        400: {"description": "Ungültige Anfrage"},
        500: {"description": "Interner Serverfehler"}
    }
)
def get_contract_service(db: Session = Depends(get_db)) -> ContractService:
    """
    ContractService Dependency Injection (Abhängigkeitsinjektion)
    Argumente:
        db: Datenbanksitzung
    Rückgabe:
        ContractService: Service-Instanz
    """
    return ContractService(db)  

# GET /contracts/ - Liste alle Verträge
@router.get("/", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
def list_contracts(
    page: int = Query(1, ge=1, description="Seitennummer"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite"),
    status: Optional[str] = Query(None, description="Filter nach Vertragsstatus"),
    contract_type: Optional[str] = Query(None, description="Filter nach Vertragstyp"),
    search: Optional[str] = Query(None, description="Suchbegriff für Titel oder Beschreibung"),
    sort_by: Optional[str] = Query("created_at", description="Feld zum Sortieren"),
    sort_order: Optional[str] = Query("desc", description="Sortierreihenfolge (asc oder desc)"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Listet Verträge mit optionaler Filterung, Suche und Paginierung auf.
    Argumente:
        page (int): Seitennummer (Standard: 1)
        per_page (int): Anzahl der Verträge pro Seite (Standard: 10, Max: 100)
        status (str, optional): Filter nach Vertragsstatus
        contract_type (str, optional): Filter nach Vertragstyp
        search (str, optional): Suchbegriff für Titel oder Beschreibung
        sort_by (str, optional): Feld zum Sortieren (Standard: created_at)
        sort_order (str, optional): Sortierreihenfolge (asc oder desc) (Standard: desc)
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        ContractListResponse: Liste der Verträge mit Paginierungsinformationen
    """
    return contract_service.list_contracts(
        page=page,
        per_page=per_page,
        status=status,
        contract_type=contract_type,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )   
# POST /contracts/ - Erstellt einen neuen Vertrag
@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
def create_contract(    
    contract: ContractCreate,
    created_by: int = Query(..., description="ID des Benutzers, der den Vertrag erstellt"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Erstellt einen neuen Vertrag.
    Argumente:
        contract (ContractCreate): Vertragsdaten
        created_by (int): ID des Benutzers, der den Vertrag erstellt
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        ContractResponse: Erstellter Vertrag
    """
    try:
        return contract_service.create_contract(contract, created_by)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Erstellen des Vertrags")     

# GET /contracts/{contract_id} - Ruft einen Vertrag nach ID ab
@router.get("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def get_contract(   
    contract_id: int,
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Ruft einen Vertrag nach seiner ID ab.
    Argumente:
        contract_id (int): ID des Vertrags
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        ContractResponse: Abgerufener Vertrag
    """
    contract = contract_service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden")
    return contract
# PUT /contracts/{contract_id} - Aktualisiert einen Vertrag nach ID
@router.put("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
def update_contract(
    contract_id: int,
    contract_data: ContractUpdate,
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Aktualisiert einen bestehenden Vertrag nach seiner ID.
    Argumente:
        contract_id (int): ID des Vertrags
        contract_data (ContractUpdate): Aktualisierte Vertragsdaten
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        ContractResponse: Aktualisierter Vertrag
    """
    try:
        updated_contract = contract_service.update_contract(contract_id, contract_data)
        if not updated_contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden")
        return updated_contract
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Aktualisieren des Vertrags")
# DELETE /contracts/{contract_id} - Löscht einen Vertrag nach ID
@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contract(
    contract_id: int,
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Löscht einen Vertrag nach seiner ID.
    Argumente:
        contract_id (int): ID des Vertrags
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        None
    """
    try:
        success = contract_service.delete_contract(contract_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Löschen des Vertrags")
# GET /contracts/stats - Ruft Vertragsstatistiken ab
@router.get("/stats", response_model=ContractStats, status_code=status.HTTP_200_OK)
def get_contract_stats(
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Ruft Statistiken über Verträge ab.
    Argumente:
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        ContractStats: Vertragsstatistiken
    """
    try:
        return contract_service.get_contract_stats()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Abrufen der Vertragsstatistiken")
    
@router.get("/search", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
def search_contracts(
    query: str = Query(..., description="Suchbegriff für Titel oder Beschreibung"),
    page: int = Query(1, ge=1, description="Seitennummer"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Durchsucht Verträge basierend auf einem Suchbegriff.
    Argumente:
        query (str): Suchbegriff für Titel oder Beschreibung
        page (int): Seitennummer (Standard: 1)
        per_page (int): Anzahl der Verträge pro Seite (Standard: 10, Max: 100)
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        ContractListResponse: Liste der gefundenen Verträge mit Paginierungsinformationen
    """
    return contract_service.search_contracts(
        query=query,
        page=page,
        per_page=per_page
    )       
@router.get("/active", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
def get_active_contracts(
    page: int = Query(1, ge=1, description="Seitennummer"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Ruft alle aktiven Verträge ab.
    Argumente:
        page (int): Seitennummer (Standard: 1)
        per_page (int): Anzahl der Verträge pro Seite (Standard: 10, Max: 100)
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        ContractListResponse: Liste der aktiven Verträge mit Paginierungsinformationen
    """
    return contract_service.get_active_contracts(
        page=page,
        per_page=per_page
    )       
# GET /contracts/expiring - Verträge abrufen, die in den nächsten X Tagen ablaufen
@router.get("/expiring", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
def get_expiring_contracts(
    days: int = Query(30, ge=1, le=365, description="Anzahl der Tage bis zum Ablauf / Número de dias até o vencimento"),
    page: int = Query(1, ge=1, description="Seitennummer / Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite / Número de contratos por página"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Verträge abrufen, die in den nächsten X Tagen ablaufen
    """
    return contract_service.get_contracts_expiring_within(
        days=days,
        page=page,
        per_page=per_page
    )

# GET /contracts/expired - Abgelaufene Verträge abrufen
@router.get("/expired", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
def get_expired_contracts(
    page: int = Query(1, ge=1, description="Seitennummer / Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite / Número de contratos por página"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Alle abgelaufenen Verträge abrufen
    """
    return contract_service.get_expired_contracts(
        page=page,
        per_page=per_page
    )
@router.get("/by-client", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
def get_contracts_by_client(
    client_name: str = Query(..., description="Name des Kunden / Nome do cliente"),
    page: int = Query(1, ge=1, description="Seitennummer / Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite / Número de contratos por página"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Verträge nach Kundenname abrufen
    """
    return contract_service.get_contracts_by_client(
        client_name=client_name,
        page=page,
        per_page=per_page
    )       
