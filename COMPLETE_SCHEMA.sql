-- ============================================
-- COMPLETE HRM DATABASE SCHEMA
-- ============================================
-- Run this in pgAdmin to create the entire database structure
-- PostgreSQL 12+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- 1. ROLE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS role (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 2. TENANT TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_tenant (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    country_code VARCHAR(10),
    currency_code VARCHAR(10),
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(100),
    modified_at TIMESTAMP,
    CONSTRAINT uc_tenant_name UNIQUE(name),
    CONSTRAINT uc_tenant_code UNIQUE(code)
);

-- Indexes for Tenant
CREATE INDEX idx_hrm_tenant_code ON hrm_tenant(code);
CREATE INDEX idx_hrm_tenant_is_active ON hrm_tenant(is_active);
CREATE INDEX idx_hrm_tenant_created_at ON hrm_tenant(created_at);

-- ============================================
-- 3. COMPANY TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_company (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES hrm_tenant(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    description TEXT,
    address TEXT,
    uen VARCHAR(50),
    registration_number VARCHAR(100),
    tax_id VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    logo_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(100),
    modified_at TIMESTAMP,
    CONSTRAINT uq_company_tenant_code UNIQUE(tenant_id, code)
);

-- Indexes for Company
CREATE INDEX idx_hrm_company_tenant_id ON hrm_company(tenant_id);
CREATE INDEX idx_hrm_company_code ON hrm_company(code);
CREATE INDEX idx_hrm_company_is_active ON hrm_company(is_active);
CREATE INDEX idx_hrm_company_created_at ON hrm_company(created_at);

-- ============================================
-- 4. ORGANIZATION TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS organization (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    address TEXT,
    uen VARCHAR(50),
    logo_path VARCHAR(255),
    tenant_id UUID REFERENCES hrm_tenant(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    modified_by VARCHAR(100)
);

-- ============================================
-- 5. USERS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(120) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    must_reset_password BOOLEAN DEFAULT TRUE NOT NULL,
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    role_id INTEGER NOT NULL REFERENCES role(id),
    reporting_manager_id INTEGER REFERENCES hrm_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Users
CREATE INDEX ix_hrm_users_role_id ON hrm_users(role_id);
CREATE INDEX ix_hrm_users_organization_id ON hrm_users(organization_id);
CREATE INDEX ix_hrm_users_reporting_manager_id ON hrm_users(reporting_manager_id);

-- ============================================
-- 6. DESIGNATION TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_designation (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    modified_by VARCHAR(100)
);

-- ============================================
-- 7. WORKING HOURS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_working_hours (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    hours_per_day NUMERIC(4, 2) NOT NULL,
    hours_per_week NUMERIC(4, 2) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. WORK SCHEDULES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_work_schedules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    break_duration INTEGER DEFAULT 60,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 9. DEPARTMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    manager_id INTEGER REFERENCES hrm_employee(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forward declaration handled by adding constraints later

-- ============================================
-- 10. EMPLOYEE TABLE (Main)
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_employee (
    id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    father_name VARCHAR(100),
    email VARCHAR(120) UNIQUE NOT NULL,
    phone VARCHAR(20),
    nric VARCHAR(20) UNIQUE NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(10),
    nationality VARCHAR(50),
    address TEXT,
    postal_code VARCHAR(10),
    location VARCHAR(100),
    profile_image_path VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'UTC',
    position VARCHAR(100) NOT NULL,
    designation_id INTEGER REFERENCES hrm_designation(id),
    department VARCHAR(100),
    hire_date DATE NOT NULL,
    employment_type VARCHAR(20),
    work_permit_type VARCHAR(30),
    work_permit_number VARCHAR(50),
    work_permit_expiry DATE,
    basic_salary NUMERIC(10, 2) NOT NULL,
    allowances NUMERIC(10, 2) DEFAULT 0,
    hourly_rate NUMERIC(8, 2),
    cpf_account VARCHAR(20),
    employee_cpf_rate NUMERIC(5, 2) DEFAULT 20.00,
    employer_cpf_rate NUMERIC(5, 2) DEFAULT 17.00,
    bank_name VARCHAR(100),
    bank_account VARCHAR(30),
    account_holder_name VARCHAR(100),
    swift_code VARCHAR(11),
    ifsc_code VARCHAR(11),
    is_active BOOLEAN DEFAULT TRUE,
    termination_date DATE,
    user_id INTEGER REFERENCES hrm_users(id),
    organization_id INTEGER NOT NULL REFERENCES organization(id),
    manager_id INTEGER REFERENCES hrm_employee(id) ON DELETE SET NULL,
    company_id UUID REFERENCES hrm_company(id) ON DELETE CASCADE,
    working_hours_id INTEGER REFERENCES hrm_working_hours(id),
    work_schedule_id INTEGER REFERENCES hrm_work_schedules(id),
    overtime_group_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    modified_by VARCHAR(100)
);

-- Now add foreign key to hrm_departments for manager
ALTER TABLE hrm_departments
ADD CONSTRAINT fk_departments_manager 
FOREIGN KEY (manager_id) REFERENCES hrm_employee(id);

-- ============================================
-- 11. TENANT PAYMENT CONFIG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_tenant_payment_config (
    id SERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES hrm_tenant(id) ON DELETE CASCADE,
    payment_type VARCHAR(20) NOT NULL DEFAULT 'Fixed',
    implementation_charges NUMERIC(10, 2) DEFAULT 0,
    monthly_charges NUMERIC(10, 2) DEFAULT 0,
    other_charges NUMERIC(10, 2) DEFAULT 0,
    frequency VARCHAR(20) NOT NULL DEFAULT 'Monthly',
    created_by VARCHAR(100) NOT NULL DEFAULT 'system',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified_by VARCHAR(100),
    modified_at TIMESTAMP
);

-- Indexes for Payment Config
CREATE INDEX idx_hrm_tenant_payment_tenant_id ON hrm_tenant_payment_config(tenant_id);

-- ============================================
-- 12. TENANT DOCUMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_tenant_documents (
    id SERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES hrm_tenant(id) ON DELETE CASCADE,
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_type VARCHAR(50),
    file_size INTEGER,
    uploaded_by VARCHAR(100) NOT NULL,
    upload_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Tenant Documents
CREATE INDEX idx_hrm_tenant_documents_tenant_id ON hrm_tenant_documents(tenant_id);

-- ============================================
-- 13. TENANT CONFIGURATION TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_tenant_configuration (
    id SERIAL PRIMARY KEY,
    tenant_id UUID NOT NULL UNIQUE REFERENCES hrm_tenant(id) ON DELETE CASCADE,
    payslip_logo_path VARCHAR(255),
    payslip_logo_filename VARCHAR(255),
    payslip_logo_uploaded_by VARCHAR(100),
    payslip_logo_uploaded_at TIMESTAMP,
    employee_id_prefix VARCHAR(50) DEFAULT 'EMP',
    employee_id_company_code VARCHAR(20),
    employee_id_format VARCHAR(100) DEFAULT 'prefix-company-number',
    employee_id_separator VARCHAR(5) DEFAULT '-',
    employee_id_next_number INTEGER DEFAULT 1,
    employee_id_pad_length INTEGER DEFAULT 4,
    employee_id_suffix VARCHAR(50),
    overtime_enabled BOOLEAN DEFAULT TRUE,
    overtime_calculation_method VARCHAR(20) DEFAULT 'By User',
    overtime_group_type VARCHAR(50),
    general_overtime_rate NUMERIC(5, 2) DEFAULT 1.5,
    holiday_overtime_rate NUMERIC(5, 2) DEFAULT 2.0,
    weekend_overtime_rate NUMERIC(5, 2) DEFAULT 1.5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(100)
);

-- Indexes for Tenant Configuration
CREATE INDEX idx_tenant_config_tenant_id ON hrm_tenant_configuration(tenant_id);

-- ============================================
-- 14. EMPLOYEE BANK INFO TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_employee_bank_info (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL UNIQUE REFERENCES hrm_employee(id) ON DELETE CASCADE,
    bank_account_name VARCHAR(100),
    bank_account_number VARCHAR(30),
    bank_code VARCHAR(20),
    paynow_no VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Employee Bank Info
CREATE INDEX ix_hrm_employee_bank_info_employee_id ON hrm_employee_bank_info(employee_id);

-- ============================================
-- 15. PAYROLL CONFIGURATION TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_payroll_configuration (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL UNIQUE REFERENCES hrm_employee(id),
    allowance_1_name VARCHAR(100) DEFAULT 'Transport Allowance',
    allowance_1_amount NUMERIC(10, 2) DEFAULT 0,
    allowance_2_name VARCHAR(100) DEFAULT 'Housing Allowance',
    allowance_2_amount NUMERIC(10, 2) DEFAULT 0,
    allowance_3_name VARCHAR(100) DEFAULT 'Meal Allowance',
    allowance_3_amount NUMERIC(10, 2) DEFAULT 0,
    allowance_4_name VARCHAR(100) DEFAULT 'Other Allowance',
    allowance_4_amount NUMERIC(10, 2) DEFAULT 0,
    levy_allowance_name VARCHAR(100) DEFAULT 'Levy Allowance',
    levy_allowance_amount NUMERIC(10, 2) DEFAULT 0,
    ot_rate_per_hour NUMERIC(8, 2),
    employer_cpf NUMERIC(10, 2) DEFAULT 0,
    employee_cpf NUMERIC(10, 2) DEFAULT 0,
    net_salary NUMERIC(10, 2) DEFAULT 0,
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES hrm_users(id)
);

-- Indexes for Payroll Configuration
CREATE INDEX ix_hrm_payroll_config_employee_id ON hrm_payroll_configuration(employee_id);

-- ============================================
-- 16. PAYROLL TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_payroll (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hrm_employee(id),
    pay_period_start DATE NOT NULL,
    pay_period_end DATE NOT NULL,
    basic_pay NUMERIC(10, 2) NOT NULL,
    overtime_pay NUMERIC(10, 2) DEFAULT 0,
    allowances NUMERIC(10, 2) DEFAULT 0,
    bonuses NUMERIC(10, 2) DEFAULT 0,
    gross_pay NUMERIC(10, 2) NOT NULL,
    employee_cpf NUMERIC(10, 2) DEFAULT 0,
    employer_cpf NUMERIC(10, 2) DEFAULT 0,
    income_tax NUMERIC(10, 2) DEFAULT 0,
    other_deductions NUMERIC(10, 2) DEFAULT 0,
    net_pay NUMERIC(10, 2) NOT NULL,
    days_worked INTEGER DEFAULT 0,
    overtime_hours NUMERIC(5, 2) DEFAULT 0,
    leave_days INTEGER DEFAULT 0,
    absent_days INTEGER DEFAULT 0,
    lop_days INTEGER DEFAULT 0,
    lop_deduction NUMERIC(10, 2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Draft',
    generated_by INTEGER REFERENCES hrm_users(id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 17. ATTENDANCE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_attendance (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hrm_employee(id),
    date DATE NOT NULL,
    clock_in TIME,
    clock_out TIME,
    break_start TIME,
    break_end TIME,
    regular_hours NUMERIC(5, 2) DEFAULT 0,
    overtime_hours NUMERIC(5, 2) DEFAULT 0,
    total_hours NUMERIC(5, 2) DEFAULT 0,
    has_overtime BOOLEAN DEFAULT FALSE,
    overtime_approved BOOLEAN,
    overtime_approved_by INTEGER REFERENCES hrm_users(id) ON DELETE SET NULL,
    overtime_approved_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Pending',
    remarks TEXT,
    lop BOOLEAN DEFAULT FALSE,
    location_lat VARCHAR(20),
    location_lng VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_attendance_employee_date UNIQUE(employee_id, date)
);

-- ============================================
-- 18. LEAVE TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_leave (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hrm_employee(id),
    leave_type VARCHAR(30) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days_requested INTEGER NOT NULL,
    reason TEXT,
    status VARCHAR(20) DEFAULT 'Pending',
    requested_by INTEGER REFERENCES hrm_users(id),
    approved_by INTEGER REFERENCES hrm_users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 19. CLAIM TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_claim (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hrm_employee(id),
    claim_type VARCHAR(30) NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    claim_date DATE NOT NULL,
    description TEXT,
    receipt_number VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Pending',
    submitted_by INTEGER REFERENCES hrm_users(id),
    approved_by INTEGER REFERENCES hrm_users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 20. APPRAISAL TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_appraisal (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hrm_employee(id),
    review_period_start DATE NOT NULL,
    review_period_end DATE NOT NULL,
    performance_rating INTEGER,
    goals_achievement INTEGER,
    teamwork_rating INTEGER,
    communication_rating INTEGER,
    overall_rating NUMERIC(3, 2),
    self_review TEXT,
    manager_feedback TEXT,
    development_goals TEXT,
    training_recommendations TEXT,
    status VARCHAR(20) DEFAULT 'Draft',
    reviewed_by INTEGER REFERENCES hrm_users(id),
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 21. EMPLOYEE DOCUMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_employee_documents (
    id SERIAL PRIMARY KEY,
    employee_id INTEGER NOT NULL REFERENCES hrm_employee(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    issue_date DATE NOT NULL,
    month INTEGER,
    year INTEGER,
    description TEXT,
    uploaded_by INTEGER REFERENCES hrm_users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Employee Documents
CREATE INDEX ix_hrm_employee_documents_employee_id ON hrm_employee_documents(employee_id);
CREATE INDEX ix_hrm_employee_documents_document_type ON hrm_employee_documents(document_type);
CREATE INDEX ix_hrm_employee_documents_year_month ON hrm_employee_documents(year, month);

-- ============================================
-- 22. COMPLIANCE REPORT TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_compliance_report (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(20) NOT NULL,
    period_month INTEGER NOT NULL,
    period_year INTEGER NOT NULL,
    file_path VARCHAR(255),
    file_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Generated',
    total_employees INTEGER,
    total_amount NUMERIC(12, 2),
    generated_by INTEGER REFERENCES hrm_users(id),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    submitted_at TIMESTAMP
);

-- ============================================
-- 23. USER ROLE MAPPING TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_user_role_mapping (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES hrm_users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES role(id) ON DELETE CASCADE,
    company_id UUID REFERENCES hrm_company(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system'
);

-- Indexes for User Role Mapping
CREATE INDEX idx_user_role_mapping_user_id ON hrm_user_role_mapping(user_id);

-- ============================================
-- 24. ROLE ACCESS CONTROL TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_role_access_control (
    id SERIAL PRIMARY KEY,
    module_name VARCHAR(100) NOT NULL,
    menu_name VARCHAR(100) NOT NULL,
    sub_menu_name VARCHAR(100),
    super_admin_access VARCHAR(20) DEFAULT 'Editable',
    tenant_admin_access VARCHAR(20) DEFAULT 'Hidden',
    hr_manager_access VARCHAR(20) DEFAULT 'Hidden',
    employee_access VARCHAR(20) DEFAULT 'Hidden',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',
    updated_by VARCHAR(100)
);

-- Indexes for Role Access Control
CREATE INDEX idx_role_access_module_menu ON hrm_role_access_control(module_name, menu_name);

-- ============================================
-- 25. AUDIT LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS hrm_audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES hrm_users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100) NOT NULL,
    changes TEXT,
    status VARCHAR(20) DEFAULT 'Success',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for Audit Log
CREATE INDEX idx_audit_log_user_id ON hrm_audit_log(user_id);
CREATE INDEX idx_audit_log_action ON hrm_audit_log(action);
CREATE INDEX idx_audit_log_created_at ON hrm_audit_log(created_at);

-- ============================================
-- 26. ALEMBIC VERSION TABLE (for migrations)
-- ============================================
CREATE TABLE IF NOT EXISTS alembic_version (
    version_num VARCHAR(32) NOT NULL,
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- ============================================
-- Verification Query
-- ============================================
-- Run this after setup to verify all tables were created:
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- ORDER BY table_name;