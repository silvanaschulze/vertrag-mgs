"""add rent_steps table

Revisions-ID: 0002_add_rent_steps
Erstellt: 2025-11-13 00:00:00.000000

Diese Migration fügt die Tabelle `rent_steps` hinzu, die zukünftige Mietanpassungen speichert.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0002_add_rent_steps'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'rent_steps',
        sa.Column('id', sa.Integer, primary_key=True, index=True, autoincrement=True),
        sa.Column('contract_id', sa.Integer, sa.ForeignKey('contracts.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('effective_date', sa.Date, nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=True),
        sa.Column('note', sa.Text, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
    )

    # Unique constraint to avoid duplicate steps for the same contract/date
    op.create_unique_constraint('uq_rent_steps_contract_date', 'rent_steps', ['contract_id', 'effective_date'])
    op.create_index('ix_rent_steps_contract_effective_date', 'rent_steps', ['contract_id', 'effective_date'])


def downgrade() -> None:
    op.drop_index('ix_rent_steps_contract_effective_date', table_name='rent_steps')
    op.drop_constraint('uq_rent_steps_contract_date', 'rent_steps', type_='unique')
    op.drop_table('rent_steps')
