-- =====================================================
-- Add Country and Currency Columns to hrm_tenant
-- =====================================================
-- This migration adds country_code and currency_code columns
-- to the hrm_tenant table to match the Python model
-- Created: 2024
-- Purpose: Fix schema mismatch for tenant country/currency fields
-- =====================================================

-- Add country_code column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hrm_tenant' AND column_name = 'country_code'
    ) THEN
        ALTER TABLE hrm_tenant ADD COLUMN country_code VARCHAR(10);
        RAISE NOTICE 'Added country_code column to hrm_tenant table';
    ELSE
        RAISE NOTICE 'country_code column already exists in hrm_tenant table';
    END IF;
END $$;

-- Add currency_code column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'hrm_tenant' AND column_name = 'currency_code'
    ) THEN
        ALTER TABLE hrm_tenant ADD COLUMN currency_code VARCHAR(10);
        RAISE NOTICE 'Added currency_code column to hrm_tenant table';
    ELSE
        RAISE NOTICE 'currency_code column already exists in hrm_tenant table';
    END IF;
END $$;

-- Add comments for documentation
COMMENT ON COLUMN hrm_tenant.country_code IS 'Country code (e.g., SG, US, IN)';
COMMENT ON COLUMN hrm_tenant.currency_code IS 'Currency code (e.g., SGD, USD, INR)';

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================
-- Summary:
-- ✅ Added country_code column to hrm_tenant table
-- ✅ Added currency_code column to hrm_tenant table
-- ✅ Migration is idempotent and safe to re-run
-- =====================================================