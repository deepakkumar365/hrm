-- ============================================
-- SAMPLE DATA FOR HRM DATABASE
-- ============================================
-- Run this AFTER running COMPLETE_SCHEMA.sql
-- This script adds sample data for testing

-- ============================================
-- 1. INSERT ROLES
-- ============================================
INSERT INTO role (name, description, is_active) VALUES
('Super Admin', 'System administrator with full access', TRUE),
('Tenant Admin', 'Tenant administrator', TRUE),
('HR Manager', 'HR department manager', TRUE),
('Employee', 'Regular employee', TRUE),
('Manager', 'Team manager', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================
-- 2. INSERT TENANT
-- ============================================
INSERT INTO hrm_tenant (name, code, description, is_active, country_code, currency_code, created_by)
VALUES 
('Default Tenant', 'DEFAULT', 'Default tenant for system', TRUE, 'SG', 'SGD', 'system')
ON CONFLICT DO NOTHING;

-- Get the tenant ID for use in next queries
-- Note: This variable is for reference, use the actual UUID in queries below

-- ============================================
-- 3. INSERT COMPANY
-- ============================================
-- First, get the tenant UUID (you need to update this with your actual tenant UUID)
INSERT INTO hrm_company (tenant_id, name, code, description, is_active, created_by)
SELECT 
    id as tenant_id,
    'Acme Corporation',
    'ACME',
    'Default company for testing',
    TRUE,
    'system'
FROM hrm_tenant 
WHERE code = 'DEFAULT'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- 4. INSERT ORGANIZATION
-- ============================================
INSERT INTO organization (name, address, uen, logo_path, created_by)
VALUES 
('Acme Corporation', '123 Business Street, Singapore 123456', 'UEN123456', 'logos/company_logo.png', 'system')
ON CONFLICT DO NOTHING;

-- ============================================
-- 5. INSERT USERS
-- ============================================
-- Super Admin User (password hash for 'password123')
INSERT INTO hrm_users (username, email, password_hash, first_name, last_name, is_active, must_reset_password, organization_id, role_id, created_at)
SELECT 
    'admin',
    'admin@acme.com',
    'pbkdf2:sha256:600000$L8I9E7E3Z8V5Q9O2$8e2a2e5a5e5a5e5a5e5a5e5a5e5a5e5a5e5a5e5a',
    'John',
    'Administrator',
    TRUE,
    FALSE,
    o.id,
    r.id,
    CURRENT_TIMESTAMP
FROM organization o, role r
WHERE o.name = 'Acme Corporation' AND r.name = 'Super Admin'
LIMIT 1
ON CONFLICT DO NOTHING;

-- HR Manager User
INSERT INTO hrm_users (username, email, password_hash, first_name, last_name, is_active, must_reset_password, organization_id, role_id, created_at)
SELECT 
    'hr_manager',
    'hr@acme.com',
    'pbkdf2:sha256:600000$L8I9E7E3Z8V5Q9O2$8e2a2e5a5e5a5e5a5e5a5e5a5e5a5e5a5e5a5e5a',
    'Sarah',
    'Manager',
    TRUE,
    TRUE,
    o.id,
    r.id,
    CURRENT_TIMESTAMP
FROM organization o, role r
WHERE o.name = 'Acme Corporation' AND r.name = 'HR Manager'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- 6. INSERT DESIGNATIONS
-- ============================================
INSERT INTO hrm_designation (name, description, is_active, created_by)
VALUES 
('Software Engineer', 'Senior software engineer position', TRUE, 'system'),
('HR Manager', 'Human Resources Manager', TRUE, 'system'),
('Project Manager', 'Project management position', TRUE, 'system'),
('Sales Executive', 'Sales and business development', TRUE, 'system'),
('Operations Manager', 'Operations management', TRUE, 'system')
ON CONFLICT DO NOTHING;

-- ============================================
-- 7. INSERT WORKING HOURS
-- ============================================
INSERT INTO hrm_working_hours (name, hours_per_day, hours_per_week, description, is_active)
VALUES 
('Standard', 8.00, 40.00, 'Standard 8 hours per day', TRUE),
('Flexible', 8.00, 40.00, 'Flexible working hours', TRUE),
('Part Time', 4.00, 20.00, 'Part-time employment', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================
-- 8. INSERT WORK SCHEDULES
-- ============================================
INSERT INTO hrm_work_schedules (name, start_time, end_time, break_duration, description, is_active)
VALUES 
('Morning Shift', '09:00:00', '18:00:00', 60, 'Standard morning shift', TRUE),
('Evening Shift', '14:00:00', '23:00:00', 60, 'Evening shift', TRUE),
('Night Shift', '23:00:00', '08:00:00', 60, 'Night shift', TRUE),
('Flexible Hours', '09:00:00', '18:00:00', 60, 'Flexible working hours', TRUE)
ON CONFLICT DO NOTHING;

-- ============================================
-- 9. INSERT EMPLOYEES
-- ============================================
INSERT INTO hrm_employee 
(employee_id, first_name, last_name, email, phone, nric, gender, nationality, 
 position, designation_id, hire_date, basic_salary, allowances, hourly_rate, 
 organization_id, company_id, working_hours_id, work_schedule_id, is_active, created_by)
SELECT 
    'EMP001',
    'John',
    'Doe',
    'john.doe@acme.com',
    '+65 9123 4567',
    'S1234567A',
    'Male',
    'Singaporean',
    'Software Engineer',
    d.id,
    '2022-01-15'::DATE,
    5000.00,
    2000.00,
    50.00,
    o.id,
    c.id,
    wh.id,
    ws.id,
    TRUE,
    'system'
FROM organization o, hrm_designation d, hrm_company c, hrm_working_hours wh, hrm_work_schedules ws
WHERE o.name = 'Acme Corporation' 
  AND d.name = 'Software Engineer' 
  AND c.code = 'ACME'
  AND wh.name = 'Standard'
  AND ws.name = 'Morning Shift'
LIMIT 1
ON CONFLICT DO NOTHING;

-- Second Employee
INSERT INTO hrm_employee 
(employee_id, first_name, last_name, email, phone, nric, gender, nationality, 
 position, designation_id, hire_date, basic_salary, allowances, hourly_rate, 
 organization_id, company_id, working_hours_id, work_schedule_id, is_active, created_by)
SELECT 
    'EMP002',
    'Jane',
    'Smith',
    'jane.smith@acme.com',
    '+65 9234 5678',
    'S2345678B',
    'Female',
    'Singaporean',
    'HR Manager',
    d.id,
    '2021-06-01'::DATE,
    6000.00,
    2500.00,
    60.00,
    o.id,
    c.id,
    wh.id,
    ws.id,
    TRUE,
    'system'
FROM organization o, hrm_designation d, hrm_company c, hrm_working_hours wh, hrm_work_schedules ws
WHERE o.name = 'Acme Corporation' 
  AND d.name = 'HR Manager' 
  AND c.code = 'ACME'
  AND wh.name = 'Standard'
  AND ws.name = 'Morning Shift'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- 10. INSERT PAYROLL DATA
-- ============================================
INSERT INTO hrm_payroll 
(employee_id, pay_period_start, pay_period_end, basic_pay, overtime_pay, allowances, 
 bonuses, gross_pay, employee_cpf, income_tax, other_deductions, net_pay, 
 days_worked, overtime_hours, status, generated_by)
SELECT 
    e.id,
    '2025-01-01'::DATE,
    '2025-01-31'::DATE,
    5000.00,
    500.00,
    2000.00,
    1000.00,
    8500.00,
    1000.00,
    500.00,
    300.00,
    6700.00,
    22,
    10.00,
    'Approved',
    u.id
FROM hrm_employee e, hrm_users u, organization o
WHERE e.employee_id = 'EMP001' 
  AND u.username = 'admin'
  AND e.organization_id = o.id
  AND o.name = 'Acme Corporation'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- 11. INSERT TENANT PAYMENT CONFIG
-- ============================================
INSERT INTO hrm_tenant_payment_config (tenant_id, payment_type, implementation_charges, monthly_charges, frequency, created_by)
SELECT 
    t.id,
    'Fixed',
    5000.00,
    2000.00,
    'Monthly',
    'system'
FROM hrm_tenant t
WHERE t.code = 'DEFAULT'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- 12. INSERT TENANT CONFIGURATION
-- ============================================
INSERT INTO hrm_tenant_configuration 
(tenant_id, payslip_logo_path, employee_id_prefix, employee_id_format, 
 overtime_enabled, overtime_calculation_method, general_overtime_rate, created_by)
SELECT 
    t.id,
    'logos/company_logo.png',
    'EMP',
    'prefix-company-number',
    TRUE,
    'By User',
    1.5,
    'system'
FROM hrm_tenant t
WHERE t.code = 'DEFAULT'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- 13. INSERT ROLE ACCESS CONTROL
-- ============================================
INSERT INTO hrm_role_access_control 
(module_name, menu_name, sub_menu_name, super_admin_access, tenant_admin_access, 
 hr_manager_access, employee_access, created_by)
VALUES 
('Dashboard', 'Dashboard', NULL, 'Editable', 'Editable', 'Viewable', 'Viewable', 'system'),
('Masters', 'Employees', 'Add Employee', 'Editable', 'Editable', 'Editable', 'Hidden', 'system'),
('Masters', 'Employees', 'View Employee', 'Editable', 'Editable', 'Viewable', 'Viewable', 'system'),
('Masters', 'Designations', NULL, 'Editable', 'Editable', 'Viewable', 'Hidden', 'system'),
('Payroll', 'Payroll', 'Generate Payroll', 'Editable', 'Editable', 'Editable', 'Hidden', 'system'),
('Payroll', 'Payroll', 'View Payroll', 'Editable', 'Editable', 'Viewable', 'Viewable', 'system'),
('Attendance', 'Attendance', 'Mark Attendance', 'Editable', 'Editable', 'Editable', 'Editable', 'system'),
('Leave', 'Leave', 'Apply Leave', 'Editable', 'Editable', 'Editable', 'Editable', 'system'),
('Leave', 'Leave', 'Approve Leave', 'Editable', 'Editable', 'Editable', 'Hidden', 'system')
ON CONFLICT DO NOTHING;

-- ============================================
-- 14. INSERT ATTENDANCE DATA
-- ============================================
INSERT INTO hrm_attendance 
(employee_id, date, clock_in, clock_out, regular_hours, overtime_hours, 
 total_hours, status, created_at)
SELECT 
    e.id,
    CURRENT_DATE,
    '09:00:00'::TIME,
    '18:00:00'::TIME,
    8.00,
    0.00,
    8.00,
    'Present',
    CURRENT_TIMESTAMP
FROM hrm_employee e
WHERE e.employee_id = 'EMP001'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- 15. INSERT LEAVE DATA
-- ============================================
INSERT INTO hrm_leave 
(employee_id, leave_type, start_date, end_date, days_requested, reason, status, created_at)
SELECT 
    e.id,
    'Casual Leave',
    CURRENT_DATE + INTERVAL '7 days',
    CURRENT_DATE + INTERVAL '9 days',
    2,
    'Personal reasons',
    'Pending',
    CURRENT_TIMESTAMP
FROM hrm_employee e
WHERE e.employee_id = 'EMP001'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- 16. INSERT CLAIM DATA
-- ============================================
INSERT INTO hrm_claim 
(employee_id, claim_type, amount, claim_date, description, status, created_at)
SELECT 
    e.id,
    'Travel Claim',
    250.00,
    CURRENT_DATE,
    'Travel expenses for business trip',
    'Pending',
    CURRENT_TIMESTAMP
FROM hrm_employee e
WHERE e.employee_id = 'EMP001'
LIMIT 1
ON CONFLICT DO NOTHING;

-- ============================================
-- Verification Queries
-- ============================================
-- Run these to verify data was inserted correctly:

-- Check Roles
SELECT 'Roles' as table_name, COUNT(*) as record_count FROM role;

-- Check Organizations
SELECT 'Organizations' as table_name, COUNT(*) as record_count FROM organization;

-- Check Employees
SELECT 'Employees' as table_name, COUNT(*) as record_count FROM hrm_employee;

-- Check Users
SELECT 'Users' as table_name, COUNT(*) as record_count FROM hrm_users;

-- Check all main tables
SELECT 
    'role' as table_name, COUNT(*) as total 
FROM role
UNION ALL
SELECT 'hrm_tenant', COUNT(*) FROM hrm_tenant
UNION ALL
SELECT 'hrm_company', COUNT(*) FROM hrm_company
UNION ALL
SELECT 'organization', COUNT(*) FROM organization
UNION ALL
SELECT 'hrm_users', COUNT(*) FROM hrm_users
UNION ALL
SELECT 'hrm_employee', COUNT(*) FROM hrm_employee
UNION ALL
SELECT 'hrm_designation', COUNT(*) FROM hrm_designation
UNION ALL
SELECT 'hrm_working_hours', COUNT(*) FROM hrm_working_hours
UNION ALL
SELECT 'hrm_work_schedules', COUNT(*) FROM hrm_work_schedules
UNION ALL
SELECT 'hrm_payroll', COUNT(*) FROM hrm_payroll
UNION ALL
SELECT 'hrm_attendance', COUNT(*) FROM hrm_attendance
UNION ALL
SELECT 'hrm_leave', COUNT(*) FROM hrm_leave
UNION ALL
SELECT 'hrm_claim', COUNT(*) FROM hrm_claim
ORDER BY table_name;

-- Check if default data is loaded
-- Show all employees
SELECT 
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) as full_name,
    e.position,
    e.email,
    e.basic_salary
FROM hrm_employee e
ORDER BY e.created_at DESC;

-- Show all users
SELECT 
    u.username,
    u.email,
    CONCAT(u.first_name, ' ', u.last_name) as full_name,
    r.name as role,
    u.is_active
FROM hrm_users u
JOIN role r ON u.role_id = r.id
ORDER BY u.created_at DESC;

-- Show payroll records
SELECT 
    p.id,
    e.employee_id,
    CONCAT(e.first_name, ' ', e.last_name) as employee_name,
    p.pay_period_start,
    p.pay_period_end,
    p.gross_pay,
    p.net_pay,
    p.status
FROM hrm_payroll p
JOIN hrm_employee e ON p.employee_id = e.id
ORDER BY p.generated_at DESC;