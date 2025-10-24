"""Financial extraction utilities (migrated from PDFReaderService)."""
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

MONEY_PATTERNS = [
    r'€\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?',
    r'EUR\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?',
    r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*€',
    r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*EUR',
]


def extract_money_values(text: str) -> Dict[str, Any]:
    """Extrai valores monetários e escolhe o maior como valor principal."""
    try:
        money_values = []
        currencies = []
        for pattern in MONEY_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                amount_match = re.search(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', match)
                if amount_match:
                    money_values.append(amount_match.group(1))
                if '€' in match or 'EUR' in match:
                    currencies.append('EUR')
        if money_values:
            highest_value = max(money_values, key=lambda x: float(x.replace('.', '').replace(',', '.')))
            currency = currencies[0] if currencies else 'EUR'
            return {'value': highest_value, 'currency': currency, 'confidence': 0.8}
        return {'value': None, 'currency': None, 'confidence': 0.0}
    except Exception as e:
        logger.error(f"Error in extract_money_values: {e}")
        return {'value': None, 'currency': None, 'confidence': 0.0}


def extract_financial_terms(text: str) -> Dict[str, Any]:
    """Extrai termos financeiros (prazos de pagamento, penalidades, descontos, impostos)."""
    try:
        financial_terms: Dict[str, Any] = {'payment_terms': [], 'penalties': [], 'discounts': [], 'taxes': []}
        payment_patterns = [
            r'(?:zahlung|bezahlung|entgelt)\s+(?:innerhalb|bis)\s+(\d+)\s*(?:tage|tagen)',
            r'(?:rechnung|rechnungsstellung)\s+(?:innerhalb|bis)\s+(\d+)\s*(?:tage|tagen)',
            r'(?:fällig|fälligkeit)\s+(?:innerhalb|bis)\s+(\d+)\s*(?:tage|tagen)',
        ]
        for pattern in payment_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                financial_terms['payment_terms'].append({'term': match.group(0), 'days': int(match.group(1)), 'confidence': 0.8})

        penalty_patterns = [
            r'(?:strafe|strafzahlung|vertragsstrafe)\s+(?:von|in höhe von)\s*€?\s*(\d+(?:\.\d{3})*(?:,\d{2})?)',
            r'(?:pönale|pönale)\s+(?:von|in höhe von)\s*€?\s*(\d+(?:\.\d{3})*(?:,\d{2})?)',
        ]
        for pattern in penalty_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                financial_terms['penalties'].append({'term': match.group(0), 'amount': match.group(1), 'confidence': 0.8})

        return financial_terms
    except Exception as e:
        logger.error(f"Error in extract_financial_terms: {e}")
        return {'payment_terms': [], 'penalties': [], 'discounts': [], 'taxes': []}
