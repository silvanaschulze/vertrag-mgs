"""add access_level, team fields and new user roles

Revision ID: 0005_add_access_level_team_and_new_roles
Revises: 0004_add_pacht_contract_type
Create Date: 2025-11-27 00:00:00.000000

DE: Fügt access_level und team zu Users hinzu, department/team/responsible_user_id zu Contracts,
    und erweitert UserRole mit neuen Rollen für granulare Berechtigungen.
PT: Adiciona access_level e team aos Users, department/team/responsible_user_id aos Contracts,
    e expande UserRole com novos papéis para permissões granulares.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0005_add_access_level_team_and_new_roles'
down_revision = '0004_add_pacht_contract_type'
branch_labels = None
depends_on = None


def upgrade():
    """
    Fügt neue Felder und erweitert Enums hinzu.
    Adiciona novos campos e expande enums.
    """
    # Add team column to users table
    # Adicionar coluna team à tabela users
    op.add_column('users', sa.Column('team', sa.String(length=100), nullable=True))
    
    # Add access_level column to users table with default value 1
    # Adicionar coluna access_level à tabela users com valor padrão 1
    op.add_column('users', sa.Column('access_level', sa.Integer(), nullable=False, server_default='1'))
    
    # Add department column to contracts table (if not exists)
    # Adicionar coluna department à tabela contracts (se não existir)
    # Note: department may already exist in contracts, check before adding
    try:
        op.add_column('contracts', sa.Column('department', sa.String(length=100), nullable=True))
        op.create_index('ix_contracts_department', 'contracts', ['department'], unique=False)
    except Exception:
        # Column may already exist
        pass
    
    # Add team column to contracts table
    # Adicionar coluna team à tabela contracts
    op.add_column('contracts', sa.Column('team', sa.String(length=100), nullable=True))
    op.create_index('ix_contracts_team', 'contracts', ['team'], unique=False)
    
    # Add responsible_user_id column to contracts table
    # Adicionar coluna responsible_user_id à tabela contracts
    op.add_column('contracts', sa.Column('responsible_user_id', sa.Integer(), nullable=True))
    op.create_index('ix_contracts_responsible_user_id', 'contracts', ['responsible_user_id'], unique=False)
    
    # Note: For SQLite, enum changes are handled by SQLAlchemy model definitions
    # For PostgreSQL in production, you would need to ALTER TYPE to add new enum values
    # The new UserRole values (system_admin, director, department_user, department_adm, 
    # team_lead, staff, read_only) will be available through the model
    
    print("Migration 0005: Added access_level, team fields and prepared for new user roles")


def downgrade():
    """
    Entfernt die hinzugefügten Felder.
    Remove os campos adicionados.
    """
    # Remove indexes
    op.drop_index('ix_contracts_responsible_user_id', table_name='contracts')
    op.drop_index('ix_contracts_team', table_name='contracts')
    try:
        op.drop_index('ix_contracts_department', table_name='contracts')
    except Exception:
        pass
    
    # Remove columns from contracts
    op.drop_column('contracts', 'responsible_user_id')
    op.drop_column('contracts', 'team')
    try:
        op.drop_column('contracts', 'department')
    except Exception:
        pass
    
    # Remove columns from users
    op.drop_column('users', 'access_level')
    op.drop_column('users', 'team')
    
    print("Migration 0005: Rolled back access_level and team fields")
