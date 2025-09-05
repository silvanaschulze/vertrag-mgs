"""
Vertragsschemas für das Vertragsverwaltungssystem

Dieses Modul enthält Pydantic-Schemas für die Validierung und Serialisierung von Vertragsdaten.
Verschiedene Schemas werden für verschiedene Operationen verwendet (erstellen, aktualisieren, antworten).
"""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator
from enum import Enum
import re

#enum für Vertragsstatus
class ContractStatus(str, Enum):
    """vertragsstatus-Enumeration"""
    DRAFT = "entwurf"                       
    ACTIVE = "aaktiv"        
    EXPIRED = "abgelaufen"
    TERMINATED = "beendet"
    PENDING_APROVAL = "wartet_auf_genehmigung"

#enum für Vertragstyp
class ContractType(str, Enum):
    """vertragstyp-Enumeration"""
    SERVICE = "dienstleistung"
    PRODUCT = "produkt"
    EMPLOYMENT = "beschäftigung"
    LASASE = "miete"
    PARTNERSHIP = "partnerschaft"
    OTHER = "sonstiges"

#basisschema mit gemeinsamen feldern
class ContractBase(BaseModel):
    """basisschema mit gemeinsamen vertragsfeldern"""
    title: str = Field(..., min_length=2, max_length=200, description="Vertrags titel")
    description: Optional[str] = Field(None, max_length=1000, description="Vertragsbeschreibung")
    type: ContractType = Field(default=ContractType.OTHER, description="Vertragstyp")
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
    def validate_end_date(cls, v, values):
        """Überprüft, ob das Enddatum nach dem Startdatum liegt"""
        if v and 'start_date' in values and v <= values ['start_date']:
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
    """Schema zum Erstellen eines neuen Vertrags"""
    pass    

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

# Schema für API-Antworten (enthält Benutzerinformationen)
class ContractResponse(ContractBase):
    """Schema für Vertragsdaten in API-Antworten"""
    id: int = Field(..., description="Eindeutige Vertrags-ID")
    created_by: int = Field(..., description="Benutzer-ID, die den Vertrag erstellt hat")
    created_at: datetime = Field(..., description="Vertragserstellungszeitstempel")
    updated_at: Optional[datetime] = Field(None, description="Zeitstempel der letzten Aktualisierung")

    class Config:
        from_attributes = True  # Ermöglicht die Konvertierung vom SQLAlchemy-Modell
        json_encoders = {
            Decimal: lambda v: float (v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }

# Schema für Vertragsdaten in der Datenbank
class ContractInDB(ContractBase):
    """Schema für Vertragsdaten wie in der Datenbank gespeichert"""
    id: int = Field(..., description="Eindeutige Vertrags-ID")
    created_by: int = Field(..., description="Benutzer-ID, die den Vertrag erstellt hat")
    created_at: datetime = Field(..., description="Vertragserstellungszeitstempel")
    updated_at: Optional[datetime] = Field(None, description="Zeitstempel der letzten Aktualisierung")
    
    class Config:
        from_attributes = True  # Ermöglicht die Konvertierung vom SQLAlchemy-Modell
        json_encoders = {
            Decimal: lambda v: float (v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }

# Schema für Vertragslisten-Antworten
class ContractListResponse(BaseModel):
    """Schema für Vertragslisten in API-Antworten"""
    contracts: List[ContractResponse] = Field(..., description="Liste der Verträge")
    total: int = Field(..., description="Gesamtanzahl der Verträge")
    page: int = Field(..., description="Aktuelle Seitennummer")
    per_page: int = Field(..., description="Anzahl der Verträge pro Seite")
    
    class Config:
        from_attributes = True  # Ermöglicht die Konvertierung vom SQLAlchemy-Modell
        json_encoders = {
            Decimal: lambda v: float (v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }
# Schema für Vertragsstatistiken
class ContractStats(BaseModel):
    """Schema für Vertragsstatistiken"""
    total_contracts: int = Field(..., description="Gesamtanzahl der Verträge")
    active_contracts: int = Field(..., description="Anzahl der aktiven Verträge")
    expired_contracts: int = Field(..., description="Anzahl der abgelaufenen Verträge")
    draft_contracts: int = Field(..., description="Anzahl der Entwurfsverträge")
    total_value: Decimal = Field(..., description="Gesamtwert aller Verträge")
    currency: str = Field(..., description="Für den Gesamtwert verwendete Währung")
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float (v),
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }