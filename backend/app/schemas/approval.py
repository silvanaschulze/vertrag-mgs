"""
Approval Schemas - Schemas de Aprovação
Genehmigungs-Schemas

DE: Pydantic-Schemas für Vertragsgenehmigungen
PT: Schemas Pydantic para aprovações de contrato
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class ApprovalStatus(str, Enum):
    """Status da aprovação / Genehmigungsstatus"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApprovalAction(str, Enum):
    """Ação de aprovação / Genehmigungsaktion"""
    APPROVE = "approve"
    REJECT = "reject"
    CANCEL = "cancel"


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================

class ApprovalRequest(BaseModel):
    """
    Requisição de aprovação de contrato / Vertragsgenehmigungs-Anfrage
    """
    comments: Optional[str] = Field(None, max_length=1000, description="Comentários opcionais / Optionale Kommentare")


class RejectionRequest(BaseModel):
    """
    Requisição de rejeição de contrato / Vertragsablehnungs-Anfrage
    """
    reason: str = Field(..., min_length=10, max_length=500, description="Motivo da rejeição / Ablehnungsgrund")
    comments: Optional[str] = Field(None, max_length=1000, description="Comentários adicionais / Zusätzliche Kommentare")


class ApprovalCreate(BaseModel):
    """
    Schema para criar solicitação de aprovação / Schema zum Erstellen einer Genehmigungsanfrage
    """
    contract_id: int = Field(..., description="ID do contrato / Vertrags-ID")
    required_approval_level: int = Field(3, ge=1, le=6, description="Nível de aprovação necessário / Erforderliche Genehmigungsstufe")
    comments: Optional[str] = Field(None, max_length=1000, description="Comentários / Kommentare")


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ApprovalResponse(BaseModel):
    """
    Resposta de aprovação / Genehmigungsantwort
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID da aprovação / Genehmigungs-ID")
    contract_id: int = Field(..., description="ID do contrato / Vertrags-ID")
    approver_id: int = Field(..., description="ID do aprovador / Genehmiger-ID")
    status: ApprovalStatus = Field(..., description="Status da aprovação / Genehmigungsstatus")
    
    comments: Optional[str] = Field(None, description="Comentários / Kommentare")
    rejection_reason: Optional[str] = Field(None, description="Motivo da rejeição / Ablehnungsgrund")
    
    approved_at: Optional[datetime] = Field(None, description="Data de aprovação / Genehmigungsdatum")
    rejected_at: Optional[datetime] = Field(None, description="Data de rejeição / Ablehnungsdatum")
    
    required_approval_level: int = Field(..., description="Nível necessário / Erforderliche Stufe")
    is_auto_approved: bool = Field(..., description="Aprovação automática / Automatische Genehmigung")
    
    created_at: datetime = Field(..., description="Data de criação / Erstellungsdatum")
    updated_at: datetime = Field(..., description="Data de atualização / Aktualisierungsdatum")


class ApprovalWithApprover(ApprovalResponse):
    """
    Aprovação com informações do aprovador / Genehmigung mit Genehmiger-Informationen
    """
    approver_name: Optional[str] = Field(None, description="Nome do aprovador / Name des Genehmigers")
    approver_email: Optional[str] = Field(None, description="Email do aprovador / E-Mail des Genehmigers")


class ApprovalHistoryResponse(BaseModel):
    """
    Histórico completo de aprovações / Vollständige Genehmigungs-Historie
    """
    contract_id: int = Field(..., description="ID do contrato / Vertrags-ID")
    contract_title: str = Field(..., description="Título do contrato / Vertragstitel")
    total_approvals: int = Field(..., description="Total de aprovações / Gesamtzahl der Genehmigungen")
    pending_approvals: int = Field(..., description="Aprovações pendentes / Ausstehende Genehmigungen")
    approvals: list[ApprovalWithApprover] = Field(..., description="Lista de aprovações / Liste der Genehmigungen")


class ApprovalActionResponse(BaseModel):
    """
    Resposta de ação de aprovação / Antwort auf Genehmigungsaktion
    """
    success: bool = Field(..., description="Sucesso da operação / Erfolg der Operation")
    message: str = Field(..., description="Mensagem / Nachricht")
    approval: ApprovalResponse = Field(..., description="Aprovação atualizada / Aktualisierte Genehmigung")
    contract_status: str = Field(..., description="Novo status do contrato / Neuer Vertragsstatus")
