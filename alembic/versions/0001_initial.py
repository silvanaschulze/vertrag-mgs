"""initial

Revision ID: 0001_initial
Revises: 
Create Date: 2025-10-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('username', sa.String(50), unique=True, index=True, nullable=True),
        sa.Column('email', sa.String(100), unique=True, index=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('department', sa.String(100), nullable=True),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('1')),
        sa.Column('is_verified', sa.Boolean, nullable=False, server_default=sa.text('0')),
        sa.Column('is_superuser', sa.Boolean, nullable=False, server_default=sa.text('0')),
        sa.Column('verification_token', sa.String(255), nullable=True),
        sa.Column('reset_token', sa.String(255), nullable=True),
        sa.Column('reset_token_expiration', sa.DateTime, nullable=True),
        sa.Column('failed_login_attempts', sa.Integer, nullable=False, server_default='0'),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('position', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer, nullable=True),
        sa.Column('updated_by', sa.Integer, nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.Integer, nullable=True),
        sa.Column('is_deleted', sa.Boolean, nullable=False, server_default=sa.text('0')),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_ip', sa.String(45), nullable=True),
        sa.Column('notes', sa.String(500), nullable=True),
        sa.Column('preferences', sa.Text, nullable=True),
    )

    # permissions
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('name', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # contracts
    op.create_table(
        'contracts',
        sa.Column('id', sa.Integer, primary_key=True, index=True, autoincrement=True),
        sa.Column('title', sa.String(200), nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('contract_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('value', sa.Numeric(12, 2), nullable=True),
        sa.Column('currency', sa.String(3), nullable=False, server_default='EUR'),
        sa.Column('start_date', sa.Date, nullable=False),
        sa.Column('end_date', sa.Date, nullable=True),
        sa.Column('renewal_date', sa.Date, nullable=True),
        sa.Column('client_name', sa.String(200), nullable=False),
        sa.Column('client_document', sa.String(20), nullable=True),
        sa.Column('client_address', sa.String(300), nullable=True),
        sa.Column('client_email', sa.String(100), nullable=True),
        sa.Column('client_phone', sa.String(20), nullable=True),
        sa.Column('terms_and_conditions', sa.Text, nullable=True),
        sa.Column('notes', sa.Text, nullable=True),
        sa.Column('created_by', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )

    # alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer, primary_key=True, index=True, autoincrement=True),
        sa.Column('contract_id', sa.Integer, nullable=False, index=True),
        sa.Column('alert_type', sa.String(20), nullable=False, index=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending', index=True),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('recipient', sa.String(255), nullable=True),
        sa.Column('subject', sa.String(255), nullable=True),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('alerts')
    op.drop_table('contracts')
    op.drop_table('permissions')
    op.drop_table('users')
