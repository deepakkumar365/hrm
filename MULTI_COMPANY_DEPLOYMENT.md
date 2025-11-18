# Multi-Company Support Deployment Guide

## 📋 Overview

This document provides step-by-step instructions for deploying the **Multi-Company Support** feature for HR Manager dashboard. This enhancement allows users to be assigned to multiple companies and access them through a centralized dropdown selector.

---

## 🔄 Changes Made

### Phase 1: Template Field Name Fixes ✅ COMPLETE

**Fixed Files:**
1. `templates/hr_manager_dashboard.html` (line 607)
   - Changed: `{{ company.company_name }}` → `{{ company.name }}`

2. `templates/hr_manager/generate_payroll.html` (line 201)
   - Changed: `{{ company.company_name }}` → `{{ company.name }}`

**Impact:** Company dropdown now displays correctly without rendering errors.

---

### Phase 2: Multi-Company Database Support ✅ COMPLETE

#### 1. **New Database Migration**
- **File:** `migrations/versions/add_user_company_access.py`
- **Creates:** `hrm_user_company_access` junction table
- **Purpose:** Links users to multiple companies (many-to-many relationship)
- **Schema:**
  ```sql
  CREATE TABLE hrm_user_company_access (
    id UUID PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES hrm_users(id) ON DELETE CASCADE,
    company_id UUID NOT NULL REFERENCES hrm_company(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL,
    modified_at TIMESTAMP,
    UNIQUE(user_id, company_id)
  );
  ```

#### 2. **Model Changes**
- **File:** `models.py`
- **Changes:**
  - Added `UserCompanyAccess` model class (junction table)
  - Updated `User` model with:
    - `company_access` relationship property
    - `get_accessible_companies()` method
  
- **New Method:** `User.get_accessible_companies()`
  - Returns all companies accessible by the user
  - Handles Super Admin (all companies)
  - Handles HR Manager/Tenant Admin (assigned companies)
  - Fallback to employee's company (legacy support)

#### 3. **Routes Enhancement**
- **File:** `routes_hr_manager.py`
- **Changes:**
  - Updated `get_user_companies()` to use new `User.get_accessible_companies()` method
  - Automatically supports multiple companies without code changes

#### 4. **Data Migration Script**
- **File:** `migrate_user_company_access.py`
- **Purpose:** Populate UserCompanyAccess with existing user-company relationships
- **Actions:**
  - Super Admin users → granted access to all companies
  - HR Manager/Tenant Admin → granted access to their employee's company
  - Prevents duplicate entries (checks existing relationships)

---

## 🚀 Deployment Steps

### Step 1: Run Database Migration

```bash
# In project root directory
flask db upgrade

# Or manually run:
python -c "from flask_migrate import upgrade; from app import app; upgrade(app=app)"
```

**Expected Output:**
```
[alembic.migration] Running upgrade add_certification_pass_renewal -> add_user_company_access
✓ Created hrm_user_company_access junction table
✓ Created index on hrm_user_company_access.company_id
✓ Created index on hrm_user_company_access.user_id
INFO [alembic.migration] Done.
```

### Step 2: Run Data Migration Script

```bash
# Populate UserCompanyAccess with existing user-company relationships
python migrate_user_company_access.py
```

**Expected Output:**
```
🔄 Starting User-Company Access Migration...
------------------------------------------------------------
✓ Super Admin 'superadmin' - Added access to 2 company(ies)
✓ HR Manager 'hr.manager' - Added access to company Acme Corp
✓ Tenant Admin 'tenant.admin' - Added access to company Tech Inc
------------------------------------------------------------
✓ Migration Complete!
  - Migrated: 3 user-company access records
  - Skipped: 0 (already exist or not applicable)
  - Errors: 0

✓ Total users processed: 10
```

### Step 3: Verify Database Changes

```bash
# Check if table was created correctly
python verify_db.py
```

Or using SQL directly:
```sql
SELECT COUNT(*) FROM hrm_user_company_access;
SELECT u.username, c.name, ua.created_at 
FROM hrm_user_company_access ua
JOIN hrm_users u ON ua.user_id = u.id
JOIN hrm_company c ON ua.company_id = c.id
LIMIT 10;
```

### Step 4: Test HR Manager Dashboard

1. **Login as HR Manager**
   - Navigate to `/dashboard/hr-manager`
   
2. **Verify Company Dropdown**
   - Should display company names (not errors)
   - If assigned to multiple companies, all should appear
   - Can switch between companies without errors

3. **Test Company Selector**
   - Click dropdown
   - Select different company
   - Dashboard data should refresh
   - URL should update with `?company_id=...`

### Step 5: Test Payroll Generation (Optional)

1. Navigate to `/dashboard/hr-manager/generate-payroll`
2. Verify company dropdown displays correctly
3. Should only show companies assigned to the user

---

## 🔍 Verification Checklist

- [ ] Database migration completed without errors
- [ ] `hrm_user_company_access` table exists in database
- [ ] Data migration script executed successfully
- [ ] HR Manager Dashboard loads without template errors
- [ ] Company dropdown displays company names correctly
- [ ] Company selector switches between companies
- [ ] Dashboard data updates when company changes
- [ ] Super Admin sees all companies
- [ ] HR Manager sees only assigned companies
- [ ] No SQL errors in application logs

---

## 🔧 Troubleshooting

### Issue: Template still shows empty dropdown or error

**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Restart Flask development server
3. Check that migration was applied:
   ```sql
   SELECT * FROM alembic_version ORDER BY version_num DESC LIMIT 1;
   ```

### Issue: "company.name" renders as empty in template

**Diagnosis:**
- Check database: `SELECT id, name FROM hrm_company LIMIT 5;`
- Verify companies have `name` field populated (not NULL)

**Solution:**
```sql
UPDATE hrm_company SET name = 'Company ' || code WHERE name IS NULL;
```

### Issue: Data migration script fails

**Diagnosis:**
```python
# Check if relationships are properly loaded
from app import app, db
from models import User, Company, UserCompanyAccess
with app.app_context():
    user = User.query.first()
    print(f"User role: {user.role}")
    print(f"Employee company: {user.employee_profile.company if user.employee_profile else 'None'}")
```

**Solution:** Ensure database migration ran successfully first, then retry migration script.

### Issue: HR Manager sees no companies after migration

**Diagnosis:**
```sql
SELECT * FROM hrm_user_company_access WHERE user_id = <user_id>;
```

**Solution:** Run migration script again or manually insert records:
```python
from app import app, db
from models import User, UserCompanyAccess

with app.app_context():
    user = User.query.filter_by(username='hr.manager').first()
    if user and user.employee_profile and user.employee_profile.company:
        access = UserCompanyAccess(
            user_id=user.id,
            company_id=user.employee_profile.company_id
        )
        db.session.add(access)
        db.session.commit()
```

---

## 📝 Future Enhancements

1. **Admin Interface for Company Assignment**
   - Add UI to assign users to multiple companies
   - Allow Super Admin to grant/revoke company access

2. **Company Selection Persistence**
   - Remember last selected company per user
   - Store in user session or database preference

3. **Audit Logging**
   - Track company access changes
   - Log which user assigned/revoked access

4. **Bulk Operations**
   - Bulk assign companies to multiple users
   - Import user-company mappings from CSV

---

## 📞 Support

If you encounter issues during deployment:

1. Check application logs: `tail -f logs/app.log`
2. Review database migration status: `flask db history`
3. Run verification script: `python verify_db.py`
4. Check model relationships in Python shell:
   ```python
   python
   from app import app, db
   from models import User, UserCompanyAccess
   with app.app_context():
       user = User.query.first()
       companies = user.get_accessible_companies()
       print(f"User {user.username} can access: {[c.name for c in companies]}")
   ```

---

## ✅ Rollback Instructions

If needed to rollback this feature:

```bash
# 1. Downgrade database migration
flask db downgrade

# 2. Revert model changes in models.py
# 3. Revert routes_hr_manager.py get_user_companies() function
```

---

**Last Updated:** December 21, 2024
**Version:** 1.0
**Status:** Ready for Production Deployment