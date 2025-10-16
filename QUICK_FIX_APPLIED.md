# Quick Fix Applied - Temporary Model Revert

## Issue
The application was failing with error:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column hrm_employee.designation_id does not exist
```

## Root Cause
The database models were updated to include new fields and relationships (designation_id, multiple companies, multiple roles), but the database migration hasn't been run yet. SQLAlchemy was trying to query columns that don't exist in the actual database.

## Solution Applied
Temporarily commented out the new model additions until the migration can be run. This allows the application to continue running with the existing database schema.

## Files Modified

### 1. `models.py`
**Changes:**
- ✅ Commented out `designation_id` column in Employee model
- ✅ Commented out `designation` relationship in Employee model
- ✅ Commented out `companies` relationship in Employee model (multiple companies)
- ✅ Commented out `roles` relationship in User model (multiple roles)
- ✅ Commented out `Designation` model class
- ✅ Commented out `employee_companies` association table
- ✅ Commented out `user_roles` association table
- ✅ Modified `role_names` property to use single role temporarily
- ✅ Modified `has_role()` method to use single role temporarily

**All commented sections are marked with:** `# UNCOMMENT AFTER MIGRATION`

### 2. `routes_masters.py`
**Changes:**
- ✅ Commented out `Designation` import
- ✅ Commented out all designation routes (list, add, edit, delete)

**All commented sections are marked with:** `# UNCOMMENT AFTER MIGRATION`

## Current State
✅ **Application should now run without errors**
- Uses existing database schema
- Single role per user (backward compatible)
- Single company per employee (backward compatible)
- Position field still in use (not designation)

## Next Steps - IMPORTANT!

### Step 1: Run the Migration
Once you're ready to proceed with the enhancements:

```bash
# From project root:
run_designation_migration.bat
```

### Step 2: Uncomment the Model Changes
After successful migration, uncomment all sections marked with `# UNCOMMENT AFTER MIGRATION` in:
1. `models.py` - All new fields, relationships, and models
2. `routes_masters.py` - Designation routes and import

### Step 3: Restart Application
```bash
# Stop the Flask app (Ctrl+C)
# Start it again
python app.py
```

### Step 4: Test Designation Master
1. Login as Admin
2. Navigate to Masters → Designations
3. Test CRUD operations

## Search and Replace Guide

When you're ready to uncomment after migration, you can use these patterns:

### In `models.py`:
1. Find: `# designation_id = db.Column`
   Replace with: `designation_id = db.Column`

2. Find: `# companies = db.relationship('Company', secondary='hrm_employee_companies'`
   Replace with: `companies = db.relationship('Company', secondary='hrm_employee_companies'`

3. Find: `# designation = db.relationship('Designation'`
   Replace with: `designation = db.relationship('Designation'`

4. Find: `# roles = db.relationship('Role', secondary='hrm_user_roles'`
   Replace with: `roles = db.relationship('Role', secondary='hrm_user_roles'`

5. Uncomment the entire `Designation` class (lines ~762-774)
6. Uncomment the `employee_companies` table (lines ~777-782)
7. Uncomment the `user_roles` table (lines ~785-790)

8. In `role_names` property:
   - Comment out: `return [self.role.name] if self.role else []  # Temporary: single role only`
   - Uncomment: `return [r.name for r in self.roles] if self.roles else []`

9. In `has_role()` method:
   - Comment out: `return self.role and self.role.name == role_name  # Temporary: single role only`
   - Uncomment: `return role_name in self.role_names or (self.role and self.role.name == role_name)`

### In `routes_masters.py`:
1. Find: `from models import Role, Department, WorkingHours, WorkSchedule, Employee  # , Designation`
   Replace with: `from models import Role, Department, WorkingHours, WorkSchedule, Employee, Designation`

2. Uncomment all designation routes (lines ~603-723)

## Verification

After uncommenting and restarting:

```python
# Test in Python shell
from models import Designation, Employee, User
from app import db

# Check Designation model works
designations = Designation.query.all()
print(f"Found {len(designations)} designations")

# Check Employee.designation relationship
emp = Employee.query.first()
print(f"Employee designation: {emp.designation.name if emp.designation else 'None'}")

# Check User.roles relationship
user = User.query.first()
print(f"User roles: {user.role_names}")
```

## Rollback (If Needed)

If you need to rollback the migration:
1. See `MIGRATION_GUIDE.md` for rollback procedures
2. The commented code is already in place, so no code changes needed

## Support

If you encounter issues:
1. Check that all sections marked `# UNCOMMENT AFTER MIGRATION` are properly handled
2. Verify the migration completed successfully
3. Check database logs for any constraint violations
4. Ensure all foreign key relationships are valid

---

**Status**: ✅ Quick fix applied - Application should run normally
**Next Action**: Run migration when ready, then uncomment model changes
**Documentation**: See `MIGRATION_GUIDE.md` for detailed migration steps