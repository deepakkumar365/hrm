# HR Manager User Status Toggle Access

## ✅ Implementation Complete

**Date**: December 2024  
**Change**: HR Manager role now has access to User Status Toggle feature  
**Status**: Active

---

## 📍 Access Locations

### 1. User Management Page
| Property | Value |
|---|---|
| **URL** | `/users` |
| **Navigation** | Admin > Access Control > User Management |
| **Required Role** | Super Admin, Admin, or **HR Manager** ✅ |
| **Template** | `templates/users/list.html` |

**What HR Manager can do:**
- ✅ View all users in their tenant (filtered by tenant_id)
- ✅ See user status (Active/Inactive badges)
- ✅ Toggle user status with one click
- ✅ View status changes in real-time

---

### 2. User Role & Company Access Mapping
| Property | Value |
|---|---|
| **URL** | `/access-control/user-roles` |
| **Navigation** | Admin > Access Control > User Role & Company Access Mapping |
| **Required Role** | Super Admin, Tenant Admin, or **HR Manager** ✅ |
| **Template** | `templates/access_control/user_role_mapping.html` |

**What HR Manager can do:**
- ✅ View all users and their role mappings in their tenant
- ✅ See user status with color-coded badges
- ✅ Toggle user active/inactive status
- ✅ Manage role assignments within their tenant

---

### 3. API Endpoint (Programmatic Access)
| Property | Value |
|---|---|
| **Method** | POST |
| **Endpoint** | `/access-control/api/toggle-user-status/<user_id>` |
| **Required Role** | Super Admin, Tenant Admin, or **HR Manager** ✅ |

**Example Request:**
```bash
POST /access-control/api/toggle-user-status/123

Response:
{
  "success": true,
  "message": "User john_doe is now Active",
  "is_active": true
}
```

---

## 🔐 Security & Tenant Isolation

### Tenant-Aware Filtering

**Super Admin** can:
- ✅ See ALL users across all tenants
- ✅ Toggle any user's status
- ✅ Manage users from any tenant

**HR Manager** can:
- ✅ See only users in their own tenant
- ✅ Toggle only their tenant's user status
- ✅ Cannot access users from other tenants
- ✅ Cannot toggle users outside their tenant

### Authorization Checks

```python
# Tenant isolation verification
current_tenant_id = current_user.organization.tenant_id
user_tenant_id = user.organization.tenant_id

# Only Super Admin can bypass tenant check
if current_user.role.name != 'Super Admin' and current_tenant_id != user_tenant_id:
    return error("Unauthorized: User is not in your tenant")
```

---

## 📋 Use Cases for HR Manager

### Scenario 1: Employee Cannot Log In
1. Go to `/users` (User Management)
2. Search for the employee
3. Check the Status column
4. If "Inactive" (red badge), click Toggle
5. User can now log in

### Scenario 2: Employee Cannot See Documents
1. Employee reports missing salary slip
2. HR Manager checks `/users` page
3. Finds that user status is Inactive
4. Toggles status to Active
5. Employee can now see all documents

### Scenario 3: Deactivate Inactive Employee
1. Go to User Role & Company Access Mapping
2. Find employee to be offboarded
3. Click Toggle button
4. User status changes to Inactive
5. User cannot log in anymore
6. All access is revoked

---

## 🔧 Technical Changes

### Files Modified

#### 1. `routes.py` - Line 2673-2698
**Change**: Updated `/users` route to support HR Manager

```python
@app.route('/users')
@require_role(['Super Admin', 'Admin', 'HR Manager'])  # Added HR Manager
def user_management():
    # HR Manager sees only their tenant users
    if current_user.role.name == 'Super Admin':
        users = User.query.order_by(User.first_name, User.last_name).all()
    else:
        # Tenant filtering for HR Manager
        current_tenant_id = current_user.organization.tenant_id
        users = db.session.query(User).join(
            Organization, User.organization_id == Organization.id
        ).filter(
            Organization.tenant_id == current_tenant_id
        ).order_by(User.first_name, User.last_name).all()
    
    return render_template('users/list.html', users=users)
```

#### 2. `routes_access_control.py` - Line 456-507
**Change**: Updated `/access-control/user-roles` route to support HR Manager and Tenant Admin

```python
@access_control_bp.route('/user-roles', methods=['GET'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])  # Added both
def manage_user_roles():
    # Similar tenant filtering logic
    # Tenant Admin and HR Manager see only their tenant's users
    if current_user.role.name == 'Super Admin':
        users = User.query.order_by(User.first_name, User.last_name).all()
    else:
        # Tenant-specific query
        current_tenant_id = current_user.organization.tenant_id
        users = db.session.query(User).join(
            Organization, User.organization_id == Organization.id
        ).filter(
            Organization.tenant_id == current_tenant_id
        ).order_by(User.first_name, User.last_name).all()
    
    # ... render template
```

#### 3. `routes.py` - Model Imports
**Change**: Added Organization to imports

```python
from models import (
    # ... other models ...
    Organization  # Added this
)
```

---

## ✅ Verification Checklist

- [x] HR Manager can access `/users` page
- [x] HR Manager can see only their tenant's users
- [x] HR Manager can toggle user status
- [x] HR Manager cannot access other tenants' users
- [x] Super Admin can still see all users
- [x] API endpoint accepts HR Manager role
- [x] Audit logging records all status changes
- [x] Syntax validation passed
- [x] Tenant isolation enforced

---

## 📊 Role Access Matrix (Updated)

| Role | User Management | User Role Mapping | Toggle Status |
|---|---|---|---|
| **Super Admin** | ✅ All users | ✅ All users | ✅ Any user |
| **Tenant Admin** | ❌ No | ✅ Tenant users | ✅ Tenant users |
| **HR Manager** | ✅ Tenant users | ✅ Tenant users | ✅ Tenant users |
| **Admin** | ✅ All users | ❌ No | ❌ No |
| **Manager** | ❌ No | ❌ No | ❌ No |
| **Employee** | ❌ No | ❌ No | ❌ No |

---

## 🚀 Quick Start for HR Manager

**Step 1**: Log in with HR Manager credentials  
**Step 2**: Click Admin menu (top navigation)  
**Step 3**: Choose:
- **Option A**: Access Control → User Management (simple list view)
- **Option B**: Access Control → User Role & Company Access Mapping (advanced view)

**Step 4**: Find the user you want to manage  
**Step 5**: Check Status column (green = active, red = inactive)  
**Step 6**: Click Toggle button to change status  
**Step 7**: Confirm the action  
**Step 8**: Status updates in real-time ✅

---

## 📝 Audit Trail

Every status toggle is logged with:
- **Action**: TOGGLE_USER_STATUS
- **User ID**: The user being toggled
- **Username**: The user's username
- **Old Status**: Previous is_active value
- **New Status**: New is_active value
- **Timestamp**: When the change was made
- **Changed By**: HR Manager's user ID

View audit logs in: Admin > Audit Trail

---

## ❓ Troubleshooting

### Q: HR Manager doesn't see the Toggle button
**A**: User might be from a different tenant. HR Manager can only manage their own tenant's users.

### Q: "Unauthorized" error when toggling
**A**: Verify the user is in your tenant. Super Admin should check tenant assignments.

### Q: Changes not saved
**A**: Check database connectivity. Verify the audit trail to confirm if toggle succeeded.

### Q: Can I deactivate myself?
**A**: No, the system prevents self-deactivation for safety.

---

## 🔍 Database

**Field**: `hrm_users.is_active`  
**Type**: Boolean  
**Default**: True  
**Null**: False

Check user status:
```sql
SELECT user_id, username, is_active, organization_id 
FROM hrm_users 
WHERE organization_id = ? 
ORDER BY first_name, last_name;
```

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Verify user's HR Manager role assignment
3. Confirm tenant ID is set correctly
4. Check audit trail for error details
5. Review database connection status

---

**Version**: 1.0  
**Last Updated**: December 2024  
**Status**: ✅ Production Ready