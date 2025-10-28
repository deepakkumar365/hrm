# How to Run SQL Scripts in pgAdmin

## Overview
This document explains how to use the SQL scripts to set up your HRM database directly in pgAdmin without using Python migrations.

## Files
1. **COMPLETE_SCHEMA.sql** - Creates all 25+ tables with proper indexes and constraints
2. **SAMPLE_DATA.sql** - Inserts sample data for testing
3. **HOW_TO_USE_SQL_SCRIPTS.md** - This file

---

## Prerequisites
- PostgreSQL 12+ installed and running
- pgAdmin installed and connected to your PostgreSQL database
- A database created (e.g., `hrm_db`)

---

## Step 1: Create a New Database in pgAdmin

1. Open pgAdmin
2. Right-click on "Databases"
3. Click "Create" → "Database"
4. Name it: `hrm_db`
5. Click "Save"

---

## Step 2: Run the Schema Script

1. In pgAdmin, right-click on `hrm_db` and select "Query Tool"
2. Copy the entire content of **COMPLETE_SCHEMA.sql**
3. Paste it into the Query Editor
4. Click "Execute" (or press F5)
5. Wait for completion - you should see "Query returned successfully with no result"

### Expected Output
✅ All tables created
✅ All indexes created
✅ All constraints created

---

## Step 3: Run the Sample Data Script

1. In the same Query Tool (or open a new one for `hrm_db`)
2. Copy the entire content of **SAMPLE_DATA.sql**
3. Paste it into the Query Editor
4. Click "Execute"
5. Wait for completion

### Expected Output
✅ Sample roles inserted
✅ Sample organization inserted
✅ Sample employees inserted
✅ Sample users inserted
✅ Sample payroll data inserted
✅ Verification queries show record counts

---

## Step 4: Verify the Setup

Run these queries in the Query Tool to verify everything worked:

### Check Total Tables
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

### Check Record Counts
```sql
SELECT 
    'role' as table_name, COUNT(*) as total FROM role
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
ORDER BY table_name;
```

### Check Users (for login)
```sql
SELECT username, email, first_name, last_name 
FROM hrm_users 
ORDER BY created_at DESC;
```

### Check Employees
```sql
SELECT employee_id, first_name, last_name, email, basic_salary
FROM hrm_employee
ORDER BY created_at DESC;
```

---

## Step 5: Configure Your .env File

Update your `.env` file with the PostgreSQL connection details:

```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/hrm_db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=hrm_db
```

---

## Step 6: Start the Application

Now you can start your Flask application:

```bash
python main.py
```

The app should:
- Connect to PostgreSQL
- Skip migrations (since DB is already set up)
- Start on http://localhost:5000

---

## Test Login Credentials

Use these credentials to log in:

| Username | Email | Password | Role |
|----------|-------|----------|------|
| admin | admin@acme.com | password123 | Super Admin |
| hr_manager | hr@acme.com | password123 | HR Manager |

---

## Troubleshooting

### Error: "Database already exists"
- Drop the database first:
  ```sql
  DROP DATABASE IF EXISTS hrm_db;
  CREATE DATABASE hrm_db;
  ```

### Error: "UUID type does not exist"
- The script should auto-create the UUID extension. If it fails, run:
  ```sql
  CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
  ```

### Error: "Foreign key constraint violation"
- Make sure you ran **COMPLETE_SCHEMA.sql** FIRST before **SAMPLE_DATA.sql**
- Tables must be created in order of dependencies

### Error: "Password hash invalid"
- The password hashes in SAMPLE_DATA.sql are placeholder hashes
- When you log in, you'll need to reset passwords via the app
- Or use the password reset scripts provided

### Tables not appearing
- Make sure you're connected to the `hrm_db` database
- Refresh the database in pgAdmin (press F5)
- Check that there were no SQL errors during execution

---

## What Was Created

### 25+ Tables
- User Management: `hrm_users`, `role`, `hrm_user_role_mapping`
- Employee Management: `hrm_employee`, `hrm_employee_documents`, `hrm_employee_bank_info`
- Organization: `organization`, `hrm_tenant`, `hrm_company`
- Payroll: `hrm_payroll`, `hrm_payroll_configuration`
- Attendance: `hrm_attendance`
- Leave Management: `hrm_leave`
- Claims: `hrm_claim`
- Appraisals: `hrm_appraisal`
- Masters: `hrm_designation`, `hrm_departments`, `hrm_working_hours`, `hrm_work_schedules`
- Configuration: `hrm_tenant_configuration`, `hrm_tenant_payment_config`, `hrm_tenant_documents`
- Access Control: `hrm_role_access_control`
- Audit: `hrm_audit_log`
- Migrations: `alembic_version`

### Sample Data
- 5 Roles
- 1 Tenant
- 1 Company
- 1 Organization
- 2 Users (admin + hr_manager)
- 5 Designations
- 3 Working Hours configurations
- 4 Work Schedules
- 2 Employees
- 1 Payroll record
- 1 Attendance record
- 1 Leave application
- 1 Claim
- 9 Role Access Control rules

---

## Next Steps

1. ✅ Create database
2. ✅ Run COMPLETE_SCHEMA.sql
3. ✅ Run SAMPLE_DATA.sql
4. ✅ Verify with queries
5. ✅ Update .env file
6. ✅ Start application
7. ✅ Log in with admin/password123
8. ✅ Configure your organization

---

## Support

If you encounter any issues:
1. Check the error message in pgAdmin Query Tool
2. Verify all prerequisites are met
3. Run the verification queries above
4. Check that PostgreSQL is running
5. Review the troubleshooting section

---

**Last Updated:** 2025-01-23
**Compatible With:** PostgreSQL 12+, pgAdmin 4+