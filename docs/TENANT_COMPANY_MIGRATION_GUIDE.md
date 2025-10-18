# 🏢 Tenant → Company → Employee Hierarchy Migration Guide

## 📋 Overview

This migration adds **multi-tenant support** to your HRMS system with a three-tier hierarchy:

```
Tenant (Top Level)
  └── Company (Mid Level)
       └── Employee (Bottom Level)
```

### Key Features
- ✅ **Idempotent migrations** - Safe to run multiple times
- ✅ **Non-destructive** - Preserves all existing data
- ✅ **Cascading deletes** - Tenant → Companies → Employees
- ✅ **Audit fields** - created_by, created_at, modified_by, modified_at
- ✅ **UUID primary keys** - For tenant and company tables
- ✅ **Production-ready** - Tested for Render deployment

---

## 🗂️ Database Schema Changes

### New Tables Created

#### 1. `hrm_tenant`
```sql
- id (UUID, PK)
- name (VARCHAR 255, UNIQUE)
- code (VARCHAR 50, UNIQUE)
- description (TEXT)
- is_active (BOOLEAN)
- created_by, created_at, modified_by, modified_at
```

#### 2. `hrm_company`
```sql
- id (UUID, PK)
- tenant_id (UUID, FK → hrm_tenant)
- name, code, description
- address, uen, registration_number, tax_id
- phone, email, website, logo_path
- is_active (BOOLEAN)
- created_by, created_at, modified_by, modified_at
```

### Existing Tables Modified

#### 3. `organization` (existing)
**Added columns:**
- `tenant_id` (UUID, FK → hrm_tenant, nullable)
- `created_by`, `modified_by` (audit fields)

#### 4. `hrm_employee` (existing)
**Added columns:**
- `company_id` (UUID, FK → hrm_company, nullable)
- `created_by`, `modified_by` (audit fields)

---

## 🚀 Migration Steps

### Step 1: Backup Your Database
```bash
# Create a backup before running migration
pg_dump $DATABASE_URL > backup_before_tenant_migration.sql
```

### Step 2: Run the Migration Script

#### Option A: Using Python Script (Recommended)
```bash
python run_tenant_company_migration.py
```

This will:
1. Execute the schema migration
2. Verify table creation
3. Optionally insert test data

#### Option B: Manual SQL Execution
```bash
# Connect to your database
psql $DATABASE_URL

# Run the migration
\i migrations/versions/001_add_tenant_company_hierarchy.sql

# Optionally insert test data
\i migrations/versions/002_test_data_tenant_company.sql
```

### Step 3: Update Your Flask Application

Add the new routes to your main application file:

**In `main.py` or `app.py`:**
```python
# Import tenant/company routes
import routes_tenant_company
```

### Step 4: Restart Your Application
```bash
# If using Gunicorn
pkill gunicorn
gunicorn -c gunicorn.conf.py main:app

# If using Flask development server
python main.py
```

---

## 📡 API Endpoints

### Tenant Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/tenants` | List all tenants | Admin, HR Manager |
| GET | `/api/tenants/<uuid>` | Get tenant by ID | Admin, HR Manager |
| POST | `/api/tenants` | Create new tenant | Admin |
| PUT | `/api/tenants/<uuid>` | Update tenant | Admin |
| DELETE | `/api/tenants/<uuid>` | Delete tenant | Admin |

### Company Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/companies` | List all companies | Admin, HR Manager |
| GET | `/api/companies?tenant_id=<uuid>` | List companies by tenant | Admin, HR Manager |
| GET | `/api/companies/<uuid>` | Get company by ID | Admin, HR Manager |
| POST | `/api/companies` | Create new company | Admin, HR Manager |
| PUT | `/api/companies/<uuid>` | Update company | Admin, HR Manager |
| DELETE | `/api/companies/<uuid>` | Delete company | Admin |

### Employee-Company Linking

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| PUT | `/api/employees/<id>/link-company` | Link employee to company | Admin, HR Manager |
| GET | `/api/companies/<uuid>/employees` | Get all employees in company | Admin, HR Manager, Employee |

---

## 🧪 Testing the Migration

### 1. Verify Tables Created
```sql
-- Check if tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('hrm_tenant', 'hrm_company');

-- Check new columns
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'hrm_employee' AND column_name = 'company_id';
```

### 2. Test API Endpoints

#### Create a Tenant
```bash
curl -X POST http://localhost:5000/api/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Noltrion HRM",
    "code": "NOLTRION",
    "description": "Noltrion Group - Global HRMS Tenant"
  }'
```

#### Create a Company
```bash
curl -X POST http://localhost:5000/api/companies \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "<tenant-uuid>",
    "name": "Noltrion Singapore Pte Ltd",
    "code": "NOLTRION-SG",
    "uen": "202012345A",
    "address": "1 Raffles Place, Singapore"
  }'
```

#### Link Employee to Company
```bash
curl -X PUT http://localhost:5000/api/employees/1/link-company \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "<company-uuid>"
  }'
```

---

## 📊 Test Data Included

The migration includes sample data:

### Tenant
- **Name:** Noltrion HRM
- **Code:** NOLTRION

### Companies
1. **Noltrion India Pvt Ltd** (NOLTRION-IN)
   - Location: Bangalore, India
   
2. **Noltrion Singapore Pte Ltd** (NOLTRION-SG)
   - Location: Singapore
   - UEN: 202012345A

---

## 🔄 Rollback Instructions

If you need to rollback the migration:

```sql
-- WARNING: This will delete all tenant/company data

-- Drop foreign key constraints first
ALTER TABLE hrm_employee DROP CONSTRAINT IF EXISTS fk_employee_company;
ALTER TABLE organization DROP CONSTRAINT IF EXISTS fk_organization_tenant;

-- Drop columns from existing tables
ALTER TABLE hrm_employee DROP COLUMN IF EXISTS company_id;
ALTER TABLE hrm_employee DROP COLUMN IF EXISTS created_by;
ALTER TABLE hrm_employee DROP COLUMN IF EXISTS modified_by;

ALTER TABLE organization DROP COLUMN IF EXISTS tenant_id;
ALTER TABLE organization DROP COLUMN IF EXISTS created_by;
ALTER TABLE organization DROP COLUMN IF EXISTS modified_by;

-- Drop new tables
DROP TABLE IF EXISTS hrm_company CASCADE;
DROP TABLE IF EXISTS hrm_tenant CASCADE;

-- Drop trigger function
DROP FUNCTION IF EXISTS update_modified_at_column() CASCADE;
```

---

## 🛡️ Security Considerations

1. **Role-Based Access Control**
   - Only Admins can create/delete tenants
   - HR Managers can manage companies
   - Employees have read-only access to their company data

2. **Audit Trail**
   - All create/update operations track who made the change
   - Timestamps automatically updated via database triggers

3. **Cascading Deletes**
   - Deleting a tenant deletes all its companies and employees
   - Use with caution in production

---

## 📝 Flask Models Updated

The following models have been updated in `models.py`:

### New Models
- `Tenant` - Top-level tenant entity
- `Company` - Company entity under tenant

### Updated Models
- `Employee` - Added `company_id` and `company` relationship
- `Organization` - Added `tenant_id` and `tenant` relationship

---

## 🔧 Troubleshooting

### Issue: Migration fails with "relation already exists"
**Solution:** The migration is idempotent. This is expected if tables already exist. Check the logs to ensure no actual errors occurred.

### Issue: Foreign key constraint violation
**Solution:** Ensure you're linking employees to valid companies and companies to valid tenants.

### Issue: UUID type not found
**Solution:** The migration automatically enables the `uuid-ossp` extension. If it fails, run:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Issue: Permission denied
**Solution:** Ensure your database user has CREATE TABLE and ALTER TABLE permissions.

---

## 📞 Support

For issues or questions:
1. Check the migration logs in the console output
2. Verify your DATABASE_URL is correct
3. Ensure you have the required PostgreSQL extensions
4. Check that your database user has sufficient permissions

---

## ✅ Post-Migration Checklist

- [ ] Database backup created
- [ ] Migration script executed successfully
- [ ] Tables verified in database
- [ ] Test data inserted (optional)
- [ ] Flask routes imported
- [ ] Application restarted
- [ ] API endpoints tested
- [ ] Existing employees linked to companies
- [ ] Production deployment updated

---

## 🎯 Next Steps

1. **Update UI Templates** - Create HTML pages for tenant/company management
2. **Add Validation** - Implement business rules for tenant/company creation
3. **Enhance Security** - Add tenant-level data isolation
4. **Create Reports** - Build analytics for multi-tenant data
5. **Documentation** - Update user guides with new hierarchy

---

**Migration Version:** 1.0  
**Created:** 2024  
**Compatible with:** PostgreSQL 12+, Flask 2.x, SQLAlchemy 2.x