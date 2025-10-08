-- =====================================================
-- Add Tenant Payment Config and Documents Tables
-- =====================================================
-- This migration creates the missing tables for tenant
-- payment configuration and document management
-- Created: 2024
-- Purpose: Complete tenant management schema
-- =====================================================

-- =====================================================
-- 1. CREATE hrm_tenant_payment_config TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS hrm_tenant_payment_config (
    id SERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    
    -- Payment Type: 'Fixed' or 'User-Based'
    payment_type VARCHAR(20) NOT NULL DEFAULT 'Fixed',
    
    -- Fixed Payment Fields
    implementation_charges NUMERIC(10, 2) DEFAULT 0,
    monthly_charges NUMERIC(10, 2) DEFAULT 0,
    other_charges NUMERIC(10, 2) DEFAULT 0,
    
    -- Payment Collection Frequency: 'Monthly', 'Quarterly', 'Half-Yearly', 'Yearly'
    frequency VARCHAR(20) NOT NULL DEFAULT 'Monthly',
    
    -- Audit fields
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_by VARCHAR(100),
    modified_at TIMESTAMPTZ,
    
    -- Constraints
    CONSTRAINT fk_payment_config_tenant FOREIGN KEY (tenant_id) 
        REFERENCES hrm_tenant(id) ON DELETE CASCADE,
    CONSTRAINT chk_payment_type CHECK (payment_type IN ('Fixed', 'User-Based')),
    CONSTRAINT chk_frequency CHECK (frequency IN ('Monthly', 'Quarterly', 'Half-Yearly', 'Yearly'))
);

-- Create index for hrm_tenant_payment_config
CREATE INDEX IF NOT EXISTS idx_hrm_tenant_payment_tenant_id ON hrm_tenant_payment_config(tenant_id);

COMMENT ON TABLE hrm_tenant_payment_config IS 'Tenant payment configuration for billing management';
COMMENT ON COLUMN hrm_tenant_payment_config.payment_type IS 'Payment type: Fixed or User-Based';
COMMENT ON COLUMN hrm_tenant_payment_config.frequency IS 'Payment collection frequency';

-- =====================================================
-- 2. CREATE hrm_tenant_documents TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS hrm_tenant_documents (
    id SERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    
    -- Audit fields
    uploaded_by VARCHAR(100) NOT NULL,
    upload_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT fk_tenant_documents_tenant FOREIGN KEY (tenant_id) 
        REFERENCES hrm_tenant(id) ON DELETE CASCADE
);

-- Create index for hrm_tenant_documents
CREATE INDEX IF NOT EXISTS idx_hrm_tenant_documents_tenant_id ON hrm_tenant_documents(tenant_id);

COMMENT ON TABLE hrm_tenant_documents IS 'Tenant document attachments';
COMMENT ON COLUMN hrm_tenant_documents.file_path IS 'Relative path under static/uploads/';
COMMENT ON COLUMN hrm_tenant_documents.file_type IS 'Document type: Contract, Agreement, License, etc.';

-- =====================================================
-- 3. CREATE TRIGGERS FOR AUTO-UPDATING modified_at
-- =====================================================

-- Trigger for hrm_tenant_payment_config
DROP TRIGGER IF EXISTS trg_hrm_tenant_payment_config_modified_at ON hrm_tenant_payment_config;
CREATE TRIGGER trg_hrm_tenant_payment_config_modified_at
    BEFORE UPDATE ON hrm_tenant_payment_config
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_at_column();

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Summary:
-- ✅ Created hrm_tenant_payment_config table
-- ✅ Created hrm_tenant_documents table
-- ✅ Added foreign key constraints to hrm_tenant
-- ✅ Created indexes for performance
-- ✅ Created triggers for auto-updating modified_at
-- ✅ All operations are idempotent and safe to re-run
-- =====================================================