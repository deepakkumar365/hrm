# Designation ID Migration - Temporary Fix

## Issue
The `designation_id` column was defined in the `Employee` model but hadn't been migrated to the database, causing:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) column hrm_employee.designation_id does not exist
```

## Temporary Fix Applied
The following changes have been made to allow the app to work while the migration is pending:

### 1. **models.py** (Line 281)
- Commented out: `designation_id = db.Column(...)`
- This prevents SQLAlchemy from trying to query the column

### 2. **routes.py** (Lines 809-815 and 1247-1253)
- Commented out code that tries to set `employee.designation_id`
- This prevents assignments to the non-existent column

### 3. **templates/employees/form.html** (Line 162)
- Simplified the conditional to not access `employee.designation_id`
- The designation selector will still appear in the form but won't pre-select values until the migration is applied

## Next Steps - When Ready to Apply the Migration

### Step 1: Restore Code
Uncomment the following lines:
1. **models.py line 281**: Uncomment the `designation_id` column definition
2. **routes.py lines 809-815**: Uncomment the designation handling code (create employee)
3. **routes.py lines 1247-1253**: Uncomment the designation handling code (edit employee)
4. **templates/employees/form.html line 162**: Restore the full conditional

### Step 2: Run the Migration
In PyCharm Terminal:
```bash
flask db upgrade
```

Or with Alembic directly:
```bash
alembic upgrade head
```

### Step 3: Restart the App
After the migration completes successfully, restart your Flask development server.

## Migration File
The migration file is located at:
```
D:/Projects/HRMS/hrm/migrations/versions/add_designation_to_employee.py
```

This migration will:
- Add the `designation_id` INTEGER column to `hrm_employee` table
- Add a foreign key constraint to `hrm_designation(id)`

---

**Status**: ⚠️ Temporary fix applied - app is functional but designation feature is disabled until migration is applied.