# Company Dropdown Not Loading - Troubleshooting Guide

## Problem
The **Select Company** dropdown on the Payroll Generate page appears empty, preventing users from generating payroll.

## Root Cause Analysis

The company dropdown requires a specific data structure:

```
Tenant (e.g., "Default Tenant")
  └─ Organization (e.g., "My Company")
       └─ User (logged-in user)
  └─ Company (e.g., "Main Branch")
       └─ Employee assignments
```

The dropdown is empty because **one or more of these links are missing**:

### Possible Issues:

1. **User's Organization is NOT linked to a Tenant**
   - Organization.tenant_id = NULL ❌
   - Solution: Link organization to tenant

2. **No Companies exist for the Tenant**
   - Company.query.filter_by(tenant_id=...) returns 0 results ❌
   - Solution: Create companies for the tenant

3. **Companies are NOT marked as active**
   - Company.is_active = False ❌
   - Solution: Mark companies as active

4. **User has NO Organization assigned**
   - User.organization = None ❌
   - Solution: Assign organization to user

---

## How to Fix

### Step 1: Build and Run the Application

```bash
# Navigate to project directory
cd D:/Projects/HRMS/hrm

# Install dependencies (if not already done)
pip install -r requirements.txt

# Run the application
python main.py
```

### Step 2: Check Debug Output

When you access the Payroll Generate page, check the **console output** for debug information:

```
[PAYROLL DEBUG] ===== PAYROLL GENERATE PAGE DEBUG INFO =====
[PAYROLL DEBUG] User: admin (ID: 1)
[PAYROLL DEBUG] User organization_id: 1
[PAYROLL DEBUG] ✅ Organization Name: Default Organization
[PAYROLL DEBUG] ✅ Organization Tenant ID: <UUID>
[PAYROLL DEBUG] ✅ Found 0 ACTIVE companies for tenant <UUID>
[PAYROLL DEBUG] ===== END DEBUG INFO =====
```

**Key indicators to look for:**
- ✅ Green checkmarks = working correctly
- ❌ Red X = issue found

### Step 3: Run the Fix Script

The fix script will automatically set up the required data:

```bash
python fix_company_dropdown.py
```

**What this script does:**
1. ✅ Creates a default Tenant if none exists
2. ✅ Links all Organizations to the Tenant
3. ✅ Creates a default Company if none exists
4. ✅ Assigns employees to the Company
5. ✅ Provides verification report

### Expected Output:

```
================================================================================
COMPANY DROPDOWN FIX SCRIPT
================================================================================

📋 STEP 1: Checking current users...
   Found 1 users

📋 STEP 2: Checking Tenant...
   ✅ Tenant found: Default Tenant (Code: DEFAULT)

📋 STEP 3: Linking Organizations to Tenant...
   Found 1 organizations
   ✅ Linked organization: Default Organization

📋 STEP 4: Checking Company...
   ✅ Company found: Default Company (Code: DEFAULT-CO)

📋 STEP 5: Assigning employees to company...
   Found 5 employees
   ✅ Assigned 5 employee(s) to company

📋 STEP 6: Final Verification...

   --- User Details ---

   User: admin
     Organization: Default Organization
     Tenant ID: <UUID>
     Companies available: 1
       - Default Company
       ✅ Companies will appear in dropdown!

================================================================================
✅ FIX SCRIPT COMPLETED SUCCESSFULLY!
================================================================================
```

### Step 4: Refresh and Verify

1. Log out from the application
2. Log back in
3. Navigate to **Payroll > Generate Payroll**
4. The **Select Company** dropdown should now display available companies

---

## Troubleshooting - Still Not Working?

### If dropdown is STILL empty after running fix script:

#### Check 1: Verify You're Logged In
- Make sure you're logged in with a user account
- The dropdown won't appear until you're authenticated

#### Check 2: Check User Permissions
The user must have one of these roles:
- `Super Admin`
- `Tenant Admin`
- `HR Manager`

Navigate to User Management to verify user role.

#### Check 3: Run Diagnostic Script
```bash
python diagnose_company_simple.py
```

This will create `DIAGNOSIS_OUTPUT.txt` with detailed information:
- All users and their organizations
- Which organizations have tenants
- Which companies exist
- Which employees are assigned to companies

#### Check 4: Check Database Connection
Verify your `.env` file has correct database credentials:

```bash
# For Development
DEV_DATABASE_URL=postgresql://user:password@localhost:5432/hrms_db
DEV_SESSION_SECRET=your-secret-key

# For Production
PROD_DATABASE_URL=postgresql://user:password@host:5432/hrms_prod
PROD_SESSION_SECRET=your-prod-secret-key
```

Run connection test:
```bash
python verify_db.py
```

---

## Database Structure Reference

### Related Tables:

| Table | Purpose | Key Field |
|-------|---------|-----------|
| `hrm_tenant` | Top-level tenant | `id` (UUID) |
| `organization` | User organization | `tenant_id` (links to tenant) |
| `hrm_users` | User accounts | `organization_id` (links to organization) |
| `hrm_company` | Company entities | `tenant_id` (links to tenant), `is_active` |
| `hrm_employee` | Employee records | `company_id` (links to company) |

### SQL Queries for Verification:

**Check if organizations have tenant_id:**
```sql
SELECT id, name, tenant_id FROM organization WHERE tenant_id IS NULL;
```

**Check if companies exist:**
```sql
SELECT id, name, tenant_id, is_active FROM hrm_company WHERE is_active = TRUE;
```

**Check if employees have company_id:**
```sql
SELECT employee_id, first_name, company_id FROM hrm_employee WHERE company_id IS NULL LIMIT 5;
```

---

## Expected Workflow

### After Fix Script Runs Successfully:

1. **Tenant** exists with code `DEFAULT`
2. **Organization** is linked to Tenant
3. **Company** exists and is marked active
4. **Employees** are assigned to Company
5. **User** can select company → month → year → Load Data

### Page Flow:

```
Payroll Generate Page (GET)
  ↓
Read User's Organization
  ↓
Check if Organization has Tenant
  ↓
Query Companies for that Tenant (WHERE is_active = TRUE)
  ↓
Display in Dropdown
  ↓
User selects Company + Month + Year
  ↓
Click "Load Employee Data"
  ↓
API Call: /api/payroll/preview?company_id=...&month=...&year=...
  ↓
Fetch Employees for Company
  ↓
Display Payroll Preview Table
```

---

## Quick Checklist

- [ ] Application is running on port 5000
- [ ] You're logged in with Super Admin or HR Manager role
- [ ] You ran `python fix_company_dropdown.py`
- [ ] No errors in console output
- [ ] Page shows "Companies available: 1" or more
- [ ] Company dropdown displays "Default Company"
- [ ] You can select month and year
- [ ] "Load Employee Data" button works
- [ ] Employee payroll data appears in table

---

## Support

If you're still experiencing issues after following these steps:

1. **Check the console output** for `[PAYROLL DEBUG]` messages
2. **Run the diagnostic script** and review the output
3. **Check the database** using provided SQL queries
4. **Review .env configuration** for database connection
5. **Verify user permissions** - user must have correct role

---

## Key Configuration Points

### routes.py - Line 1700-1736
The payroll_generate route that populates the dropdown

### templates/payroll/generate.html - Line 32-54
The dropdown UI and error messages

### models.py
- Line 592: Organization model
- Line 99: Company model
- Line 52: Tenant model
- Line 240: Employee model

### app.py
Database configuration and Flask app setup