from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlalchemy import Column, String, Integer, Date, DateTime, Numeric, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base

class ContractStatus(str,enum.Enum):
    """Vertragsstatus Aufzählung"""
    DRAFT = "entwurf"               #Entwurf
    ACTIVE = "aktiv"                #Aktiv  
    EXPIRED = "abgelaufen"          #Abgelaufen
    TERMINATED = "beendet"          #Beendet
    PENDING_APPROVAL = "wartet_auf_genehmigung" #Wartet auf Genehmigung

class ContractType(str,enum.Enum):
    """Vertragstyp Aufzählung"""
    SERVICE = "dienstleistung"      #Dienstleistung
    PRODUCT = "produkt"             #Produkt
    EMPLOYMENT = "beschäftigung"    #Beschäftigung
    LEASE = "miete"                 #Miete
    PARTNERSHIP = "partnerschaft"   #Partnerschaft
    OTHER = "sonstiges"             #Sonstiges

class Contract(Base):
    """Vertragsmodell für die Datenbank"""
    __cpdb__ = "contracts"

    #prämärschlüssel
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    #Grundlegende Felder
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    contrac_type = Column(Enum(ContractType), default=ContractType.OTHER, nullable=False)
    status = Column(Enum(ContractStatus), default=ContractStatus.DRAFT, nullable=False)

    #Finanzfelder
    value = Column(Numeric(12, 2), nullable=True)  #Maximalwert 9999999999.99
    currency = Column(String(3), default="EUR", nullable=False)  #ISO 4217 Währungscode

    #Datumsfelder
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    renewal_date = Column(Date, nullable=True)

    #Kundenfelder
    client_name = Column(String(200), nullable=False)  #z.B. Firma oder Einzelperson
    client_document = Column(String(20), nullable=True) #z.B. Steuernummer, Handelsregisternummer
    client_address = Column(String(300), nullable=True) #Rechnungsadresse
    client_email = Column(String(100), nullable=True)
    client_phone = Column(String(20), nullable=True)

    #Zusätzliche Felder
    terms_and_conditions = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    #audit felder
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    #Beziehung zum Benutzer
    creator = relationship("User", back_populates="contracts")

    def __repr__(self) -> str:
        """String-Darstellung des Vertrags"""
        return f"<Contract(id={self.id}, title={self.title}, status={self.status.value})>"

    def is_active(self) -> bool:
        """Überprufen, ob der Vertrag aktiv ist """
        return self.status == ContractStatus.ACTIVE

    def is_expired(self) -> bool:
        """ Überprufen, ob der Vertrag abgelaufen ist """
        if not self.end_date:
            return False 
        return self.end_date < datetime.now().date()

    def days_until_expiry(self) -> Optional[int]:
        """ Berechnen der Tage bis zum Vertragsend """
        if not self.end_date:
            return None
        delta = self.end_date - datetime.now().date()
        return delta.days

    def get_formatted_value(self) -> str:
        """ Formatieren Vertragswert mit Währung erhalten """
        if not self.value:
            return "N/A"
        return f"{self.value:,.2f} {self.currency}"

    def update_status(self) -> None:
        """ Vertragsstatus basierend auf Daten aktualisieren """
        if self.is_expired():
            self.status = ContractStatus.EXPIRED

# Klassenkonfiguration 
    class Config:
        """Konfiguration für SQLAlchemy - Modell """
        #Ermöglich automatische Konvertierung von SQLAlchemy zu Pydantic-Modellen
        from_attributes = True

        #Validierungskonfiguration
        validate_assignment = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }


# Hilfsfunktionen für das Modell
def get_contract_by_id(db, contract_id: int) -> Optional[Contract]:
    """ Vertrag anhand der ID abrufen aus Datenbank abrufen """
    return db.query(Contract).filter(Contract.id == contract_id).first()    

def get_active_contracts(db) -> list[Contract]:
    """ Alle aktiven Verträge abrufen aus Datenbank abrufen """
    return db.query(Contract).filter(Contract.status == ContractStatus.ACTIVE).all() 

def get_expired_contracts(db, days:int =30) -> list[Contract]:
    """ Verträge abrufen, die innerhalb der angegebenen Tage ablaufen  """
    from datetime import timedelta
    expiry_date = datetime.now().date() + timedelta(days=days)
    return db.query(Contract).filter(
        Contract.end_date <= expiry_date,
        Contract.status == ContractStatus.ACTIVE
    ).all() 

