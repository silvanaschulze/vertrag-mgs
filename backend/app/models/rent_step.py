from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional
from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from .contract import Contract


class RentStep(Base):
    """Repräsentiert eine zukünftige Mietanpassung (Mietstaffelung).

    Felder:
    - contract_id: Verweis auf den zugehörigen Vertrag
    - effective_date: Datum, an dem der neue Betrag wirksam wird
    - amount: Betrag in Vertragswährung
    - currency: ISO 4217 Währungscode (optional)
    - note: Freitexthinweis (optional)
    - created_by: ID des Benutzers, der die Staffel erstellt hat (optional)
    - created_at: Zeitstempel der Erstellung
    """

    __tablename__ = "rent_steps"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)

    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationship back to Contract
    contract: Mapped["Contract"] = relationship("Contract", back_populates="rent_steps")

    def __repr__(self) -> str:  # pragma: no cover - trivial repr
        return f"<RentStep(id={self.id}, contract_id={self.contract_id}, effective_date={self.effective_date}, amount={self.amount})>"

