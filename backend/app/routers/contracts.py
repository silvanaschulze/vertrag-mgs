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
from sqlalchemy.ext.asyncio import AsyncSession  

from app.core.database import get_db
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ContractStats,
)
import os
import asyncio
from app.services.contract_service import ContractService
from app.utils.document_generator import render_docx_bytes, _convert_docx_bytes_to_pdf_bytes
from fastapi.responses import StreamingResponse, Response
from fastapi import UploadFile, File
from app.core.config import settings
from pathlib import Path
from fastapi import Depends
from app.core.security import get_current_active_user
from app.models.user import User
from app.core.permissions import require_view_original

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
def get_contract_service(db: AsyncSession = Depends(get_db)) -> ContractService:
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
async def list_contracts(
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
    return await contract_service.list_contracts(
        skip=(page - 1) * per_page,
        limit=per_page,
        filters={
            'status': status,
            'contract_type': contract_type
        } if status or contract_type else None,
        search=search,
    sort_by=sort_by or "created_at",
    sort_order=sort_order or "desc"
    )   
# POST /contracts/ - Erstellt einen neuen Vertrag
@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(    
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
        created = await contract_service.create_contract(contract, created_by)

        # Wenn Extraktions-Metadaten vorhanden sind, automatisch die Datei anhängen
        try:
            meta = getattr(contract, "extraction_metadata", None)
            if meta and (meta.original_file_storage_name or meta.original_file_name):
                storage_name = meta.original_file_storage_name or meta.original_file_name
                # Pfad zum Upload-Ordner: settings.UPLOAD_DIR/contracts
                file_path = os.path.join(settings.UPLOAD_DIR, "contracts", storage_name)
                filename = meta.original_file_name or storage_name
                file_sha256 = meta.original_file_sha256 or ""
                ocr_text = meta.ocr_text or ""
                ocr_sha256 = meta.ocr_text_sha256 or ""
                # Versuche die Attachment-Operation; Fehler hier sollen den Erstellungsfluss
                # nicht komplett abbrechen (aber werden geloggt und als 500 zurückgegeben).
                await contract_service.attach_original_pdf(created.id, file_path, filename, file_sha256, ocr_text, ocr_sha256)
        except Exception as attach_err:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Fehler beim Anhängen der Original-PDF: {str(attach_err)}")

        return created
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Erstellen des Vertrags")

# GET /contracts/{contract_id} - Ruft einen Vertrag nach ID ab
@router.get("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
async def get_contract(   
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
    contract = await contract_service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden")
    return contract
# PUT /contracts/{contract_id} - Aktualisiert einen Vertrag nach ID
@router.put("/{contract_id}", response_model=ContractResponse, status_code=status.HTTP_200_OK)
async def update_contract(
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
        updated_contract = await contract_service.update_contract(contract_id, contract_data)
        if not updated_contract:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden")
        return updated_contract
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Aktualisieren des Vertrags")
# DELETE /contracts/{contract_id} - Löscht einen Vertrag nach ID
@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
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
        success = await contract_service.delete_contract(contract_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Löschen des Vertrags")
# GET /contracts/stats - Ruft Vertragsstatistiken ab
@router.get("/stats", response_model=ContractStats, status_code=status.HTTP_200_OK)
async def get_contract_stats(
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
        return await contract_service.get_contract_stats()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Fehler beim Abrufen der Vertragsstatistiken")
    
@router.get("/search", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
async def search_contracts(
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
    return await contract_service.search_contracts(
        query=query,
        skip=(page - 1) * per_page,
        limit=per_page
    )       
@router.get("/active", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
async def get_active_contracts(
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
    return await contract_service.get_active_contracts(
        skip=(page - 1) * per_page,
        limit=per_page
    )       
# GET /contracts/expiring - Verträge abrufen, die in den nächsten X Tagen ablaufen
@router.get("/expiring", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
async def get_expiring_contracts(
    days: int = Query(30, ge=1, le=365, description="Anzahl der Tage bis zum Ablauf / Número de dias até o vencimento"),
    page: int = Query(1, ge=1, description="Seitennummer / Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite / Número de contratos por página"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Verträge abrufen, die in den nächsten X Tagen ablaufen
    """
    return await contract_service.get_contracts_expiring_within(
        days=days,
        skip=(page - 1) * per_page,
        limit=per_page
    )

# GET /contracts/expired - Abgelaufene Verträge abrufen
@router.get("/expired", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
async def get_expired_contracts(
    page: int = Query(1, ge=1, description="Seitennummer / Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite / Número de contratos por página"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Alle abgelaufenen Verträge abrufen
    """
    return await contract_service.get_expired_contracts(
        skip=(page - 1) * per_page,
        limit=per_page
    )


@router.get("/{contract_id}/document", status_code=status.HTTP_200_OK)
async def generate_contract_document(
    contract_id: int,
    format: Optional[str] = Query("pdf", regex="^(pdf|docx)$", description="Formato do documento: pdf ou docx"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Erzeugt und liefert das Vertragsdokument (DOCX oder PDF).
    - Rendert ein .docx-Template mit den Vertragsdaten
    - Konvertiert zu PDF mittels LibreOffice (`soffice`) falls gewünscht und verfügbar
    """
    contract = await contract_service.get_contract(contract_id)
    if not contract:
        # Vertrag nicht gefunden / Contrato não encontrado
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden / Contrato não encontrado")

    # Preparar dados para template — usar model_dump para Pydantic
    try:
        data = contract.model_dump() if hasattr(contract, "model_dump") else dict(contract)
    except Exception:
        # Fallback: einfache Konvertierung zu dict
        data = dict(contract)

    # Determinar caminho do template — permitir que haja um template por tipo/empresa
    template_path = f"templates/contract_template.docx"
    if not os.path.exists(template_path):
        # Template fehlt / Template não encontrado
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Template nicht gefunden / Template não encontrado")

    # Gerar bytes do docx em thread para não bloquear
    docx_bytes = await asyncio.to_thread(render_docx_bytes, template_path, data)

    if format == "docx":
        return Response(content=docx_bytes, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f"attachment; filename=contract_{contract_id}.docx"})

    # se PDF solicitado, tentar converter em thread (blocking)
    pdf_bytes = await asyncio.to_thread(_convert_docx_bytes_to_pdf_bytes, docx_bytes)
    if pdf_bytes:
        return Response(content=pdf_bytes, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=contract_{contract_id}.pdf"})

    # fallback: retornar docx com aviso
    return Response(content=docx_bytes, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", headers={"Content-Disposition": f"attachment; filename=contract_{contract_id}.docx"})


@router.get("/{contract_id}/original")
async def download_original_pdf(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Liefert die original hochgeladene PDF-Datei (wenn vorhanden).
    Berechtigungsprüfung: ADMIN/MANAGER oder Eigentümer des Vertrags.
    """
    contract = await ContractService(db).get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")

    # Berechtigung prüfen
    try:
        require_view_original(current_user, contract.created_by)
    except HTTPException:
        raise

    file_path = getattr(contract, "original_pdf_path", None)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Original-PDF nicht vorhanden")

    def iterfile():
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b''):
                yield chunk

    filename = contract.original_pdf_filename or f"contract_{contract_id}.pdf"
    return StreamingResponse(iterfile(), media_type="application/pdf", headers={"Content-Disposition": f"inline; filename={filename}"})


@router.post("/{contract_id}/template", status_code=status.HTTP_201_CREATED)
async def upload_contract_template(
    contract_id: int,
    file: UploadFile = File(...),
):
    """Upload de template .docx para um contrato específico.

    Valida extensão .docx e tamanho (usando settings.MAX_FILE_SIZE).
    Salva em uploads/templates/contract_{id}.docx
    """
    filename = file.filename or "template.docx"
    if not filename.lower().endswith(".docx"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apenas arquivos .docx são aceitos / Nur .docx Dateien erlaubt")

    contents = await file.read()
    if len(contents) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo muito grande / Datei zu groß")

    upload_dir = Path(settings.UPLOAD_DIR) / "templates"
    upload_dir.mkdir(parents=True, exist_ok=True)
    target_path = upload_dir / f"contract_{contract_id}.docx"

    # salvar em disco
    with open(target_path, "wb") as f:
        f.write(contents)

    return {"message": "Template uploaded / Template hochgeladen", "path": str(target_path)}
@router.get("/by-client", response_model=ContractListResponse, status_code=status.HTTP_200_OK)
async def get_contracts_by_client(
    client_name: str = Query(..., description="Name des Kunden / Nome do cliente"),
    page: int = Query(1, ge=1, description="Seitennummer / Número da página"),
    per_page: int = Query(10, ge=1, le=100, description="Anzahl der Verträge pro Seite / Número de contratos por página"),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Verträge nach Kundenname abrufen
    """
    return await contract_service.get_contracts_by_client(
        client_name=client_name,
        skip=(page - 1) * per_page,
        limit=per_page
    )       
