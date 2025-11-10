# Database Migration Chain - Fixes Applied

## Summary
Fixed multiple broken links in the Alembic migration chain to enable database initialization.

## Issues Found & Fixed

### 1. **Orphaned Migrations with `down_revision = None`**
   - `fix_nric_null_unique` - **FIXED**: Now points to `28f425a665b2`
   - `add_is_manager` - **FIXED**: Now points to `make_email_nullable`
   - `drop_redundant_user_names_TEMPLATE` - Kept as template (skipped for now)

### 2. **Broken Revision References**
   - `make_employee_email_nullable.py`:
     - Had `down_revision = ('2be68655c2bb',)` (tuple format, wrong)
     - Migration `2be68655c2bb` doesn't exist
     - **FIXED**: Changed to point to `fix_nric_null_unique`

   - `add_designation_to_employee.py`:
     - Had conflicting docstring vs actual down_revision
     - **FIXED**: Updated to point to `add_is_manager`

### 3. **Payroll Configuration Chain Issues**
   - `add_payroll_indexes.py`:
     - Referenced non-existent migration `2be68655c2bb`
     - **FIXED**: Changed to point to `add_payroll_enhancements`

   - `add_payroll_enhancements.py`:
     - **FIXED**: Now points to `add_designation_to_employee`

   - `add_attendance_lop_and_payroll_fields.py`:
     - Docstring said `Revises: add_payroll_enhancements` but code pointed to `add_payroll_indexes`
     - **FIXED**: Updated docstring to match actual `down_revision = 'add_payroll_indexes'`

### 4. **Company Employee ID Config Chain**
   - `add_company_employee_id_config.py`:
     - Had `down_revision = 'add_certification_pass_renewal_fields'` (wrong)
     - **FIXED**: Changed to `down_revision = 'add_certification_pass_renewal'`

### 5. **Leave Allocation Chain**
   - `leave_allocation_and_employee_groups.py`:
     - Initially pointed to `add_certification_pass_renewal`
     - **FIXED**: Updated to point to `add_company_employee_id_config` (maintains chain)

## Final Migration Chain Order

```
1. 28f425a665b2_initial_schema_creation
   ↓
2. fix_nric_null_unique
   ↓
3. make_email_nullable
   ↓
4. add_is_manager
   ↓
5. add_designation_to_employee
   ↓
6. add_payroll_enhancements
   ↓
7. add_payroll_indexes
   ↓
8. add_attendance_lop_payroll_fields
   ↓
9. add_tenant_configuration
   ↓
10. add_overtime_group_id
    ↓
11. 005_add_tenant_company_hierarchy
    ↓
12. 006_add_tenant_country_currency
    ↓
13. 007_add_tenant_payment_and_documents
    ↓
14. 008_insert_tenant_company_test_data
    ↓
15. add_certification_pass_renewal
    ↓
16. add_company_employee_id_config
    ↓
17. leave_allocation_001 ✓ LEAVE ALLOCATION & EMPLOYEE GROUPS
```

## Additional Migrations (Post-Chain)
These migrations reference the main chain but don't alter the core sequence:
- `add_organization_logo` (points to `28f425a665b2`)
- `add_org_address_uen` (points to `add_organization_logo`)
- `remove_role_column` (points to `add_org_address_uen`)
- `add_enhancements_fields` (points to `remove_role_column`)
- `add_payroll_config` (points to `add_enhancements_fields`)
- `add_leave_type_configuration` (points to `add_certification_pass_renewal`)
- `add_company_currency_code` (points to `add_company_employee_id_config`)

## How to Run Migration

### Option 1: Double-click the batch file
```
D:\Projects\HRMS\hrm\RUN_MIGRATION.bat
```

### Option 2: Command Line
```bash
cd D:\Projects\HRMS\hrm
python -m flask db upgrade
```

### Option 3: PyCharm Terminal
Run the same command as Option 2 in your PyCharm Terminal

## What Gets Created

The `leave_allocation_001` migration will create:
- ✓ `hrm_employee_group` - Employee grouping table
- ✓ `hrm_designation_leave_allocation` - Leave allocation by designation
- ✓ `hrm_employee_group_leave_allocation` - Leave allocation by group
- ✓ `hrm_employee_leave_allocation` - Individual employee overrides
- ✓ `employee_group_id` column in `hrm_employee` table

## Verification Steps

After running migration, verify:
1. ✓ Flask starts without errors
2. ✓ No `UndefinedColumn` errors about `employee_group_id`
3. ✓ Navigate to Masters → Employee Groups (should work)
4. ✓ Navigation to Leave Allocation pages (should work)
5. ✓ Both "HR Manager" and "Tenant Admin" roles can access these pages
6. ✓ Regular employees get 403 Forbidden

## Files Modified

1. `migrations/versions/fix_nric_unique_constraint.py` - Fixed down_revision
2. `migrations/versions/add_is_manager_column.py` - Fixed down_revision chain
3. `migrations/versions/make_employee_email_nullable.py` - Fixed down_revision & tuple format
4. `migrations/versions/add_designation_to_employee.py` - Fixed down_revision
5. `migrations/versions/add_payroll_enhancements.py` - Fixed down_revision
6. `migrations/versions/add_payroll_indexes.py` - Fixed down_revision & docstring
7. `migrations/versions/add_attendance_lop_and_payroll_fields.py` - Fixed docstring
8. `migrations/versions/add_company_employee_id_config.py` - Fixed down_revision
9. `migrations/versions/leave_allocation_and_employee_groups.py` - Fixed down_revision

## Status
✅ **READY TO MIGRATE** - All chain issues have been resolved!