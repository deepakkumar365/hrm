# Leave Configuration - Database Migration Guide

## Problem
The "Configure Leave Types" menu is showing an error because the `hrm_leave_type` table hasn't been created in your database yet.

## Solution - Run Database Migration

### Option 1: Using Batch File (Easiest - Windows)
1. Double-click the file: `run_migration.bat`
2. Wait for it to complete
3. Refresh your browser and try again

### Option 2: Using Command Line / Terminal
```bash
# Navigate to project directory
cd D:\Projects\HRMS\hrm

# Run migration using Flask CLI
python -m flask db upgrade

# OR run the migration script directly
python run_migration.py
```

### Option 3: Using PyCharm IDE
1. Open PyCharm
2. Go to: **Tools** > **Python Console** (or **Terminal**)
3. Run this command:
   ```bash
   flask db upgrade
   ```
4. You should see: `✅ Migration completed successfully!`

### Option 4: Manual Python Command
```bash
python -c "from app import app; from flask_migrate import upgrade; app.app_context().push(); upgrade()"
```

## Verification

After running the migration:
1. Log in as HR Manager or Tenant Admin
2. Go to **Leave Management** > **Configure Leave Types**
3. You should now see the leave configuration page ✅

## What This Migration Does

Creates a new database table `hrm_leave_type` with:
- Leave type name, code, description
- Annual allocation (number of days)
- Color coding for visual identification
- Company-level association (each company has independent leave types)
- Active/Inactive status
- Audit trail (created_by, created_at, modified_by, modified_at)

## If You Still Get an Error

1. Check your database connection is working
2. Verify you have proper database permissions
3. Check the application logs for detailed error messages
4. Try running: `python verify_db.py` to diagnose database issues

## Rolling Back (If Needed)

To undo the migration:
```bash
flask db downgrade
```

---
**Need Help?** Run this to verify everything:
```bash
python -c "from models import LeaveType; print(f'✅ LeaveType model loaded successfully')"
```