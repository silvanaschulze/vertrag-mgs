"""add_company_fields

Revision ID: 835d4b7f7e59
Revises: 0006_add_contract_approvals
Create Date: 2026-01-11

Adiciona campos company_name e legal_form à tabela contracts
Fügt Felder company_name und legal_form zur Tabelle contracts hinzu
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '835d4b7f7e59'
down_revision = '0006_add_contract_approvals'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adiciona coluna company_name
    op.add_column('contracts', sa.Column('company_name', sa.String(length=200), nullable=True))
    
    # Adiciona coluna legal_form
    op.add_column('contracts', sa.Column('legal_form', sa.String(length=50), nullable=True))


def downgrade() -> None:
    # Remove colunas adicionadas
    op.drop_column('contracts', 'legal_form')
    op.drop_column('contracts', 'company_name')
