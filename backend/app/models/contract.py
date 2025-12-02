from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
import enum
from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


"""Vertragsstatus Aufzählung"""
if TYPE_CHECKING:
    from .alert import Alert
    from .user import User
    from .rent_step import RentStep

class ContractStatus(str, enum.Enum):
    DRAFT = "entwurf"               #Entwurf
    ACTIVE = "aktiv"                #Aktiv  
    EXPIRED = "abgelaufen"          #Abgelaufen
    TERMINATED = "beendet"          #Beendet
    PENDING_APPROVAL = "wartet_auf_genehmigung" #Wartet auf Genehmigung

class ContractType(str, enum.Enum):
    """Vertragstyp Aufzählung"""
    SERVICE = "dienstleistung"      #Dienstleistung
    PRODUCT = "produkt"             #Produkt
    EMPLOYMENT = "beschäftigung"    #Beschäftigung
    LEASE = "miete"                 #Miete
    PACHT = "pacht"                 #Pacht (Pachtvertrag)
    PARTNERSHIP = "partnerschaft"   #Partnerschaft
    OTHER = "sonstiges"             #Sonstiges

class Contract(Base):
    """Vertragsmodell für die Datenbank"""
    __tablename__ = "contracts"  

    #prämärschlüssel
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    #Grundlegende Felder
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contract_type: Mapped[ContractType] = mapped_column(Enum(ContractType), default=ContractType.OTHER, nullable=False)
    status: Mapped[ContractStatus] = mapped_column(Enum(ContractStatus), default=ContractStatus.DRAFT, nullable=False)

    #Finanzfelder
    value: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)  #Maximalwert 9999999999.99
    currency: Mapped[str] = mapped_column(String(3), default="EUR", nullable=False)  #ISO 4217 Währungscode

    #Datumsfelder
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    renewal_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    #Kundenfelder
    client_name: Mapped[str] = mapped_column(String(200), nullable=False)  #z.B. Firma oder Einzelperson
    client_document: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) #z.B. Steuernummer, Handelsregisternummer
    client_address: Mapped[Optional[str]] = mapped_column(String(300), nullable=True) #Rechnungsadresse
    client_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    client_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    #Organisationsfelder / Campos organizacionais
    department: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # Bereich / Departamento
    team: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)  # Team / Time
    responsible_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)  # Verantwortlicher Benutzer / Usuário responsável

    #Zusätzliche Felder
    terms_and_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    #audit felder
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    #Beziehung zum Benutzer
    creator: Mapped["User"] = relationship("User", back_populates="contracts")

    # Beziehung zu Alerts
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="contract")

    # Mietstaffelungen / Rent steps
    rent_steps: Mapped[list["RentStep"]] = relationship(
        "RentStep",
        back_populates="contract",
        cascade="all, delete-orphan",
        order_by="RentStep.effective_date",
        lazy="selectin"  # Eager loading para evitar MissingGreenlet em testes síncronos
    )

    # =========================
    # Metadaten der Original-PDF
    # Persistente Speicherung der hochgeladenen Original-PDF und OCR-Metadaten.
    # Hinweis: Diese Felder erfordern später eine Alembic-Migration.
    # =========================
    original_pdf_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Serverinterner Pfad zur Original-PDF
    original_pdf_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Ursprünglicher Dateiname
    original_pdf_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)  # SHA256 der Datei (Duplikatprüfung)
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Extrahierter Text (OCR / Text-Extraction)
    ocr_text_sha256: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)  # SHA256 des normalisierten OCR-Texts
    uploaded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)  # Zeitpunkt des Uploads

    def __repr__(self) -> str:
        """String-Darstellung des Vertrags"""
        # Protege contra status == None durante criação/coleção de objetos nos testes
        status_value = self.status.value if getattr(self, "status", None) is not None else "None"
        return f"<Contract(id={self.id}, title={self.title}, status={status_value})>"

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




