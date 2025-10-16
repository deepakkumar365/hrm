# Migration Guide: Designation and Role Enhancements

## Overview
This migration adds support for:
- Designation Master (replacing Position field)
- Multiple company mapping per employee
- Multiple role assignment per user

## Pre-Migration Checklist

### 1. Backup Database
```bash
# Create a backup of your PostgreSQL database
pg_dump -h dpg-d2kq4515pdvs739uk9h0-a.oregon-postgres.render.com \
        -U noltrion_admin \
        -d pgnoltrion \
        -f backup_before_designation_migration.sql
```

### 2. Verify Current State
- [ ] Check number of employees in system
- [ ] Check number of unique positions
- [ ] Check number of users with roles
- [ ] Verify application is running correctly

### 3. Stop Application (Optional but Recommended)
```bash
# Stop Flask application to prevent concurrent access during migration
# Press Ctrl+C in the terminal running the Flask app
```

## Running the Migration

### Option 1: Using Batch File (Windows)
```bash
# Double-click or run from command prompt:
run_designation_migration.bat
```

### Option 2: Using Python Directly
```bash
# From project root directory:
cd D:\Projects\HRMS\hrm
python run_designation_migration.py
```

## Migration Steps (Automatic)

The script will perform these steps automatically:

### Step 1: Create hrm_designations Table
- Creates table with columns: id, name, description, is_active, created_at, updated_at
- Creates indexes on name and is_active columns

### Step 2: Migrate Position Data
- Extracts all unique position values from hrm_employees
- Inserts them into hrm_designations table
- Handles duplicates gracefully

### Step 3: Add designation_id Column
- Adds designation_id column to hrm_employees table
- Creates foreign key constraint to hrm_designations

### Step 4: Update Employee Records
- Maps existing position values to designation_id
- Updates all employee records with correct designation_id

### Step 5: Create hrm_employee_companies Table
- Creates association table for many-to-many relationship
- Creates indexes for performance

### Step 6: Migrate Company Relationships
- Copies existing company_id relationships to association table
- Maintains data integrity

### Step 7: Create hrm_user_roles Table
- Creates association table for many-to-many relationship
- Creates indexes for performance

### Step 8: Migrate Role Relationships
- Copies existing role_id relationships to association table
- Maintains data integrity

### Step 9: Verification
- Counts records in all new tables
- Verifies foreign key constraints
- Displays sample data

## Expected Output

```
============================================================
🚀 STARTING DESIGNATION & ROLE ENHANCEMENT MIGRATION
============================================================

📡 Connecting to database...
✅ Connected successfully!

============================================================
⚙️  Creating hrm_designations table
============================================================
✅ SUCCESS: Creating hrm_designations table

============================================================
📊 MIGRATING POSITION DATA
============================================================
📋 Found 15 unique positions to migrate
   ✅ Migrated: Software Engineer
   ✅ Migrated: HR Manager
   ✅ Migrated: Project Manager
   ... (more positions)

============================================================
⚙️  Adding designation_id column to hrm_employees
============================================================
✅ SUCCESS: Adding designation_id column to hrm_employees

============================================================
🔄 UPDATING EMPLOYEE DESIGNATION IDs
============================================================
✅ Updated 50 employee records with designation_id

... (more steps)

============================================================
✅ TRANSACTION COMMITTED
============================================================

============================================================
🔍 VERIFICATION
============================================================

✅ hrm_designations table has 15 records
✅ hrm_employee_companies table has 50 records
✅ hrm_user_roles table has 50 records
✅ 50 employees have designation_id assigned

============================================================
🎉 MIGRATION COMPLETED SUCCESSFULLY!
============================================================
```

## Post-Migration Steps

### 1. Verify Migration Success
```sql
-- Check designations were created
SELECT COUNT(*) FROM hrm_designations;

-- Check employees have designation_id
SELECT COUNT(*) FROM hrm_employees WHERE designation_id IS NOT NULL;

-- Check employee-company relationships
SELECT COUNT(*) FROM hrm_employee_companies;

-- Check user-role relationships
SELECT COUNT(*) FROM hrm_user_roles;
```

### 2. Restart Application
```bash
# Start Flask application
python app.py
# or
flask run
```

### 3. Test Designation Master
1. Login as Super Admin or Admin
2. Navigate to Masters → Designations
3. Verify all designations are listed
4. Try adding a new designation
5. Try editing an existing designation

### 4. Test Employee Form
1. Navigate to Employees → Add Employee
2. Verify Designation dropdown is populated
3. Verify Position field is removed (after form update)
4. Test creating a new employee

### 5. Verify Data Integrity
```sql
-- Check for employees without designation
SELECT id, first_name, last_name, position 
FROM hrm_employees 
WHERE designation_id IS NULL;

-- Check designation usage
SELECT d.name, COUNT(e.id) as employee_count
FROM hrm_designations d
LEFT JOIN hrm_employees e ON e.designation_id = d.id
GROUP BY d.id, d.name
ORDER BY employee_count DESC;
```

## Rollback Procedure (If Needed)

### If Migration Fails
The script automatically rolls back on error. No manual action needed.

### If You Need to Manually Rollback
```sql
-- Start transaction
BEGIN;

-- Drop new tables
DROP TABLE IF EXISTS hrm_user_roles CASCADE;
DROP TABLE IF EXISTS hrm_employee_companies CASCADE;
DROP TABLE IF EXISTS hrm_designations CASCADE;

-- Remove designation_id column
ALTER TABLE hrm_employees DROP COLUMN IF EXISTS designation_id;

-- Commit rollback
COMMIT;

-- Restore from backup
psql -h dpg-d2kq4515pdvs739uk9h0-a.oregon-postgres.render.com \
     -U noltrion_admin \
     -d pgnoltrion \
     -f backup_before_designation_migration.sql
```

## Troubleshooting

### Issue: "Cannot connect to database"
**Solution**: 
- Check database credentials in run_designation_migration.py
- Verify network connectivity
- Check if database server is running

### Issue: "Table already exists"
**Solution**: 
- Migration is idempotent - safe to run again
- Script will skip existing tables
- Check if previous migration partially completed

### Issue: "Foreign key constraint violation"
**Solution**: 
- Check if there are orphaned records
- Verify data integrity before migration
- Contact support for manual cleanup

### Issue: "No positions found to migrate"
**Solution**: 
- This is normal if no employees have position data
- Migration will still create tables
- You can manually add designations later

### Issue: "Some employees don't have designation_id"
**Solution**: 
```sql
-- Find employees without designation
SELECT id, first_name, last_name, position 
FROM hrm_employees 
WHERE designation_id IS NULL;

-- Manually assign designation
UPDATE hrm_employees 
SET designation_id = (SELECT id FROM hrm_designations WHERE name = 'Employee' LIMIT 1)
WHERE designation_id IS NULL;
```

## Verification Queries

### Check Migration Completeness
```sql
-- 1. Verify all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_name IN ('hrm_designations', 'hrm_employee_companies', 'hrm_user_roles');

-- 2. Check foreign keys
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY' 
AND tc.table_name IN ('hrm_employees', 'hrm_employee_companies', 'hrm_user_roles');

-- 3. Check data migration
SELECT 
    (SELECT COUNT(*) FROM hrm_designations) as designation_count,
    (SELECT COUNT(*) FROM hrm_employees WHERE designation_id IS NOT NULL) as employees_with_designation,
    (SELECT COUNT(*) FROM hrm_employee_companies) as employee_company_links,
    (SELECT COUNT(*) FROM hrm_user_roles) as user_role_links;
```

## Performance Considerations

- Migration typically takes 1-5 minutes depending on data volume
- Indexes are created automatically for optimal performance
- No downtime required if application handles missing columns gracefully

## Support

If you encounter issues:
1. Check the migration output for specific error messages
2. Review the troubleshooting section above
3. Check database logs for detailed error information
4. Verify all prerequisites are met
5. Contact system administrator with error details

## Next Steps After Migration

1. ✅ Migration completed successfully
2. ⏳ Update employee form to use designation dropdown
3. ⏳ Update navigation menu to show Designation Master
4. ⏳ Update role-based access controls
5. ⏳ Add company filters to HR Manager screens
6. ⏳ Add filters to reports

See `IMPLEMENTATION_STATUS.md` for detailed next steps.

---

**Migration Script**: `run_designation_migration.py`
**Batch File**: `run_designation_migration.bat`
**Database**: PostgreSQL (Render.com)
**Estimated Time**: 1-5 minutes
**Rollback**: Automatic on error