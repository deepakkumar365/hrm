# User Status Toggle Feature - Guide

## Overview
You now have the ability to **view and toggle user active/inactive status** in the HRM system. This allows you to:
- ✅ See if a user (like AKSL093) is active or inactive
- ✅ Activate inactive users
- ✅ Deactivate active users (except your own account)

## Why This Matters for Your Payslip Issue

**The Problem**: Employee AKSL093 may not be able to see their salary slip documents because their **user account might be deactivated**.

When a user's `is_active` field is `False`, they cannot:
1. ✗ Log in to the system
2. ✗ See their documents (including salary slips)
3. ✗ Access payroll information
4. ✗ View attendance records

**The Solution**: Toggle the user to `is_active = True` and they should be able to see their salary slip documents.

---

## How to Access the Feature

### Option 1: User Management Interface (Simpler)
1. Navigate to: **Super Admin > Access Control > User Management** (or similar admin section)
2. Look for the "Status" column showing **Active** or **Inactive** badges
3. Click the **Toggle** button (⚡ icon) next to the user
4. Confirm the action

### Option 2: Advanced Access Control Interface (More detailed)
1. Navigate to: **Super Admin > Access Control > User Role & Company Access Mapping**
2. Look at the table showing all users with their current status
3. Each user row has:
   - **Status Badge**: Shows if they're Active (green ✓) or Inactive (red ✗)
   - **Toggle Button**: Click to activate/deactivate the user

---

## Testing for AKSL093

### Step 1: Check Current Status
1. Go to User Management
2. Search for or scroll to find **AKSL093** user
3. Check the **Status** column

### Step 2: Enable if Inactive
If the status shows **Inactive** (red badge):
1. Click the **Toggle** button
2. Confirm: "Are you sure you want to toggle the status of [User Name]?"
3. Wait for success message
4. Status badge should change to **Active** (green)

### Step 3: Verify Payslip Access
1. Log in as **AKSL093** (if possible) or have them log in
2. Navigate to: **My Documents** or **My Payslips**
3. The salary slip should now appear in their documents list

---

## Technical Details

### What Changed

#### Backend (routes_access_control.py)
- ✅ Added new route: `POST /access-control/api/toggle-user-status/<user_id>`
- ✅ Updated `manage_user_roles()` to fetch ALL users (including inactive ones)
- ✅ Added validation to prevent deactivating your own account
- ✅ Added audit logging for the action

#### Frontend (Templates)
- ✅ Updated `templates/users/list.html` with status column and toggle button
- ✅ Updated `templates/access_control/user_role_mapping.html` with enhanced status display
- ✅ Added interactive toggle functionality with live UI updates

### User Status Field
The database field: `hrm_users.is_active` (Boolean, default: True)

---

## Important Notes

⚠️ **Cannot Deactivate Self**  
You cannot deactivate your own user account to prevent locking yourself out.

⚠️ **Authorization**
- Super Admin can toggle any user
- Tenant Admin/HR Manager can only toggle users within their tenant

⚠️ **Document Creation Timing**
Remember: Salary slip documents are created during **payroll generation**, not during approval/finalization. Make sure:
1. Payroll was generated for this employee
2. The employee is now active
3. They can see the generated documents

---

## Troubleshooting

### Issue: Toggle button doesn't work
- Ensure you're logged in as Super Admin or appropriate role
- Check browser console (F12) for error messages
- Verify the URL is correct: `/access-control/api/toggle-user-status/{user_id}`

### Issue: Status changes but documents still don't appear
- Verify payroll was actually generated for this employee (check Payroll > Payroll Management)
- Check if `EmployeeDocument` records exist in the database for this employee
- Verify the employee profile is linked to the user account

### Issue: Can't find the user management page
- As Super Admin, look for: **Settings > Access Control > User Management**
- Or try: **Admin > User Roles & Company Access**

---

## Next Steps for Your Payslip Issue

1. **Check AKSL093 Status**
   - Navigate to User Management
   - Verify current is_active status

2. **Enable if Needed**
   - Toggle to Active if currently Inactive

3. **Verify Payroll Generated**
   - Check Payroll > Payroll Management
   - Confirm payroll exists for this employee

4. **Test Access**
   - Log in as AKSL093 and check "My Documents"
   - Salary slip should appear

5. **Debug if Still Not Working**
   - Check database: `SELECT * FROM hrm_employee_documents WHERE employee_id = ?`
   - Verify `document_type = 'Salary Slip'`
   - Check month and year fields match the payroll period

---

## Questions?

Check the system documentation or admin logs for audit trail of status changes:
- View audit logs in: **Admin Settings > Audit Logs**
- Look for action: `TOGGLE_USER_STATUS`