"""
Alert schemas with contract info for enriched API responses.
Schemas de alerta com informações do contrato para respostas enriquecidas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.alert import AlertStatus, AlertType

class AlertWithContractInfo(BaseModel):
    id: int = Field(..., description="ID do alerta")
    contract_id: int = Field(..., description="ID do contrato")
    alert_type: AlertType = Field(..., description="Tipo de alerta")
    status: AlertStatus = Field(..., description="Status do alerta")
    scheduled_for: Optional[datetime] = Field(None, description="Data agendada para envio")
    sent_at: Optional[datetime] = Field(None, description="Data de envio")
    created_at: datetime = Field(..., description="Data de criação do alerta")
    updated_at: Optional[datetime] = Field(None, description="Data de atualização do alerta")
    recipient: Optional[str] = Field(None, description="Destinatário do alerta")
    subject: Optional[str] = Field(None, description="Assunto do alerta")
    # Dados do contrato
    company_name: Optional[str] = Field(None, description="Nome da empresa do contrato")
    created_by_name: Optional[str] = Field(None, description="Nome de quem criou o contrato")
    responsible_user_name: Optional[str] = Field(None, description="Nome do responsável pelo contrato")

    model_config = ConfigDict(from_attributes=True)

class AlertWithContractListResponse(BaseModel):
    total: int = Field(..., description="Total de alertas")
    alerts: list[AlertWithContractInfo] = Field(..., description="Lista de alertas com info do contrato")
    page: int = Field(..., description="Página atual")
    per_page: int = Field(..., description="Itens por página")

    model_config = ConfigDict(from_attributes=True)
