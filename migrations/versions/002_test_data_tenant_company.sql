-- =====================================================
-- TEST DATA: Tenant → Company → Employee Hierarchy
-- =====================================================
-- This script inserts sample data for testing the hierarchy
-- Safe to run multiple times (uses INSERT ... ON CONFLICT)
-- =====================================================

-- =====================================================
-- 1. INSERT TENANT DATA
-- =====================================================
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

-- =====================================================
-- 2. INSERT COMPANY DATA
-- =====================================================
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

-- =====================================================
-- 3. UPDATE EXISTING ORGANIZATION TO LINK TO TENANT
-- =====================================================
-- Link the first organization to the tenant (if exists)
UPDATE organization 
SET 
    tenant_id = '00000000-0000-0000-0000-000000000001'::UUID,
    modified_by = 'admin@noltrion.com',
    modified_at = NOW()
WHERE id = (SELECT MIN(id) FROM organization)
  AND tenant_id IS NULL;

-- =====================================================
-- 4. LINK EXISTING EMPLOYEES TO COMPANIES (EXAMPLE)
-- =====================================================
-- This is a sample - adjust based on your actual employee data
-- Link first 3 employees to Noltrion Singapore (if they exist)
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

-- =====================================================
-- 5. VERIFICATION QUERIES
-- =====================================================
-- Run these to verify the data was inserted correctly

-- Check tenants
-- SELECT * FROM hrm_tenant;

-- Check companies
-- SELECT c.*, t.name as tenant_name 
-- FROM hrm_company c
-- JOIN hrm_tenant t ON c.tenant_id = t.id;

-- Check employees linked to companies
-- SELECT 
--     e.employee_id,
--     e.first_name,
--     e.last_name,
--     c.name as company_name,
--     t.name as tenant_name
-- FROM hrm_employee e
-- LEFT JOIN hrm_company c ON e.company_id = c.id
-- LEFT JOIN hrm_tenant t ON c.tenant_id = t.id
-- WHERE e.company_id IS NOT NULL;

-- =====================================================
-- TEST DATA INSERTION COMPLETE
-- =====================================================