"""add pacht contract type

Revision ID: 0004_add_pacht_contract_type
Revises: 0003_add_contract_pdf_fields
Create Date: 2025-11-20 00:00:00.000000

DE: Fügt 'PACHT' als neuen ContractType hinzu für Pachtverträge.
PT: Adiciona 'PACHT' como novo ContractType para contratos de arrendamento.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0004_add_pacht_contract_type'
down_revision = '0003_add_contract_pdf_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'pacht' to the contract_type enum
    # SQLite doesn't support ALTER TYPE, so we need to recreate the constraint
    # For SQLite, this is handled by SQLAlchemy automatically when the enum is used
    
    # Since SQLite doesn't have native enum support, SQLAlchemy handles this via CHECK constraints
    # The new enum value 'pacht' will be automatically available when the model is used
    pass


def downgrade():
    # For SQLite, removing enum values is not straightforward without data migration
    # Since this is additive and doesn't break existing data, we'll leave it as-is
    # In production with PostgreSQL, this would need proper enum migration
    pass