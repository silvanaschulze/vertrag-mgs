"""
Vertragsimport-Router für das Vertragsverwaltungssystem
Router de importação de contratos para o Sistema de Gerenciamento de Contratos

Dieses Modul enthält Endpoints für den Import und die Verarbeitung von PDF-Verträgen.
Este módulo contém endpoints para importação e processamento de contratos PDF.
Unterstützt Upload, Extraktion und Validierung von Vertragsdaten.
Suporta upload, extração e validação de dados de contrato.
"""

import os
import time
import logging
from typing import Optional, List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

# Lokale Imports / Imports locais
from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.extracted_contract import (
    ExtractedContractDraft, 
    ExtractionRequest, 
    ExtractionResponse
)
from app.services.pdf_reader import PDFReaderService
import asyncio
# Contract Extractor Service wurde in PDFReaderService integriert
# Serviço de extração de contrato foi integrado no PDFReaderService

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
UPLOAD_DIR = "uploads/contracts"

# Upload-Verzeichnis erstellen / Criar diretório de upload
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
        
        # Eindeutigen Dateinamen erstellen / Criar nome de arquivo único
        timestamp = int(time.time())
        safe_filename = f"{current_user.id}_{timestamp}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
        # Datei speichern / Salvar arquivo (in Thread auslagern um Event-Loop nicht zu blockieren)
        def _write_file(path: str, content: bytes) -> None:
            with open(path, "wb") as buffer:
                buffer.write(content)

        await asyncio.to_thread(_write_file, file_path, file_content)
        
        logger.info(f"Datei gespeichert / Arquivo salvo: {file_path}")

        # PDF-Reader-Service initialisieren / Inicializar serviço de leitura de PDF
        pdf_reader = PDFReaderService()

        # PDF validieren / Validar PDF (executar em thread se for CPU/IO-bound)
        validation_result = await asyncio.to_thread(pdf_reader.validate_pdf, file_path)
        if not validation_result.get('valid'):
            try:
                os.remove(file_path)
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ungültige PDF-Datei / Arquivo PDF inválido: {validation_result.get('error', 'Unbekannter Fehler')}"
            )

        # Text extrahieren (möglicherweise IO/CPU-bound) - in Thread auslagern
        if extraction_method == "combined":
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_combined, file_path)
        elif extraction_method == "pdfplumber":
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_with_pdfplumber, file_path)
        elif extraction_method == "pypdf2":
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_with_pypdf2, file_path)
        elif extraction_method == "pymupdf":
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_with_pymupdf, file_path)
        else:
            extraction_result = await asyncio.to_thread(pdf_reader.extract_text_combined, file_path)

        if not extraction_result.get('success'):
            try:
                os.remove(file_path)
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Textextraktion fehlgeschlagen / Extração de texto falhou: {extraction_result.get('error', 'Unbekannter Fehler')}"
            )

        # Intelligente Extraktion durchführen / Executar extração inteligente
        intelligent_data = await asyncio.to_thread(pdf_reader.extract_intelligent_data, extraction_result.get('text', ''))

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

        logger.info(f"PDF-Import erfolgreich / Importação de PDF bem-sucedida: {processing_time:.2f}s")

        return ExtractionResponse(
            success=True,
            extracted_data=extracted_data,
            processing_time=processing_time,
            file_size=file_size,
            error_message=None
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
        # Aufräumen bei Fehlern / Limpeza em caso de erros
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"Temporäre Datei gelöscht / Arquivo temporário deletado: {file_path}")
            except Exception as e:
                logger.warning(f"Fehler beim Löschen der temporären Datei / Erro ao deletar arquivo temporário: {str(e)}")

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
        file_path = os.path.join(UPLOAD_DIR, safe_filename)
        
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
        
        logger.info(f"Vertragsupload erfolgreich / Upload de contrato bem-sucedido: {processing_time:.2f}s")
        
        return ExtractionResponse(
            success=True,
            extracted_data=extracted_data,
            processing_time=processing_time,
            file_size=file_size,
            error_message=None
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
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.warning(f"Fehler beim Löschen der temporären Datei / Erro ao deletar arquivo temporário: {str(e)}")

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
        upload_dir_exists = os.path.exists(UPLOAD_DIR)
        upload_dir_writable = os.access(UPLOAD_DIR, os.W_OK) if upload_dir_exists else False
        
        # Dateien im Upload-Verzeichnis zählen / Contar arquivos no diretório de upload
        file_count = 0
        if upload_dir_exists:
            file_count = len([f for f in os.listdir(UPLOAD_DIR) if f.endswith('.pdf')])
        
        return {
            "status": "online" if upload_dir_exists and upload_dir_writable else "offline",
            "upload_directory": UPLOAD_DIR,
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
