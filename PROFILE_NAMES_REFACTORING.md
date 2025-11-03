# Profile Names Refactoring Guide

## Overview
This document describes the refactoring to move profile names from the `hrm_users` table to the `hrm_employee` table. This is a gradual transition to ensure data consistency and reduce redundancy.

## Problem Statement
- Both `hrm_users` and `hrm_employee` tables store `first_name` and `last_name` (redundant)
- Different parts of the application fetch names from different sources (inconsistent)
- `hrm_employee` is the source of truth for employee information
- Goal: Centralize all profile names in `hrm_employee` table

## Solution Architecture

### Current State (Transition Phase)
```
hrm_users Table:
- first_name (to be deprecated)
- last_name (to be deprecated)

hrm_employee Table:
- first_name (source of truth)
- last_name (source of truth)

Relationship:
- Employee.user_id → User.id (optional)
- User.employee_profile → Employee (one-to-one)
```

### New Properties Added to User Model

```python
@property
def get_first_name(self):
    """Get first name from employee profile if available, fallback to user column"""
    if self.employee_profile and self.employee_profile.first_name:
        return self.employee_profile.first_name
    return self.first_name

@property
def get_last_name(self):
    """Get last name from employee profile if available, fallback to user column"""
    if self.employee_profile and self.employee_profile.last_name:
        return self.employee_profile.last_name
    return self.last_name

@property
def full_name(self):
    """Get full name from employee profile if available, fallback to user columns"""
    first = self.get_first_name
    last = self.get_last_name
    return f"{first} {last}".strip()
```

## Migration Steps

### Step 1: Run Data Migration Script
This ensures all users have employee profiles:

```bash
python migrate_profile_names.py
```

**What it does:**
- Creates employee profiles for any users that don't have them
- Syncs names between user and employee tables
- Generates employee IDs
- Sets placeholder values for required fields (NRIC, position, etc.)

### Step 2: Update Code References

#### Python Routes
Change from:
```python
f"Updated by {current_user.first_name} {current_user.last_name}"
```

Change to:
```python
f"Updated by {current_user.full_name}"
```

#### Templates (Jinja2)
Option 1 - Continue using existing columns (backward compatible):
```jinja2
{{ current_user.first_name }} {{ current_user.last_name }}
```

Option 2 - Use new properties (recommended):
```jinja2
{{ current_user.get_first_name }} {{ current_user.get_last_name }}
```

Option 3 - Use full_name property (simplest):
```jinja2
{{ current_user.full_name }}
```

### Step 3: Verify Data Consistency

Run verification to ensure all users have proper profiles:

```bash
python migrate_profile_names.py
```

Then test:
- User login ✓
- Profile display ✓
- Employee list ✓
- Audit logs ✓
- Reports ✓

## File Changes Made

### Models (models.py)
- Added `get_first_name` property to User class
- Added `get_last_name` property to User class
- Added `full_name` property to User class

### Routes (routes.py)
- Updated attendance correction note (line ~1833)
- Updated attendance marking (line ~1968)

### New Migration Scripts
- `migrate_profile_names.py` - Main migration script
- `refactor_profile_names_helper.py` - Helper for analysis and tracking

## Backward Compatibility

During the transition phase:
- **Columns remain**: `first_name` and `last_name` still exist in `hrm_users`
- **Both synced**: When employee profile is updated, user table is synced
- **Properties available**: Use `get_first_name`, `get_last_name`, or `full_name`
- **Direct access still works**: `user.first_name` still returns user column value

## Templates to Update

Priority order for template updates:

### High Priority (User-facing)
1. `templates/base.html` - Navigation bar
2. `templates/dashboard.html` - Welcome message
3. `templates/super_admin_dashboard.html` - Admin welcome
4. `templates/profile.html` - User profile page
5. `templates/profile_edit.html` - Profile editing

### Medium Priority (Data display)
6. `templates/employees/view.html` - Employee details
7. `templates/employees/form.html` - Employee form
8. `templates/users/list.html` - User list
9. `templates/leave/list.html` - Leave requests
10. `templates/claims/list.html` - Claims

### Lower Priority (Reports)
11. `templates/payroll/*.html` - Payroll forms and reports
12. `templates/reports/*.html` - Various reports
13. `templates/attendance/bulk_manage.html` - Attendance bulk management
14. `templates/team/team_list.html` - Team member list

## Phase 2: Drop Redundant Columns (Future)

After all code has been updated and tested:

1. Create a migration to drop columns:
```python
# migrations/versions/xxx_drop_user_names.py
op.drop_column('hrm_users', 'first_name')
op.drop_column('hrm_users', 'last_name')
```

2. Update User model to remove columns and properties

## Testing Checklist

- [ ] Run migration script without errors
- [ ] All users have employee profiles
- [ ] User login works
- [ ] Profile display shows correct names
- [ ] Employee list shows correct names
- [ ] Audit logs record correct names
- [ ] Reports display correct names
- [ ] Name updates in employee profile reflect everywhere
- [ ] New employee creation still works
- [ ] New user registration still works (if applicable)
- [ ] Admin functions work correctly

## Rollback Plan

If issues occur:

1. The `first_name` and `last_name` columns in `hrm_users` still contain data
2. Can revert to using direct column access
3. Migration is reversible by dropping the new relationships if needed

## Notes for Developers

### When Accessing User Names:

❌ **Avoid:**
```python
user.first_name  # Direct column access (will be removed)
```

✅ **Prefer:**
```python
user.get_first_name  # Gets from employee profile with fallback
user.full_name      # Combined name from employee profile
```

### When Displaying Names in Templates:

❌ **Old (still works during transition):**
```jinja2
{{ current_user.first_name }} {{ current_user.last_name }}
```

✅ **New (recommended):**
```jinja2
{{ current_user.full_name }}
```

### In Employee Objects:

Employee names should always come from the employee directly:
```python
employee.first_name  # Always use directly - these are the source of truth
employee.last_name
```

## Performance Considerations

- The `employee_profile` relationship is `uselist=False` (optimized)
- Properties use lazy evaluation (only load when accessed)
- No additional queries for properties (data loaded with user)

## Future Improvements

1. Add name change audit trail
2. Add employee name history tracking
3. Consider full-text search on employee names
4. Add name formatting options (display order)

---

**Last Updated:** 2024
**Status:** In Progress - Phase 1 Complete