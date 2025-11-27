"""Analysis utilities: complexity, key terms, legal entities, advanced context.

Implementations migrated from PDFReaderService to avoid delegation.
"""
from typing import Dict, Any, List
import logging
import re
from .dates import calculate_notice_period
from .financials import extract_financial_terms

logger = logging.getLogger(__name__)


def analyze_contract_complexity(text: str) -> Dict[str, Any]:
    try:
        word_count = len(text.split())
        sentence_count = len([s for s in text.split('.') if s.strip()])
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        complex_words = sum(1 for word in text.split() if len(word) > 6)
        complex_word_ratio = complex_words / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        complexity_score = min(1.0, (avg_sentence_length / 20) + (complex_word_ratio * 2))
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'avg_sentence_length': avg_sentence_length,
            'complex_word_ratio': complex_word_ratio,
            'complexity_score': complexity_score,
            'complexity_level': 'high' if complexity_score > 0.7 else 'medium' if complexity_score > 0.4 else 'low'
        }
    except Exception as e:
        logger.error(f"Error in analyze_contract_complexity: {e}")
        return {'complexity_score': 0.5, 'complexity_level': 'medium'}


def extract_key_terms(text: str) -> List[Dict[str, Any]]:
    try:
        legal_terms = [
            'kündigung', 'kündigungsfrist', 'verlängerung', 'automatische verlängerung',
            'vertragsende', 'vertragsbeginn', 'leistung', 'vergütung', 'zahlung',
            'haftung', 'haftungsausschluss', 'gewährleistung', 'garantie',
            'streitbeilegung', 'schiedsgericht', 'gerichtsstand', 'anwendbares recht'
        ]
        text_lower = text.lower()
        found_terms = []
        for term in legal_terms:
            if term in text_lower:
                start_pos = text_lower.find(term)
                context_start = max(0, start_pos - 30)
                context_end = min(len(text), start_pos + len(term) + 30)
                context = text[context_start:context_end]
                found_terms.append({'term': term, 'context': context, 'position': start_pos, 'confidence': 0.8})
        return found_terms
    except Exception as e:
        logger.error(f"Error in extract_key_terms: {e}")
        return []


def extract_legal_entities(text: str) -> List[Dict[str, Any]]:
    try:
        entity_patterns = [
            r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:GmbH|GmbH & Co\\. KG)\b',
            r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:AG|Aktiengesellschaft)\b',
            r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:KG|Kommanditgesellschaft)\b',
            r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:OHG|Offene Handelsgesellschaft)\b',
            r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:UG|Unternehmergesellschaft)\b',
            r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:e.V|eingetragener Verein)\b',
            r'\b([A-ZÄÖÜ][a-zäöüß\s]+)\s+(?:&Co|Kommanditgesellschaft)\b',
        ]
        entities = []
        for pattern in entity_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                entities.append({'name': match.group(1).strip(), 'full_text': match.group(0), 'type': 'legal_entity', 'confidence': 0.9})
        return entities
    except Exception as e:
        logger.error(f"Error in extract_legal_entities: {e}")
        return []


def extract_advanced_context_data(text: str) -> Dict[str, Any]:
    try:
        context_data = {
            'notice_period': calculate_notice_period(text),
            'contract_complexity': analyze_contract_complexity(text),
            'key_terms': extract_key_terms(text),
            'legal_entities': extract_legal_entities(text),
            'financial_terms': extract_financial_terms(text)
        }
        return context_data
    except Exception as e:
        logger.error(f"Error in extract_advanced_context_data: {e}")
        return {}
