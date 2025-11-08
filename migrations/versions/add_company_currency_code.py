"""Add currency_code column to hrm_company table for payroll configuration

This migration:
1. Adds the currency_code column to hrm_company table with default value 'SGD'
2. Makes currency_code NOT NULL with a default

Revision ID: add_company_currency_code
Revises: add_company_employee_id_config
Create Date: 2025-01-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_company_currency_code'
down_revision = 'add_company_employee_id_config'
branch_labels = None
depends_on = None


def upgrade():
    """Add currency_code column to hrm_company"""
    # Add the currency_code column with NOT NULL constraint and default value
    op.add_column('hrm_company',
        sa.Column('currency_code', sa.String(length=10), nullable=False, server_default='SGD')
    )
    print("✅ Added currency_code column to hrm_company table")
    print("   - Default value: SGD")
    print("   - Used for: Payroll calculations and financial reports")


def downgrade():
    """Remove currency_code column from hrm_company"""
    op.drop_column('hrm_company', 'currency_code')
    print("⏮️  Removed currency_code column from hrm_company table")