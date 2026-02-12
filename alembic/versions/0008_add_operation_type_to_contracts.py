"""
Alembic migration: Adiciona campo operation_type à tabela contracts
Fügt Feld operation_type zur Tabelle contracts hinzu
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# Revisão e dependências
revision = '0008_add_operation_type_to_contracts'
down_revision = '0007_add_payment_frequency'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('contracts',
        sa.Column('operation_type', sa.Enum('INCOME', 'EXPENSE', name='operationtype'),
                  nullable=False, server_default='INCOME', index=True, comment='Eingabewert/Ausgabewert | Entrada/Saída')
    )

    # Atualiza contratos existentes para INCOME por padrão
    op.execute("UPDATE contracts SET operation_type = 'INCOME' WHERE operation_type IS NULL")

def downgrade():
    op.drop_column('contracts', 'operation_type')
    sa.Enum(name='operationtype').drop(op.get_bind(), checkfirst=True)
