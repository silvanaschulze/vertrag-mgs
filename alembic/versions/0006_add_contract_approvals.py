"""add contract approvals table

Revision ID: 0006
Revises: 0005
Create Date: 2025-12-27 10:00:00.000000

DE: Migration für Vertragsgenehmigungs-Tabelle
PT: Migração para tabela de aprovações de contrato
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0006_add_contract_approvals'
down_revision: Union[str, None] = '0005_add_access_level_team_and_new_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Cria tabela contract_approvals / Erstellt contract_approvals Tabelle
    """
    op.create_table(
        'contract_approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('approver_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'cancelled', name='approvalstatus'), nullable=False),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('required_approval_level', sa.Integer(), nullable=False),
        sa.Column('is_auto_approved', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        
        sa.PrimaryKeyConstraint('id'),
        
        # Foreign keys inline (funciona no SQLite / works in SQLite)
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['approver_id'], ['users.id'])
    )
    
    # Índices para performance / Indizes für Performance
    op.create_index(op.f('ix_contract_approvals_id'), 'contract_approvals', ['id'], unique=False)
    op.create_index(op.f('ix_contract_approvals_contract_id'), 'contract_approvals', ['contract_id'], unique=False)
    op.create_index(op.f('ix_contract_approvals_approver_id'), 'contract_approvals', ['approver_id'], unique=False)
    op.create_index(op.f('ix_contract_approvals_status'), 'contract_approvals', ['status'], unique=False)


def downgrade() -> None:
    """
    Remove tabela contract_approvals / Entfernt contract_approvals Tabelle
    """
    op.drop_table('contract_approvals')
    
    # Drop enum type (SQLite ignora, PostgreSQL/MySQL precisam)
    # Drop enum type (SQLite ignores, PostgreSQL/MySQL need it)
    sa.Enum(name='approvalstatus').drop(op.get_bind(), checkfirst=True)
