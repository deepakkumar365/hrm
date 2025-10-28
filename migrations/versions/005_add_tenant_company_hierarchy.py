"""Add tenant company hierarchy - HRMS Tenant → Company → Employee Hierarchy

Revision ID: 005
Revises: 
Create Date: 2024-01-01

This migration adds multi-tenant support with Company hierarchy.
Idempotent and safe to run multiple times.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_tenant_company_hierarchy'
down_revision = 'add_overtime_group_id'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade migration - Add tenant company hierarchy schema"""
    
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    
    # 1. CREATE hrm_tenant TABLE
    op.create_table(
        'hrm_tenant',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        
        # Audit fields
        sa.Column('created_by', sa.String(100), nullable=False, server_default=sa.text("'system'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_by', sa.String(100), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.CheckConstraint("LENGTH(TRIM(name)) > 0", name='chk_tenant_name_not_empty'),
        sa.CheckConstraint("LENGTH(TRIM(code)) > 0", name='chk_tenant_code_not_empty'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for hrm_tenant
    op.create_index('idx_hrm_tenant_code', 'hrm_tenant', ['code'])
    op.create_index('idx_hrm_tenant_is_active', 'hrm_tenant', ['is_active'])
    op.create_index('idx_hrm_tenant_created_at', 'hrm_tenant', ['created_at'])
    
    # Add table comments
    op.execute("COMMENT ON TABLE hrm_tenant IS 'Top-level tenant entity for multi-tenant HRMS'")
    op.execute("COMMENT ON COLUMN hrm_tenant.code IS 'Unique tenant code for identification'")
    
    # 2. CREATE hrm_company TABLE
    op.create_table(
        'hrm_company',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        
        # Company details
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('uen', sa.String(50), nullable=True),  # Unique Entity Number (Singapore)
        sa.Column('registration_number', sa.String(100), nullable=True),
        sa.Column('tax_id', sa.String(50), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('logo_path', sa.String(255), nullable=True),
        
        # Status
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        
        # Audit fields
        sa.Column('created_by', sa.String(100), nullable=False, server_default=sa.text("'system'")),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('modified_by', sa.String(100), nullable=True),
        sa.Column('modified_at', sa.DateTime(timezone=True), nullable=True),
        
        # Constraints
        sa.ForeignKeyConstraint(['tenant_id'], ['hrm_tenant.id'], ondelete='CASCADE', name='fk_company_tenant'),
        sa.CheckConstraint("LENGTH(TRIM(name)) > 0", name='chk_company_name_not_empty'),
        sa.CheckConstraint("LENGTH(TRIM(code)) > 0", name='chk_company_code_not_empty'),
        sa.UniqueConstraint('tenant_id', 'code', name='uq_company_tenant_code'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for hrm_company
    op.create_index('idx_hrm_company_tenant_id', 'hrm_company', ['tenant_id'])
    op.create_index('idx_hrm_company_code', 'hrm_company', ['code'])
    op.create_index('idx_hrm_company_is_active', 'hrm_company', ['is_active'])
    op.create_index('idx_hrm_company_created_at', 'hrm_company', ['created_at'])
    
    # Add table comments
    op.execute("COMMENT ON TABLE hrm_company IS 'Company entities belonging to a tenant'")
    op.execute("COMMENT ON COLUMN hrm_company.tenant_id IS 'Foreign key to hrm_tenant'")
    op.execute("COMMENT ON COLUMN hrm_company.uen IS 'Singapore Unique Entity Number'")
    
    # 3. ADD tenant_id TO organization TABLE
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'organization' AND column_name = 'tenant_id'
            ) THEN
                ALTER TABLE organization ADD COLUMN tenant_id UUID;
                ALTER TABLE organization 
                    ADD CONSTRAINT fk_organization_tenant 
                    FOREIGN KEY (tenant_id) REFERENCES hrm_tenant(id) ON DELETE SET NULL;
                CREATE INDEX idx_organization_tenant_id ON organization(tenant_id);
                RAISE NOTICE 'Added tenant_id column to organization table';
            END IF;
        END $$;
    """)
    
    # 4. ADD company_id TO hrm_employee TABLE
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_employee' AND column_name = 'company_id'
            ) THEN
                ALTER TABLE hrm_employee ADD COLUMN company_id UUID;
                ALTER TABLE hrm_employee 
                    ADD CONSTRAINT fk_employee_company 
                    FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE;
                CREATE INDEX idx_hrm_employee_company_id ON hrm_employee(company_id);
                RAISE NOTICE 'Added company_id column to hrm_employee table';
            END IF;
        END $$;
    """)
    
    # 5. ADD AUDIT FIELDS TO hrm_employee
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_employee' AND column_name = 'created_by'
            ) THEN
                ALTER TABLE hrm_employee ADD COLUMN created_by VARCHAR(100) DEFAULT 'system';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_employee' AND column_name = 'modified_by'
            ) THEN
                ALTER TABLE hrm_employee ADD COLUMN modified_by VARCHAR(100);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_employee' AND column_name = 'modified_at'
            ) THEN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'hrm_employee' AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE hrm_employee RENAME COLUMN updated_at TO modified_at;
                ELSE
                    ALTER TABLE hrm_employee ADD COLUMN modified_at TIMESTAMPTZ;
                END IF;
            END IF;
        END $$;
    """)
    
    # 6. ADD AUDIT FIELDS TO organization
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'organization' AND column_name = 'created_by'
            ) THEN
                ALTER TABLE organization ADD COLUMN created_by VARCHAR(100) DEFAULT 'system';
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'organization' AND column_name = 'modified_by'
            ) THEN
                ALTER TABLE organization ADD COLUMN modified_by VARCHAR(100);
            END IF;
            
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'organization' AND column_name = 'modified_at'
            ) THEN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'organization' AND column_name = 'updated_at'
                ) THEN
                    ALTER TABLE organization RENAME COLUMN updated_at TO modified_at;
                ELSE
                    ALTER TABLE organization ADD COLUMN modified_at TIMESTAMPTZ;
                END IF;
            END IF;
        END $$;
    """)
    
    # 7. CREATE TRIGGER FUNCTION FOR AUTO-UPDATING modified_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_modified_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.modified_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # 8. CREATE TRIGGERS FOR AUTO-UPDATING modified_at
    op.execute("""
        DROP TRIGGER IF EXISTS trg_hrm_tenant_modified_at ON hrm_tenant;
        CREATE TRIGGER trg_hrm_tenant_modified_at
            BEFORE UPDATE ON hrm_tenant
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_at_column();
    """)
    
    op.execute("""
        DROP TRIGGER IF EXISTS trg_hrm_company_modified_at ON hrm_company;
        CREATE TRIGGER trg_hrm_company_modified_at
            BEFORE UPDATE ON hrm_company
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_at_column();
    """)
    
    op.execute("""
        DROP TRIGGER IF EXISTS trg_hrm_employee_modified_at ON hrm_employee;
        CREATE TRIGGER trg_hrm_employee_modified_at
            BEFORE UPDATE ON hrm_employee
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_at_column();
    """)
    
    op.execute("""
        DROP TRIGGER IF EXISTS trg_organization_modified_at ON organization;
        CREATE TRIGGER trg_organization_modified_at
            BEFORE UPDATE ON organization
            FOR EACH ROW
            EXECUTE FUNCTION update_modified_at_column();
    """)


def downgrade():
    """Downgrade migration - Remove tenant company hierarchy schema"""
    
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS trg_organization_modified_at ON organization")
    op.execute("DROP TRIGGER IF EXISTS trg_hrm_employee_modified_at ON hrm_employee")
    op.execute("DROP TRIGGER IF EXISTS trg_hrm_company_modified_at ON hrm_company")
    op.execute("DROP TRIGGER IF EXISTS trg_hrm_tenant_modified_at ON hrm_tenant")
    
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_modified_at_column()")
    
    # Remove columns and constraints from existing tables
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'hrm_employee' AND column_name = 'company_id'
            ) THEN
                ALTER TABLE hrm_employee DROP CONSTRAINT IF EXISTS fk_employee_company;
                ALTER TABLE hrm_employee DROP COLUMN company_id;
            END IF;
        END $$;
    """)
    
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'organization' AND column_name = 'tenant_id'
            ) THEN
                ALTER TABLE organization DROP CONSTRAINT IF EXISTS fk_organization_tenant;
                ALTER TABLE organization DROP COLUMN tenant_id;
            END IF;
        END $$;
    """)
    
    # Drop tables
    op.drop_table('hrm_company')
    op.drop_table('hrm_tenant')