"""
Contract Approval Model - Modelo de Aprovação de Contrato
Vertragsgenehmigungs-Modell

DE: Modell für Vertragsgenehmigungen mit Audit-Trail
PT: Modelo para aprovações de contrato com trilha de auditoria
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
import enum

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base

if TYPE_CHECKING:
    from .contract import Contract
    from .user import User


class ApprovalStatus(str, enum.Enum):
    """Status da aprovação / Genehmigungsstatus"""
    PENDING = "pending"           # Aguardando aprovação / Wartet auf Genehmigung
    APPROVED = "approved"         # Aprovado / Genehmigt
    REJECTED = "rejected"         # Rejeitado / Abgelehnt
    CANCELLED = "cancelled"       # Cancelado / Abgebrochen


class ContractApproval(Base):
    """
    Modelo de aprovação de contrato / Vertragsgenehmigungs-Modell
    
    Registra todas as aprovações/rejeições de contratos com histórico completo.
    Registriert alle Vertragsgenehmigungen/-ablehnungen mit vollständiger Historie.
    """
    __tablename__ = "contract_approvals"

    # Chave primária / Primärschlüssel
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)

    # Relacionamentos / Beziehungen
    contract_id: Mapped[int] = mapped_column(Integer, ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True)
    approver_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Status e resultado / Status und Ergebnis
    status: Mapped[ApprovalStatus] = mapped_column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False, index=True)
    
    # Comentários e justificativa / Kommentare und Begründung
    comments: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Metadados de aprovação / Genehmigungs-Metadaten
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    rejected_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Nível de aprovação requerido / Erforderliche Genehmigungsstufe
    required_approval_level: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    
    # Indicador de aprovação automática / Automatische Genehmigungsindikator
    is_auto_approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Audit / Auditierung
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now(), nullable=False)

    # Relacionamentos reversos / Rückwärts-Beziehungen
    contract: Mapped["Contract"] = relationship("Contract", back_populates="approvals")
    approver: Mapped["User"] = relationship("User", foreign_keys=[approver_id])

    def approve(self, comments: Optional[str] = None) -> None:
        """
        Aprova o contrato / Genehmigt den Vertrag
        
        Args:
            comments: Comentários opcionais / Optionale Kommentare
        """
        self.status = ApprovalStatus.APPROVED
        self.approved_at = datetime.now(timezone.utc)
        self.comments = comments
        self.rejection_reason = None

    def reject(self, reason: str, comments: Optional[str] = None) -> None:
        """
        Rejeita o contrato / Lehnt den Vertrag ab
        
        Args:
            reason: Motivo da rejeição / Ablehnungsgrund
            comments: Comentários adicionais / Zusätzliche Kommentare
        """
        self.status = ApprovalStatus.REJECTED
        self.rejected_at = datetime.now(timezone.utc)
        self.rejection_reason = reason
        self.comments = comments

    def cancel(self) -> None:
        """
        Cancela a solicitação de aprovação / Bricht den Genehmigungsantrag ab
        """
        self.status = ApprovalStatus.CANCELLED

    def __repr__(self) -> str:
        return f"<ContractApproval(id={self.id}, contract_id={self.contract_id}, status={self.status.value})>"
