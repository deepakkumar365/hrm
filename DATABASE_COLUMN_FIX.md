# 🔧 Database Schema Fix: Missing currency_code Column

## 🚨 Problem

When accessing the Companies Master as a Tenant Admin user, you're getting this error:

```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column hrm_company.currency_code does not exist
```

## 📋 Root Cause

The Python model (`models.py`) has been updated to include a `currency_code` column for the Company table, but **the actual database table hasn't been updated** with this column yet. This is a database schema mismatch.

**Model Definition (exists in code):**
```python
# models.py, line 148
currency_code = db.Column(db.String(10), nullable=False, default='SGD')
```

**Database Table (missing in database):**
```
hrm_company table does NOT have the currency_code column
```

## ✅ Solution

The missing column needs to be added to the database table. There are two ways to fix this:

### Option 1: Automatic Fix (Recommended) ⚡

**Step 1:** Run the fix script
```bash
python fix_currency_column.py
```

Or use the batch file:
```bash
apply_fix.bat
```

**What it does:**
- Checks if the column already exists
- Adds the `currency_code` column with:
  - Type: VARCHAR(10)
  - Default value: 'SGD' (Singapore Dollar)
  - Nullable: NO

**Expected output:**
```
✅ Successfully added currency_code column to hrm_company
   - Column type: VARCHAR(10)
   - Default value: 'SGD'
   - Nullable: NO
```

### Option 2: Manual SQL Fix 🛠️

If you prefer to run SQL directly:

```sql
ALTER TABLE hrm_company 
ADD COLUMN currency_code VARCHAR(10) NOT NULL DEFAULT 'SGD';
```

### Option 3: Using Alembic Migration 📦

If you want to apply this as a proper database migration:

```bash
alembic upgrade head
```

This will apply all pending migrations, including `add_company_currency_code.py`.

## 🧪 Verification

After applying the fix, verify it worked:

```python
python verify_db.py
```

Or using SQL:
```sql
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='hrm_company' AND column_name='currency_code';
```

## 🎯 What This Column Does

The `currency_code` column stores the currency for each company:

- **Field Name:** currency_code
- **Type:** VARCHAR(10)
- **Default:** SGD (Singapore Dollar)
- **Purpose:** 
  - Stores company's primary currency
  - Used in payroll calculations
  - Used in financial reports
  - Supports: SGD, USD, EUR, GBP, INR, MYR, THB, IDR, PHP, VND

## 📊 Impact

After the fix:

✅ Tenant Admin can access Companies Master  
✅ Can create/edit/delete companies  
✅ Can set company currency  
✅ All payroll calculations work correctly  
✅ All financial reports display with correct currency  

## 🚀 Next Steps

1. **Apply the fix:**
   ```bash
   python fix_currency_column.py
   ```

2. **Restart your application**

3. **Test access:**
   - Log in as Tenant Admin
   - Navigate to: `/companies`
   - Verify companies list loads ✅

4. **Create a test company:**
   - Click "Add Company"
   - Select currency (e.g., SGD, USD)
   - Submit ✅

## 🆘 Troubleshooting

### Error: "column already exists"
This is fine - the column is already there. The fix script will detect this and skip.

### Error: "Permission denied" (during fix)
You may need admin/elevated privileges to modify the database. Try:
```bash
sudo python fix_currency_column.py
```

### Error: Database connection failed
Check:
1. Database is running
2. Database credentials in `.env` are correct
3. Network connectivity to database server

### Still getting the error after fix?
Try restarting the Flask application to refresh the SQLAlchemy connection pool.

## 📝 Files Involved

- **Model Definition:** `models.py` (line 148)
- **Migration File:** `migrations/versions/add_company_currency_code.py`
- **Fix Script:** `fix_currency_column.py` (created)
- **Batch File:** `apply_fix.bat` (created)
- **Routes:** `routes_tenant_company.py` (uses currency_code)

## 🔄 Prevention

To prevent this in the future:

1. **Always run migrations after pulling code:**
   ```bash
   alembic upgrade head
   ```

2. **Check for pending migrations:**
   ```bash
   alembic current
   ```

3. **Create new migrations when modifying models:**
   ```bash
   alembic revision --autogenerate -m "Description of change"
   ```

## 💡 Additional Notes

- This is a **one-time fix** (the column only needs to be added once)
- The fix is **safe and reversible** (can be rolled back if needed)
- The fix **doesn't affect existing data**
- All existing companies will get the default currency: SGD

## 📞 Support

If you continue to experience issues:

1. Check the logs: `tail -f app.log`
2. Verify database connectivity
3. Ensure all migrations are up to date
4. Restart the application

---

**Status:** ⚠️ Database schema out of sync - requires immediate attention  
**Solution:** Add missing currency_code column to hrm_company table  
**Effort:** < 1 minute (automatic fix available)  
**Risk:** Low (safe schema addition with sensible defaults)  