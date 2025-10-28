"""Add country and currency columns to hrm_tenant

Revision ID: 006
Revises: 005_add_tenant_company_hierarchy
Create Date: 2024-01-02

This migration adds country_code and currency_code columns to the hrm_tenant table
to match the Python model. Fix schema mismatch for tenant country/currency fields.
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_add_tenant_country_currency'
down_revision = '005_add_tenant_company_hierarchy'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade migration - Add country and currency columns"""
    
    # Add country_code column if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_tenant' AND column_name = 'country_code'
            ) THEN
                ALTER TABLE hrm_tenant ADD COLUMN country_code VARCHAR(10);
                RAISE NOTICE 'Added country_code column to hrm_tenant table';
            END IF;
        END $$;
    """)
    
    # Add currency_code column if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_tenant' AND column_name = 'currency_code'
            ) THEN
                ALTER TABLE hrm_tenant ADD COLUMN currency_code VARCHAR(10);
                RAISE NOTICE 'Added currency_code column to hrm_tenant table';
            END IF;
        END $$;
    """)
    
    # Add comments for documentation
    op.execute("COMMENT ON COLUMN hrm_tenant.country_code IS 'Country code (e.g., SG, US, IN)'")
    op.execute("COMMENT ON COLUMN hrm_tenant.currency_code IS 'Currency code (e.g., SGD, USD, INR)'")


def downgrade():
    """Downgrade migration - Remove country and currency columns"""
    
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_tenant' AND column_name = 'currency_code'
            ) THEN
                ALTER TABLE hrm_tenant DROP COLUMN currency_code;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_tenant' AND column_name = 'country_code'
            ) THEN
                ALTER TABLE hrm_tenant DROP COLUMN country_code;
            END IF;
        END $$;
    """)