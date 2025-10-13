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
import fitz  # pymupdf
import pdfplumber
import PyPDF2
import pytesseract
from PIL import Image
import io
import dateparser
import spacy
from spacy.matcher import Matcher

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
        
        # Spacy-Modell laden / Carregar modelo Spacy
        try:
            self.nlp = spacy.load("de_core_news_sm")
            logger.info("Deutsches Spacy-Modell geladen / Modelo Spacy alemão carregado")
        except OSError:
            logger.warning("Deutsches Spacy-Modell nicht gefunden / Modelo Spacy alemão não encontrado")
            self.nlp = None
        
        logger.info("PDF-Reader-Service initialisiert / PDF Reader Service initialized")
    
    def extract_text_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrahiert Text aus PDF mit pdfplumber
        Extrai texto de PDF com pdfplumber
        
        Args / Argumentos:
            pdf_path (str): Pfad zur PDF-Datei / Caminho para o arquivo PDF
            
        Returns / Retorna:
            Dict[str, Any]: Extrahierter Text und Metadaten / Texto extraído e metadados
        """
        try:
            logger.info(f"Textextraktion mit pdfplumber gestartet / Extração de texto com pdfplumber iniciada: {pdf_path}")
            
            text_content = []
            metadata = {}
            
            with pdfplumber.open(pdf_path) as pdf:
                # Metadaten extrahieren / Extrair metadados
                metadata = {
                    'pages': len(pdf.pages),
                    'title': pdf.metadata.get('Title', ''),
                    'author': pdf.metadata.get('Author', ''),
                    'creator': pdf.metadata.get('Creator', ''),
                    'producer': pdf.metadata.get('Producer', ''),
                    'creation_date': pdf.metadata.get('CreationDate', ''),
                    'modification_date': pdf.metadata.get('ModDate', '')
                }
                
                # Text von jeder Seite extrahieren / Extrair texto de cada página
                for page_num, page in enumerate(pdf.pages, 1):
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
            logger.error(f"Fehler bei pdfplumber-Extraktion / Erro na extração com pdfplumber: {str(e)}")
            return {
                'method': 'pdfplumber',
                'success': False,
                'error': str(e),
                'text': '',
                'pages': [],
                'metadata': {}
            }
    
    def extract_text_with_pypdf2(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrahiert Text aus PDF mit PyPDF2
        Extrai texto de PDF com PyPDF2
        
        Args / Argumentos:
            pdf_path (str): Pfad zur PDF-Datei / Caminho para o arquivo PDF
            
        Returns / Retorna:
            Dict[str, Any]: Extrahierter Text und Metadaten / Texto extraído e metadados
        """
        try:
            logger.info(f"Textextraktion mit PyPDF2 gestartet / Extração de texto com PyPDF2 iniciada: {pdf_path}")
            
            text_content = []
            metadata = {}
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Metadaten extrahieren / Extrair metadados
                if pdf_reader.metadata:
                    metadata = {
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
                
                # Text von jeder Seite extrahieren / Extrair texto de cada página
                for page_num, page in enumerate(pdf_reader.pages, 1):
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
            logger.error(f"Fehler bei PyPDF2-Extraktion / Erro na extração com PyPDF2: {str(e)}")
            return {
                'method': 'pypdf2',
                'success': False,
                'error': str(e),
                'text': '',
                'pages': [],
                'metadata': {}
            }
    
    def extract_text_with_pymupdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extrahiert Text aus PDF mit pymupdf (fitz)
        Extrai texto de PDF com pymupdf (fitz)
        
        Args / Argumentos:
            pdf_path (str): Pfad zur PDF-Datei / Caminho para o arquivo PDF
            
        Returns / Retorna:
            Dict[str, Any]: Extrahierter Text und Metadaten / Texto extraído e metadados
        """
        try:
            logger.info(f"Textextraktion mit pymupdf gestartet / Extração de texto com pymupdf iniciada: {pdf_path}")
            
            text_content = []
            metadata = {}
            
            doc = fitz.open(pdf_path)
            
            # Metadaten extrahieren / Extrair metadados
            metadata = {
                'title': doc.metadata.get('title', ''),
                'author': doc.metadata.get('author', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'modification_date': doc.metadata.get('modDate', '')
            }
            
            # Text von jeder Seite extrahieren / Extrair texto de cada página
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text:
                    text_content.append({
                        'page': page_num + 1,
                        'text': page_text,
                        'char_count': len(page_text)
                    })
            
            doc.close()
            
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
            logger.error(f"Fehler bei pymupdf-Extraktion / Erro na extração com pymupdf: {str(e)}")
            return {
                'method': 'pymupdf',
                'success': False,
                'error': str(e),
                'text': '',
                'pages': [],
                'metadata': {}
            }
    
    def ocr_with_pytesseract(self, image_path: str, language: str = 'deu') -> Dict[str, Any]:
        """
        Führt OCR mit pytesseract durch
        Executa OCR com pytesseract
        
        Args / Argumentos:
            image_path (str): Pfad zur Bilddatei / Caminho para o arquivo de imagem
            language (str): OCR-Sprache / Idioma do OCR
            
        Returns / Retorna:
            Dict[str, Any]: OCR-Ergebnis / Resultado do OCR
        """
        try:
            logger.info(f"OCR mit pytesseract gestartet / OCR com pytesseract iniciado: {image_path}")
            
            # Bild laden / Carregar imagem
            image = Image.open(image_path)
            
            # OCR durchführen / Executar OCR
            text = pytesseract.image_to_string(image, lang=language)
            
            # Zusätzliche Informationen / Informações adicionais
            data = pytesseract.image_to_data(image, lang=language, output_type=pytesseract.Output.DICT)
            
            result = {
                'method': 'pytesseract',
                'success': True,
                'text': text,
                'confidence': sum([int(conf) for conf in data['conf'] if int(conf) > 0]) / len([conf for conf in data['conf'] if int(conf) > 0]) if data['conf'] else 0,
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
        try:
            logger.info(f"PDF-Validierung gestartet / Validação de PDF iniciada: {pdf_path}")
            
            if not os.path.exists(pdf_path):
                return {
                    'valid': False,
                    'error': 'Datei nicht gefunden / Arquivo não encontrado',
                    'file_size': 0
                }
            
            file_size = os.path.getsize(pdf_path)
            
            # Dateigröße prüfen / Verificar tamanho do arquivo
            if file_size == 0:
                return {
                    'valid': False,
                    'error': 'Leere Datei / Arquivo vazio',
                    'file_size': file_size
                }
            
            # PDF-Format prüfen / Verificar formato PDF
            try:
                with open(pdf_path, 'rb') as file:
                    header = file.read(4)
                    if header != b'%PDF':
                        return {
                            'valid': False,
                            'error': 'Ungültiges PDF-Format / Formato PDF inválido',
                            'file_size': file_size
                        }
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Fehler beim Lesen der Datei / Erro ao ler arquivo: {str(e)}',
                    'file_size': file_size
                }
            
            logger.info(f"PDF-Validierung erfolgreich / Validação de PDF bem-sucedida: {file_size} Bytes")
            return {
                'valid': True,
                'file_size': file_size,
                'message': 'PDF-Datei ist gültig / Arquivo PDF é válido'
            }
            
        except Exception as e:
            logger.error(f"Fehler bei PDF-Validierung / Erro na validação de PDF: {str(e)}")
            return {
                'valid': False,
                'error': str(e),
                'file_size': 0
            }
    
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
            
            logger.info("Intelligente Datenextraktion erfolgreich / Extração inteligente de dados bem-sucedida")
            return extracted_data
            
        except Exception as e:
            logger.error(f"Fehler bei intelligenter Datenextraktion / Erro na extração inteligente de dados: {str(e)}")
            return {}
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extrahiert Vertragstitel / Extrai título do contrato"""
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
            
            # Fallback: Erste Zeile als Titel / Fallback: primeira linha como título
            first_line = text.split('\n')[0].strip()
            if len(first_line) > 5 and len(first_line) < 100:
                return first_line
            
            return None
            
        except Exception as e:
            logger.error(f"Fehler bei Titel-Extraktion / Erro na extração de título: {str(e)}")
            return None
    
    def _extract_client_name(self, text: str) -> Optional[str]:
        """Extrahiert Kundenname / Extrai nome do cliente"""
        try:
            for pattern in self.patterns['company_patterns']:
                matches = re.findall(pattern, text)
                if matches:
                    return max(matches, key=len)
            
            between_pattern = r'zwischen\s+([^,\n]+)'
            match = re.search(between_pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
            
            return None
            
        except Exception as e:
            logger.error(f"Fehler bei Kundenname-Extraktion / Erro na extração de nome do cliente: {str(e)}")
            return None
    
    def _extract_email(self, text: str) -> Optional[str]:
        """Extrahiert E-Mail-Adressen / Extrai endereços de e-mail"""
        try:
            for pattern in self.patterns['email_patterns']:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0]
            return None
        except Exception as e:
            logger.error(f"Fehler bei E-Mail-Extraktion / Erro na extração de e-mail: {str(e)}")
            return None
    
    def _extract_phone(self, text: str) -> Optional[str]:
        """Extrahiert Telefonnummern / Extrai números de telefone"""
        try:
            for pattern in self.patterns['phone_patterns']:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0]
            return None
        except Exception as e:
            logger.error(f"Fehler bei Telefon-Extraktion / Erro na extração de telefone: {str(e)}")
            return None
    
    def _extract_address(self, text: str) -> Optional[str]:
        """Extrahiert Adressen / Extrai endereços"""
        try:
            address_patterns = [
                r'([A-ZÄÖÜ][a-zäöüß]+\s+\d+[a-z]?,\s*\d{5}\s+[A-ZÄÖÜ][a-zäöüß]+)',
                r'([A-ZÄÖÜ][a-zäöüß]+\s+\d+[a-z]?,\s*\d{5})',
            ]
            
            for pattern in address_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    return matches[0]
            return None
        except Exception as e:
            logger.error(f"Fehler bei Adress-Extraktion / Erro na extração de endereço: {str(e)}")
            return None
    
    def _extract_money_values(self, text: str) -> Dict[str, Any]:
        """Extrahiert Geldbeträge / Extrai valores monetários"""
        try:
            money_values = []
            currencies = []
            
            for pattern in self.patterns['money_patterns']:
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
                
                return {
                    'value': highest_value,
                    'currency': currency,
                    'confidence': 0.8
                }
            
            return {'value': None, 'currency': None, 'confidence': 0.0}
            
        except Exception as e:
            logger.error(f"Fehler bei Geldbetrag-Extraktion / Erro na extração de valor monetário: {str(e)}")
            return {'value': None, 'currency': None, 'confidence': 0.0}
    
    def _extract_dates(self, text: str) -> Dict[str, Any]:
        """Extrahiert Datumsangaben / Extrai datas"""
        try:
            dates = []
            
            for pattern in self.patterns['date_patterns']:
                matches = re.findall(pattern, text)
                for match in matches:
                    parsed_date = dateparser.parse(match, languages=['de'])
                    if parsed_date:
                        dates.append({
                            'raw': match,
                            'parsed': parsed_date,
                            'confidence': 0.8
                        })
            
            # Datumsangaben nach Kontext kategorisieren / Categorizar datas por contexto
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
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'renewal_date': renewal_date
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Datums-Extraktion / Erro na extração de datas: {str(e)}")
            return {
                'start_date': None,
                'end_date': None,
                'renewal_date': None
            }
    
    def _extract_terms_and_conditions(self, text: str) -> Optional[str]:
        """Extrahiert AGB und Bedingungen / Extrai termos e condições"""
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
            logger.error(f"Fehler bei AGB-Extraktion / Erro na extração de termos: {str(e)}")
            return None
    
    def _extract_description(self, text: str) -> Optional[str]:
        """Extrahiert Beschreibung / Extrai descrição"""
        try:
            sentences = text.split('.')[:3]
            description = '. '.join(sentences).strip()
            
            if len(description) > 20 and len(description) < 500:
                return description
            
            return None
            
        except Exception as e:
            logger.error(f"Fehler bei Beschreibungs-Extraktion / Erro na extração de descrição: {str(e)}")
            return None
