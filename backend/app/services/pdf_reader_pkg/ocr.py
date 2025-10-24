"""OCR wrapper module

Delegates to original PDF reader implementation when available.
"""
from typing import Dict, Any


def ocr_with_pytesseract(image_path: str, language: str = 'deu') -> Dict[str, Any]:
    try:
        from app.services.pdf_reader import PDFReaderService as _PDFReaderService
        return _PDFReaderService().ocr_with_pytesseract(image_path, language=language)
    except Exception:
        raise NotImplementedError("pytesseract wrapper not available")
