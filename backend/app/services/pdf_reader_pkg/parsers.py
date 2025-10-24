"""Parsers for title, client, email, phone, address, description.

Implementations moved from the original `PDFReaderService` private methods.
These are pure functions that operate on text.
"""
from typing import Optional
import re
import logging

logger = logging.getLogger(__name__)

# Patterns and helpers (kept close to original implementation)
COMPANY_PATTERNS = [
    r'\b[A-ZÄÖÜ][a-zäöüß]+\s+GmbH\b',
    r'\b[A-ZÄÖÜ][a-zäöüß]+\s+AG\b',
    r'\b[A-ZÄÖÜ][a-zäöüß]+\s+KG\b',
    r'\b[A-ZÄÖÜ][a-zäöüß]+\s+OHG\b',
]

ADDRESS_PATTERNS = [
    r'([A-ZÄÖÜ][a-zäöüß]+\s+\d+[a-z]?,\s*\d{5}\s+[A-ZÄÖÜ][a-zäöüß]+)',
    r'([A-ZÄÖÜ][a-zäöüß]+\s+\d+[a-z]?,\s*\d{5})',
]

EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


def extract_title(text: str) -> Optional[str]:
    """Extrai título do contrato (heurística)."""
    try:
        title_patterns = [
            r'Vertrag\s+über\s+([^.\n]+)',
            r'Vereinbarung\s+über\s+([^.\n]+)',
            r'Dienstleistungsvertrag\s+([^.\n]+)',
            r'Werkvertrag\s+([^.\n]+)',
            r'Mietvertrag\s+([^.\n]+)',
            r'Kaufvertrag\s+([^.\n]+)',
        ]
        for pattern in title_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                if len(title) > 5:
                    return title

        first_line = text.split('\n')[0].strip()
        if 5 < len(first_line) < 100:
            return first_line
        return None
    except Exception as e:
        logger.error(f"Error in extract_title: {e}")
        return None


def extract_client_name(text: str) -> Optional[str]:
    try:
        for pattern in COMPANY_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                return max(matches, key=len)

        between_pattern = r'zwischen\s+([^,\n]+)'
        match = re.search(between_pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return None
    except Exception as e:
        logger.error(f"Error in extract_client_name: {e}")
        return None


def extract_email(text: str) -> Optional[str]:
    try:
        matches = re.findall(EMAIL_PATTERN, text)
        return matches[0] if matches else None
    except Exception as e:
        logger.error(f"Error in extract_email: {e}")
        return None


def extract_phone(text: str) -> Optional[str]:
    try:
        phone_patterns = [
            r'(\+49\s?)?(\(0\))?[0-9\s\-\(\)]{10,}',
            r'(\+49\s?)?[0-9]{2,4}\s?[0-9]{2,4}\s?[0-9]{2,4}',
        ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # re.findall with groups returns tuples; recover original match
                raw = re.search(pattern, text)
                if raw:
                    return raw.group(0)
        return None
    except Exception as e:
        logger.error(f"Error in extract_phone: {e}")
        return None


def extract_address(text: str) -> Optional[str]:
    try:
        for pattern in ADDRESS_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return None
    except Exception as e:
        logger.error(f"Error in extract_address: {e}")
        return None


def extract_description(text: str) -> Optional[str]:
    try:
        sentences = text.split('.')[:3]
        description = '. '.join(sentences).strip()
        if 20 < len(description) < 500:
            return description
        return None
    except Exception as e:
        logger.error(f"Error in extract_description: {e}")
        return None


def extract_terms_and_conditions(text: str) -> Optional[str]:
    """Extrai cláusulas de termos e condições (AGB) do texto."""
    try:
        agb_patterns = [
            r'Allgemeine Geschäftsbedingungen[:\s]*([^.]{50,500})',
            r'AGB[:\s]*([^.]{50,500})',
            r'Bedingungen[:\s]*([^.]{50,500})',
        ]
        for pattern in agb_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                terms = match.group(1).strip()
                if len(terms) > 50:
                    return terms
        return None
    except Exception as e:
        logger.error(f"Error in extract_terms_and_conditions: {e}")
        return None
