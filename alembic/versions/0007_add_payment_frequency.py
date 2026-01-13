"""add payment frequency fields

Revision ID: 0007_add_payment_frequency
Revises: 0006_add_contract_approvals
Create Date: 2025-01-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0007_add_payment_frequency'
down_revision: Union[str, None] = '835d4b7f7e59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Adiciona campos payment_frequency e payment_custom_years à tabela contracts
    """
    # Adicionar coluna payment_frequency
    op.add_column('contracts', sa.Column('payment_frequency', sa.String(length=50), nullable=True))
    
    # Adicionar coluna payment_custom_years
    op.add_column('contracts', sa.Column('payment_custom_years', sa.Integer(), nullable=True))


def downgrade() -> None:
    """
    Remove campos payment_frequency e payment_custom_years da tabela contracts
    """
    op.drop_column('contracts', 'payment_custom_years')
    op.drop_column('contracts', 'payment_frequency')
