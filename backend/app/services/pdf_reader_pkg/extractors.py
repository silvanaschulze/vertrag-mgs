"""Extractors wrapper module

Funções delegam para `app.services.pdf_reader` para preservar comportamento
existente enquanto permitimos refatoração incremental.
"""
from typing import Dict, Any, List
import os
import io

import logging

logger = logging.getLogger(__name__)


def extract_text_with_pdfplumber(reader, pdf_path: str) -> Dict[str, Any]:
    """Implementation moved from PDFReaderService.extract_text_with_pdfplumber

    reader: instance of PDFReaderService (used for config like max_pages)
    """
    try:
        import pdfplumber

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        max_size = 50 * 1024 * 1024
        if os.path.getsize(pdf_path) > max_size:
            raise ValueError(f"PDF file too large (>50MB): {pdf_path}")
        logger.info(f"Textextraktion mit pdfplumber gestartet / Extração de texto com pdfplumber iniciada: {pdf_path}")

    text_content: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

        with pdfplumber.open(pdf_path) as pdf:
            metadata = {
                'pages': len(pdf.pages),
                'title': pdf.metadata.get('Title', ''),
                'author': pdf.metadata.get('Author', ''),
                'creator': pdf.metadata.get('Creator', ''),
                'producer': pdf.metadata.get('Producer', ''),
                'creation_date': pdf.metadata.get('CreationDate', ''),
                'modification_date': pdf.metadata.get('ModDate', '')
            }
            for page_num, page in enumerate(pdf.pages[: reader.max_pages], 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append({
                        'page': page_num,
                        'text': page_text,
                        'char_count': len(page_text)
                    })

        result = {
            'method': 'pdfplumber',
            'success': True,
            'text': '\n'.join([page['text'] for page in text_content]),
            'pages': text_content,
            'metadata': metadata,
            'total_chars': sum([page['char_count'] for page in text_content])
        }

        logger.info(f"Textextraktion mit pdfplumber erfolgreich / Extração de texto com pdfplumber bem-sucedida: {result['total_chars']} Zeichen")
        return result

    except Exception as e:
        logger.exception(f"Fehler bei pdfplumber-Extraktion / Erro na extração com pdfplumber: {str(e)}")
        return {
            'method': 'pdfplumber',
            'success': False,
            'error': str(e),
            'text': '',
            'pages': [],
            'metadata': {}
        }


def extract_text_with_pypdf2(reader, pdf_path: str) -> Dict[str, Any]:
    try:
        import PyPDF2

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        max_size = 50 * 1024 * 1024
        if os.path.getsize(pdf_path) > max_size:
            raise ValueError(f"PDF file too large (>50MB): {pdf_path}")
        logger.info(f"Textextraktion mit PyPDF2 gestartet / Extração de texto com PyPDF2 iniciada: {pdf_path}")

    text_content: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            if pdf_reader.metadata:
                metadata = {
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                    'modification_date': pdf_reader.metadata.get('/ModDate', '')
                }
            for page_num, page in enumerate(pdf_reader.pages[: reader.max_pages], 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append({
                        'page': page_num,
                        'text': page_text,
                        'char_count': len(page_text)
                    })

        result = {
            'method': 'pypdf2',
            'success': True,
            'text': '\n'.join([page['text'] for page in text_content]),
            'pages': text_content,
            'metadata': metadata,
            'total_chars': sum([page['char_count'] for page in text_content])
        }

        logger.info(f"Textextraktion mit PyPDF2 erfolgreich / Extração de texto com PyPDF2 bem-sucedida: {result['total_chars']} Zeichen")
        return result

    except Exception as e:
        logger.exception(f"Fehler bei PyPDF2-Extraktion / Erro na extração com PyPDF2: {str(e)}")
        return {
            'method': 'pypdf2',
            'success': False,
            'error': str(e),
            'text': '',
            'pages': [],
            'metadata': {}
        }


def extract_text_with_pymupdf(reader, pdf_path: str) -> Dict[str, Any]:
    try:
        import fitz

        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        max_size = 50 * 1024 * 1024
        if os.path.getsize(pdf_path) > max_size:
            raise ValueError(f"PDF file too large (>50MB): {pdf_path}")
        logger.info(f"Textextraktion mit pymupdf gestartet / Extração de texto com pymupdf iniciada: {pdf_path}")

    text_content: List[Dict[str, Any]] = []
    metadata: Dict[str, Any] = {}

        with fitz.open(pdf_path) as doc:
            raw_md = doc.metadata or {}
            md = dict(raw_md)
            metadata = {
                'title': md.get('title', '') or '',
                'author': md.get('author', '') or '',
                'creator': md.get('creator', '') or '',
                'producer': md.get('producer', '') or '',
                'creation_date': md.get('creationDate', '') or '',
                'modification_date': md.get('modDate', '') or '',
            }
            for page_num in range(min(doc.page_count, reader.max_pages)):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    text_content.append({
                        'page': page_num + 1,
                        'text': page_text,
                        'char_count': len(page_text)
                    })

        result = {
            'method': 'pymupdf',
            'success': True,
            'text': '\n'.join([page['text'] for page in text_content]),
            'pages': text_content,
            'metadata': metadata,
            'total_chars': sum([page['char_count'] for page in text_content])
        }

        logger.info(f"Textextraktion mit pymupdf erfolgreich / Extração de texto com pymupdf bem-sucedida: {result['total_chars']} Zeichen")
        return result

    except Exception as e:
        logger.exception(f"Fehler bei pymupdf-Extraktion / Erro na extração com pymupdf: {str(e)}")
        return {
            'method': 'pymupdf',
            'success': False,
            'error': str(e),
            'text': '',
            'pages': [],
            'metadata': {}
        }


def ocr_with_pytesseract(reader, image_path: str, language: str = 'deu') -> Dict[str, Any]:
    try:
        from PIL import Image
        import pytesseract

        logger.info(f"OCR mit pytesseract gestartet / OCR com pytesseract iniciado: {image_path}")
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image, lang=language)
        data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
    conf_values: List[int] = [int(conf) for conf in data.get('conf', []) if isinstance(conf, (int, str)) and int(conf) > 0]
        avg_conf = int(sum(conf_values) / len(conf_values)) if conf_values else 0
        result = {
            'method': 'pytesseract',
            'success': True,
            'text': text,
            'confidence': avg_conf,
            'language': language,
            'char_count': len(text)
        }
        logger.info(f"OCR mit pytesseract erfolgreich / OCR com pytesseract bem-sucedido: {result['char_count']} Zeichen")
        return result
    except Exception as e:
        logger.error(f"Fehler bei pytesseract-OCR / Erro no OCR com pytesseract: {str(e)}")
        return {
            'method': 'pytesseract',
            'success': False,
            'error': str(e),
            'text': '',
            'confidence': 0,
            'language': language,
            'char_count': 0
        }


def extract_text_combined(reader, pdf_path: str) -> Dict[str, Any]:
    logger.info(f"Kombinierte Textextraktion gestartet / Extração de texto combinada iniciada: {pdf_path}")
    results = {}
    methods = [
        ('pdfplumber', extract_text_with_pdfplumber),
        ('pypdf2', extract_text_with_pypdf2),
        ('pymupdf', extract_text_with_pymupdf)
    ]
    for method_name, method_func in methods:
        try:
            result = method_func(reader, pdf_path)
            results[method_name] = result
            logger.info(f"Extraktion mit {method_name}: {'Erfolgreich' if result['success'] else 'Fehlgeschlagen'}")
        except Exception as e:
            logger.error(f"Fehler bei {method_name}: {str(e)}")
            results[method_name] = {'method': method_name, 'success': False, 'error': str(e)}

    successful_results = [r for r in results.values() if r.get('success', False)]
    if successful_results:
        best_result = max(successful_results, key=lambda x: x.get('total_chars', 0))
        best_result['all_methods'] = results
        best_result['combined'] = True
        logger.info(f"Beste Extraktionsmethode ausgewählt / Melhor método de extração selecionado: {best_result['method']}")
        return best_result
    else:
        logger.error("Alle Extraktionsmethoden fehlgeschlagen / Todos os métodos de extração falharam")
        return {'method': 'combined', 'success': False, 'error': 'Alle Extraktionsmethoden fehlgeschlagen', 'text': '', 'all_methods': results, 'combined': True}


def validate_pdf(reader, pdf_path: str) -> Dict[str, Any]:
    try:
        logger.info(f"PDF-Validierung gestartet / Validação de PDF iniciada: {pdf_path}")
        import os
        if not os.path.exists(pdf_path):
            return {'valid': False, 'error': 'Datei nicht gefunden / Arquivo não encontrado', 'file_size': 0}
        file_size = os.path.getsize(pdf_path)
        if file_size == 0:
            return {'valid': False, 'error': 'Leere Datei / Arquivo vazio', 'file_size': file_size}
        try:
            with open(pdf_path, 'rb') as file:
                header = file.read(4)
                if header != b'%PDF':
                    return {'valid': False, 'error': 'Ungültiges PDF-Format / Formato PDF inválido', 'file_size': file_size}
        except Exception as e:
            return {'valid': False, 'error': f'Fehler beim Lesen der Datei / Erro ao ler arquivo: {str(e)}', 'file_size': file_size}
        logger.info(f"PDF-Validierung erfolgreich / Validação de PDF bem-sucedida: {file_size} Bytes")
        return {'valid': True, 'file_size': file_size, 'message': 'PDF-Datei ist gültig / Arquivo PDF é válido'}
    except Exception as e:
        logger.error(f"Fehler bei PDF-Validierung / Erro na validação de PDF: {str(e)}")
        return {'valid': False, 'error': str(e), 'file_size': 0}
