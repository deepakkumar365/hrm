# Quick Start - After Migration Fix

## What Was Fixed
The application had a **"Multiple head revisions" error** in Alembic migrations. This has been completely resolved by:
1. Consolidating 2 separate migration branches into 1 linear chain
2. Fixing broken migration references
3. Removing an empty merge migration
4. Replacing Unicode emoji with ASCII text for Windows compatibility

## How to Run

### Option 1: Run WITHOUT Auto-Migration (Current Setup)
```bash
python main.py
```
The app will start but warn that database tables don't exist. Run migrations separately:
```bash
flask db upgrade
```

### Option 2: Run WITH Auto-Migration (Recommended)
```bash
# Windows PowerShell
$env:AUTO_MIGRATE_ON_STARTUP="true"
python main.py

# Linux/Mac
export AUTO_MIGRATE_ON_STARTUP=true
python main.py
```
This will automatically run all migrations on startup.

### Option 3: Make it Permanent (Add to .env)
Edit `.env` file and add:
```
AUTO_MIGRATE_ON_STARTUP=true
```

## Verify Everything Works

1. **Check migrations are applied:**
   ```bash
   flask db current
   ```
   Should show: `08_insert_tenant_company_test_data` (the last migration)

2. **Check database tables exist:**
   ```bash
   flask shell
   >>> from sqlalchemy import inspect
   >>> inspector = inspect(db.engine)
   >>> inspector.get_table_names()
   ```

3. **View migration history:**
   ```bash
   flask db history
   ```

## Troubleshooting

### If you see "Multiple head revisions" error again:
1. Clear Python cache: `find . -type d -name __pycache__ -exec rm -r {} +`
2. Re-run: `python main.py`

### If migrations don't run:
1. Check environment variable: `echo $env:AUTO_MIGRATE_ON_STARTUP` (Windows) or `echo $AUTO_MIGRATE_ON_STARTUP` (Linux)
2. Manually run: `flask db upgrade`

### If database connection fails:
1. Ensure PostgreSQL is running
2. Check `.env` file has correct `DEV_DATABASE_URL` or `PROD_DATABASE_URL`
3. Test connection: `flask shell` (should not error)

## What Changed

✅ **Fixed Files:**
- 13 migration files updated (down_revision references corrected)
- 1 migration file deleted (empty merge migration)
- `routes.py` updated (emoji to ASCII conversion)

✅ **Migration Chain:**
- Before: 2 heads, multiple broken branches
- After: 1 head, 16 migrations in linear chain

✅ **Status:**
- ✅ App starts without errors
- ✅ Single migration head confirmed
- ✅ No broken references
- ✅ Windows PowerShell compatible

## Files Reference

**Key Migration Files (In Order):**
1. `28f425a665b2_initial_schema_creation.py` - Root/Initial tables
2. `add_organization_logo.py` - Organization logo
3. `add_org_address_uen.py` - Organization address
4. `remove_role_column_from_users.py` - User role changes
5. `add_enhancements_fields.py` - Document & enhancement fields
6. `add_payroll_configuration.py` - Payroll config table
7. `add_payroll_enhancements.py` - Payroll enhancements
8. `add_designation_to_employee.py` - Designation field
9. `add_payroll_indexes.py` - Performance indexes
10. `add_attendance_lop_and_payroll_fields.py` - Attendance fields
11. `add_tenant_configuration.py` - Tenant config
12. `add_overtime_group_id.py` - Overtime grouping
13-16. Tenant hierarchy migrations

## Next Steps

1. Run the application: `python main.py`
2. Visit: `http://localhost:5000`
3. Set up your organization and users
4. Start using the HRM system!

For more details, see: `MIGRATION_FIX_SUMMARY.md`