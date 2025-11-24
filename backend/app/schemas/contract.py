"""
Vertragsschemas für das Vertragsverwaltungssystem

Dieses Modul enthält Pydantic-Schemas für die Validierung und Serialisierung von Vertragsdaten.
Verschiedene Schemas werden für verschiedene Operationen verwendet (erstellen, aktualisieren, antworten).
"""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator, ValidationInfo, ConfigDict, field_serializer
from enum import Enum
import re
from typing import Optional as _Opt


# --- Extraction metadata schema (optional payload for create) ---
class ExtractionMetadata(BaseModel):
    """Metadaten, wie sie von der Extraktion/Upload zurückgeliefert werden."""
    original_file_name: _Opt[str] = Field(None, description="Original hochgeladene PDF-Datei")
    original_file_storage_name: _Opt[str] = Field(None, description="Interner Dateiname im Upload-Ordner")
    original_file_sha256: _Opt[str] = Field(None, description="SHA256 Hash der Original-PDF")
    ocr_text: _Opt[str] = Field(None, description="Extrahierter OCR-Text (optional)")
    ocr_text_sha256: _Opt[str] = Field(None, description="SHA256 des OCR-Texts")
    uploaded_at: _Opt[datetime] = Field(None, description="Zeitpunkt des Uploads (UTC)")

#enum für Vertragsstatus
class ContractStatus(str, Enum):
    """vertragsstatus-Enumeration"""
    DRAFT = "entwurf"                       
    ACTIVE = "aktiv"        
    EXPIRED = "abgelaufen"
    TERMINATED = "beendet"
    PENDING_APPROVAL = "wartet_auf_genehmigung"

#enum für Vertragstyp
class ContractType(str, Enum):
    """vertragstyp-Enumeration"""
    SERVICE = "dienstleistung"
    PRODUCT = "produkt"
    EMPLOYMENT = "beschäftigung"
    LEASE = "miete"
    PARTNERSHIP = "partnerschaft"
    OTHER = "sonstiges"

#basisschema mit gemeinsamen feldern
class ContractBase(BaseModel):
    """basisschema mit gemeinsamen vertragsfeldern"""
    title: str = Field(..., min_length=2, max_length=200, description="Vertrags titel")
    description: Optional[str] = Field(None, max_length=1000, description="Vertragsbeschreibung")
    contract_type: ContractType = Field(default=ContractType.OTHER, description="Vertragstyp")
    status: ContractStatus = Field(default=ContractStatus.DRAFT, description="Vertragsstatus")

   #Finanzfelder
    value: Optional[Decimal] = Field (None, ge=0, description="")
    currency: str =Field(default="EUR", min_length=3, max_length=3, description="Währungscode (ISO 4217)")

    #Datumsfelder
    start_date: date=Field(..., description="Vertragsbeginn")
    end_date: Optional[date] = Field(None, description="Vertragsende")
    renewal_date: Optional[date] = Field(None, description="Verlängerungsdatum")


    #Beteiligte Parteien
    client_name: str = Field(..., min_length=2, max_length=200, description="Kunden-/Auftragnehmername") #z.B. Firma oder Einzelperso
    client_document: Optional[str] = Field(None, max_length=20, description="Kundendokument") #z.B. Steuernummer, Handelsregisternummer
    client_address: Optional[str] = Field(None, max_length=300, description="Kundenadresse (Rechnungsadresse)")
    client_email: Optional[str] = Field(None, max_length=100, description="Kunden-E-Mail")
    client_phone: Optional[str] = Field(None, max_length=20, description="Kundentelefonnummer")

    #Zusätzliche Felder
    terms_and_conditions: Optional[str] = Field(None, description="Allgemeine Geschäftsbedingungen")
    notes: Optional[str] = Field(None, max_length=500, description="Zusätzliche Notizen")

    @field_validator('end_date')
    @classmethod
    def validate_end_date(cls, v, info: ValidationInfo):
        """Überprüft, ob das Enddatum nach dem Startdatum liegt"""
        if v and 'start_date' in info.data and v <= info.data['start_date']:
            raise ValueError('Das Enddatum muss nach dem Startdatum liegen.')
        return v
    
    @field_validator('client_document')
    def validate_client_document(cls, v):
        """Überprüft des Kundendokumentformats"""
        if v: 
            # Akzeptiere jedes Format, das Zahlen, / und - enthält
            if not re.match(r'^[\d/-]+$', v):
                raise ValueError('Kundendokument darf nur Zahlen, / und - enthalten.')
        return v
    
# Schema zum Erstellen eines neuen Vertrags
class ContractCreate(ContractBase):
    """Schema zum Erstellen eines neuen Vertrags

    Optional: `extraction_metadata` kann Metadaten enthalten, die von
    `/contracts/import`/`/contracts/import/upload` zurückgegeben werden.
    Wenn vorhanden, wird die Datei automatisch an den erstellten Vertrag angehängt.
    """
    extraction_metadata: Optional[ExtractionMetadata] = Field(None, description="Metadaten der extrahierten/uploaded PDF, optional")

# Schema zum Aktualisieren von Vertragsdaten
class ContractUpdate(BaseModel):
    """Schema zum Aktualisieren von Vertragsdaten"""
    title: Optional[str] = Field(None, min_length=3, max_length=200, description="Vertragstitel")
    description: Optional[str] = Field(None, max_length=1000, description="Vertragsbeschreibung")
    contract_type: Optional[ContractType] = Field(None, description="Vertragstyp")
    status: Optional[ContractStatus] = Field(None, description="Vertragsstatus")

    # Finanzfelder
    value: Optional[Decimal] = Field(None, ge=0, description="Vertragswert")
    currency: Optional[str] = Field(None, max_length=3, description="Währungscode")

    # Datumsfelder
    start_date: Optional[date] = Field(None, description="Vertragsbeginn")
    end_date: Optional[date] = Field(None, description="Vertragsende")
    renewal_date: Optional[date] = Field(None, description="Vertragsverlängerungsdatum")

    # Beteiligte Parteien
    client_name: Optional[str] = Field(None, min_length=2, max_length=200, description="Kunden-/Auftragnehmername")
    client_document: Optional[str] = Field(None, max_length=20, description="Kundendokument")
    client_email: Optional[str] = Field(None, max_length=100, description="Kunden-E-Mail")
    client_phone: Optional[str] = Field(None, max_length=20, description="Kundentelefon")
    client_address: Optional[str] = Field(None, max_length=200, description="Kundenadresse")

    # Zusätzliche Felder
    terms_and_conditions: Optional[str] = Field(None, description="Geschäftsbedingungen")
    notes: Optional[str] = Field(None, max_length=500, description="Zusätzliche Notizen")
    
    # Schemas für RentStep (Mietstaffelung)
    class RentStepBase(BaseModel):
        """Basisschema für eine Mietstaffelung (zukünftige Mietanpassung)."""
        effective_date: date = Field(..., description="Datum, an dem der Betrag wirksam wird")
        amount: Decimal = Field(..., ge=0, description="Betrag in Vertragswährung")
        currency: Optional[str] = Field(None, min_length=3, max_length=3, description="ISO 4217 Währungscode (optional)")
        note: Optional[str] = Field(None, max_length=300, description="Optionaler Hinweis")

    class RentStepCreate(RentStepBase):
        """Schema zum Erstellen einer RentStep"""
        pass

    class RentStepUpdate(BaseModel):
        effective_date: Optional[date] = Field(None, description="Neues Wirksamkeitsdatum")
        amount: Optional[Decimal] = Field(None, ge=0, description="Neuer Betrag")
        currency: Optional[str] = Field(None, min_length=3, max_length=3, description="ISO 4217 Währungscode (optional)")
        note: Optional[str] = Field(None, max_length=300, description="Optionaler Hinweis")

    class RentStepResponse(RentStepBase):
        model_config = ConfigDict(from_attributes=True)
        
        id: int = Field(..., description="Eindeutige ID der RentStep")
        contract_id: int = Field(..., description="ID des zugehörigen Vertrags")
        
        @field_serializer('amount')
        def serialize_amount(self, amount: Decimal) -> float:
            return float(amount)
        
        @field_serializer('effective_date')
        def serialize_date(self, dt: date) -> str:
            return dt.isoformat()

# Schema für API-Antworten (enthält Benutzerinformationen)
class RentStepBase(BaseModel):
    """Basisschema für eine Mietstaffelung (zukünftige Mietanpassung)."""
    effective_date: date = Field(..., description="Datum, an dem der Betrag wirksam wird")
    amount: Decimal = Field(..., ge=0, description="Betrag in Vertragswährung")
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="ISO 4217 Währungscode (optional)")
    note: Optional[str] = Field(None, max_length=300, description="Optionaler Hinweis")


class RentStepCreate(RentStepBase):
    """Schema zum Erstellen einer RentStep"""
    pass


class RentStepUpdate(BaseModel):
    effective_date: Optional[date] = Field(None, description="Neues Wirksamkeitsdatum")
    amount: Optional[Decimal] = Field(None, ge=0, description="Neuer Betrag")
    currency: Optional[str] = Field(None, min_length=3, max_length=3, description="ISO 4217 Währungscode (optional)")
    note: Optional[str] = Field(None, max_length=300, description="Optionaler Hinweis")


class RentStepResponse(RentStepBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Eindeutige ID der RentStep")
    contract_id: int = Field(..., description="ID des zugehörigen Vertrags")
    
    @field_serializer('amount')
    def serialize_amount(self, amount: Decimal) -> float:
        return float(amount) if amount else 0.0
    
    @field_serializer('effective_date')
    def serialize_date(self, dt: date) -> str:
        return dt.isoformat()


class ContractResponse(ContractBase):
    """Schema für Vertragsdaten in API-Antworten"""
    id: int = Field(..., description="Eindeutige Vertrags-ID")
    created_by: int = Field(..., description="Benutzer-ID, die den Vertrag erstellt hat")
    created_at: datetime = Field(..., description="Vertragserstellungszeitstempel")
    updated_at: Optional[datetime] = Field(None, description="Zeitstempel der letzten Aktualisierung")
    # Mietstaffelungen (zukünftige Anpassungen)
    rent_steps: Optional[List["RentStepResponse"]] = Field(default_factory=list, description="Liste der zukünftigen Mietstaffelungen")
    # Original-PDF Metadaten (optional)
    original_pdf_filename: Optional[str] = Field(None, description="Original hochgeladene PDF-Datei")
    original_pdf_sha256: Optional[str] = Field(None, description="SHA256 Hash der Original-PDF")
    uploaded_at: Optional[datetime] = Field(None, description="Zeitpunkt des Uploads der Original-PDF (UTC)")

    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('value', when_used='unless-none')
    def serialize_value(self, value: Decimal) -> float:
        return float(value)
    
    @field_serializer('start_date', 'end_date', 'renewal_date', when_used='unless-none')
    def serialize_dates(self, dt: date) -> str:
        return dt.isoformat()
    
    @field_serializer('created_at', 'updated_at', 'uploaded_at', when_used='unless-none')
    def serialize_datetimes(self, dt: datetime) -> str:
        return dt.isoformat()

# Schema für Vertragsdaten in der Datenbank
class ContractInDB(ContractBase):
    """Schema für Vertragsdaten wie in der Datenbank gespeichert"""
    id: int = Field(..., description="Eindeutige Vertrags-ID")
    created_by: int = Field(..., description="Benutzer-ID, die den Vertrag erstellt hat")
    created_at: datetime = Field(..., description="Vertragserstellungszeitstempel")
    updated_at: Optional[datetime] = Field(None, description="Zeitstempel der letzten Aktualisierung")
    rent_steps: Optional[List["RentStepResponse"]] = Field(default_factory=list, description="Liste der zukünftigen Mietstaffelungen")
    # Original-PDF Metadaten
    original_pdf_path: Optional[str] = Field(None, description="Serverinterner Pfad zur Original-PDF (internal)")
    original_pdf_filename: Optional[str] = Field(None, description="Original hochgeladene PDF-Datei")
    original_pdf_sha256: Optional[str] = Field(None, description="SHA256 Hash der Original-PDF")
    ocr_text_sha256: Optional[str] = Field(None, description="SHA256 des OCR-Texts")
    uploaded_at: Optional[datetime] = Field(None, description="Zeitpunkt des Uploads der Original-PDF")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('value', when_used='unless-none')
    def serialize_value(self, value: Decimal) -> float:
        return float(value)
    
    @field_serializer('start_date', 'end_date', 'renewal_date', when_used='unless-none')
    def serialize_dates(self, dt: date) -> str:
        return dt.isoformat()
    
    @field_serializer('created_at', 'updated_at', 'uploaded_at', when_used='unless-none')
    def serialize_datetimes(self, dt: datetime) -> str:
        return dt.isoformat()

# Schema für Vertragslisten-Antworten
class ContractListResponse(BaseModel):
    """Schema für Vertragslisten in API-Antworten"""
    contracts: List[ContractResponse] = Field(..., description="Liste der Verträge")
    total: int = Field(..., description="Gesamtanzahl der Verträge")
    page: int = Field(..., description="Aktuelle Seitennummer")
    per_page: int = Field(..., description="Anzahl der Verträge pro Seite")
    
    model_config = ConfigDict(from_attributes=True)
# Schema für Vertragsstatistiken
class ContractStats(BaseModel):
    """Schema für Vertragsstatistiken"""
    total_contracts: int = Field(..., description="Gesamtanzahl der Verträge")
    active_contracts: int = Field(..., description="Anzahl der aktiven Verträge")
    expired_contracts: int = Field(..., description="Anzahl der abgelaufenen Verträge")
    draft_contracts: int = Field(..., description="Anzahl der Entwurfsverträge")
    total_value: Decimal = Field(..., description="Gesamtwert aller Verträge")
    currency: str = Field(..., description="Für den Gesamtwert verwendete Währung")
    
    model_config = ConfigDict(from_attributes=True)
    
    @field_serializer('total_value')
    def serialize_total_value(self, value: Decimal) -> float:
        return float(value)