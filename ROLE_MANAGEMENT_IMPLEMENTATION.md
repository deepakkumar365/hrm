# Role Management & Access Control Implementation Guide

## Overview
This document outlines the implementation of proper role management and access control for the HRMS system based on requirements: **GEN-EMP-001 through GEN-EMP-006**, **SUP-ADM-001 through SUP-ADM-003**, **HRM-001 through HRM-003**, **ROLE-001**, and **RPT-001 through RPT-002**.

---

## Phase 1: Changes Implemented ✓

### 1. Database Schema Updates

#### New Models Added to `models.py`:

**A. Designation Master (GEN-EMP-004)**
```python
class Designation(db.Model):
    """Master data for job designations/positions"""
    - name: Unique designation name (e.g., "Software Engineer")
    - description: Detailed description
    - is_active: Activation flag
    - created_by, modified_by: Audit fields
```

**B. UserRoleMapping (ROLE-001)**
```python
class UserRoleMapping(db.Model):
    """Maps users to multiple roles and companies"""
    - user_id: Foreign key to User
    - role_id: Foreign key to Role
    - company_id: Foreign key to Company (nullable for tenant-level roles)
    - is_active: Status flag
    - Support for multiple role + company combinations per user
```

**C. RoleAccessControl**
```python
class RoleAccessControl(db.Model):
    """Dynamic access control matrix"""
    - module_name: Module name (e.g., "Payroll", "Attendance")
    - menu_name: Menu name (e.g., "Payroll List")
    - sub_menu_name: Sub-menu name (optional)
    - Access levels per role: 'Editable', 'View Only', 'Hidden'
      * super_admin_access
      * tenant_admin_access
      * hr_manager_access
      * employee_access
```

#### Employee Model Updates:
- Added `designation_id` field (foreign key to Designation)
- Added relationship to Designation model
- Maintains backward compatibility with existing `position` field

### 2. Employee Form Updates

**Changes in `templates/employees/form.html`:**

**Removed:**
- "Position" dropdown using all roles ❌

**Added:**
- "Designation" dropdown (GEN-EMP-004)
  - Dynamically loaded from Designation Master
  - Single selection (can be extended for multi-select)
  - Synchronized with employee.designation_id

**Updated User Role Dropdown:**
- Filtered to exclude "Superadmin" role (GEN-EMP-002)
- Includes "Tenantadmin" role (GEN-EMP-001) when created
- Shows only appropriate system roles

### 3. Routes Updates (`routes.py`)

**Changes in `employee_add` route:**
```python
# Import new models
from models import Designation, UserRoleMapping, RoleAccessControl

# Filter user_roles - exclude Superadmin
user_roles = Role.query.filter(
    Role.is_active==True,
    Role.name.notlike('%superadmin%')
).order_by(Role.name).all()

# Load designations from master
designations = Designation.query.filter_by(is_active=True).all()

# Save designation_id when creating employee
designation_id = request.form.get('designation_id')
if designation_id:
    employee.designation_id = int(designation_id)
    designation = Designation.query.get(int(designation_id))
    if designation:
        employee.position = designation.name  # Backward compatibility
```

**Same updates applied to:**
- `employee_edit` route (3 locations)
- All error handler return statements
- Both GET and POST method handlers

### 4. User Role Filtering

All places where `user_roles` are loaded now use:
```python
user_roles = Role.query.filter(
    Role.is_active==True,
    Role.name.notlike('%superadmin%')
).order_by(Role.name).all()
```

This ensures:
- ✓ Superadmin role excluded from employee dropdown
- ✓ Tenantadmin role included (once created)
- ✓ Consistent filtering across all forms

---

## Phase 2: Required Setup Steps

### Step 1: Run Migration Script
```bash
cd E:/Gobi/Pro/HRMS/hrm
python migrate_to_role_management.py
```

**This will:**
- ✓ Create Designation table
- ✓ Create UserRoleMapping table
- ✓ Create RoleAccessControl table
- ✓ Add 'Tenantadmin' role to database
- ✓ Populate 25 default designations
- ✓ Display migration summary

### Step 2: Verify Database Changes
```bash
# Connect to database and verify tables exist:
# - hrm_designation
# - hrm_user_role_mapping
# - hrm_role_access_control
# - Updated hrm_employee (new designation_id column)
```

### Step 3: Test Employee Form
1. Navigate to Add Employee page
2. Verify:
   - ✓ "Position" field is gone
   - ✓ "Designation" dropdown appears (with 25+ options)
   - ✓ "User Role" dropdown excludes "Superadmin"
   - ✓ Form saves successfully

### Step 4: Test Employee Edit
1. Navigate to Edit existing employee
2. Verify:
   - ✓ Designation field shows selected value
   - ✓ All role filtering works correctly

---

## Phase 3: Additional Implementation (Next Steps)

### A. Multi-Company Selection (GEN-EMP-006)
**To enable multiple company mapping:**

1. **Update Employee Form Template:**
   ```html
   <!-- Change from single select to multi-select -->
   <select class="form-select" id="company_ids" name="company_ids" multiple required>
       {% for company in companies %}
       <option value="{{ company.id }}" ...>
   </select>
   ```

2. **Create Company Mapping Table:**
   ```python
   class EmployeeCompanyMapping(db.Model):
       employee_id: FK to Employee
       company_id: FK to Company
       is_primary: Boolean (for default)
   ```

3. **Update Routes:**
   - Parse multiple company selections
   - Create EmployeeCompanyMapping records
   - Support filtering by company

### B. Designation Master Management Screen (SUP-ADM-001)
**Create `/admin/designation-master`:**

1. **Routes needed:**
   ```python
   @app.route('/admin/designation-master')
   def designation_master_list()  # List view with filter

   @app.route('/admin/designation-master/add', methods=['GET', 'POST'])
   def designation_add()  # Add new

   @app.route('/admin/designation-master/<int:id>/edit', methods=['GET', 'POST'])
   def designation_edit(id)  # Edit existing

   @app.route('/admin/designation-master/<int:id>/delete', methods=['POST'])
   def designation_delete(id)  # Soft delete
   ```

2. **Role Checks:**
   - ✓ Super Admin: Full access (CRUD)
   - ✓ Tenant Admin: Full access (SUP-ADM-002)
   - ✓ HR Manager: Full access (SUP-ADM-002)
   - ✗ User: Hidden (SUP-ADM-003)

### C. Access Control Management UI
**Create `/admin/access-control-configuration`:**

1. **Display Role Access Matrix:**
   - Rows: All modules, menus, sub-menus
   - Columns: Super Admin, Tenant Admin, HR Manager, Employee
   - Values: 'Editable', 'View Only', 'Hidden'

2. **Features:**
   - Save Changes (update RoleAccessControl)
   - Reset to Default (restore defaults)
   - Export as Excel
   - Import from Excel

3. **Backend:**
   ```python
   @app.route('/admin/access-control', methods=['GET', 'POST'])
   @require_role(['Super Admin'])
   def access_control_matrix():
       # Load/Save RoleAccessControl
   ```

### D. Company Filtering for HR Manager (HRM-001, HRM-002, HRM-003)
**Update employee list and payroll screens:**

1. **Add Company Filter:**
   ```python
   if current_user.role.name == 'HR Manager':
       # Get all companies under tenant
       companies = Company.query.filter_by(
           tenant_id=current_user.organization.tenant_id
       ).all()
       # Filter employees by selected company
   ```

2. **Payroll List Access (HRM-003):**
   - Create `/payroll/list` route with role check
   - Filter by HR Manager's companies

### E. Report Filters (RPT-001, RPT-002)
**Update report screens with filter section:**

Filters to add:
- Company
- Department
- Role
- Designation

Affected reports:
- Employee History
- Payroll Configuration
- Attendance Report

---

## Phase 4: Testing Checklist

### Employee Form Tests
- [ ] Add Employee: Designation field shows and saves
- [ ] Add Employee: User Role excludes Superadmin
- [ ] Add Employee: Position field is removed
- [ ] Edit Employee: Designation value persists
- [ ] Edit Employee: All form fields work
- [ ] Error handling: Form re-renders with correct dropdowns

### Role Tests
- [ ] Tenantadmin role exists and is active
- [ ] Superadmin NOT in employee User Role dropdown
- [ ] Other roles appear correctly

### Database Tests
- [ ] New columns in hrm_employee table
- [ ] New tables created successfully
- [ ] Data integrity maintained

---

## File Summary

### Modified Files:
1. **models.py**
   - Added Designation class (lines 752-774)
   - Added UserRoleMapping class (lines 780-801)
   - Added RoleAccessControl class (lines 807-844)
   - Updated Employee model (added designation_id field & relationship)

2. **routes.py**
   - Added imports (line 15)
   - Updated employee_add route (user_roles filtering, designation handling)
   - Updated employee_edit route (user_roles filtering, designation handling)
   - All error handlers updated with new filtering

3. **templates/employees/form.html**
   - Replaced Position dropdown with Designation dropdown (lines 157-169)
   - User Role dropdown now receives filtered user_roles

### New Files:
1. **migrate_to_role_management.py**
   - Migration script to set up new tables and data

---

## SQL Reference (if manual setup needed)

```sql
-- Tenantadmin Role
INSERT INTO role (name, description, is_active, created_at, updated_at)
VALUES ('Tenantadmin', 'Tenant Administrator', true, NOW(), NOW());

-- Sample Designations
INSERT INTO hrm_designation (name, description, is_active, created_by, created_at, updated_at)
VALUES 
  ('Software Engineer', 'Software development role', true, 'system', NOW(), NOW()),
  ('Senior Software Engineer', 'Senior development role', true, 'system', NOW(), NOW()),
  ('HR Manager', 'HR management role', true, 'system', NOW(), NOW()),
  ...;
```

---

## Requirements Mapping

### Completed (Phase 1)
- ✓ GEN-EMP-001: Tenantadmin role in dropdown (ready, needs role to be created)
- ✓ GEN-EMP-002: Remove Superadmin from dropdown (filtering implemented)
- ✓ GEN-EMP-003: Remove Position field (done)
- ✓ GEN-EMP-004: Add Designation field (done, with master data)
- ⏳ GEN-EMP-005: Edit access control (role checks in routes)
- ⏳ GEN-EMP-006: Multi-company support (ready, needs implementation)

### In Progress (Phase 2-4)
- SUP-ADM-001: Designation Master menu (needs routes & template)
- SUP-ADM-002: Edit access (can use role checks)
- SUP-ADM-003: Hide for User role (can use role checks)
- HRM-001: Company filter (needs routes update)
- HRM-002: Tenant-wide access (needs logic)
- HRM-003: Payroll List access (needs route)
- ROLE-001: Multiple roles support (UserRoleMapping ready)
- RPT-001: Report filters (needs template updates)
- RPT-002: Filter options (needs query updates)

---

## Troubleshooting

### Issue: "Designation not found" error
**Solution:** Run migration script
```bash
python migrate_to_role_management.py
```

### Issue: Form shows old Position dropdown
**Solution:** Clear browser cache (Ctrl+F5) and verify template was updated

### Issue: Superadmin still appears in dropdown
**Solution:** Verify routes.py has the notlike filter applied correctly

---

## Success Indicators

✓ Migration script runs successfully
✓ Employee form displays Designation instead of Position
✓ User Role dropdown excludes Superadmin
✓ New employee can be created with designation
✓ Existing employees can be edited with designation
✓ Database integrity maintained
✓ No breaking changes to existing functionality

---

## Next Review Point
After Phase 1 completion, proceed with:
1. Role-wise access control implementation
2. Multi-company employee support
3. Access Control Management UI
4. Report filtering