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
import re
import os
import asyncio
import hashlib
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, status, Form
from sqlalchemy.ext.asyncio import AsyncSession  

from app.core.database import get_db
from app.schemas.contract import (
    ContractCreate,
    ContractUpdate,
    ContractResponse,
    ContractListResponse,
    ContractStats,
)
from app.schemas.approval import ApprovalRequest, RejectionRequest
from app.services.contract_service import ContractService
from app.utils.document_generator import render_docx_bytes, _convert_docx_bytes_to_pdf_bytes
from fastapi.responses import StreamingResponse, Response
from fastapi import UploadFile, File
from app.core.config import settings
from pathlib import Path
from fastapi import Depends
from app.core.security import get_current_active_user
from app.models.user import User
from app.models.contract import Contract, ContractStatus
from app.core.permissions import require_view_original
from sqlalchemy import select

# Hilfsfunktionen / Funções auxiliares

def move_temp_to_persisted_contract(temp_file_path: str, contract_id: int, original_filename: str) -> str:
    """
    Verschiebt temporäre Datei in organisierte permanente Struktur
    Move arquivo temporário para estrutura permanente organizada por contrato
    """
    if not temp_file_path or not os.path.exists(temp_file_path):
        raise ValueError("Temporäre Datei nicht gefunden / Arquivo temporário não encontrado")
    
    # Verzeichnis für diesen Vertrag erstellen / Criar diretório para este contrato  
    persisted_dir = os.path.join(settings.UPLOAD_DIR, "contracts", "persisted")
    contract_dir = os.path.join(persisted_dir, f"contract_{contract_id}")
    os.makedirs(contract_dir, exist_ok=True)
    
    # Zieldatei: immer "original.pdf" / Arquivo destino: sempre "original.pdf"
    target_path = os.path.join(contract_dir, "original.pdf")
    
    # Datei verschieben / Mover arquivo
    import shutil
    shutil.move(temp_file_path, target_path)
    
    return target_path

def get_contract_pdf_path(contract_id: int) -> Optional[str]:
    """
    Lokalisiert PDF-Datei für einen Vertrag in neuer oder alter Struktur
    Localiza arquivo PDF para um contrato em estrutura nova ou antiga
    """
    # Neue Struktur: uploads/contracts/persisted/contract_{id}/original.pdf
    new_path = os.path.join(settings.UPLOAD_DIR, "contracts", "persisted", f"contract_{contract_id}", "original.pdf")
    if os.path.exists(new_path):
        return new_path
    
    # Fallback: alte Struktur (für Migration) - suche pattern *_{contract_id}_*
    old_dir = os.path.join(settings.UPLOAD_DIR, "contracts")
    if os.path.exists(old_dir):
        import glob
        pattern = os.path.join(old_dir, f"*_{contract_id}_*.pdf")
        matches = glob.glob(pattern)
        if matches:
            return matches[0]  # Erstes Match zurückgeben
    
    return None

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
    # 🐛 DEBUG: Log dos parâmetros recebidos
    print(f"📥 [BACKEND] Parâmetros recebidos: page={page}, per_page={per_page}, status={status}, contract_type={contract_type}, search={search}, sort_by={sort_by}, sort_order={sort_order}")
    
    result = await contract_service.list_contracts(
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
    
    # 🐛 DEBUG: Log da resposta que será enviada
    print(f"📤 [BACKEND] Resposta: total={result.total}, contracts={len(result.contracts)}, page={result.page}, per_page={result.per_page}")
    
    return result   
# POST /contracts/ - Erstellt einen neuen Vertrag
@router.post("/", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract(    
    contract: ContractCreate,
    current_user: User = Depends(get_current_active_user),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Erstellt einen neuen Vertrag.
    Argumente:
        contract (ContractCreate): Vertragsdaten
        current_user (User): Aktueller authentifizierter Benutzer
        contract_service (ContractService): Dienst für Vertragsoperationen
    Rückgabe:
        ContractResponse: Erstellter Vertrag
    """
    try:
        created = await contract_service.create_contract(contract, current_user.id)

        # Wenn Extraktions-Metadaten vorhanden sind, automatisch die Datei anhängen und verschieben
        try:
            meta = getattr(contract, "extraction_metadata", None)
            if meta and hasattr(meta, 'temp_file_path') and meta.temp_file_path:
                # Datei von temp/ zu persisted/contract_{id}/ verschieben
                final_path = move_temp_to_persisted_contract(
                    meta.temp_file_path, 
                    created.id, 
                    meta.original_file_name or "original.pdf"
                )
                filename = meta.original_file_name or "original.pdf"
                file_sha256 = meta.original_file_sha256 or ""
                ocr_text = getattr(meta, 'ocr_text', "") or ""
                ocr_sha256 = meta.ocr_text_sha256 or ""
                
                # Attachment-Operation mit finalem Pfad
                await contract_service.attach_original_pdf(created.id, final_path, filename, file_sha256, ocr_text, ocr_sha256)
            elif meta and (meta.original_file_storage_name or meta.original_file_name):
                # Fallback: alte Struktur (für Kompatibilität)
                storage_name = meta.original_file_storage_name or meta.original_file_name
                file_path = os.path.join(settings.UPLOAD_DIR, "contracts", storage_name)
                filename = meta.original_file_name or storage_name
                file_sha256 = meta.original_file_sha256 or ""
                ocr_text = getattr(meta, 'ocr_text', "") or ""
                ocr_sha256 = meta.ocr_text_sha256 or ""
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

# POST /contracts/with-upload - Erstellt einen neuen Vertrag mit PDF-Upload
# POST /contracts/with-upload - Cria novo contrato com upload de PDF
@router.post("/with-upload", response_model=ContractResponse, status_code=status.HTTP_201_CREATED)
async def create_contract_with_upload(
    # Campos obrigatórios / Pflichtfelder
    title: str = Form(..., min_length=2, max_length=200, description="Vertragstitel / Título"),
    client_name: str = Form(..., min_length=2, max_length=200, description="Kundenname / Nome do cliente"),
    start_date: date = Form(..., description="Startdatum / Data início"),
    
    # Campos opcionais / Optionale Felder
    description: Optional[str] = Form(None, max_length=1000),
    contract_type: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    end_date: Optional[date] = Form(None),
    renewal_date: Optional[date] = Form(None),
    value: Optional[Decimal] = Form(None),
    currency: Optional[str] = Form(None),
    payment_frequency: Optional[str] = Form(None),
    payment_custom_years: Optional[int] = Form(None),
    
    company_name: Optional[str] = Form(None),
    legal_form: Optional[str] = Form(None),
    client_document: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    client_phone: Optional[str] = Form(None),
    client_address: Optional[str] = Form(None),
    
    department: Optional[str] = Form(None),
    team: Optional[str] = Form(None),
    responsible_user_id: Optional[int] = Form(None),
    
    terms_and_conditions: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    
    # PDF (opcional) / PDF (optional)
    pdf_file: Optional[UploadFile] = File(None),
    
    # Dependencies
    current_user: User = Depends(get_current_active_user),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Cria contrato com upload de PDF em uma única requisição.
    Creates contract with PDF upload in a single request.
    
    Vantagens / Advantages:
    - Upload único / Single upload
    - Validação unificada / Unified validation
    - Transação atômica / Atomic transaction
    """
    try:
        # 1. Validar PDF se existe / Validate PDF if exists
        if pdf_file and pdf_file.filename:
            if not pdf_file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail="Apenas arquivos PDF são permitidos / Only PDF files allowed"
                )
            
            # Ler conteúdo para validar tamanho / Read content to validate size
            content = await pdf_file.read()
            if len(content) > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=413, 
                    detail="Arquivo muito grande. Máximo 10MB / File too large. Max 10MB"
                )
            await pdf_file.seek(0)  # Reset para reler / Reset to re-read
        
        # 2. Criar objeto ContractCreate para usar validações existentes
        # Create ContractCreate object to use existing validations
        print(f"🔍 DEBUG - Dados recebidos no endpoint:")
        print(f"  - department: {department}")
        print(f"  - team: {team}")
        print(f"  - responsible_user_id: {responsible_user_id}")
        print(f"  - company_name: {company_name}")
        
        contract_data = ContractCreate(
            title=title,
            client_name=client_name,
            start_date=start_date,
            description=description,
            contract_type=contract_type,
            status=status,
            end_date=end_date,
            renewal_date=renewal_date,
            value=value,
            currency=currency or "EUR",
            payment_frequency=payment_frequency,
            payment_custom_years=payment_custom_years,
            company_name=company_name,
            legal_form=legal_form,
            client_document=client_document,
            client_email=client_email,
            client_phone=client_phone,
            client_address=client_address,
            department=department,
            team=team,
            responsible_user_id=responsible_user_id,
            terms_and_conditions=terms_and_conditions,
            notes=notes
        ) # type: ignore
        
        print(f"📦 DEBUG - ContractCreate object:")
        print(f"  - department: {contract_data.department}")
        print(f"  - team: {contract_data.team}")
        print(f"  - responsible_user_id: {contract_data.responsible_user_id}")
        print(f"  - company_name: {contract_data.company_name}")
        
        # 3. Criar contrato (reutilizar lógica existente)
        # Create contract (reuse existing logic)
        created = await contract_service.create_contract(contract_data, current_user.id)
        
        # 4. Se tem PDF, salvar e anexar / If has PDF, save and attach
        if pdf_file and pdf_file.filename:
            # Criar diretório / Create directory
            contract_dir = os.path.join(
                settings.UPLOAD_DIR, 
                "contracts", 
                "persisted", 
                f"contract_{created.id}"
            )
            os.makedirs(contract_dir, exist_ok=True)
            
            # Salvar PDF / Save PDF
            file_path = os.path.join(contract_dir, "original.pdf")
            content = await pdf_file.read()
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Calcular hash / Calculate hash
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Anexar ao contrato / Attach to contract
            await contract_service.attach_original_pdf(
                created.id, 
                file_path, 
                pdf_file.filename, 
                file_hash, 
                "",  # ocr_text vazio / empty
                ""   # ocr_sha256 vazio / empty
            )
            
            # Refresh para pegar metadados do PDF / Refresh to get PDF metadata
            updated = await contract_service.get_contract(created.id)
            return updated
        
        return created
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Fehler beim Erstellen des Vertrags / Erro ao criar contrato: {str(e)}"
        )

# ============================================================================
# ENDPOINTS COM CAMINHOS FIXOS (devem vir ANTES de /{contract_id})
# ENDPOINTS MIT FESTEN PFADEN (müssen VOR /{contract_id} kommen)
# ============================================================================

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

# ============================================================================
# ENDPOINTS COM PATH PARAMETERS (devem vir DEPOIS de caminhos fixos)
# ENDPOINTS MIT PATH-PARAMETERN (müssen NACH festen Pfaden kommen)
# ============================================================================

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

# PUT /contracts/{contract_id}/with-upload - Atualiza contrato com PDF
# PUT /contracts/{contract_id}/with-upload - Aktualisiert Vertrag mit PDF
@router.put("/{contract_id}/with-upload", response_model=ContractResponse, status_code=status.HTTP_200_OK)
async def update_contract_with_upload(
    contract_id: int,
    
    # Todos os campos são opcionais / Alle Felder sind optional
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    contract_type: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    
    value: Optional[Decimal] = Form(None),
    currency: Optional[str] = Form(None),
    payment_frequency: Optional[str] = Form(None),
    payment_custom_years: Optional[int] = Form(None),
    
    start_date: Optional[date] = Form(None),
    end_date: Optional[date] = Form(None),
    renewal_date: Optional[date] = Form(None),
    
    client_name: Optional[str] = Form(None),
    company_name: Optional[str] = Form(None),
    legal_form: Optional[str] = Form(None),
    client_document: Optional[str] = Form(None),
    client_email: Optional[str] = Form(None),
    client_phone: Optional[str] = Form(None),
    client_address: Optional[str] = Form(None),
    
    department: Optional[str] = Form(None),
    team: Optional[str] = Form(None),
    responsible_user_id: Optional[int] = Form(None),
    
    terms_and_conditions: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    
    # PDF (opcional) / PDF (optional)
    pdf_file: Optional[UploadFile] = File(None),
    
    # Dependencies
    current_user: User = Depends(get_current_active_user),
    contract_service: ContractService = Depends(get_contract_service)
):
    """
    Atualiza contrato com possibilidade de substituir PDF.
    Updates contract with option to replace PDF.
    
    Comportamento / Behavior:
    - Se pdf_file fornecido → substitui PDF antigo / If pdf_file provided → replaces old PDF
    - Se pdf_file None → mantém PDF existente / If pdf_file None → keeps existing PDF
    """
    try:
        # 1. Validar PDF se existe / Validate PDF if exists
        if pdf_file and pdf_file.filename:
            if not pdf_file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400, 
                    detail="Apenas arquivos PDF são permitidos / Only PDF files allowed"
                )
            
            content = await pdf_file.read()
            if len(content) > 10 * 1024 * 1024:  # 10MB
                raise HTTPException(
                    status_code=413, 
                    detail="Arquivo muito grande. Máximo 10MB / File too large. Max 10MB"
                )
            await pdf_file.seek(0)
        
        # 2. Criar objeto ContractUpdate com campos fornecidos
        # Create ContractUpdate object with provided fields
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if description is not None:
            update_data['description'] = description
        if contract_type is not None:
            update_data['contract_type'] = contract_type
        if status is not None:
            update_data['status'] = status
        if value is not None:
            update_data['value'] = value
        if currency is not None:
            update_data['currency'] = currency
        if payment_frequency is not None:
            update_data['payment_frequency'] = payment_frequency
        if payment_custom_years is not None:
            update_data['payment_custom_years'] = payment_custom_years
        if start_date is not None:
            update_data['start_date'] = start_date
        if end_date is not None:
            update_data['end_date'] = end_date
        if renewal_date is not None:
            update_data['renewal_date'] = renewal_date
        if client_name is not None:
            update_data['client_name'] = client_name
        if company_name is not None:
            update_data['company_name'] = company_name
        if legal_form is not None:
            update_data['legal_form'] = legal_form
        if client_document is not None:
            update_data['client_document'] = client_document
        if client_email is not None:
            update_data['client_email'] = client_email
        if client_phone is not None:
            update_data['client_phone'] = client_phone
        if client_address is not None:
            update_data['client_address'] = client_address
        if department is not None:
            update_data['department'] = department
        if team is not None:
            update_data['team'] = team
        if responsible_user_id is not None:
            update_data['responsible_user_id'] = responsible_user_id
        if terms_and_conditions is not None:
            update_data['terms_and_conditions'] = terms_and_conditions
        if notes is not None:
            update_data['notes'] = notes
        
        contract_update = ContractUpdate(**update_data)
        
        # 3. Atualizar contrato / Update contract
        updated = await contract_service.update_contract(contract_id, contract_update)
        if not updated:
            raise HTTPException(status_code=404, detail="Vertrag nicht gefunden / Contrato não encontrado")
        
        # 4. Se tem PDF, substituir / If has PDF, replace
        if pdf_file and pdf_file.filename:
            # Remover PDF antigo se existe / Remove old PDF if exists
            old_pdf_path = get_contract_pdf_path(contract_id)
            if old_pdf_path and os.path.exists(old_pdf_path):
                try:
                    os.remove(old_pdf_path)
                except Exception as e:
                    # Log mas não falha / Log but don't fail
                    print(f"Aviso: não foi possível remover PDF antigo: {e}")
            
            # Criar diretório / Create directory
            contract_dir = os.path.join(
                settings.UPLOAD_DIR, 
                "contracts", 
                "persisted", 
                f"contract_{contract_id}"
            )
            os.makedirs(contract_dir, exist_ok=True)
            
            # Salvar novo PDF / Save new PDF
            file_path = os.path.join(contract_dir, "original.pdf")
            content = await pdf_file.read()
            
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Calcular hash / Calculate hash
            file_hash = hashlib.sha256(content).hexdigest()
            
            # Anexar ao contrato / Attach to contract
            await contract_service.attach_original_pdf(
                contract_id, 
                file_path, 
                pdf_file.filename, 
                file_hash, 
                "",  # ocr_text vazio / empty
                ""   # ocr_sha256 vazio / empty
            )
            
            # Refresh para pegar metadados do PDF / Refresh to get PDF metadata
            updated = await contract_service.get_contract(contract_id)
        
        return updated
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Fehler beim Aktualisieren / Erro ao atualizar: {str(e)}"
        )

# DELETE /contracts/{contract_id} - Löscht einen Vertrag nach ID
@router.delete("/{contract_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contract(
    contract_id: int,
    current_user: User = Depends(get_current_active_user),
    contract_service: ContractService = Depends(get_contract_service),
    db: AsyncSession = Depends(get_db)
):
    """
    Löscht einen Vertrag nach seiner ID, mit checagem de permissão.
    """
    from app.core.permissions import can_delete_contract
    from sqlalchemy.exc import IntegrityError
    # Buscar contrato
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden / Contrato não encontrado")
    # Checar permissão
    if not can_delete_contract(current_user, contract):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para deletar este contrato.")
    try:
        success = await contract_service.delete_contract(contract_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vertrag nicht gefunden / Contrato não encontrado")
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não é possível deletar: existem dependências vinculadas (ex: alertas, rent steps, aprovações).")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Fehler beim Löschen des Vertrags: {str(e)}")

# DELETE /contracts/{contract_id}/original - Remove o PDF original do contrato
@router.delete("/{contract_id}/original", status_code=status.HTTP_204_NO_CONTENT)
async def delete_original_pdf(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove o PDF original anexado ao contrato.
    Entfernt die original angehängte PDF vom Vertrag.
    """
    import os
    from sqlalchemy import select, update
    from app.models.contract import Contract
    
    # Buscar contrato
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden / Contrato não encontrado")
    
    if not contract.original_pdf_path:
        raise HTTPException(status_code=404, detail="Kein PDF vorhanden / Nenhum PDF anexado")
    
    # Deletar arquivo físico se existir
    if os.path.exists(contract.original_pdf_path):
        try:
            os.remove(contract.original_pdf_path)
        except Exception as e:
            print(f"Error deleting PDF file: {e}")
    
    # Atualizar registro no banco
    await db.execute(
        update(Contract)
        .where(Contract.id == contract_id)
        .values(
            original_pdf_path=None,
            original_pdf_filename=None,
            original_pdf_sha256=None,
            uploaded_at=None
        )
    )
    await db.commit()
    
    return None


@router.get("/{contract_id}/document", status_code=status.HTTP_200_OK)
async def generate_contract_document(
    contract_id: int,
    format: Optional[str] = Query("pdf", pattern="^(pdf|docx)$", description="Formato do documento: pdf ou docx"),
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
    Lädt die original hochgeladene PDF-Datei herunter (als Attachment).
    Faz download do arquivo PDF original carregado (como anexo).
    Berechtigungsprüfung: ADMIN/MANAGER oder Eigentümer des Vertrags.
    Verificação de permissão: ADMIN/MANAGER ou proprietário do contrato.
    """
    contract = await ContractService(db).get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden")

    # Berechtigung prüfen
    try:
        require_view_original(current_user, contract.created_by)
    except HTTPException:
        raise

    # PDF-Datei mit neuer Suchfunktion lokalisieren
    file_path = get_contract_pdf_path(contract_id)
    
    # Fallback: aus Datenbank gespeicherter Pfad (für Kompatibilität)
    if not file_path:
        db_file_path = getattr(contract, "original_pdf_path", None)
        if db_file_path and os.path.exists(db_file_path):
            file_path = db_file_path
    
    if not file_path:
        raise HTTPException(status_code=404, detail="Original-PDF nicht vorhanden")

    def iterfile():
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b''):
                yield chunk

    # Filename com suporte a UTF-8 (caracteres alemães: ä, ö, ü, ß)
    # Filename with UTF-8 support (German characters: ä, ö, ü, ß)
    filename = contract.original_pdf_filename or f"contract_{contract_id}.pdf"
    
    # RFC 5987: filename* para suporte UTF-8
    # Manter filename simples para browsers antigos + filename* para modernos
    safe_filename_ascii = re.sub(r'[^\w\s.-]', '_', filename)  # Fallback ASCII
    safe_filename_utf8 = quote(filename.encode('utf-8'))  # UTF-8 encoding
    
    headers = {
        "Content-Disposition": (
            f'attachment; '
            f'filename="{safe_filename_ascii}"; '
            f"filename*=UTF-8''{safe_filename_utf8}"
        ),
        "Content-Type": "application/pdf"
    }
    
    return StreamingResponse(iterfile(), media_type="application/pdf", headers=headers)


@router.get("/{contract_id}/view")
async def view_original_pdf(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Zeigt die original hochgeladene PDF-Datei inline im Browser an.
    Exibe o arquivo PDF original carregado inline no navegador.
    Berechtigungsprüfung: ADMIN/MANAGER oder Eigentümer des Vertrags.
    Verificação de permissão: ADMIN/MANAGER ou proprietário do contrato.
    """
    contract = await ContractService(db).get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Vertrag nicht gefunden / Contrato não encontrado")

    # Berechtigung prüfen / Verificar permissão
    try:
        require_view_original(current_user, contract.created_by)
    except HTTPException:
        raise

    # PDF-Datei mit neuer Suchfunktion lokalisieren / Localizar arquivo PDF com nova função de busca
    file_path = get_contract_pdf_path(contract_id)
    
    # Fallback: aus Datenbank gespeicherter Pfad (für Kompatibilität)
    # Fallback: caminho salvo no banco de dados (para compatibilidade)
    if not file_path:
        db_file_path = getattr(contract, "original_pdf_path", None)
        if db_file_path and os.path.exists(db_file_path):
            file_path = db_file_path
    
    if not file_path:
        raise HTTPException(status_code=404, detail="Original-PDF nicht vorhanden / PDF original não disponível")

    def iterfile():
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b''):
                yield chunk

    # Filename com suporte a UTF-8 (caracteres alemães: ä, ö, ü, ß)
    # Filename with UTF-8 support (German characters: ä, ö, ü, ß)
    filename = getattr(contract, "original_pdf_filename", None) or f"contract_{contract_id}.pdf"
    
    # RFC 5987: filename* para suporte UTF-8
    safe_filename_ascii = re.sub(r'[^\w\s.-]', '_', filename)  # Fallback ASCII
    safe_filename_utf8 = quote(filename.encode('utf-8'))  # UTF-8 encoding
    
    # IMPORTANTE: usar APENAS inline, sem filename, para forçar visualização no navegador
    # IMPORTANT: use ONLY inline, without filename, to force browser viewing
    headers = {
        "Content-Disposition": "inline",
        "Content-Type": "application/pdf",
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-Content-Type-Options": "nosniff"
    }
    
    return StreamingResponse(
        iterfile(), 
        media_type="application/pdf", 
        headers=headers
    )


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


@router.post("/{contract_id}/upload-pdf", status_code=status.HTTP_200_OK)
async def upload_original_pdf(
    contract_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Anexar PDF original a um contrato existente
    Original-PDF an bestehenden Vertrag anhängen
    """
    # Verificar se contrato existe
    contract_service = ContractService(db)
    contract = await contract_service.get_contract(contract_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado / Vertrag nicht gefunden")
    
    # Validar arquivo
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF / Nur PDF-Dateien")
    
    # Ler conteúdo
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=413, detail="Arquivo muito grande / Datei zu groß (max 10MB)")
    
    # Criar diretório para este contrato
    contract_dir = os.path.join(settings.UPLOAD_DIR, "contracts", "persisted", f"contract_{contract_id}")
    os.makedirs(contract_dir, exist_ok=True)
    
    # Salvar como original.pdf
    file_path = os.path.join(contract_dir, "original.pdf")
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Calcular hash
    import hashlib
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Anexar ao contrato
    relative_path = os.path.join("uploads", "contracts", "persisted", f"contract_{contract_id}", "original.pdf")
    await contract_service.attach_original_pdf(
        contract_id, 
        file_path, 
        file.filename, 
        file_hash, 
        "", # ocr_text vazio
        ""  # ocr_sha256 vazio
    )
    
    return {
        "message": "PDF anexado com sucesso / PDF erfolgreich angehängt",
        "filename": file.filename,
        "path": relative_path
    }


# ============================================================================
# ENDPOINTS DE APROVAÇÃO / GENEHMIGUNGSENDPUNKTE
# ============================================================================

@router.post("/{contract_id}/approve", status_code=status.HTTP_200_OK)
async def approve_contract(
    contract_id: int,
    approval_request: "ApprovalRequest",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Aprova um contrato / Vertrag genehmigen
    
    Logik / Lógica:
    - Verifica permissões do usuário / Überprüft Benutzerberechtigungen
    - Cria registro de aprovação / Erstellt Genehmigungsdatensatz
    - Atualiza status do contrato para ACTIVE / Aktualisiert Vertragsstatus auf ACTIVE
    
    Requires / Erfordert:
    - Access Level 3+ (DEPARTMENT_USER ou superior)
    - Permissão can_approve_contract()
    """
    from app.schemas.approval import ApprovalRequest, ApprovalActionResponse, ApprovalResponse
    from app.models.contract_approval import ContractApproval
    from sqlalchemy import select
    from app.core.permissions import can_approve_contract
    
    # Buscar contrato / Vertrag suchen
    contract_service = ContractService(db)
    contract_response = await contract_service.get_contract(contract_id)
    
    if not contract_response:
        raise HTTPException(status_code=404, detail="Contrato não encontrado / Vertrag nicht gefunden")
    
    # Buscar model real para verificação de permissões
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado / Vertrag nicht gefunden")
    
    # Verificar permissão / Berechtigung prüfen
    if not can_approve_contract(current_user, contract):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para aprovar este contrato / Keine Berechtigung, diesen Vertrag zu genehmigen"
        )
    
    # Verificar se já existe aprovação pendente deste usuário
    existing_result = await db.execute(
        select(ContractApproval).where(
            ContractApproval.contract_id == contract_id,
            ContractApproval.approver_id == current_user.id,
            ContractApproval.status == "pending"
        )
    )
    existing_approval = existing_result.scalar_one_or_none()
    
    if existing_approval:
        # Atualizar aprovação existente
        existing_approval.approve(approval_request.comments)
        await db.commit()
        await db.refresh(existing_approval)
        approval = existing_approval
    else:
        # Criar nova aprovação
        approval = ContractApproval(
            contract_id=contract_id,
            approver_id=current_user.id,
            required_approval_level=current_user.access_level,
            status="approved"
        )
        approval.approve(approval_request.comments)
        db.add(approval)
        await db.commit()
        await db.refresh(approval)
    
    # Atualizar status do contrato para ACTIVE
    if contract.status == ContractStatus.PENDING_APPROVAL:
        contract.status = ContractStatus.ACTIVE
        await db.commit()
        await db.refresh(contract)
    
    return ApprovalActionResponse(
        success=True,
        message="Contrato aprovado com sucesso / Vertrag erfolgreich genehmigt",
        approval=ApprovalResponse.model_validate(approval),
        contract_status=contract.status.value
    )


@router.post("/{contract_id}/reject", status_code=status.HTTP_200_OK)
async def reject_contract(
    contract_id: int,
    rejection_request: "RejectionRequest",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Rejeita um contrato / Vertrag ablehnen
    
    Logik / Lógica:
    - Verifica permissões do usuário / Überprüft Benutzerberechtigungen
    - Cria registro de rejeição / Erstellt Ablehnungsdatensatz
    - Atualiza status do contrato para DRAFT / Aktualisiert Vertragsstatus auf DRAFT
    
    Requires / Erfordert:
    - Access Level 3+ (DEPARTMENT_USER ou superior)
    - Permissão can_approve_contract()
    """
    from app.schemas.approval import RejectionRequest, ApprovalActionResponse, ApprovalResponse
    from app.models.contract_approval import ContractApproval
    from sqlalchemy import select
    from app.core.permissions import can_approve_contract
    
    # Buscar contrato
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado / Vertrag nicht gefunden")
    
    # Verificar permissão
    if not can_approve_contract(current_user, contract):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para rejeitar este contrato / Keine Berechtigung, diesen Vertrag abzulehnen"
        )
    
    # Verificar se já existe aprovação pendente deste usuário
    existing_result = await db.execute(
        select(ContractApproval).where(
            ContractApproval.contract_id == contract_id,
            ContractApproval.approver_id == current_user.id,
            ContractApproval.status == "pending"
        )
    )
    existing_approval = existing_result.scalar_one_or_none()
    
    if existing_approval:
        # Atualizar aprovação existente
        existing_approval.reject(rejection_request.reason, rejection_request.comments)
        await db.commit()
        await db.refresh(existing_approval)
        approval = existing_approval
    else:
        # Criar nova rejeição
        approval = ContractApproval(
            contract_id=contract_id,
            approver_id=current_user.id,
            required_approval_level=current_user.access_level,
            status="rejected"
        )
        approval.reject(rejection_request.reason, rejection_request.comments)
        db.add(approval)
        await db.commit()
        await db.refresh(approval)
    
    # Atualizar status do contrato para DRAFT
    if contract.status == ContractStatus.PENDING_APPROVAL:
        contract.status = ContractStatus.DRAFT
        await db.commit()
        await db.refresh(contract)
    
    return ApprovalActionResponse(
        success=True,
        message="Contrato rejeitado / Vertrag abgelehnt",
        approval=ApprovalResponse.model_validate(approval),
        contract_status=contract.status.value
    )


@router.get("/{contract_id}/approval-history")
async def get_approval_history(
    contract_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Obtém histórico de aprovações de um contrato / Ruft Genehmigungsverlauf eines Vertrags ab
    
    Returns / Retorna:
    - Lista de todas as aprovações/rejeições
    - Liste aller Genehmigungen/Ablehnungen
    """
    from app.schemas.approval import ApprovalHistoryResponse, ApprovalWithApprover
    from app.models.contract_approval import ContractApproval
    from sqlalchemy import select
    from app.core.permissions import can_view_contract
    
    # Buscar contrato
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato não encontrado / Vertrag nicht gefunden")
    
    # Verificar permissão de visualização
    if not can_view_contract(current_user, contract):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sem permissão para ver este contrato / Keine Berechtigung, diesen Vertrag zu sehen"
        )
    
    # Buscar todas as aprovações
    approvals_result = await db.execute(
        select(ContractApproval, User).join(
            User, ContractApproval.approver_id == User.id
        ).where(
            ContractApproval.contract_id == contract_id
        ).order_by(ContractApproval.created_at.desc())
    )
    
    approvals_with_users = approvals_result.all()
    
    # Montar response com informações do aprovador
    approvals_list = []
    pending_count = 0
    
    for approval, approver in approvals_with_users:
        approval_dict = ApprovalWithApprover.model_validate(approval).model_dump()
        approval_dict['approver_name'] = approver.name
        approval_dict['approver_email'] = approver.email
        approvals_list.append(ApprovalWithApprover(**approval_dict))
        
        if approval.status.value == "pending":
            pending_count += 1
    
    return ApprovalHistoryResponse(
        contract_id=contract_id,
        contract_title=contract.title,
        total_approvals=len(approvals_list),
        pending_approvals=pending_count,
        approvals=approvals_list
    )

