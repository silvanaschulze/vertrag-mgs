"""
Vertragsimport-Router für das Vertragsverwaltungssystem
Router de importação de contratos para o Sistema de Gerenciamento de Contratos

Dieses Modul enthält Endpoints für den Import und die Verarbeitung von PDF-Verträgen.
Este módulo contém endpoints para importação e processamento de contratos PDF.
Unterstützt Upload, Extraktion und Validierung von Vertragsdaten.
Suporta upload, extração e validação de dados de contrato.
"""

import asyncio
import os
import time
import logging
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

import hashlib
from datetime import datetime, timezone
from sqlalchemy import select
from app.models.contract import Contract
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.extracted_contract import ExtractionResponse
from app.services.pdf_reader import PDFReaderService

# Logging konfigurieren / Configurar logging
logger = logging.getLogger(__name__)

# Router-Konfiguration
router = APIRouter(
    prefix="/contracts/import",
    tags=["contract-import"],
    responses={
        400: {"description": "Ungültige Anfrage / Solicitação inválida"},
        401: {"description": "Authentifizierung erforderlich / Autenticação necessária"},
        403: {"description": "Unzureichende Berechtigung / Permissão insuficiente"},
        404: {"description": "Datei nicht gefunden / Arquivo não encontrado"},
        413: {"description": "Datei zu groß / Arquivo muito grande"},
        415: {"description": "Ungültiger Dateityp / Tipo de arquivo inválido"},
        500: {"description": "Interner Serverfehler / Erro interno do servidor"}
    }
)

# Globale Konfiguration / Configuração global
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = ['.pdf']
TEMP_UPLOAD_DIR = "uploads/contracts/temp"
PERSISTED_UPLOAD_DIR = "uploads/contracts/persisted"

# Upload-Verzeichnisse erstellen / Criar diretórios de upload
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
os.makedirs(PERSISTED_UPLOAD_DIR, exist_ok=True)

def move_temp_file_to_persisted(temp_file_path: str, contract_id: int, original_filename: str) -> str:
    """
    Verschiebt temporäre Datei in organisierte permanente Struktur
    Move arquivo temporário para estrutura permanente organizada
    
    Args:
        temp_file_path (str): Caminho do arquivo temporário
        contract_id (int): ID do contrato
        original_filename (str): Nome original do arquivo
        
    Returns:
        str: Novo caminho do arquivo permanente
    """
    # Verzeichnis für diesen Vertrag erstellen / Criar diretório para este contrato
    contract_dir = os.path.join(PERSISTED_UPLOAD_DIR, f"contract_{contract_id}")
    os.makedirs(contract_dir, exist_ok=True)
    
    # Zieldatei: immer "original.pdf" / Arquivo destino: sempre "original.pdf"
    target_path = os.path.join(contract_dir, "original.pdf")
    
    # Datei verschieben / Mover arquivo
    import shutil
    shutil.move(temp_file_path, target_path)
    
    logger.info(f"Datei verschoben / Arquivo movido: {temp_file_path} → {target_path}")
    return target_path

@router.post("/pdf", response_model=ExtractionResponse)
async def import_contract_pdf(
    file: UploadFile = File(..., description="PDF-Datei des Vertrags / Arquivo PDF do contrato"),
    extraction_method: str = Form("combined", description="Extraktionsmethode / Método de extração"),
    language: str = Form("de", description="Sprache für OCR / Idioma para OCR"),
    include_ocr: bool = Form(True, description="OCR einschließen / Incluir OCR"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Importiert einen Vertrag aus einer PDF-Datei
    Importa um contrato de um arquivo PDF
    
    Args / Argumentos:
        file (UploadFile): PDF-Datei / Arquivo PDF
        extraction_method (str): Extraktionsmethode / Método de extração
        language (str): Sprache für OCR / Idioma para OCR
        include_ocr (bool): OCR einschließen / Incluir OCR
        db (AsyncSession): Datenbanksitzung / Sessão de banco de dados
        current_user (User): Aktueller Benutzer / Usuário atual
        
    Returns / Retorna:
        ExtractionResponse: Extraktionsergebnis / Resultado da extração
    """
    start_time = time.time()
    file_path = None

    try:
        logger.info(f"PDF-Import gestartet / Importação de PDF iniciada: {file.filename} von Benutzer / do usuário {current_user.id}")
        
        # Datei validieren / Validar arquivo
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kein Dateiname angegeben / Nenhum nome de arquivo fornecido"
            )
        
        # Dateierweiterung prüfen / Verificar extensão do arquivo
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Ungültiger Dateityp / Tipo de arquivo inválido: {file_extension}. Erlaubt / Permitido: {ALLOWED_EXTENSIONS}"
            )
        
        # Dateigröße prüfen / Verificar tamanho do arquivo
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Datei zu groß / Arquivo muito grande: {file_size} Bytes. Maximum / Máximo: {MAX_FILE_SIZE} Bytes"
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Leere Datei / Arquivo vazio"
            )
        
        # Eindeutigen temporären Dateinamen erstellen / Criar nome de arquivo temporário único
        timestamp = int(time.time())
        safe_filename = f"temp_{current_user.id}_{timestamp}_{file.filename}"
        temp_file_path = os.path.join(TEMP_UPLOAD_DIR, safe_filename)
        
        # Datei temporär speichern / Salvar arquivo temporariamente (in Thread auslagern um Event-Loop nicht zu blockieren)
        def _write_file(path: str, content: bytes) -> None:
            with open(path, "wb") as buffer:
                buffer.write(content)

        await asyncio.to_thread(_write_file, temp_file_path, file_content)
        
        logger.info(f"Datei temporär gespeichert / Arquivo salvo temporariamente: {temp_file_path}")

        # PDF-Reader-Service initialisieren / Inicializar serviço de leitura de PDF
        pdf_reader = PDFReaderService()

        # PDF validieren / Validar PDF (executar em thread se for CPU/IO-bound)
        validation_result = await asyncio.to_thread(pdf_reader.validate_pdf, temp_file_path)
        if not validation_result.get('valid'):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ungültige PDF-Datei / Arquivo PDF inválido: {validation_result.get('error', 'Unbekannter Fehler')}"
            )

        # Text extrahieren (möglicherweise IO/CPU-bound) - in Thread auslagern
        if extraction_method == "combined":
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_combined, temp_file_path)
        elif extraction_method == "pdfplumber":
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_with_pdfplumber, temp_file_path)
        elif extraction_method == "pypdf2":
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_with_pypdf2, temp_file_path)
        elif extraction_method == "pymupdf":
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_with_pymupdf, temp_file_path)
        else:
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_combined, temp_file_path)

        if not extraction_result.get('success'):
            try:
                os.remove(temp_file_path)
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Textextraktion fehlgeschlagen / Extração de texto falhou: {extraction_result.get('error', 'Unbekannter Fehler')}"
            )

        # Intelligente Extraktion durchführen / Executar extração inteligente
        intelligent_data = await asyncio.to_thread(pdf_reader.extract_intelligent_data, extraction_result.get('text', ''))

        # --------------------
        # SHA256-Hashes berechnen und Duplikatsprüfung (exakt)
        # --------------------
        file_hash = hashlib.sha256(file_content).hexdigest()
        ocr_text_raw = extraction_result.get('text', '') or ''
        normalized_text = " ".join(ocr_text_raw.lower().split())
        ocr_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

        # Duplikatprüfung: exakter Datei-Hash
        try:
            existing_res = await db.execute(select(Contract).where(Contract.original_pdf_sha256 == file_hash))
            existing_contract = existing_res.scalar_one_or_none()
            if existing_contract:
                # Bei exaktem Duplikat: temporäre Datei entfernen und Fehler melden mit Hinweis auf existierenden Vertrag
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplikat: dieselbe Datei ist bereits im System (contract_id={existing_contract.id})"
                )

            # Duplikatprüfung per OCR-Hash
            existing_res2 = await db.execute(select(Contract).where(Contract.ocr_text_sha256 == ocr_hash))
            existing_contract2 = existing_res2.scalar_one_or_none()
            if existing_contract2:
                try:
                    os.remove(temp_file_path)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplikat: derselbe Vertragsinhalt wurde bereits hochgeladen (contract_id={existing_contract2.id})"
                )
        except HTTPException:
            raise
        except Exception as e:
            # Bei DB-Fehlern nicht automatisch ablehnen – loggen und weiter (vorsichtig)
            logger.warning(f"Warnung während Duplikatprüfung: {e}")

        # ExtractedContractDraft erstellen / Criar ExtractedContractDraft
        from app.schemas.extracted_contract import ExtractedContractDraft, ConfidenceLevel
        extracted_data = ExtractedContractDraft(
            extraction_method=extraction_method,
            raw_text=extraction_result.get('text', ''),
            pdf_metadata=extraction_result.get('metadata', {}),
            title=intelligent_data.get('title'),
            title_confidence=0.8 if intelligent_data.get('title') else 0.0,
            client_name=intelligent_data.get('client_name'),
            client_name_confidence=0.7 if intelligent_data.get('client_name') else 0.0,
            client_email=intelligent_data.get('client_email'),
            client_email_confidence=0.9 if intelligent_data.get('client_email') else 0.0,
            client_phone=intelligent_data.get('client_phone'),
            client_phone_confidence=0.8 if intelligent_data.get('client_phone') else 0.0,
            client_address=intelligent_data.get('client_address'),
            client_address_confidence=0.7 if intelligent_data.get('client_address') else 0.0,
            value=intelligent_data.get('money_values', {}).get('value'),
            value_confidence=intelligent_data.get('money_values', {}).get('confidence', 0.0),
            currency=intelligent_data.get('money_values', {}).get('currency'),
            currency_confidence=0.9 if intelligent_data.get('money_values', {}).get('currency') else 0.0,
            start_date=intelligent_data.get('dates', {}).get('start_date'),
            start_date_confidence=0.7 if intelligent_data.get('dates', {}).get('start_date') else 0.0,
            end_date=intelligent_data.get('dates', {}).get('end_date'),
            end_date_confidence=0.7 if intelligent_data.get('dates', {}).get('end_date') else 0.0,
            renewal_date=intelligent_data.get('dates', {}).get('renewal_date'),
            renewal_date_confidence=0.7 if intelligent_data.get('dates', {}).get('renewal_date') else 0.0,
            terms_and_conditions=intelligent_data.get('terms_and_conditions'),
            terms_and_conditions_confidence=0.6 if intelligent_data.get('terms_and_conditions') else 0.0,
            description=intelligent_data.get('description'),
            description_confidence=0.4 if intelligent_data.get('description') else 0.0,
            raw_text_confidence=0.7,
            client_document=None,
            client_document_confidence=0.0,
            notes=None,
            notes_confidence=0.0,
            overall_confidence=0.0,
            confidence_level=ConfidenceLevel.UNKNOWN,
        )

        # OCR durchführen falls gewünscht / Executar OCR se desejado
        if include_ocr and extraction_result.get('total_chars', 0) < 100:
            logger.info("OCR wird durchgeführt / OCR será executado - wenig Text extrahiert / pouco texto extraído")
            # Hier könnte OCR implementiert werden / Aqui OCR poderia ser implementado

        processing_time = time.time() - start_time
        uploaded_at = datetime.now(timezone.utc)

        logger.info(f"PDF-Import erfolgreich / Importação de PDF bem-sucedida: {processing_time:.2f}s")

        return ExtractionResponse(
            success=True,
            extracted_data=extracted_data,
            processing_time=processing_time,
            file_size=file_size,
            error_message=None,
            # Metadados do arquivo temporário (será movido após criação do contrato)
            original_file_name=file.filename,
            original_file_storage_name=safe_filename,
            original_file_sha256=file_hash,
            ocr_text_sha256=ocr_hash,
            uploaded_at=uploaded_at,
            temp_file_path=temp_file_path  # Caminho temporário para movimentação posterior
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unerwarteter Fehler beim PDF-Import / Erro inesperado na importação de PDF: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interner Serverfehler / Erro interno do servidor: {str(e)}"
        )
    finally:
        # Aufräumen bei Fehlern: nur löschen, wenn nicht erfolgreich persistiert
        # (Wenn oben ein Duplikat erkannt wurde, haben wir die Datei bereits gelöscht.)
        # NOTE: In Erfolgsfall behalten wir die Datei im Upload-Ordner als persistenten Speicher.
        if file_path and os.path.exists(file_path):
            # Wenn ein Fehler aufgetreten ist und wir nicht erfolgreich zurückgegeben haben, entfernen
            # (Die Erfolgs-Rückgabe passiert bereits oben; hier behandeln wir nur Fälle mit Exception)
            # Versuche Entfernung; falls fehlschlägt, loggen
            try:
                # Prüfe ob letzte Operation eine Exception war: im Ausnahmefall bleibt file_path bestehen
                pass
            except Exception:
                logger.debug("Finally block reached (kein automatisches Löschen im Erfolgsfall)")

@router.post("/upload", response_model=ExtractionResponse)
async def upload_contract_with_metadata(
    file: UploadFile = File(..., description="PDF-Datei des Vertrags / Arquivo PDF do contrato"),
    title: Optional[str] = Form(None, description="Vertragstitel / Título do contrato"),
    client_name: Optional[str] = Form(None, description="Kundenname / Nome do cliente"),
    contract_type: Optional[str] = Form(None, description="Vertragstyp / Tipo de contrato"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lädt einen Vertrag mit Metadaten hoch
    Faz upload de um contrato com metadados
    
    Args / Argumentos:
        file (UploadFile): PDF-Datei / Arquivo PDF
        title (Optional[str]): Vertragstitel / Título do contrato
        client_name (Optional[str]): Kundenname / Nome do cliente
        contract_type (Optional[str]): Vertragstyp / Tipo de contrato
        db (AsyncSession): Datenbanksitzung / Sessão de banco de dados
        current_user (User): Aktueller Benutzer / Usuário atual
        
    Returns / Retorna:
        ExtractionResponse: Upload-Ergebnis / Resultado do upload
    """
    start_time = time.time()
    file_path = None

    try:
        logger.info(f"Vertragsupload mit Metadaten gestartet / Upload de contrato com metadados iniciado: {file.filename}")
        
        # Gleiche Validierung wie bei PDF-Import / Mesma validação do import de PDF
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Kein Dateiname angegeben / Nenhum nome de arquivo fornecido"
            )
        
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Ungültiger Dateityp / Tipo de arquivo inválido: {file_extension}"
            )
        
        file_content = await file.read()
        file_size = len(file_content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Datei zu groß / Arquivo muito grande: {file_size} Bytes"
            )
        
        # Datei speichern / Salvar arquivo
        timestamp = int(time.time())
        safe_filename = f"{current_user.id}_{timestamp}_{file.filename}"
        file_path = os.path.join(TEMP_UPLOAD_DIR, safe_filename)
        
        # Salvar arquivo sem bloquear o event loop
        def _write_file(path: str, content: bytes) -> None:
            with open(path, "wb") as buffer:
                buffer.write(content)

        await asyncio.to_thread(_write_file, file_path, file_content)
        
        # PDF verarbeiten / Processar PDF (in thread, evita bloquear o event loop)
        pdf_reader = PDFReaderService()
        extraction_result = await asyncio.to_thread(pdf_reader.extract_text_combined, file_path)

        if not extraction_result or not extraction_result.get('success'):
            try:
                os.remove(file_path)
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Textextraktion fehlgeschlagen / Extração de texto falhou: {extraction_result.get('error') if extraction_result else 'Unknown error'}"
            )

        # Intelligente Extraktion in thread
        intelligent_data = await asyncio.to_thread(pdf_reader.extract_intelligent_data, extraction_result.get('text', ''))
        
        # ExtractedContractDraft erstellen / Criar ExtractedContractDraft
        from app.schemas.extracted_contract import ExtractedContractDraft, ConfidenceLevel
        extracted_data = ExtractedContractDraft(
            extraction_method="combined",
            raw_text=extraction_result['text'],
            pdf_metadata=extraction_result.get('metadata', {}),
            title=intelligent_data.get('title'),
            title_confidence=0.8 if intelligent_data.get('title') else 0.0,
            client_name=intelligent_data.get('client_name'),
            client_name_confidence=0.7 if intelligent_data.get('client_name') else 0.0,
            client_email=intelligent_data.get('client_email'),
            client_email_confidence=0.9 if intelligent_data.get('client_email') else 0.0,
            client_phone=intelligent_data.get('client_phone'),
            client_phone_confidence=0.8 if intelligent_data.get('client_phone') else 0.0,
            client_address=intelligent_data.get('client_address'),
            client_address_confidence=0.7 if intelligent_data.get('client_address') else 0.0,
            value=intelligent_data.get('money_values', {}).get('value'),
            value_confidence=intelligent_data.get('money_values', {}).get('confidence', 0.0),
            currency=intelligent_data.get('money_values', {}).get('currency'),
            currency_confidence=0.9 if intelligent_data.get('money_values', {}).get('currency') else 0.0,
            start_date=intelligent_data.get('dates', {}).get('start_date'),
            start_date_confidence=0.7 if intelligent_data.get('dates', {}).get('start_date') else 0.0,
            end_date=intelligent_data.get('dates', {}).get('end_date'),
            end_date_confidence=0.7 if intelligent_data.get('dates', {}).get('end_date') else 0.0,
            renewal_date=intelligent_data.get('dates', {}).get('renewal_date'),
            renewal_date_confidence=0.7 if intelligent_data.get('dates', {}).get('renewal_date') else 0.0,
            terms_and_conditions=intelligent_data.get('terms_and_conditions'),
            terms_and_conditions_confidence=0.6 if intelligent_data.get('terms_and_conditions') else 0.0,
            description=intelligent_data.get('description'),
            description_confidence=0.4 if intelligent_data.get('description') else 0.0,
            raw_text_confidence=0.7,
            client_document=None,
            client_document_confidence=0.0,
            notes=None,
            notes_confidence=0.0,
            overall_confidence=0.0,
            confidence_level=ConfidenceLevel.UNKNOWN,
        )
        
        # Übergebene Metadaten verwenden / Usar metadados fornecidos
        if title:
            extracted_data.title = title
            extracted_data.title_confidence = 1.0  # Manuell eingegeben / Inserido manualmente
        
        if client_name:
            extracted_data.client_name = client_name
            extracted_data.client_name_confidence = 1.0
        
        if contract_type:
            # Hier könnte eine Validierung des Vertragstyps erfolgen / Aqui poderia ocorrer validação do tipo de contrato
            pass
        
        processing_time = time.time() - start_time
        uploaded_at = datetime.now(timezone.utc)

        # SHA256-Hashes berechnen und Duplikatsprüfung (exakt) für Upload mit Metadaten
        file_hash = hashlib.sha256(file_content).hexdigest()
        ocr_text_raw = extraction_result.get('text', '') or ''
        normalized_text = " ".join(ocr_text_raw.lower().split())
        ocr_hash = hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()

        try:
            existing_res = await db.execute(select(Contract).where(Contract.original_pdf_sha256 == file_hash))
            existing_contract = existing_res.scalar_one_or_none()
            if existing_contract:
                try:
                    os.remove(file_path)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplikat: dieselbe Datei ist bereits im System (contract_id={existing_contract.id})"
                )

            existing_res2 = await db.execute(select(Contract).where(Contract.ocr_text_sha256 == ocr_hash))
            existing_contract2 = existing_res2.scalar_one_or_none()
            if existing_contract2:
                try:
                    os.remove(file_path)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplikat: derselbe Vertragsinhalt wurde bereits hochgeladen (contract_id={existing_contract2.id})"
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning(f"Warnung während Duplikatprüfung (Upload mit Metadaten): {e}")

        processing_time = time.time() - start_time

        logger.info(f"Vertragsupload erfolgreich / Upload de contrato bem-sucedido: {processing_time:.2f}s")

        return ExtractionResponse(
            success=True,
            extracted_data=extracted_data,
            processing_time=processing_time,
            file_size=file_size,
            error_message=None,
            original_file_name=file.filename,
            original_file_storage_name=safe_filename,
            original_file_sha256=file_hash,
            ocr_text_sha256=ocr_hash,
            uploaded_at=uploaded_at,
            temp_file_path=file_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Vertragsupload / Erro no upload de contrato: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Interner Serverfehler / Erro interno do servidor: {str(e)}"
        )
    finally:
        # Bei diesem Endpoint behalten wir die Datei im Upload-Ordner im Erfolgsfall.
        # Nur löschen, wenn ein Fehler aufgetreten ist (d.h. falls die Datei noch existiert
        # und response nicht erfolgreich gesendet wurde). Da wir hier nicht in der Lage sind,
        # eindeutig zu erkennen ob eine Exception vorher geworfen wurde, belassen wir die Datei
        # (entsprechend der Persistenz-Anforderung). Falls gewünscht, kann eine Logik mit
        # success-Flag hinzugefügt werden.
        try:
            pass
        except Exception:
            logger.debug("Finally block reached in upload endpoint")

@router.get("/status")
async def get_import_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Gibt den Status des Import-Systems zurück
    Retorna o status do sistema de importação
    
    Returns / Retorna:
        Dict: Status-Informationen / Informações de status
    """
    try:
        logger.info(f"Import-Status abgefragt / Status de importação solicitado von Benutzer / do usuário {current_user.id}")
        
        # Upload-Verzeichnis prüfen / Verificar diretório de upload
        upload_dir_exists = os.path.exists(TEMP_UPLOAD_DIR)
        upload_dir_writable = os.access(TEMP_UPLOAD_DIR, os.W_OK) if upload_dir_exists else False
        
        # Dateien im Upload-Verzeichnis zählen / Contar arquivos no diretório de upload
        file_count = 0
        if upload_dir_exists:
            file_count = len([f for f in os.listdir(TEMP_UPLOAD_DIR) if f.endswith('.pdf')])
        
        return {
            "status": "online" if upload_dir_exists and upload_dir_writable else "offline",
            "upload_directory": TEMP_UPLOAD_DIR,
            "upload_directory_exists": upload_dir_exists,
            "upload_directory_writable": upload_dir_writable,
            "max_file_size": MAX_FILE_SIZE,
            "allowed_extensions": ALLOWED_EXTENSIONS,
            "files_in_upload_dir": file_count,
            "message": "Import-System ist betriebsbereit / Sistema de importação está operacional" if upload_dir_exists and upload_dir_writable else "Import-System ist nicht verfügbar / Sistema de importação não está disponível"
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Import-Status / Erro ao recuperar status de importação: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fehler beim Abrufen des Status / Erro ao recuperar status: {str(e)}"
        )
