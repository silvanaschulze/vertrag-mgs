"""
PDF-Reader-Service für das Vertragsverwaltungssystem
Serviço de leitura de PDF para o Sistema de Gerenciamento de Contratos

Dieses Modul enthält Funktionen zum Lesen und Verarbeiten von PDF-Dokumenten.
Este módulo contém funções para leitura e processamento de documentos PDF.
Unterstützt verschiedene PDF-Bibliotheken für optimale Ergebnisse.
Suporta várias bibliotecas PDF para resultados ótimos.
"""

import os
import re
import logging
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from pathlib import Path
import io
from typing import Dict, Any, cast

# Logging konfigurieren / Configurar logging
logger = logging.getLogger(__name__)

class PDFReaderService:
    """
    PDF-Reader-Service für verschiedene Extraktionsmethoden
    Serviço de leitura de PDF para diferentes métodos de extração
    
    Unterstützt mehrere PDF-Bibliotheken für optimale Textextraktion.
    Suporta várias bibliotecas PDF para extração de texto otimizada.
    """
    
    def __init__(self):
        """
        Initialisiert den PDF-Reader-Service
        Inicializa o serviço de leitura de PDF
        """
        self.supported_formats = ['.pdf']
        
        # Deutsche Schlüsselwörter / Palavras-chave alemãs
        self.german_keywords = {
            'kündigungsfrist': ['kündigungsfrist', 'kündigung', 'kündigen', 'beendigung'],
            'läuft_bis': ['läuft bis', 'gültig bis', 'endet am', 'bis zum'],
            'endet_am': ['endet am', 'beendet am', 'auslaufend am', 'ablaufend am'],
            'verlängert': ['verlängert', 'verlängerung', 'automatische verlängerung', 'verlängert sich'],
            'gmbh': ['gmbh', 'gesellschaft mit beschränkter haftung'],
            'ag': ['ag', 'aktiengesellschaft'],
            'eur': ['eur', 'euro', '€']
        }
        
        # Regex-Patterns für deutsche Verträge / Padrões regex para contratos alemães
        self.patterns = {
            'date_patterns': [
                r'\b\d{1,2}\.\d{1,2}\.\d{4}\b',  # DD.MM.YYYY
                r'\b\d{1,2}\/\d{1,2}\/\d{4}\b',   # DD/MM/YYYY
                r'\b\d{1,2}-\d{1,2}-\d{4}\b',     # DD-MM-YYYY
                r'\b\d{1,2}\.\s*\d{1,2}\.\s*\d{4}\b',  # DD. MM. YYYY
            ],
            'money_patterns': [
                r'€\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?',  # € 1.000,00
                r'EUR\s*\d{1,3}(?:\.\d{3})*(?:,\d{2})?', # EUR 1.000,00
                r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*€',  # 1.000,00 €
                r'\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*EUR', # 1.000,00 EUR
            ],
            'company_patterns': [
                r'\b[A-ZÄÖÜ][a-zäöüß]+\s+GmbH\b',  # Nome GmbH
                r'\b[A-ZÄÖÜ][a-zäöüß]+\s+AG\b',    # Nome AG
                r'\b[A-ZÄÖÜ][a-zäöüß]+\s+KG\b',    # Nome KG
                r'\b[A-ZÄÖÜ][a-zäöüß]+\s+OHG\b',   # Nome OHG
            ],
            'email_patterns': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'phone_patterns': [
                r'(\+49\s?)?(\(0\))?[0-9\s\-\(\)]{10,}',  # Deutsche Telefonnummern
                r'(\+49\s?)?[0-9]{2,4}\s?[0-9]{2,4}\s?[0-9]{2,4}',
            ]
        }
        
        # lazy-loaded NLP und Parser libraries
        self._nlp = None
        self._dateparser = None
        # máximo de páginas a processar por documento para evitar uso excessivo de memória
        self.max_pages = 500

        logger.info("PDF-Reader-Service initialisiert / PDF Reader Service initialized")

    def _ensure_nlp(self):
        """Lazy-load das Spacy-Modell; safe-fallback, returns None if nicht verfügbar."""
        if self._nlp is not None:
            return self._nlp
        try:
            import spacy
            self._nlp = spacy.load("de_core_news_sm")
            logger.info("Deutsches Spacy-Modell geladen / Modelo Spacy alemão carregado")
        except Exception:
            logger.warning("Deutsches Spacy-Modell nicht gefunden / Modelo Spacy alemão não encontrado")
            self._nlp = None
        return self._nlp

    def _ensure_dateparser(self):
        """Lazy-load dateparser; returns module or None."""
        if self._dateparser is not None:
            return self._dateparser
        try:
            import dateparser
            self._dateparser = dateparser
        except Exception:
            logger.warning("dateparser nicht verfügbar / dateparser não disponível")
            self._dateparser = None
        return self._dateparser
    
    def extract_text_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrahiert Text aus PDF mit pdfplumber
        Extrai texto de PDF com pdfplumber
        
        Args / Argumentos:
            pdf_path (str): Pfad zur PDF-Datei / Caminho para o arquivo PDF
            
        Returns / Retorna:
            Dict[str, Any]: Extrahierter Text und Metadaten / Texto extraído e metadados
        """
        # delega a implementação para o módulo refatorado
        from app.services.pdf_reader_pkg import extractors
        return extractors.extract_text_with_pdfplumber(self, pdf_path)

    def extract_text_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """Delegiert an pdf_reader_pkg.extractors.extract_text_with_pypdf2"""
        from app.services.pdf_reader_pkg import extractors
        return extractors.extract_text_with_pypdf2(self, pdf_path)

    def extract_text_with_pymupdf(self, pdf_path: str) -> Dict[str, Any]:
        """Delegiert an pdf_reader_pkg.extractors.extract_text_with_pymupdf"""
        from app.services.pdf_reader_pkg import extractors
        return extractors.extract_text_with_pymupdf(self, pdf_path)

    def ocr_with_pytesseract(self, image_path: str, language: str = 'deu') -> Dict[str, Any]:
        """Delegiert an pdf_reader_pkg.extractors.ocr_with_pytesseract"""
        from app.services.pdf_reader_pkg import extractors
        return extractors.ocr_with_pytesseract(self, image_path, language)
    
    def extract_text_combined(self, pdf_path: str) -> Dict[str, Any]:
        """
        Kombiniert verschiedene Extraktionsmethoden für optimale Ergebnisse
        Combina diferentes métodos de extração para resultados ótimos
        
        Args / Argumentos:
            pdf_path (str): Pfad zur PDF-Datei / Caminho para o arquivo PDF
            
        Returns / Retorna:
            Dict[str, Any]: Kombiniertes Extraktionsergebnis / Resultado de extração combinado
        """
        logger.info(f"Kombinierte Textextraktion gestartet / Extração de texto combinada iniciada: {pdf_path}")
        
        results = {}
        
        # Verschiedene Methoden ausprobieren / Tentar diferentes métodos
        methods = [
            ('pdfplumber', self.extract_text_with_pdfplumber),
            ('pypdf2', self.extract_text_with_pypdf2),
            ('pymupdf', self.extract_text_with_pymupdf)
        ]
        
        for method_name, method_func in methods:
            try:
                result = method_func(pdf_path)
                results[method_name] = result
                logger.info(f"Extraktion mit {method_name}: {'Erfolgreich' if result['success'] else 'Fehlgeschlagen'}")
            except Exception as e:
                logger.error(f"Fehler bei {method_name}: {str(e)}")
                results[method_name] = {
                    'method': method_name,
                    'success': False,
                    'error': str(e)
                }
        
        # Bestes Ergebnis auswählen / Selecionar melhor resultado
        successful_results = [r for r in results.values() if r.get('success', False)]
        
        if successful_results:
            # Ergebnis mit dem meisten Text auswählen / Selecionar resultado com mais texto
            best_result = max(successful_results, key=lambda x: x.get('total_chars', 0))
            best_result['all_methods'] = results
            best_result['combined'] = True
            
            logger.info(f"Beste Extraktionsmethode ausgewählt / Melhor método de extração selecionado: {best_result['method']}")
            return best_result
        else:
            logger.error("Alle Extraktionsmethoden fehlgeschlagen / Todos os métodos de extração falharam")
            return {
                'method': 'combined',
                'success': False,
                'error': 'Alle Extraktionsmethoden fehlgeschlagen',
                'text': '',
                'all_methods': results,
                'combined': True
            }
    
    def validate_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Validiert PDF-Datei auf Lesbarkeit und Format
        Valida arquivo PDF para legibilidade e formato
        
        Args / Argumentos:
            pdf_path (str): Pfad zur PDF-Datei / Caminho para o arquivo PDF
            
        Returns / Retorna:
            Dict[str, Any]: Validierungsergebnis / Resultado da validação
        """
        # delega a implementação para o módulo refatorado
        from app.services.pdf_reader_pkg import extractors
        return extractors.validate_pdf(self, pdf_path)
    
    def extract_intelligent_data(self, text: str) -> Dict[str, Any]:
        """
        Extrahiert intelligente Vertragsdaten aus Text
        Extrai dados inteligentes de contrato do texto
        
        Args / Argumentos:
            text (str): Roher Text aus PDF / Texto bruto do PDF
            
        Returns / Retorna:
            Dict[str, Any]: Extrahierte Vertragsdaten / Dados de contrato extraídos
        """
        try:
            logger.info("Intelligente Datenextraktion gestartet / Extração inteligente de dados iniciada")
            # Extração básica / Grundlegende Extraktion
            extracted_data = {
                'title': self._extract_title(text),
                'client_name': self._extract_client_name(text),
                'client_email': self._extract_email(text),
                'client_phone': self._extract_phone(text),
                'client_address': self._extract_address(text),
                'money_values': self._extract_money_values(text),
                'dates': self._extract_dates(text),
                'terms_and_conditions': self._extract_terms_and_conditions(text),
                'description': self._extract_description(text)
            }
            
            # Extração avançada / Erweiterte Extraktion
            advanced_data = self.extract_advanced_context_data(text)
            extracted_data.update(advanced_data)

            logger.info("Intelligente Datenextraktion erfolgreich / Extração inteligente de dados bem-sucedida")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Fehler bei intelligenter Datenextraktion / Erro na extração inteligente de dados: {str(e)}")
            return {}
    
    def _extract_title(self, text: str) -> Optional[str]:
        from app.services.pdf_reader_pkg.parsers import extract_title
        return extract_title(text)
    
    def _extract_client_name(self, text: str) -> Optional[str]:
        from app.services.pdf_reader_pkg.parsers import extract_client_name
        return extract_client_name(text)
    
    def _extract_email(self, text: str) -> Optional[str]:
        from app.services.pdf_reader_pkg.parsers import extract_email
        return extract_email(text)
    
    def _extract_phone(self, text: str) -> Optional[str]:
        from app.services.pdf_reader_pkg.parsers import extract_phone
        return extract_phone(text)
    
    def _extract_address(self, text: str) -> Optional[str]:
        from app.services.pdf_reader_pkg.parsers import extract_address
        return extract_address(text)
    
    def _extract_money_values(self, text: str) -> Dict[str, Any]:
        from app.services.pdf_reader_pkg.financials import extract_money_values
        return extract_money_values(text)
    
    def _extract_dates(self, text: str) -> Dict[str, Any]:
        from app.services.pdf_reader_pkg.dates import extract_dates
        return extract_dates(text)
    
    def _extract_terms_and_conditions(self, text: str) -> Optional[str]:
        from app.services.pdf_reader_pkg.parsers import extract_terms_and_conditions
        return extract_terms_and_conditions(text)
    
    def _extract_description(self, text: str) -> Optional[str]:
        """Delegiert an pdf_reader_pkg.parsers.extract_description (lazy import)"""
        try:
            from app.services.pdf_reader_pkg.parsers import extract_description
            return extract_description(text)
        except Exception as e:
            logger.warning(f"Delegation der Beschreibungsextraktion fehlgeschlagen: {str(e)}")
            return None

    def calculate_notice_period(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Calcula período de aviso prévio / Berechnet Kündigungsfrist
        
        Args / Argumentos:
            text (str): Texto do contrato / Vertragstext
            
        Returns / Retorna:
            Optional[Dict[str, Any]]: Informações do período de aviso / Kündigungsfrist-Informationen
        """
        # Delegation to refactored dates module to avoid duplicating logic here.
        try:
            from app.services.pdf_reader_pkg.dates import calculate_notice_period as _calc
            return _calc(text)
        except Exception as e:
            logger.warning(f"Delegation der Kündigungsfrist-Berechnung fehlgeschlagen, fallback: {str(e)}")
            return None
    
    def extract_advanced_context_data(self, text: str) -> Dict[str, Any]:
        """
        Extrai dados contextuais avançados / Extrahiert erweiterte Kontextdaten
        
        Args / Argumentos:
            text (str): Texto do contrato / Vertragstext
            
        Returns / Retorna:
            Dict[str, Any]: Dados contextuais / Kontextdaten
        """
        try:
            logger.info("Erweiterte Kontextanalyse gestartet / Advanced context analysis started")
            
            context_data = {
                'notice_period': self.calculate_notice_period(text),
                'contract_complexity': self._analyze_contract_complexity(text),
                'key_terms': self._extract_key_terms(text),
                'legal_entities': self._extract_legal_entities(text),
                'financial_terms': self._extract_financial_terms(text)
            }
            logger.info("Erweiterte Kontextanalyse erfolgreich / Advanced context analysis successful")
            return context_data
            
        except Exception as e:
            logger.error(f"Fehler bei erweiterter Kontextanalyse / Error in advanced context analysis: {str(e)}")
            return {}
    
    def _analyze_contract_complexity(self, text: str) -> Dict[str, Any]:
        """Analisa complexidade do contrato / Analysiert Vertragskomplexität"""
        try:
            from app.services.pdf_reader_pkg.analysis import analyze_contract_complexity
            return analyze_contract_complexity(text)
        except Exception as e:
            logger.warning(f"Delegation der Komplexitätsanalyse fehlgeschlagen: {str(e)}")
            return {'complexity_score': 0.5, 'complexity_level': 'medium'}
    
    def _extract_key_terms(self, text: str) -> List[Dict[str, Any]]:
        try:
            from app.services.pdf_reader_pkg.analysis import extract_key_terms
            return extract_key_terms(text)
        except Exception as e:
            logger.warning(f"Delegation der Schlüsselbegriff-Extraktion fehlgeschlagen: {str(e)}")
            return []
    
    def _extract_legal_entities(self, text: str) -> List[Dict[str, Any]]:
        """Delegiert an pdf_reader_pkg.analysis.extract_legal_entities (lazy import)"""
        try:
            from app.services.pdf_reader_pkg.analysis import extract_legal_entities
            return extract_legal_entities(text)
        except Exception as e:
            logger.warning(f"Delegation der rechtlichen Entitätsextraktion fehlgeschlagen: {str(e)}")
            return []
    
    def _extract_financial_terms(self, text: str) -> Dict[str, Any]:
        """Delegiert an pdf_reader_pkg.financials.extract_financial_terms (lazy import)"""
        try:
            from app.services.pdf_reader_pkg.financials import extract_financial_terms
            return extract_financial_terms(text)
        except Exception as e:
            logger.warning(f"Delegation der finanziellen Begriffsextraktion fehlgeschlagen: {str(e)}")
            return {'payment_terms': [], 'penalties': [], 'discounts': [], 'taxes': []}