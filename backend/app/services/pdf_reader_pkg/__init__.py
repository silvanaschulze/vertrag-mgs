"""PDF Reader package wrapper

Este pacote fornece pontos de entrada modulares que delegam para a
implementação existente em `app.services.pdf_reader`. O objetivo é criar
um scaffold seguro para futuras refatorações sem quebrar imports.

Documentação / Logs: Alemão/Português.
"""

from .service import PDFReaderService, get_pdf_reader_service
from .extractors import (
    extract_text_with_pdfplumber,
    extract_text_with_pypdf2,
    extract_text_with_pymupdf,
    extract_text_combined,
)
from .ocr import ocr_with_pytesseract
from .validate import validate_pdf
from .parsers import (
    extract_title,
    extract_client_name,
    extract_email,
    extract_phone,
    extract_address,
    extract_description,
)
from .financials import extract_money_values, extract_financial_terms
from .dates import extract_dates, calculate_notice_period
from .analysis import (
    analyze_contract_complexity,
    extract_key_terms,
    extract_legal_entities,
    extract_advanced_context_data,
)

__all__ = [
    "PDFReaderService",
    "get_pdf_reader_service",
    "extract_text_with_pdfplumber",
    "extract_text_with_pypdf2",
    "extract_text_with_pymupdf",
    "extract_text_combined",
    "ocr_with_pytesseract",
    "validate_pdf",
    "extract_title",
    "extract_client_name",
    "extract_email",
    "extract_phone",
    "extract_address",
    "extract_description",
    "extract_money_values",
    "extract_financial_terms",
    "extract_dates",
    "calculate_notice_period",
    "analyze_contract_complexity",
    "extract_key_terms",
    "extract_legal_entities",
    "extract_advanced_context_data",
]
