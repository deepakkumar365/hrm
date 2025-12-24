-- Sample Data Setup for Payslip Testing
-- Run this after applying the migration

-- ============================================
-- 1. Update Organization with Logo
-- ============================================

-- Update the first organization with a logo path
UPDATE organization 
SET logo_path = 'logos/company_logo.png'
WHERE id = 1;

-- Verify the update
SELECT id, name, logo_path FROM organization;

-- ============================================
-- 2. Sample Employee Data (if needed)
-- ============================================

-- Check existing employees
SELECT 
    id,
    employee_id,
    first_name,
    last_name,
    position,
    department,
    basic_salary,
    allowances,
    employee_cpf_rate
FROM hrm_employee
LIMIT 5;

-- Update an employee with proper allowances (if needed)
-- UPDATE hrm_employee 
-- SET 
--     allowances = 2000.00,
--     employee_cpf_rate = 20.00,
--     bank_name = 'DBS Bank',
--     bank_account = '1234567890'
-- WHERE id = 1;

-- ============================================
-- 3. Sample Payroll Data (if needed)
-- ============================================

-- Check existing payroll records
SELECT 
    p.id,
    e.first_name,
    e.last_name,
    p.pay_period_start,
    p.pay_period_end,
    p.basic_pay,
    p.allowances,
    p.gross_pay,
    p.employee_cpf,
    p.income_tax,
    p.other_deductions,
    p.net_pay,
    p.status
FROM hrm_payroll p
JOIN hrm_employee e ON p.employee_id = e.id
ORDER BY p.generated_at DESC
LIMIT 5;

-- ============================================
-- 4. Create Sample Payroll Record (Optional)
-- ============================================

-- Uncomment and modify as needed:
/*
INSERT INTO hrm_payroll (
    employee_id,
    pay_period_start,
    pay_period_end,
    basic_pay,
    overtime_pay,
    allowances,
    bonuses,
    gross_pay,
    employee_cpf,
    employer_cpf,
    income_tax,
    other_deductions,
    net_pay,
    days_worked,
    overtime_hours,
    leave_days,
    status,
    generated_by,
    generated_at
) VALUES (
    1,                          -- employee_id (change to valid employee ID)
    '2025-01-01',              -- pay_period_start
    '2025-01-31',              -- pay_period_end
    5000.00,                   -- basic_pay
    500.00,                    -- overtime_pay
    2000.00,                   -- allowances
    1000.00,                   -- bonuses
    8500.00,                   -- gross_pay (basic + overtime + allowances + bonuses)
    1000.00,                   -- employee_cpf (20% of basic)
    850.00,                    -- employer_cpf (17% of basic)
    500.00,                    -- income_tax
    300.00,                    -- other_deductions
    6700.00,                   -- net_pay (gross - employee_cpf - income_tax - other_deductions)
    22,                        -- days_worked
    10.00,                     -- overtime_hours
    0,                         -- leave_days
    'Approved',                -- status
    1,                         -- generated_by (user ID)
    CURRENT_TIMESTAMP          -- generated_at
);
*/

-- ============================================
-- 5. Verification Queries
-- ============================================

-- Check if organization has logo
SELECT 
    id,
    name,
    logo_path,
    CASE 
        WHEN logo_path IS NULL THEN '❌ No logo set'
        ELSE '✅ Logo configured'
    END as logo_status
FROM organization;

-- Check employee data completeness
SELECT 
    e.id,
    e.employee_id,
    e.first_name || ' ' || e.last_name as full_name,
    e.position,
    e.department,
    e.basic_salary,
    e.allowances,
    e.bank_account,
    e.nric,
    CASE 
        WHEN e.allowances IS NULL OR e.allowances = 0 THEN '⚠️ No allowances'
        ELSE '✅ Allowances set'
    END as allowances_status,
    CASE 
        WHEN e.bank_account IS NULL THEN '⚠️ No bank account'
        ELSE '✅ Bank account set'
    END as bank_status
FROM hrm_employee e
WHERE e.is_active = 1
LIMIT 10;

-- Check payroll data completeness
SELECT 
    p.id,
    e.first_name || ' ' || e.last_name as employee_name,
    p.pay_period_start,
    p.pay_period_end,
    p.basic_pay,
    p.allowances,
    p.gross_pay,
    p.employee_cpf,
    p.income_tax,
    p.other_deductions,
    p.net_pay,
    p.status,
    CASE 
        WHEN p.allowances > 0 THEN '✅ Has allowances'
        ELSE '⚠️ No allowances'
    END as allowances_status,
    CASE 
        WHEN p.employee_cpf > 0 OR p.income_tax > 0 OR p.other_deductions > 0 THEN '✅ Has deductions'
        ELSE '⚠️ No deductions'
    END as deductions_status
FROM hrm_payroll p
JOIN hrm_employee e ON p.employee_id = e.id
ORDER BY p.generated_at DESC
LIMIT 10;

-- ============================================
-- 6. Sample Calculation Verification
-- ============================================

-- Verify payroll calculations
SELECT 
    p.id,
    e.first_name || ' ' || e.last_name as employee_name,
    
    -- Earnings
    p.basic_pay,
    p.overtime_pay,
    p.allowances,
    p.bonuses,
    p.gross_pay,
    
    -- Verify gross calculation
    (p.basic_pay + COALESCE(p.overtime_pay, 0) + COALESCE(p.allowances, 0) + COALESCE(p.bonuses, 0)) as calculated_gross,
    CASE 
        WHEN ABS(p.gross_pay - (p.basic_pay + COALESCE(p.overtime_pay, 0) + COALESCE(p.allowances, 0) + COALESCE(p.bonuses, 0))) < 0.01 
        THEN '✅ Correct'
        ELSE '❌ Mismatch'
    END as gross_check,
    
    -- Deductions
    p.employee_cpf,
    p.income_tax,
    p.other_deductions,
    (COALESCE(p.employee_cpf, 0) + COALESCE(p.income_tax, 0) + COALESCE(p.other_deductions, 0)) as total_deductions,
    
    -- Net Pay
    p.net_pay,
    (p.gross_pay - COALESCE(p.employee_cpf, 0) - COALESCE(p.income_tax, 0) - COALESCE(p.other_deductions, 0)) as calculated_net,
    CASE 
        WHEN ABS(p.net_pay - (p.gross_pay - COALESCE(p.employee_cpf, 0) - COALESCE(p.income_tax, 0) - COALESCE(p.other_deductions, 0))) < 0.01 
        THEN '✅ Correct'
        ELSE '❌ Mismatch'
    END as net_check
    
FROM hrm_payroll p
JOIN hrm_employee e ON p.employee_id = e.id
ORDER BY p.generated_at DESC
LIMIT 5;

-- ============================================
-- 7. Allowances Breakdown Preview
-- ============================================

-- Preview how allowances will be broken down in the payslip
SELECT 
    e.id,
    e.employee_id,
    e.first_name || ' ' || e.last_name as employee_name,
    e.allowances as total_allowances,
    ROUND(e.allowances * 0.40, 2) as hra_40_percent,
    ROUND(e.allowances * 0.30, 2) as da_30_percent,
    ROUND(e.allowances * 0.20, 2) as travel_20_percent,
    ROUND(e.allowances * 0.10, 2) as special_10_percent,
    ROUND(e.allowances * 0.40 + e.allowances * 0.30 + e.allowances * 0.20 + e.allowances * 0.10, 2) as breakdown_total
FROM hrm_employee e
WHERE e.is_active = 1 AND e.allowances > 0
LIMIT 10;

-- ============================================
-- 8. Deductions Breakdown Preview
-- ============================================

-- Preview how other deductions will be broken down in the payslip
SELECT 
    p.id,
    e.first_name || ' ' || e.last_name as employee_name,
    p.other_deductions as total_other_deductions,
    ROUND(p.other_deductions * 0.40, 2) as professional_tax_40_percent,
    ROUND(p.other_deductions * 0.30, 2) as esi_30_percent,
    ROUND(p.other_deductions * 0.20, 2) as insurance_20_percent,
    ROUND(p.other_deductions * 0.10, 2) as other_10_percent,
    ROUND(p.other_deductions * 0.40 + p.other_deductions * 0.30 + p.other_deductions * 0.20 + p.other_deductions * 0.10, 2) as breakdown_total
FROM hrm_payroll p
JOIN hrm_employee e ON p.employee_id = e.id
WHERE p.other_deductions > 0
ORDER BY p.generated_at DESC
LIMIT 10;

-- ============================================
-- 9. Complete Payslip Data Preview
-- ============================================

-- This query shows all data that will appear on the payslip
SELECT 
    -- Organization
    o.name as company_name,
    o.logo_path,
    
    -- Employee Info
    e.employee_id as emp_code,
    e.first_name || ' ' || e.last_name as employee_name,
    e.department,
    e.position as designation,
    e.bank_account,
    e.nric as tax_id,
    
    -- Pay Period
    strftime('%Y-%m', p.pay_period_start) as pay_period,
    date(p.generated_at) as pay_date,
    
    -- Earnings
    p.basic_pay,
    ROUND(e.allowances * 0.40, 2) as hra,
    ROUND(e.allowances * 0.30, 2) as da,
    ROUND(e.allowances * 0.20, 2) as travel_allowance,
    ROUND(e.allowances * 0.10, 2) as special_allowance,
    p.overtime_pay,
    p.overtime_hours,
    p.bonuses,
    p.gross_pay,
    
    -- Deductions
    p.employee_cpf,
    e.employee_cpf_rate,
    p.income_tax,
    ROUND(p.other_deductions * 0.40, 2) as professional_tax,
    ROUND(p.other_deductions * 0.30, 2) as esi,
    ROUND(p.other_deductions * 0.20, 2) as insurance,
    ROUND(p.other_deductions * 0.10, 2) as other_ded,
    (COALESCE(p.employee_cpf, 0) + COALESCE(p.income_tax, 0) + COALESCE(p.other_deductions, 0)) as total_deductions,
    
    -- Net Pay
    p.net_pay,
    
    -- Footer
    p.generated_at,
    u.first_name as generated_by_name,
    e.bank_name
    
FROM hrm_payroll p
JOIN hrm_employee e ON p.employee_id = e.id
JOIN organization o ON e.organization_id = o.id
LEFT JOIN hrm_users u ON p.generated_by = u.id
ORDER BY p.generated_at DESC
LIMIT 1;

-- ============================================
-- Notes
-- ============================================

/*
IMPORTANT NOTES:

1. Logo Setup:
   - Place your company logo in: static/logos/company_logo.png
   - Update organization.logo_path to: 'logos/company_logo.png'
   - Recommended size: 120px × 80px

2. Allowances Breakdown:
   - HRA: 40% of employee.allowances
   - DA: 30% of employee.allowances
   - Travel: 20% of employee.allowances
   - Special: 10% of employee.allowances

3. Deductions Breakdown:
   - Professional Tax: 40% of payroll.other_deductions
   - ESI: 30% of payroll.other_deductions
   - Insurance: 20% of payroll.other_deductions
   - Other: 10% of payroll.other_deductions

4. Currency:
   - All amounts displayed as: S$ 1,234.56
   - Singapore Dollar format

5. Testing:
   - After running these queries, visit: /payroll/<payroll_id>/payslip
   - Test print functionality
   - Generate PDF to verify layout
*/