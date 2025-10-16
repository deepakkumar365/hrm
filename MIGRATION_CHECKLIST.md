# Migration Checklist - Quick Reference

## ✅ Pre-Migration (Complete)
- [x] Database models created
- [x] Migration script created (`run_designation_migration.py`)
- [x] Batch file created (`run_designation_migration.bat`)
- [x] Designation CRUD routes implemented
- [x] Templates created
- [x] Documentation complete
- [x] Temporary fix applied (app running)

## 📋 Migration Steps (To Do)

### Step 1: Backup Database ⏳
```bash
pg_dump -h dpg-d2kq4515pdvs739uk9h0-a.oregon-postgres.render.com \
        -U noltrion_admin \
        -d pgnoltrion \
        -f backup_$(date +%Y%m%d_%H%M%S).sql
```
- [ ] Backup created
- [ ] Backup file verified
- [ ] Backup location noted: _______________

### Step 2: Stop Application (Optional) ⏳
```bash
# Press Ctrl+C in Flask terminal
```
- [ ] Application stopped

### Step 3: Run Migration ⏳
```bash
# From: D:/Projects/HRMS/hrm
run_designation_migration.bat
```
- [ ] Migration started
- [ ] No errors in output
- [ ] All steps completed
- [ ] Verification passed

**Expected Output:**
```
✅ Creating hrm_designations table
✅ Migrated X positions
✅ Added designation_id column
✅ Updated X employee records
✅ Created hrm_employee_companies table
✅ Created hrm_user_roles table
✅ MIGRATION COMPLETED SUCCESSFULLY!
```

### Step 4: Verify Migration ⏳
```sql
-- Run these queries
SELECT COUNT(*) FROM hrm_designations;
SELECT COUNT(*) FROM hrm_employees WHERE designation_id IS NOT NULL;
SELECT COUNT(*) FROM hrm_employee_companies;
SELECT COUNT(*) FROM hrm_user_roles;
```
- [ ] hrm_designations has records: _____
- [ ] Employees have designation_id: _____
- [ ] hrm_employee_companies has records: _____
- [ ] hrm_user_roles has records: _____

### Step 5: Restore Model Changes ⏳

#### 5.1: models.py
- [ ] Line ~291: Uncomment `designation_id = db.Column(...)`
- [ ] Line ~342: Uncomment `companies = db.relationship(...)`
- [ ] Line ~343: Uncomment `designation = db.relationship(...)`
- [ ] Line ~37: Uncomment `roles = db.relationship(...)`
- [ ] Lines ~55-56: Uncomment `role_names` property (multi-role version)
- [ ] Lines ~60-61: Uncomment `has_role()` method (multi-role version)
- [ ] Lines ~762-774: Uncomment `class Designation(db.Model):`
- [ ] Lines ~777-782: Uncomment `employee_companies = db.Table(...)`
- [ ] Lines ~785-790: Uncomment `user_roles = db.Table(...)`

#### 5.2: routes.py
- [ ] Line ~15: Uncomment `Designation` in imports

#### 5.3: routes_masters.py
- [ ] Line ~12: Uncomment `Designation` in imports
- [ ] Lines ~603-723: Uncomment all designation routes

### Step 6: Restart Application ⏳
```bash
python app.py
# or
flask run
```
- [ ] Application started
- [ ] No import errors
- [ ] No database errors
- [ ] Home page loads

### Step 7: Test Designation Master ⏳
- [ ] Navigate to `/masters/designations`
- [ ] Designation list displays
- [ ] Can add new designation
- [ ] Can edit designation
- [ ] Can delete designation (if not assigned)
- [ ] Cannot delete if assigned to employees

### Step 8: Test Models ⏳
```python
from models import Designation, Employee, User
from app import db

# Test queries
designations = Designation.query.all()
emp = Employee.query.first()
user = User.query.first()

print(f"Designations: {len(designations)}")
print(f"Employee designation: {emp.designation.name if emp.designation else 'None'}")
print(f"User roles: {user.role_names}")
```
- [ ] Designation query works
- [ ] Employee.designation relationship works
- [ ] User.roles relationship works
- [ ] No errors in console

## 🎉 Migration Complete!

### Post-Migration Tasks
- [ ] Update `IMPLEMENTATION_STATUS.md` with new status
- [ ] Mark Phase 1 as complete
- [ ] Begin Phase 2: Employee Form Updates
- [ ] Update navigation menu
- [ ] Add company filters
- [ ] Add report filters

## 🆘 Rollback (If Needed)

### If Migration Fails:
- [ ] Check error message in migration output
- [ ] Migration auto-rolled back (no manual action needed)
- [ ] Review `MIGRATION_GUIDE.md` troubleshooting section
- [ ] Fix issue and re-run migration

### If Need to Manually Rollback:
```sql
BEGIN;
DROP TABLE IF EXISTS hrm_user_roles CASCADE;
DROP TABLE IF EXISTS hrm_employee_companies CASCADE;
DROP TABLE IF EXISTS hrm_designations CASCADE;
ALTER TABLE hrm_employees DROP COLUMN IF EXISTS designation_id;
COMMIT;
```
- [ ] Rollback SQL executed
- [ ] Restore from backup if needed
- [ ] Keep code commented until issue resolved

## 📊 Progress Tracking

**Overall Progress**: _____ / 16 requirements complete

**Phase 1**: Database & Designation Master
- [x] Models created
- [x] Migration script created
- [x] Routes implemented
- [x] Templates created
- [ ] Migration executed
- [ ] Code restored
- [ ] Testing complete

**Phase 2**: Employee Form (Pending)
- [ ] Remove Position field
- [ ] Add Designation dropdown
- [ ] Add Multiple Company selection
- [ ] Update User Role dropdown

**Phase 3**: Access Control (Pending)
- [ ] Update navigation menu
- [ ] Update @require_role decorator
- [ ] Test multiple roles

**Phase 4**: Filtering (Pending)
- [ ] Company filter - Employee list
- [ ] Company filter - Payroll
- [ ] Company filter - Reports
- [ ] Designation filter - Reports

## 📝 Notes

**Migration Date**: _______________
**Migration Time**: _______________
**Performed By**: _______________
**Issues Encountered**: 
_______________________________________________
_______________________________________________

**Verification Results**:
- Designations created: _____
- Employees updated: _____
- Association records: _____

**Next Steps**:
_______________________________________________
_______________________________________________

---

**Quick Links**:
- Full Guide: `MIGRATION_GUIDE.md`
- Next Steps: `POST_FIX_INSTRUCTIONS.md`
- Status Report: `IMPLEMENTATION_STATUS.md`
- Current State: `README_CURRENT_STATE.md`