"""
Extrahierte Vertragsschemas für das Vertragsverwaltungssystem
Schemas de contrato extraído para o Sistema de Gerenciamento de Contratos

Dieses Modul enthält Pydantic-Schemas für extrahierte Vertragsdaten aus PDFs.
Este módulo contém schemas Pydantic para dados de contrato extraídos de PDFs.
Unterstützt Confidence-Scores und Validierung der extrahierten Daten.
Suporta Confidence-Scores e validação dos dados extraídos.
"""

from datetime import date, datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from enum import Enum

# Confidence-Score-Enumeration
class ConfidenceLevel(str, Enum):
    """Confidence-Level für extrahierte Daten / Nível de confiança para dados extraídos"""
    HIGH = "hoch"           # > 80%
    MEDIUM = "mittel"       # 50-80%
    LOW = "niedrig"         # < 50%
    UNKNOWN = "unbekannt"   # Nicht extrahiert / Não extraído

# Extrahierte Vertragsdaten
class ExtractedContractDraft(BaseModel):
    """
    Schema für extrahierte Vertragsdaten aus PDF
    Schema para dados de contrato extraídos de PDF
    
    Enthält alle möglichen Felder mit Confidence-Scores.
    Contém todos os campos possíveis com Confidence-Scores.
    """
    
    # Grundlegende Informationen / Informações básicas
    title: Optional[str] = Field(None, description="Extrahierter Vertragstitel / Título do contrato extraído")
    title_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Titel / Score de confiança para título")
    
    description: Optional[str] = Field(None, description="Extrahierte Beschreibung / Descrição extraída")
    description_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Beschreibung / Score de confiança para descrição")
    
    # Parteien / Partes
    client_name: Optional[str] = Field(None, description="Extrahierter Kundenname / Nome do cliente extraído")
    client_name_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Kundenname / Score de confiança para nome do cliente")
    
    client_document: Optional[str] = Field(None, description="Extrahierte Kundendokumentnummer / Número do documento do cliente extraído")
    client_document_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Kundendokument / Score de confiança para documento do cliente")
    
    client_email: Optional[str] = Field(None, description="Extrahierte Kunden-E-Mail / E-mail do cliente extraído")
    client_email_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für E-Mail / Score de confiança para e-mail")
    
    client_phone: Optional[str] = Field(None, description="Extrahierte Telefonnummer / Telefone extraído")
    client_phone_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Telefon / Score de confiança para telefone")
    
    client_address: Optional[str] = Field(None, description="Extrahierte Adresse / Endereço extraído")
    client_address_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Adresse / Score de confiança para endereço")
    
    # Finanzielle Informationen / Informações financeiras
    value: Optional[str] = Field(None, description="Extrahierter Vertragswert / Valor do contrato extraído")
    value_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Wert / Score de confiança para valor")
    
    currency: Optional[str] = Field(None, description="Extrahierte Währung / Moeda extraída")
    currency_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Währung / Score de confiança para moeda")
    
    # Datumsinformationen / Informações de datas
    start_date: Optional[str] = Field(None, description="Extrahierter Starttermin / Data de início extraída")
    start_date_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Startdatum / Score de confiança para data de início")
    
    end_date: Optional[str] = Field(None, description="Extrahierter Endtermin / Data de fim extraída")
    end_date_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Enddatum / Score de confiança para data de fim")
    
    renewal_date: Optional[str] = Field(None, description="Extrahierter Verlängerungstermin / Data de renovação extraída")
    renewal_date_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Verlängerungsdatum / Score de confiança para data de renovação")
    
    # Zusätzliche Informationen / Informações adicionais
    terms_and_conditions: Optional[str] = Field(None, description="Extrahierte AGB / Termos e condições extraídos")
    terms_and_conditions_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für AGB / Score de confiança para termos")
    
    notes: Optional[str] = Field(None, description="Extrahierte Notizen / Notas extraídas")
    notes_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Notizen / Score de confiança para notas")
    
    # Metadaten der Extraktion / Metadados da extração
    extraction_method: str = Field(..., description="Verwendete Extraktionsmethode / Método de extração usado")
    extraction_timestamp: datetime = Field(default_factory=datetime.now, description="Zeitstempel der Extraktion / Timestamp da extração")
    
    raw_text: str = Field(..., description="Roher extrahierter Text / Texto extraído bruto")
    raw_text_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence-Score für Rohtext / Score de confiança para texto bruto")
    
    # Zusätzliche Metadaten / Metadados adicionais
    pdf_metadata: Dict[str, Any] = Field(default_factory=dict, description="PDF-Metadaten / Metadados do PDF")
    extraction_errors: List[str] = Field(default_factory=list, description="Extraktionsfehler / Erros de extração")
    
    # Gesamtbewertung / Avaliação geral
    overall_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Gesamt-Confidence-Score / Score de confiança geral")
    confidence_level: ConfidenceLevel = Field(ConfidenceLevel.UNKNOWN, description="Confidence-Level / Nível de confiança")
    
    @field_validator('overall_confidence', mode='before')
    @classmethod
    def calculate_overall_confidence(cls, v, info):
        """
        Berechnet den Gesamt-Confidence-Score
        Calcula o score de confiança geral
        """
        confidence_fields = [
            'title_confidence', 'description_confidence', 'client_name_confidence',
            'client_document_confidence', 'client_email_confidence', 'client_phone_confidence',
            'client_address_confidence', 'value_confidence', 'currency_confidence',
            'start_date_confidence', 'end_date_confidence', 'renewal_date_confidence',
            'terms_and_conditions_confidence', 'notes_confidence', 'raw_text_confidence'
        ]
        
        values_data = info.data if hasattr(info, 'data') else {}
        scores = [values_data.get(field, 0.0) for field in confidence_fields]
        non_zero_scores = [score for score in scores if score > 0]
        
        if non_zero_scores:
            return sum(non_zero_scores) / len(non_zero_scores)
        return 0.0
    
    @field_validator('confidence_level', mode='before')
    @classmethod
    def determine_confidence_level(cls, v, info):
        """
        Bestimmt das Confidence-Level basierend auf dem Gesamtscore
        Determina o nível de confiança baseado no score geral
        """
        values_data = info.data if hasattr(info, 'data') else {}
        overall_confidence = values_data.get('overall_confidence', 0.0)
        
        if overall_confidence >= 0.8:
            return ConfidenceLevel.HIGH
        elif overall_confidence >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif overall_confidence > 0.0:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.UNKNOWN
    
    def get_high_confidence_fields(self) -> Dict[str, Any]:
        """
        Gibt Felder mit hoher Confidence zurück
        Retorna campos com alta confiança
        
        Returns / Retorna:
            Dict[str, Any]: Felder mit Confidence > 0.8 / Campos com confiança > 0.8
        """
        high_confidence_fields = {}
        
        for field_name in self.__fields__:
            if field_name.endswith('_confidence'):
                base_field = field_name.replace('_confidence', '')
                confidence_value = getattr(self, field_name, 0.0)
                
                if confidence_value > 0.8:
                    field_value = getattr(self, base_field, None)
                    if field_value:
                        high_confidence_fields[base_field] = {
                            'value': field_value,
                            'confidence': confidence_value
                        }
        
        return high_confidence_fields
    
    def get_medium_confidence_fields(self) -> Dict[str, Any]:
        """
        Gibt Felder mit mittlerer Confidence zurück
        Retorna campos com confiança média
        
        Returns / Retorna:
            Dict[str, Any]: Felder mit Confidence 0.5-0.8 / Campos com confiança 0.5-0.8
        """
        medium_confidence_fields = {}
        
        for field_name in self.__fields__:
            if field_name.endswith('_confidence'):
                base_field = field_name.replace('_confidence', '')
                confidence_value = getattr(self, field_name, 0.0)
                
                if 0.5 <= confidence_value <= 0.8:
                    field_value = getattr(self, base_field, None)
                    if field_value:
                        medium_confidence_fields[base_field] = {
                            'value': field_value,
                            'confidence': confidence_value
                        }
        
        return medium_confidence_fields
    
    def get_low_confidence_fields(self) -> Dict[str, Any]:
        """
        Gibt Felder mit niedriger Confidence zurück
        Retorna campos com baixa confiança
        
        Returns / Retorna:
            Dict[str, Any]: Felder mit Confidence < 0.5 / Campos com confiança < 0.5
        """
        low_confidence_fields = {}
        
        for field_name in self.__fields__:
            if field_name.endswith('_confidence'):
                base_field = field_name.replace('_confidence', '')
                confidence_value = getattr(self, field_name, 0.0)
                
                if 0.0 < confidence_value < 0.5:
                    field_value = getattr(self, base_field, None)
                    if field_value:
                        low_confidence_fields[base_field] = {
                            'value': field_value,
                            'confidence': confidence_value
                        }
        
        return low_confidence_fields
    
    def get_extraction_summary(self) -> Dict[str, Any]:
        """
        Gibt eine Zusammenfassung der Extraktion zurück
        Retorna um resumo da extração
        
        Returns / Retorna:
            Dict[str, Any]: Extraktionszusammenfassung / Resumo da extração
        """
        return {
            'overall_confidence': self.overall_confidence,
            'confidence_level': self.confidence_level.value,
            'extraction_method': self.extraction_method,
            'extraction_timestamp': self.extraction_timestamp,
            'high_confidence_fields': len(self.get_high_confidence_fields()),
            'medium_confidence_fields': len(self.get_medium_confidence_fields()),
            'low_confidence_fields': len(self.get_low_confidence_fields()),
            'total_fields_extracted': len([f for f in self.__fields__ if not f.endswith('_confidence') and getattr(self, f, None) is not None]),
            'extraction_errors': self.extraction_errors,
            'raw_text_length': len(self.raw_text)
        }

# Schema für Extraktionsanfrage
class ExtractionRequest(BaseModel):
    """
    Schema für Extraktionsanfrage
    Schema para solicitação de extração
    """
    pdf_path: str = Field(..., description="Pfad zur PDF-Datei / Caminho para o arquivo PDF")
    extraction_method: str = Field("combined", description="Extraktionsmethode / Método de extração")
    language: str = Field("de", description="Sprache für OCR / Idioma para OCR")
    include_ocr: bool = Field(True, description="OCR einschließen / Incluir OCR")

# Schema für Extraktionsantwort
class ExtractionResponse(BaseModel):
    """
    Schema für Extraktionsantwort
    Schema para resposta de extração
    """
    success: bool = Field(..., description="Erfolg der Extraktion / Sucesso da extração")
    extracted_data: Optional[ExtractedContractDraft] = Field(None, description="Extrahierte Daten / Dados extraídos")
    error_message: Optional[str] = Field(None, description="Fehlermeldung / Mensagem de erro")
    processing_time: float = Field(..., description="Verarbeitungszeit in Sekunden / Tempo de processamento em segundos")
    file_size: int = Field(..., description="Dateigröße in Bytes / Tamanho do arquivo em bytes")
    # Metadaten des hochgeladenen Originals (optional)
    original_file_name: Optional[str] = Field(None, description="Original hochgeladene PDF-Datei")
    original_file_sha256: Optional[str] = Field(None, description="SHA256 Hash der Original-PDF")
    original_file_storage_name: Optional[str] = Field(None, description="Interner Dateiname im Upload-Ordner / Nome de armazenamento interno")
    ocr_text_sha256: Optional[str] = Field(None, description="SHA256 des normalisierten OCR-Texts")
    uploaded_at: Optional[datetime] = Field(None, description="Zeitpunkt des Uploads (UTC)")
    temp_file_path: Optional[str] = Field(None, description="Temporärer Dateipfad für Bewegung / Caminho temporário para movimentação")
