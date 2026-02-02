"""
Schemas para Alertas / Schemas für Benachrichtigungen

PT: Schemas Pydantic para operações de alerta.
DE: Pydantic-Schemas für Alert-Operationen.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class AlertUpdate(BaseModel):
    """
    Schema para atualização parcial de alerta.
    Schema für partielle Aktualisierung eines Alerts.
    """
    responsible_user_id: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    status: Optional[str] = None
    