# Access Control Management Implementation Guide

## Overview

The Access Control Management system allows **Super Admin** users to dynamically manage role-based access to all modules, menus, and sub-menus through a user-friendly web interface. This eliminates the need for code-level changes and provides audit trails for all modifications.

## Features Implemented

### 1. **Role-Based Access Matrix**
- Visual table displaying all modules, menus, and sub-menus
- Columns for each role (Super Admin, Tenant Admin, HR Manager, Employee)
- Dropdown selectors for access levels: Editable, View Only, Hidden
- Real-time updates with AJAX
- Automatic audit logging

### 2. **Access Level Types**
- **Editable**: Full access - user can view, create, edit, and delete
- **View Only**: Read-only access - user can only view data
- **Hidden**: No access - menu is completely hidden from the user

### 3. **User Role & Company Mapping**
- Assign multiple roles to a single user
- Grant access to multiple companies
- Edit existing mappings
- Clear all mappings for a user

### 4. **Import/Export Functionality**
- Export access matrix as Excel file
- Import and update matrix from Excel
- Excel format: Module | Menu | Sub-Menu | Super Admin | Tenant Admin | HR Manager | Employee

### 5. **Audit Trail**
- All changes logged to `hrm_audit_log` table
- Tracks user, action, timestamp, and changes
- Immutable audit history for compliance

## Database Schema

### Table: hrm_role_access_control
```sql
CREATE TABLE hrm_role_access_control (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    module_name VARCHAR(100) NOT NULL,
    menu_name VARCHAR(100) NOT NULL,
    sub_menu_name VARCHAR(100),
    super_admin_access VARCHAR(20) DEFAULT 'Editable',
    tenant_admin_access VARCHAR(20) DEFAULT 'Hidden',
    hr_manager_access VARCHAR(20) DEFAULT 'Hidden',
    employee_access VARCHAR(20) DEFAULT 'Hidden',
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW() ON UPDATE NOW(),
    created_by VARCHAR(100) DEFAULT 'system',
    updated_by VARCHAR(100),
    INDEX idx_role_access_module_menu (module_name, menu_name)
);
```

### Table: hrm_user_role_mapping
```sql
CREATE TABLE hrm_user_role_mapping (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    role_id INTEGER NOT NULL,
    company_id UUID,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT NOW(),
    updated_at DATETIME DEFAULT NOW() ON UPDATE NOW(),
    created_by VARCHAR(100) DEFAULT 'system',
    FOREIGN KEY (user_id) REFERENCES hrm_users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES role(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE,
    INDEX idx_user_role_mapping_user_id (user_id)
);
```

### Table: hrm_audit_log
```sql
CREATE TABLE hrm_audit_log (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(100) NOT NULL,
    changes TEXT,
    status VARCHAR(20) DEFAULT 'Success',
    created_at DATETIME NOT NULL DEFAULT NOW(),
    FOREIGN KEY (user_id) REFERENCES hrm_users(id) ON DELETE SET NULL,
    INDEX idx_audit_log_user_id (user_id),
    INDEX idx_audit_log_action (action),
    INDEX idx_audit_log_created_at (created_at)
);
```

## File Structure

### New Files Created
1. **routes_access_control.py** - Main routes and business logic
2. **templates/access_control/access_matrix.html** - Access matrix UI
3. **templates/access_control/user_role_mapping.html** - User role mapping UI
4. **ACCESS_CONTROL_IMPLEMENTATION.md** - This documentation

### Modified Files
1. **models.py** - Added RoleAccessControl, UserRoleMapping, AuditLog models
2. **routes.py** - Added AuditLog import
3. **main.py** - Added routes_access_control import

## API Endpoints

### 1. View Access Matrix
**Route**: `/access-control/matrix`  
**Method**: `GET`  
**Auth**: Super Admin only  
**Description**: Displays the role-based access control matrix

### 2. Update Access Level
**Route**: `/access-control/matrix/update`  
**Method**: `POST`  
**Auth**: Super Admin only  
**Payload**:
```json
{
    "access_id": 1,
    "role": "super_admin",
    "access_level": "Editable"
}
```

### 3. Reset Matrix
**Route**: `/access-control/matrix/reset`  
**Method**: `POST`  
**Auth**: Super Admin only  
**Description**: Reset all access levels to default values

### 4. Export Matrix
**Route**: `/access-control/matrix/export`  
**Method**: `GET`  
**Auth**: Super Admin only  
**Response**: Excel file download

### 5. Import Matrix
**Route**: `/access-control/matrix/import`  
**Method**: `POST`  
**Auth**: Super Admin only  
**Payload**: FormData with file

### 6. User Role Mapping Interface
**Route**: `/access-control/user-roles`  
**Method**: `GET`  
**Auth**: Super Admin only  
**Description**: Display user role and company access mapping interface

### 7. Save User Role Mapping
**Route**: `/access-control/user-roles/save`  
**Method**: `POST`  
**Auth**: Super Admin only  
**Payload**:
```json
{
    "user_id": 1,
    "role_ids": [1, 2, 3],
    "company_ids": ["uuid1", "uuid2"]
}
```

### 8. Get User Role Mappings (API)
**Route**: `/api/user-role-mappings/<user_id>`  
**Method**: `GET`  
**Auth**: Super Admin only  
**Response**:
```json
{
    "success": true,
    "mappings": [
        {
            "id": 1,
            "user_id": 1,
            "role_id": 2,
            "role_name": "HR Manager",
            "company_id": "uuid1",
            "company_name": "ACME Corp"
        }
    ]
}
```

## Usage Instructions

### Accessing the Interface

1. **Login** with Super Admin credentials
2. Navigate to **Admin Settings** → **Access Control Configuration**

### Managing Access Matrix

#### Viewing and Modifying Access Levels

1. Open the **Access Matrix** page
2. Locate the module, menu, and sub-menu in the table
3. Click the dropdown in the corresponding role column
4. Select new access level: **Editable**, **View Only**, or **Hidden**
5. Changes are saved automatically via AJAX
6. Audit log entries created for each change

#### Resetting to Defaults

1. Click the **Reset to Default** button
2. Confirm the action in the dialog
3. All access levels will be reset to system defaults
4. Audit trail recorded

#### Exporting Access Matrix

1. Click **Export as Excel** button
2. Excel file downloads with current matrix
3. File name format: `access_matrix_YYYYMMDD_HHMMSS.xlsx`

#### Importing Access Matrix

1. Prepare an Excel file with columns: Module | Menu | Sub-Menu | Super Admin | Tenant Admin | HR Manager | Employee
2. Click **Import Matrix** button
3. Select the file
4. Click **Import**
5. System validates and updates records
6. Success message shows number of records imported

### Managing User Roles

#### Assigning Multiple Roles to a User

1. Navigate to **Access Control** → **User Role & Company Access Mapping**
2. Select a user from the dropdown
3. Check roles to assign (can select multiple)
4. Optionally select companies for restricted access
5. Click **Save Mapping**
6. User can now access selected roles across specified companies

#### Viewing All Mappings

The page displays a table of all users with their:
- Assigned roles (badges)
- Company access
- Active status

## Implementation Examples

### Example 1: Restrict Payroll Module

To restrict payroll access to Super Admin and Tenant Admin only:

1. Go to Access Matrix
2. Find all rows with Module = "Payroll"
3. Set access levels:
   - Super Admin: **Editable**
   - Tenant Admin: **Editable**
   - HR Manager: **View Only**
   - Employee: **Hidden**

### Example 2: Assign User Multiple Roles

To make a user both HR Manager and Finance Officer:

1. Go to User Role Mapping
2. Select the user
3. Check "HR Manager" and "Finance Officer" roles
4. Click Save Mapping

The user can now switch between these roles.

### Example 3: Company-Specific Access

To restrict a user to a specific company:

1. Go to User Role Mapping
2. Select the user
3. Assign HR Manager role
4. Check "ACME Singapore" company
5. Leave other companies unchecked
6. Save Mapping

The user now has access only to data for ACME Singapore.

## Enforcing Access Control in Routes

To enforce access control in existing routes, use these utility functions:

### Check if Module is Visible
```python
from routes_access_control import check_ui_access

# In your route
user_role = current_user.role.name
if check_ui_access(user_role, 'Payroll', 'Payroll Management'):
    # Show menu item in template
```

### Check Edit Permission
```python
from routes_access_control import check_edit_permission

# Verify permission before allowing edit
if not check_edit_permission(user_role, 'Payroll', 'Payroll Generation'):
    return "Access Denied", 403
```

### Check Module Access Level
```python
from routes_access_control import check_module_access

access_level = check_module_access(user_role, 'Payroll')
# Returns: 'Editable', 'View Only', or 'Hidden'
```

### Template Usage
```html
{% if check_ui_access(current_user.role.name, 'Payroll', 'Payroll Management') %}
    <li><a href="/payroll">Payroll</a></li>
{% endif %}
```

## Default Access Configuration

### Modules and Default Access

**Payroll Module**
- Payroll Management: SA-Edit, TA-Edit, HM-View, E-View
- Payslip Management: SA-Edit, TA-Edit, HM-View, E-View
- Payroll Reports: SA-Edit, TA-Edit, HM-View, E-View

**Attendance Module**
- Attendance Management: SA-Edit, TA-Edit, HM-View, E-View
- Leave Management: SA-Edit, TA-Edit, HM-Edit, E-Edit

**Employees Module**
- Employee Management: SA-Edit, TA-Edit, HM-View, E-Hidden
- Employee Documents: SA-Edit, TA-Edit, HM-View, E-View

**Admin Settings**
- Access Control: SA-Edit, TA-Hidden, HM-Hidden, E-Hidden
- Master Data: SA-Edit, TA-Edit, HM-Hidden, E-Hidden

*Abbreviations: SA=Super Admin, TA=Tenant Admin, HM=HR Manager, E=Employee*

## Audit Trail

All changes are logged to the `hrm_audit_log` table. Audit entries include:

- **Action**: The type of change (UPDATE_ACCESS_CONTROL, CREATE_USER, etc.)
- **User ID**: Who made the change
- **Resource Type**: What was changed (RoleAccessControl, User, etc.)
- **Resource ID**: ID of the changed resource
- **Changes**: JSON with before/after values
- **Timestamp**: When the change occurred
- **Status**: Success or Failed

### Viewing Audit Logs

```python
from models import AuditLog

# Get all access control changes
logs = AuditLog.query.filter_by(
    action='UPDATE_ACCESS_CONTROL'
).order_by(AuditLog.created_at.desc()).all()

for log in logs:
    print(f"{log.created_at} - {log.user.username} - {log.changes}")
```

## Troubleshooting

### Issue: Changes not saving

1. Check browser console for JavaScript errors
2. Verify user has Super Admin role
3. Check database connection
4. Look for audit log entries to confirm attempts

### Issue: Access matrix showing empty

1. The first load will initialize default values
2. Refresh the page if needed
3. Check database for `hrm_role_access_control` table

### Issue: User mappings not applying

1. Verify UserRoleMapping records exist
2. Check company_id matches user's organization
3. Confirm is_active = true
4. Verify role exists and is not deleted

## Security Considerations

1. **Authentication**: All access control routes require Super Admin role
2. **Authorization**: Changes are restricted to Super Admin only
3. **Audit Trail**: Immutable log of all changes with user information
4. **Data Validation**: Input validation on all role and access level values
5. **CSRF Protection**: Flask-WTF CSRF tokens in forms
6. **Session Management**: Secure session cookies with HTTPOnly flag

## Integration Checklist

- [ ] Database migrations run successfully
- [ ] Models (RoleAccessControl, UserRoleMapping, AuditLog) created
- [ ] routes_access_control.py imported in main.py
- [ ] Access Control menu added to base.html navigation
- [ ] Test accessing /access-control/matrix
- [ ] Test creating user role mappings
- [ ] Test export/import functionality
- [ ] Verify audit logs being created
- [ ] Test access enforcement in routes
- [ ] Super Admin can access interface
- [ ] Other roles cannot access interface
- [ ] Excel import/export working

## Testing Scenarios

### Scenario 1: Update Single Access Level
1. Navigate to access matrix
2. Change one dropdown value
3. Verify instant update without page reload
4. Check audit log for change entry

### Scenario 2: Export and Import
1. Export current matrix
2. Open Excel file
3. Modify one access level
4. Save and import
5. Verify changes applied

### Scenario 3: Role Mapping
1. Assign user two roles
2. Assign to specific companies
3. Save
4. View mappings table
5. Verify user appears with correct roles and companies

### Scenario 4: Audit Trail
1. Make changes to access matrix
2. Query audit logs
3. Verify entries for each change
4. Check user_id, timestamp, and changes JSON

## Support and Maintenance

### Regular Maintenance
- Review audit logs monthly for suspicious changes
- Backup access matrix configuration monthly
- Test import/export quarterly
- Update default configurations as business needs change

### Monitoring
- Monitor audit log table size
- Archive old audit logs if table grows large
- Track failed access attempts

## Future Enhancements

Possible improvements for future versions:
1. Role-based field-level access control
2. Time-based access restrictions
3. Approval workflow for access changes
4. Access request self-service portal
5. Dashboard with access analytics
6. Bulk role assignment for multiple users
7. Template-based access profiles
8. Department-based default access

## Contact and Support

For issues or questions regarding the Access Control Management system:
1. Check the audit log for related activities
2. Review this documentation
3. Check application logs for errors
4. Contact system administrator

---

**Implementation Date**: 2024  
**Last Updated**: 2024  
**Version**: 1.0