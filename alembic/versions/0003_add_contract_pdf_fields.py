"""add contract original pdf fields

Revision ID: 0003_add_contract_pdf_fields
Revises: 0002_add_rent_steps
Create Date: 2025-11-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_add_contract_pdf_fields'
down_revision = '0002_add_rent_steps'
branch_labels = None
depends_on = None


def upgrade():
    # Add columns for persistent original PDF storage and OCR metadata
    op.add_column('contracts', sa.Column('original_pdf_path', sa.String(length=500), nullable=True))
    op.add_column('contracts', sa.Column('original_pdf_filename', sa.String(length=255), nullable=True))
    op.add_column('contracts', sa.Column('original_pdf_sha256', sa.String(length=64), nullable=True))
    op.add_column('contracts', sa.Column('ocr_text', sa.Text(), nullable=True))
    op.add_column('contracts', sa.Column('ocr_text_sha256', sa.String(length=64), nullable=True))
    op.add_column('contracts', sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=True))

    # Indexes to accelerate duplicate checks
    op.create_index('ix_contracts_original_pdf_sha256', 'contracts', ['original_pdf_sha256'], unique=False)
    op.create_index('ix_contracts_ocr_text_sha256', 'contracts', ['ocr_text_sha256'], unique=False)


def downgrade():
    # Drop indexes then columns
    op.drop_index('ix_contracts_ocr_text_sha256', table_name='contracts')
    op.drop_index('ix_contracts_original_pdf_sha256', table_name='contracts')

    op.drop_column('contracts', 'uploaded_at')
    op.drop_column('contracts', 'ocr_text_sha256')
    op.drop_column('contracts', 'ocr_text')
    op.drop_column('contracts', 'original_pdf_sha256')
    op.drop_column('contracts', 'original_pdf_filename')
    op.drop_column('contracts', 'original_pdf_path')
