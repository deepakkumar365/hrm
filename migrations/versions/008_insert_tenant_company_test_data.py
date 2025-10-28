"""Insert tenant and company test data

Revision ID: 008
Revises: 007_add_tenant_payment_and_documents
Create Date: 2024-01-04

This migration inserts sample data for testing the hierarchy.
Safe to run multiple times (uses upsert operations).
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

# revision identifiers, used by Alembic.
revision = '008_insert_tenant_company_test_data'
down_revision = '007_add_tenant_payment_and_documents'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade migration - Insert test data"""
    
    # 1. INSERT TENANT DATA (using upsert pattern)
    op.execute("""
        INSERT INTO hrm_tenant (id, name, code, description, is_active, created_by, created_at)
        VALUES 
            (
                '00000000-0000-0000-0000-000000000001'::UUID,
                'Noltrion HRM',
                'NOLTRION',
                'Noltrion Group - Global HRMS Tenant',
                TRUE,
                'admin@noltrion.com',
                NOW()
            )
        ON CONFLICT (code) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            modified_by = 'admin@noltrion.com',
            modified_at = NOW();
    """)
    
    # 2. INSERT COMPANY DATA (using upsert pattern)
    op.execute("""
        INSERT INTO hrm_company (
            id, 
            tenant_id, 
            name, 
            code, 
            description, 
            address, 
            uen, 
            phone, 
            email, 
            website,
            is_active, 
            created_by, 
            created_at
        )
        VALUES 
            -- Company 1: Noltrion India
            (
                '00000000-0000-0000-0000-000000000101'::UUID,
                '00000000-0000-0000-0000-000000000001'::UUID,
                'Noltrion India Pvt Ltd',
                'NOLTRION-IN',
                'Noltrion India Private Limited - Software Development',
                'Bangalore, Karnataka, India',
                NULL,
                '+91-80-12345678',
                'india@noltrion.com',
                'https://noltrion.in',
                TRUE,
                'admin@noltrion.com',
                NOW()
            ),
            -- Company 2: Noltrion Singapore
            (
                '00000000-0000-0000-0000-000000000102'::UUID,
                '00000000-0000-0000-0000-000000000001'::UUID,
                'Noltrion Singapore Pte Ltd',
                'NOLTRION-SG',
                'Noltrion Singapore Private Limited - Regional HQ',
                '1 Raffles Place, #20-01, Singapore 048616',
                '202012345A',
                '+65-6123-4567',
                'singapore@noltrion.com',
                'https://noltrion.sg',
                TRUE,
                'admin@noltrion.com',
                NOW()
            )
        ON CONFLICT (tenant_id, code) DO UPDATE SET
            name = EXCLUDED.name,
            description = EXCLUDED.description,
            address = EXCLUDED.address,
            phone = EXCLUDED.phone,
            email = EXCLUDED.email,
            website = EXCLUDED.website,
            modified_by = 'admin@noltrion.com',
            modified_at = NOW();
    """)
    
    # 3. UPDATE EXISTING ORGANIZATION TO LINK TO TENANT
    op.execute("""
        UPDATE organization 
        SET 
            tenant_id = '00000000-0000-0000-0000-000000000001'::UUID,
            modified_by = 'admin@noltrion.com',
            modified_at = NOW()
        WHERE id = (SELECT MIN(id) FROM organization)
          AND tenant_id IS NULL;
    """)
    
    # 4. LINK EXISTING EMPLOYEES TO COMPANIES (EXAMPLE)
    op.execute("""
        UPDATE hrm_employee 
        SET 
            company_id = '00000000-0000-0000-0000-000000000102'::UUID,
            modified_by = 'admin@noltrion.com',
            modified_at = NOW()
        WHERE id IN (
            SELECT id FROM hrm_employee 
            WHERE company_id IS NULL 
            ORDER BY id 
            LIMIT 3
        );
    """)


def downgrade():
    """Downgrade migration - Remove inserted test data"""
    
    # Remove linked employees
    op.execute("""
        UPDATE hrm_employee 
        SET 
            company_id = NULL,
            modified_by = 'migration_rollback',
            modified_at = NOW()
        WHERE company_id = '00000000-0000-0000-0000-000000000102'::UUID;
    """)
    
    # Remove organization tenant link
    op.execute("""
        UPDATE organization 
        SET 
            tenant_id = NULL,
            modified_by = 'migration_rollback',
            modified_at = NOW()
        WHERE tenant_id = '00000000-0000-0000-0000-000000000001'::UUID;
    """)
    
    # Remove companies
    op.execute("""
        DELETE FROM hrm_company 
        WHERE tenant_id = '00000000-0000-0000-0000-000000000001'::UUID;
    """)
    
    # Remove tenant
    op.execute("""
        DELETE FROM hrm_tenant 
        WHERE code = 'NOLTRION';
    """)