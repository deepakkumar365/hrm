# Leave Allocation Configuration - Implementation Guide

## Overview

This implementation adds a comprehensive leave allocation system to the HRMS, allowing you to configure total available leave days based on **Designation** and/or **Employee Groups**, with support for individual employee overrides.

## What Was Implemented

### 1. **New Database Models**

#### a) **EmployeeGroup** (`hrm_employee_group`)
- Master data for grouping employees (Department, Grade, Shift, Location, Team, etc.)
- Company-specific (each company has independent groups)
- Attributes:
  - Name (unique per company)
  - Category (Department, Grade, Shift, Location, Team, Other)
  - Description
  - Active/Inactive status

#### b) **DesignationLeaveAllocation** (`hrm_designation_leave_allocation`)
- Configures leave days for each Designation-LeaveType combination
- Unique per company
- Attributes:
  - Designation ID
  - Leave Type ID
  - Total days available per year

#### c) **EmployeeGroupLeaveAllocation** (`hrm_employee_group_leave_allocation`)
- Configures leave days for each EmployeeGroup-LeaveType combination
- Unique per company
- Attributes:
  - Employee Group ID
  - Leave Type ID
  - Total days available per year

#### d) **EmployeeLeaveAllocation** (`hrm_employee_leave_allocation`)
- Individual employee override allocations
- Allows exceptions to designation or group allocations
- Unique per employee per leave type
- Attributes:
  - Employee ID
  - Leave Type ID
  - Total days
  - Override reason

#### e) **Employee Model Enhancement**
- Added `employee_group_id` foreign key
- Employees can now belong to one employee group

### 2. **New Routes & Routes Files**

#### **routes_employee_group.py** - Employee Group Master Management
- `GET /masters/employee-groups` - List all employee groups
- `GET /masters/employee-groups/add` - Add new group (form)
- `POST /masters/employee-groups/add` - Create new group
- `GET /masters/employee-groups/<id>/edit` - Edit group (form)
- `POST /masters/employee-groups/<id>/edit` - Update group
- `POST /masters/employee-groups/<id>/delete` - Delete group (soft delete if employees exist)
- `GET /api/employee-groups/<company_id>` - API to get groups for a company

#### **routes_leave_allocation.py** - Leave Allocation Configuration
**Designation-based allocations:**
- `GET /leave-management/allocation/designation` - List designation allocations
- `GET /leave-management/allocation/designation/form` - Add/edit form
- `POST /leave-management/allocation/designation/form` - Save allocation
- `POST /leave-management/allocation/designation/<id>/delete` - Delete allocation

**Employee Group-based allocations:**
- `GET /leave-management/allocation/employee-group` - List employee group allocations
- `GET /leave-management/allocation/employee-group/form` - Add/edit form
- `POST /leave-management/allocation/employee-group/form` - Save allocation
- `POST /leave-management/allocation/employee-group/<id>/delete` - Delete allocation

**Individual employee allocations:**
- `GET /leave-management/allocation/employee` - List employee overrides
- `POST /leave-management/allocation/employee/<id>/delete` - Delete override

### 3. **New Templates**

**Employee Group Management:**
- `templates/employee_groups/list.html` - List employee groups with search, filter, and pagination
- `templates/employee_groups/form.html` - Add/edit employee group form

**Leave Allocation Configuration:**
- `templates/leave/allocation_designation_list.html` - List designation-based allocations
- `templates/leave/allocation_designation_form.html` - Add/edit designation allocation
- `templates/leave/allocation_employee_group_list.html` - List employee group allocations
- `templates/leave/allocation_employee_group_form.html` - Add/edit employee group allocation
- `templates/leave/allocation_employee_list.html` - List individual employee overrides

### 4. **Database Migration**

File: `migrations/versions/leave_allocation_and_employee_groups.py`

Includes:
- Creates all new tables with proper indexes and constraints
- Adds `employee_group_id` column to `hrm_employee` table
- Supports rollback

## How to Use

### Step 1: Run Database Migration

```bash
# Using Flask-Migrate
python -m flask db upgrade

# Or using the migration file directly
python migrations/versions/leave_allocation_and_employee_groups.py
```

### Step 2: Create Employee Groups (Optional but Recommended)

1. Navigate to: **Masters → Employee Groups**
2. Click **"Add Employee Group"**
3. Fill in:
   - Group Name (e.g., "Senior Management", "Support Team")
   - Category (Department, Grade, Shift, etc.)
   - Description (optional)
4. Click **"Create Employee Group"**

### Step 3: Assign Employee Groups to Employees

1. Go to **Employees** list
2. Edit an employee
3. Select their **Employee Group** (if applicable)
4. Save

### Step 4: Configure Designation-Based Leave Allocation

1. Navigate to: **Leave Management → Allocation → Designation**
2. Select Company and Designation
3. Click **"Add Allocation"**
4. Fill in:
   - Designation (e.g., "Senior Manager")
   - Leave Type (e.g., "Annual Leave")
   - Total Days (e.g., 20 days)
5. Click **"Create Allocation"**

**All employees with this designation automatically get this leave allocation**

### Step 5: Configure Employee Group-Based Leave Allocation

1. Navigate to: **Leave Management → Allocation → Employee Group**
2. Select Company and Employee Group
3. Click **"Add Allocation"**
4. Fill in:
   - Employee Group (e.g., "Support Team")
   - Leave Type (e.g., "Sick Leave")
   - Total Days (e.g., 10 days)
5. Click **"Create Allocation"**

**All employees in this group automatically get this leave allocation**

### Step 6: Create Individual Employee Overrides (If Needed)

1. Navigate to: **Leave Management → Allocation → Employee**
2. Search for employee
3. Create override with:
   - Employee ID
   - Leave Type
   - Custom days
   - Reason for override

## Priority Resolution

When an employee has both designation and employee group allocations:

### Current Implementation (Priority-based):
- **Individual Allocation** (Highest Priority) - If exists, use this
- **Employee Group Allocation** - If no individual allocation, use this
- **Designation Allocation** (Lowest Priority) - Use if no other allocation exists

### To Use Designation Only (Ignore Groups):
Simply don't create employee group allocations for that leave type

### To Use Employee Group Only (Ignore Designation):
Simply don't create designation allocations for that leave type

## Access Control

**Who can manage:**
- ✅ Super Admin
- ✅ Tenant Admin
- ✅ HR Manager

**Who cannot manage:**
- ❌ Regular Employees
- ❌ Managers (unless also HR Manager)

## Key Features

### ✅ Company-Specific Configuration
Each company has independent:
- Employee Groups
- Designation allocations
- Employee group allocations
- Employee overrides

### ✅ Easy Management
- List views with search and filter
- Company selector to switch context
- Batch view options for efficiency

### ✅ Soft Delete for Data Integrity
- Employee Groups: Soft deleted if employees exist (can be manually reassigned)
- Leave Allocations: Soft deleted if used in actual leave requests

### ✅ Audit Trail
- Created by, Created at
- Modified by, Modified at
- For all tables

### ✅ Flexible Configuration
- Configure for any leave type
- Any number of employee groups
- Override individual cases easily

## Database Schema

### New Tables

```
hrm_employee_group
├── id (PK)
├── company_id (FK) → hrm_company
├── name
├── category (Department, Grade, Shift, Location, Team, Other)
├── description
├── is_active
├── created_by, created_at
├── modified_by, modified_at
└── Constraints: UNIQUE(company_id, name)

hrm_designation_leave_allocation
├── id (PK)
├── company_id (FK) → hrm_company
├── designation_id (FK) → hrm_designation
├── leave_type_id (FK) → hrm_leave_type
├── total_days
├── created_by, created_at
├── modified_by, modified_at
└── Constraints: UNIQUE(company_id, designation_id, leave_type_id)

hrm_employee_group_leave_allocation
├── id (PK)
├── company_id (FK) → hrm_company
├── employee_group_id (FK) → hrm_employee_group
├── leave_type_id (FK) → hrm_leave_type
├── total_days
├── created_by, created_at
├── modified_by, modified_at
└── Constraints: UNIQUE(company_id, employee_group_id, leave_type_id)

hrm_employee_leave_allocation
├── id (PK)
├── employee_id (FK) → hrm_employee
├── leave_type_id (FK) → hrm_leave_type
├── total_days
├── override_reason
├── created_by, created_at
├── modified_by, modified_at
└── Constraints: UNIQUE(employee_id, leave_type_id)

hrm_employee (Enhanced)
├── ... existing columns ...
├── employee_group_id (FK) → hrm_employee_group  [NEW]
└── Constraints: nullable, SET NULL on delete
```

## Implementation Details

### File Changes

**Modified Files:**
- `models.py` - Added 5 new model classes + employee_group_id to Employee
- `main.py` - Added 2 new route imports

**New Files Created:**
- `routes_employee_group.py` - Employee group CRUD routes
- `routes_leave_allocation.py` - Leave allocation configuration routes
- `templates/employee_groups/list.html` - Employee groups list page
- `templates/employee_groups/form.html` - Employee group add/edit form
- `templates/leave/allocation_designation_list.html` - Designation allocations list
- `templates/leave/allocation_designation_form.html` - Designation allocation form
- `templates/leave/allocation_employee_group_list.html` - Employee group allocations list
- `templates/leave/allocation_employee_group_form.html` - Employee group allocation form
- `templates/leave/allocation_employee_list.html` - Employee overrides list
- `migrations/versions/leave_allocation_and_employee_groups.py` - Database migration

## Future Enhancements

Possible improvements for future versions:

1. **Bulk Import** - Import employee groups from CSV
2. **Leave Year Configuration** - Set different allocations for different years
3. **Carryover Rules** - Configure carry-forward rules per allocation
4. **Department Mapping** - Auto-assign groups based on department
5. **Reports** - Leave allocation vs. usage reports
6. **Alerts** - Notifications when leave is below threshold
7. **API Endpoints** - REST API for third-party integrations

## Testing Checklist

- [ ] Run migration successfully
- [ ] Create employee groups
- [ ] Assign employees to groups
- [ ] Create designation allocations
- [ ] Create employee group allocations
- [ ] Create individual employee overrides
- [ ] Verify priority resolution
- [ ] Test soft delete functionality
- [ ] Test company filtering
- [ ] Test search and pagination
- [ ] Verify access control (non-admins cannot access)

## Troubleshooting

### Migration fails
```bash
# Check current head
alembic current

# Show all revisions
alembic history --verbose

# Reset migration (careful - deletes data!)
python -m flask db stamp head
python -m flask db upgrade
```

### Cannot add employee groups
- Ensure migration ran successfully
- Check if you're a Super Admin, Tenant Admin, or HR Manager
- Verify company exists and is active

### Leave allocation not reflecting
- Check employee has correct group assigned
- Verify allocation exists for the leave type
- Check if individual override exists (has priority)

## Support

For issues or questions:
1. Check this documentation
2. Review error messages in application logs
3. Verify database integrity with `python verify_db.py`
4. Check migrations with `python -m flask db current`

---

**Version:** 1.0  
**Created:** 2024  
**Last Updated:** 2024