# Role-Based Access Control (RBAC) Plan

Based on the analysis of `routes/routes_access_control.py` and `core/models.py`, here is the breakdown of permissions for each role.

## 1. Role Hierarchy

| Role Name | Scope | Description |
| :--- | :--- | :--- |
| **Super Admin** | **Global System** | Complete control over the entire system, all tenants, and all configurations. Can manage the Access Matrix itself. |
| **Tenant Admin** | **Organization (Full)** | Administrator for a specific client/tenant. Can manage all master data, users, and settings *within their own organization*. |
| **HR Manager** | **Organization (Operational)** | Focuses on day-to-day HR operations: Payroll, Attendance, Leaves, and Employee management. Restricted from system-wide configs. |
| **Employee** | **Self-Service** | Limited access. Can only view their own data (Payslips, Profile) and perform self-service actions (Apply Leave, Clock In/Out). |

## 2. Permission Matrix (Default Configuration)

This matrix is dynamically enforced by the `RoleAccessControl` model.

### **Legend**
*   **Editable**: Can View, Add, Edit, and Delete.
*   **View Only**: Can only View and Download reports.
*   **Hidden**: Menu item is completely invisible.

| Module | Feature / Menu | Super Admin | Tenant Admin | HR Manager | Employee |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Admin Settings** | **Master Data** (Roles, Depts) | **Editable** | **Editable** | Hidden | Hidden |
| | Access Control Config | **Editable** | Hidden | Hidden | Hidden |
| | User Role Mapping | **Editable** | Hidden | Hidden | Hidden |
| **Employees** | Employee List / View | **Editable** | **Editable** | **Editable** | **View Only** (Self) |
| | Add / Edit Employee | **Editable** | **Editable** | **Editable** | Hidden |
| | Documents | **Editable** | **Editable** | **Editable** | **View Only** (Self) |
| **Payroll** | Generation & Processing | **Editable** | **Editable** | **Editable** | Hidden |
| | Payslips | **Editable** | **Editable** | **Editable** | **View Only** (Self) |
| | Payroll Reports | **Editable** | **Editable** | **View Only** | Hidden |
| **Attendance** | Mark Attendance | **Editable** | **Editable** | **Editable** | **Editable** (Self) |
| | Reports & Lists | **Editable** | **Editable** | **Editable** | **View Only** (Self) |
| **Leaves** | Application | **Editable** | **Editable** | **Editable** | **Editable** (Self) |
| | Approvals | **Editable** | **Editable** | **Editable** | Hidden |
| **Appraisals** | Management | **Editable** | **Editable** | **Editable** | **View Only** (Self) |

## 3. Key Differentiators in Code

*   **Super Admin vs. Tenant Admin**:
    *   **Code:** `routes_access_control.py` lines 94-121.
    *   **Logic:** Super Admin gets `Editable` on *everything*. Tenant Admin is explicitly blocked (`Hidden`) from "Access Control Configuration" and "User Role Mapping" to prevent them from elevating their own privileges.

*   **HR Manager vs. Tenant Admin**:
    *   **Logic:** HR Managers are often restricted to `View Only` on sensitive configuration or financial reports that only the Tenant Admin should change.
    *   **Master Data:** HR Managers cannot change system-wide Master Data (like creating new Departments or Designations) by default; this is reserved for Tenant Admins.

*   **Employee Restrictions**:
    *   **Logic:** Employees are strictly `Hidden` from all management menus.
    *   **Self-Service:** They have specific `Editable` access *only* for "Mark Attendance" and "Apply Leave".

## 4. Implementation Logic

The system checks permissions in two ways:

1.  **Menu Visibility (Frontend):**
    *   Before rendering the sidebar, the app queries `RoleAccessControl` to see if a menu should be shown.
    *   *Function:* `check_ui_access(user_role, module, menu)`

2.  **Route Protection (Backend):**
    *   Critical actions (like `POSt /save-employee`) checks if the user has `Editable` rights.
    *   *Function:* `check_edit_permission(user_role, module)`
