"""Date extraction and notice period utilities (migrated implementations)."""
from typing import Dict, Any, Optional, List
import re
import logging

logger = logging.getLogger(__name__)

DATE_PATTERNS = [
    r'\b\d{1,2}\.\d{1,2}\.\d{4}\b',
    r'\b\d{1,2}\/\d{1,2}\/\d{4}\b',
    r'\b\d{1,2}-\d{1,2}-\d{4}\b',
    r'\b\d{1,2}\.\s*\d{1,2}\.\s*\d{4}\b',
]


def extract_dates(text: str) -> Dict[str, Any]:
    """Extrai datas do texto e tenta classificá-las (start/end/renewal)."""
    try:
        dates: List[Dict[str, Any]] = []
        for pattern in DATE_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    import dateparser
                    parsed_date = dateparser.parse(match, languages=['de'])
                except Exception:
                    parsed_date = None
                if parsed_date:
                    dates.append({'raw': match, 'parsed': parsed_date, 'confidence': 0.8})

        start_date = None
        end_date = None
        renewal_date = None
        for date_info in dates:
            date_str = date_info['raw']
            context_start = max(0, text.find(date_str) - 50)
            context_end = min(len(text), text.find(date_str) + 50)
            context = text[context_start:context_end].lower()
            if any(keyword in context for keyword in ['start', 'beginn', 'anfang', 'von']):
                start_date = date_str
            elif any(keyword in context for keyword in ['ende', 'end', 'bis', 'until']):
                end_date = date_str
            elif any(keyword in context for keyword in ['verlängerung', 'renewal', 'extension']):
                renewal_date = date_str

        return {'start_date': start_date, 'end_date': end_date, 'renewal_date': renewal_date}
    except Exception as e:
        logger.error(f"Error in extract_dates: {e}")
        return {'start_date': None, 'end_date': None, 'renewal_date': None}


def calculate_notice_period(text: str) -> Optional[Dict[str, Any]]:
    """Detecta cláusulas de Kündigungsfrist/notice period e retorna o período mais relevante."""
    try:
        logger.info("Notice period calculation started")
        notice_patterns = [
            r'kündigungsfrist\s*:?\s*(\d+)\s*(?:tage|tagen|monate|monaten|jahre|jahren)',
            r'kündigung\s+(?:mit|nach)\s*(\d+)\s*(?:tage|tagen|monate|monaten|jahre|jahren)',
            r'kündigbar\s+(?:mit|nach)\s*(\d+)\s*(?:tage|tagen|monate|monaten|jahre|jahren)',
            r'beendigung\s+(?:mit|nach)\s*(\d+)\s*(?:tage|tagen|monate|monaten|jahre|jahren)',
            r'(\d+)\s*(?:tage|tagen|monate|monaten|jahre|jahren)\s*kündigungsfrist',
            r'(\d+)\s*(?:tage|tagen|monate|monaten|jahre|jahren)\s*(?:vor|vorher)',
        ]
        text_lower = text.lower()
    notice_periods: List[Dict[str, Any]] = []
        for pattern in notice_patterns:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                period_value = int(match.group(1))
                period_text = match.group(0)
                if any(unit in period_text for unit in ['jahre', 'jahren']):
                    unit = 'years'
                    days = period_value * 365
                elif any(unit in period_text for unit in ['monate', 'monaten']):
                    unit = 'months'
                    days = period_value * 30
                else:
                    unit = 'days'
                    days = period_value
                notice_periods.append({'value': period_value, 'unit': unit, 'days': days, 'text': period_text, 'confidence': 0.9})

        if notice_periods:
            best_period = max(notice_periods, key=lambda x: int(x['days']))
            logger.info(f"Notice period found: {best_period['value']} {best_period['unit']}")
            return best_period
        logger.info("No notice period found")
        return None
    except Exception as e:
        logger.error(f"Error in calculate_notice_period: {e}")
        return None
