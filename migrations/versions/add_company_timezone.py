"""Add timezone column to hrm_company table for company-level timezone configuration

This migration:
1. Adds the timezone column to hrm_company table with default value 'UTC'
2. Makes timezone NOT NULL with a default for existing records
3. Timezone is used to display attendance/OT times in the company's local timezone

Revision ID: add_company_timezone
Revises: add_company_currency_code
Create Date: 2025-01-24 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_company_timezone'
down_revision = 'add_company_currency_code'
branch_labels = None
depends_on = None


def upgrade():
    """Add timezone column to hrm_company"""
    # Add the timezone column with NOT NULL constraint and default value
    op.add_column('hrm_company',
        sa.Column('timezone', sa.String(length=50), nullable=False, server_default='UTC')
    )
    print("✅ Added timezone column to hrm_company table")
    print("   - Default value: UTC")
    print("   - Used for: Display attendance and OT times in company's local timezone")
    print("   - Supported formats: IANA timezone identifiers (e.g., Asia/Singapore, America/New_York)")


def downgrade():
    """Remove timezone column from hrm_company"""
    op.drop_column('hrm_company', 'timezone')
    print("⏮️  Removed timezone column from hrm_company table")