"""Validation wrapper module for PDFs"""
from typing import Dict, Any


def validate_pdf(pdf_path: str) -> Dict[str, Any]:
    try:
        from app.services.pdf_reader import PDFReaderService as _PDFReaderService
        return _PDFReaderService().validate_pdf(pdf_path)
    except Exception:
        raise NotImplementedError("validate_pdf wrapper not available")
