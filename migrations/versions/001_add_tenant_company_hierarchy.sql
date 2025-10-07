-- =====================================================
-- HRMS Tenant → Company → Employee Hierarchy Migration
-- =====================================================
-- This migration is IDEMPOTENT and safe to run multiple times
-- Created: 2024
-- Purpose: Add multi-tenant support with Company hierarchy
-- =====================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =====================================================
-- 1. CREATE hrm_tenant TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS hrm_tenant (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- Audit fields
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_by VARCHAR(100),
    modified_at TIMESTAMPTZ,
    
    -- Metadata
    CONSTRAINT chk_tenant_name_not_empty CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT chk_tenant_code_not_empty CHECK (LENGTH(TRIM(code)) > 0)
);

-- Create indexes for hrm_tenant
CREATE INDEX IF NOT EXISTS idx_hrm_tenant_code ON hrm_tenant(code);
CREATE INDEX IF NOT EXISTS idx_hrm_tenant_is_active ON hrm_tenant(is_active);
CREATE INDEX IF NOT EXISTS idx_hrm_tenant_created_at ON hrm_tenant(created_at);

COMMENT ON TABLE hrm_tenant IS 'Top-level tenant entity for multi-tenant HRMS';
COMMENT ON COLUMN hrm_tenant.code IS 'Unique tenant code for identification';

-- =====================================================
-- 2. CREATE hrm_company TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS hrm_company (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    description TEXT,
    
    -- Company details
    address TEXT,
    uen VARCHAR(50), -- Unique Entity Number (Singapore)
    registration_number VARCHAR(100),
    tax_id VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    logo_path VARCHAR(255),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- Audit fields
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_by VARCHAR(100),
    modified_at TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT fk_company_tenant FOREIGN KEY (tenant_id) 
        REFERENCES hrm_tenant(id) ON DELETE CASCADE,
    CONSTRAINT chk_company_name_not_empty CHECK (LENGTH(TRIM(name)) > 0),
    CONSTRAINT chk_company_code_not_empty CHECK (LENGTH(TRIM(code)) > 0),
    CONSTRAINT uq_company_tenant_code UNIQUE (tenant_id, code)
);

-- Create indexes for hrm_company
CREATE INDEX IF NOT EXISTS idx_hrm_company_tenant_id ON hrm_company(tenant_id);
CREATE INDEX IF NOT EXISTS idx_hrm_company_code ON hrm_company(code);
CREATE INDEX IF NOT EXISTS idx_hrm_company_is_active ON hrm_company(is_active);
CREATE INDEX IF NOT EXISTS idx_hrm_company_created_at ON hrm_company(created_at);

COMMENT ON TABLE hrm_company IS 'Company entities belonging to a tenant';
COMMENT ON COLUMN hrm_company.tenant_id IS 'Foreign key to hrm_tenant';
COMMENT ON COLUMN hrm_company.uen IS 'Singapore Unique Entity Number';

-- =====================================================
-- 3. ADD tenant_id TO organization TABLE (if not exists)
-- =====================================================
-- Link existing Organization table to Tenant
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'organization' AND column_name = 'tenant_id'
    ) THEN
        ALTER TABLE organization ADD COLUMN tenant_id UUID;
        
        -- Add foreign key constraint
        ALTER TABLE organization 
            ADD CONSTRAINT fk_organization_tenant 
            FOREIGN KEY (tenant_id) REFERENCES hrm_tenant(id) ON DELETE SET NULL;
        
        -- Create index
        CREATE INDEX idx_organization_tenant_id ON organization(tenant_id);
        
        RAISE NOTICE 'Added tenant_id column to organization table';
    ELSE
        RAISE NOTICE 'tenant_id column already exists in organization table';
    END IF;
END $$;

-- =====================================================
-- 4. ADD company_id TO hrm_employee TABLE (if not exists)
-- =====================================================
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hrm_employee' AND column_name = 'company_id'
    ) THEN
        ALTER TABLE hrm_employee ADD COLUMN company_id UUID;
        
        -- Add foreign key constraint
        ALTER TABLE hrm_employee 
            ADD CONSTRAINT fk_employee_company 
            FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE;
        
        -- Create index
        CREATE INDEX idx_hrm_employee_company_id ON hrm_employee(company_id);
        
        RAISE NOTICE 'Added company_id column to hrm_employee table';
    ELSE
        RAISE NOTICE 'company_id column already exists in hrm_employee table';
    END IF;
END $$;

-- =====================================================
-- 5. ADD AUDIT FIELDS TO hrm_employee (if not exists)
-- =====================================================
DO $$ 
BEGIN
    -- Add created_by
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hrm_employee' AND column_name = 'created_by'
    ) THEN
        ALTER TABLE hrm_employee ADD COLUMN created_by VARCHAR(100) DEFAULT 'system';
        RAISE NOTICE 'Added created_by column to hrm_employee table';
    END IF;
    
    -- Add modified_by
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hrm_employee' AND column_name = 'modified_by'
    ) THEN
        ALTER TABLE hrm_employee ADD COLUMN modified_by VARCHAR(100);
        RAISE NOTICE 'Added modified_by column to hrm_employee table';
    END IF;
    
    -- Add modified_at (if created_at exists but modified_at doesn't)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hrm_employee' AND column_name = 'modified_at'
    ) THEN
        -- Check if updated_at exists (might be named differently)
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'hrm_employee' AND column_name = 'updated_at'
        ) THEN
            -- Rename updated_at to modified_at for consistency
            ALTER TABLE hrm_employee RENAME COLUMN updated_at TO modified_at;
            RAISE NOTICE 'Renamed updated_at to modified_at in hrm_employee table';
        ELSE
            ALTER TABLE hrm_employee ADD COLUMN modified_at TIMESTAMPTZ;
            RAISE NOTICE 'Added modified_at column to hrm_employee table';
        END IF;
    END IF;
END $$;

-- =====================================================
-- 6. ADD AUDIT FIELDS TO organization (if not exists)
-- =====================================================
DO $$ 
BEGIN
    -- Add created_by
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'organization' AND column_name = 'created_by'
    ) THEN
        ALTER TABLE organization ADD COLUMN created_by VARCHAR(100) DEFAULT 'system';
        RAISE NOTICE 'Added created_by column to organization table';
    END IF;
    
    -- Add modified_by
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'organization' AND column_name = 'modified_by'
    ) THEN
        ALTER TABLE organization ADD COLUMN modified_by VARCHAR(100);
        RAISE NOTICE 'Added modified_by column to organization table';
    END IF;
    
    -- Add modified_at
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'organization' AND column_name = 'modified_at'
    ) THEN
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'organization' AND column_name = 'updated_at'
        ) THEN
            ALTER TABLE organization RENAME COLUMN updated_at TO modified_at;
            RAISE NOTICE 'Renamed updated_at to modified_at in organization table';
        ELSE
            ALTER TABLE organization ADD COLUMN modified_at TIMESTAMPTZ;
            RAISE NOTICE 'Added modified_at column to organization table';
        END IF;
    END IF;
END $$;

-- =====================================================
-- 7. CREATE TRIGGER FUNCTION FOR AUTO-UPDATING modified_at
-- =====================================================
CREATE OR REPLACE FUNCTION update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- 8. CREATE TRIGGERS FOR AUTO-UPDATING modified_at
-- =====================================================

-- Trigger for hrm_tenant
DROP TRIGGER IF EXISTS trg_hrm_tenant_modified_at ON hrm_tenant;
CREATE TRIGGER trg_hrm_tenant_modified_at
    BEFORE UPDATE ON hrm_tenant
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

-- Trigger for hrm_company
DROP TRIGGER IF EXISTS trg_hrm_company_modified_at ON hrm_company;
CREATE TRIGGER trg_hrm_company_modified_at
    BEFORE UPDATE ON hrm_company
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

-- Trigger for hrm_employee
DROP TRIGGER IF EXISTS trg_hrm_employee_modified_at ON hrm_employee;
CREATE TRIGGER trg_hrm_employee_modified_at
    BEFORE UPDATE ON hrm_employee
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

-- Trigger for organization
DROP TRIGGER IF EXISTS trg_organization_modified_at ON organization;
CREATE TRIGGER trg_organization_modified_at
    BEFORE UPDATE ON organization
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

-- =====================================================
-- 9. GRANT PERMISSIONS (adjust as needed for your setup)
-- =====================================================
-- Uncomment and modify if you have specific database users
-- GRANT SELECT, INSERT, UPDATE, DELETE ON hrm_tenant TO your_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON hrm_company TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Summary:
-- ✅ Created hrm_tenant table with audit fields
-- ✅ Created hrm_company table with audit fields
-- ✅ Added tenant_id to organization table
-- ✅ Added company_id to hrm_employee table
-- ✅ Added audit fields (created_by, modified_by, modified_at) to existing tables
-- ✅ Created triggers for auto-updating modified_at timestamps
-- ✅ All operations are idempotent and safe to re-run
-- =====================================================