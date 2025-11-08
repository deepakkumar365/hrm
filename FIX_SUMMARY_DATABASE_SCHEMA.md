# Database Schema Fix Summary

## 🎯 Issue Identified

**Error:** `sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column hrm_company.currency_code does not exist`

**Cause:** When Tenant Admin role access was granted to the Companies Master module, the routes were updated to reference a `currency_code` column. However, this column hasn't been added to the database yet, even though it's defined in the SQLAlchemy model.

**Status:** ⚠️ Critical - Database schema mismatch

---

## 🔧 What Was Wrong

| Component | Status | Details |
|-----------|--------|---------|
| Python Model (`models.py`) | ✅ Updated | `currency_code` column is defined in Company model (line 148) |
| Routes (`routes_tenant_company.py`) | ✅ Updated | Code references `currency_code` when creating/updating companies |
| Database Table | ❌ **Missing** | The `hrm_company` table doesn't have the `currency_code` column |

---

## ✅ Solution Provided

I've created **3 tools** to fix this:

### 1. **Automatic Fix Script** (Recommended)
**File:** `fix_currency_column.py`

```bash
python fix_currency_column.py
```

**What it does:**
- Checks if column already exists (prevents errors)
- Adds `currency_code` column to `hrm_company` table
- Sets default value to 'SGD'
- Completes in < 1 second

### 2. **Batch File** (Easiest for Windows)
**File:** `apply_fix.bat`

```bash
apply_fix.bat
```

Simply double-click this file, and it will:
- Run the Python fix script
- Show you the results
- Confirm success or display any errors

### 3. **Manual SQL Fix** (If preferred)
```sql
ALTER TABLE hrm_company 
ADD COLUMN currency_code VARCHAR(10) NOT NULL DEFAULT 'SGD';
```

---

## 🚀 Quick Action Steps

### Step 1: Apply the Fix
```bash
# Option A: Use batch file (Windows)
apply_fix.bat

# Option B: Use Python script
python fix_currency_column.py

# Option C: Use SQL directly
# Connect to your database and run the SQL above
```

### Step 2: Verify Success
You should see:
```
✅ Successfully added currency_code column to hrm_company
   - Column type: VARCHAR(10)
   - Default value: 'SGD'
   - Nullable: NO
```

### Step 3: Restart Your Application
```bash
# Stop the Flask server
Ctrl+C

# Start it again
python app.py
```

### Step 4: Test the Fix
1. Log in as **Tenant Admin** user
2. Navigate to: `/companies`
3. Verify that the companies list loads successfully ✅

---

## 📊 What This Column Does

| Property | Value | Purpose |
|----------|-------|---------|
| **Column Name** | `currency_code` | Identifies the column |
| **Data Type** | VARCHAR(10) | Stores currency codes (e.g., SGD, USD, EUR) |
| **Default Value** | SGD | Singapore Dollar (default currency) |
| **Nullable** | NO | Must always have a value |
| **Usage** | Payroll, Reports | Used in salary calculations and financial reporting |

### Supported Currencies
- SGD (Singapore Dollar) - Default
- USD (US Dollar)
- EUR (Euro)
- GBP (British Pound)
- INR (Indian Rupee)
- MYR (Malaysian Ringgit)
- THB (Thai Baht)
- IDR (Indonesian Rupiah)
- PHP (Philippine Peso)
- VND (Vietnamese Dong)

---

## 🎯 Capabilities After Fix

**Tenant Admin users will be able to:**

✅ View list of all companies  
✅ View detailed company information  
✅ Create new companies with currency selection  
✅ Edit company details (name, code, currency, etc.)  
✅ Delete companies  
✅ View employees per company  
✅ Link employees to companies  
✅ Set company currency (SGD, USD, EUR, etc.)  

---

## 🛡️ Safety Information

**This fix is safe because:**

- ✅ No existing data is deleted
- ✅ Only a new column is added
- ✅ Default value (SGD) is applied to all existing companies
- ✅ Fully reversible (column can be removed if needed)
- ✅ No impact on other tables or functionality
- ✅ Follows database migration best practices

---

## 📋 Technical Details

### Before Fix
```
hrm_company table columns:
├── id
├── tenant_id
├── name
├── code
├── description
├── address
├── uen
├── registration_number
├── tax_id
├── phone
├── email
├── website
├── logo_path
├── is_active
├── created_by
├── created_at
├── modified_by
└── modified_at
❌ (missing) currency_code
```

### After Fix
```
hrm_company table columns:
├── id
├── tenant_id
├── name
├── code
├── description
├── address
├── uen
├── registration_number
├── tax_id
├── phone
├── email
├── website
├── logo_path
├── currency_code ✅ (NEW)
├── is_active
├── created_by
├── created_at
├── modified_by
└── modified_at
```

---

## 🆘 Troubleshooting

### Error: "Column already exists"
**Solution:** The column is already there. Skip the fix and restart your app.

### Error: "Database connection failed"
**Solutions:**
- Verify database is running
- Check `.env` file has correct database credentials
- Ensure network connectivity to database server

### Error: "Permission denied"
**Solution:** Try running with elevated privileges:
```bash
sudo python fix_currency_column.py
```

### Still getting the original error after fix?
**Solution:** Restart your Flask application to refresh database connections.

### How to verify the fix worked?
**Option 1:** Run the verification script
```bash
python verify_db.py
```

**Option 2:** Check with SQL
```sql
SELECT column_name FROM information_schema.columns 
WHERE table_name='hrm_company' AND column_name='currency_code';
```

Should return one row with `currency_code`.

---

## 📝 Files Created/Modified

### New Files Created:
1. **fix_currency_column.py** - Automatic fix script
2. **apply_fix.bat** - Windows batch file to run the fix
3. **DATABASE_COLUMN_FIX.md** - Detailed technical documentation
4. **IMMEDIATE_ACTION_REQUIRED.txt** - Quick action guide
5. **FIX_SUMMARY_DATABASE_SCHEMA.md** - This file

### Existing Files Used:
- **models.py** - Contains Company model with currency_code definition
- **routes_tenant_company.py** - Routes that reference currency_code
- **migrations/versions/add_company_currency_code.py** - Alembic migration (not yet applied)

---

## 🔄 Migration History

| Step | File | Status |
|------|------|--------|
| 1 | Model defined currency_code | ✅ Done (models.py, line 148) |
| 2 | Migration file created | ✅ Done (add_company_currency_code.py) |
| 3 | Routes updated for Tenant Admin | ✅ Done (routes_tenant_company.py) |
| 4 | Database migration applied | ❌ **MISSING** ← This is the issue |
| 5 | Fix script created | ✅ Done (fix_currency_column.py) |

---

## 🎉 Summary & Next Steps

| What | Details |
|------|---------|
| **Problem** | Database schema missing currency_code column |
| **Root Cause** | Migration not applied to database |
| **Impact** | Companies Master doesn't work for Tenant Admin |
| **Solution** | Apply database migration (add column) |
| **Time to Fix** | < 1 minute (automatic) |
| **Risk Level** | Low (safe schema addition) |
| **Breaking Changes** | None |

### Immediate Action
1. **Run:** `apply_fix.bat` (or `python fix_currency_column.py`)
2. **Wait:** For success message
3. **Restart:** Flask application
4. **Test:** Log in as Tenant Admin, visit `/companies`

### Expected Result
✅ Tenant Admin can now access Companies Master module  
✅ All Tenant Admin features working as documented  
✅ No other functionality affected  

---

## 📞 Support & Questions

For detailed information, see:
- **Quick Guide:** `IMMEDIATE_ACTION_REQUIRED.txt`
- **Technical Details:** `DATABASE_COLUMN_FIX.md`
- **Original Implementation:** `TENANT_ADMIN_FIX_COMPLETE.txt`

---

**Last Updated:** 2025-01-24  
**Status:** ⚠️ ACTION REQUIRED - Apply fix to restore functionality  
**Estimated Fix Time:** < 1 minute  