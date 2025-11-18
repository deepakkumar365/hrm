# HRM System Dashboards - Complete Guide by Role

## System Roles Available
The HRM system supports the following roles:
1. **Super Admin** - System administrator with full access
2. **Tenant Admin** - Administrator for a specific tenant
3. **HR Manager** - HR department manager
4. **Manager** - Team/Department manager
5. **Employee** - Regular employee

---

## Dashboard Breakdown by Role

### 🔴 Super Admin (1 Dashboard)

#### 1. **Super Admin Dashboard**
- **Route**: `/dashboard`
- **Template**: `super_admin_dashboard.html`
- **URL Path**: Route redirects to this when user.role.name == 'Super Admin'
- **Features**:
  - Tenant statistics (total, active tenants)
  - Company statistics across all tenants
  - User statistics (total, active users)
  - Company-wise user count (top 10 companies)
  - Payroll statistics (last 6 months)
  - Revenue tracking (monthly, quarterly, yearly)
  - Payment collection status
  - Recent tenants with metrics
  - Multi-company user distribution chart
  - Payslip generation trends
  - Revenue analytics

**Access Restrictions**: Super Admin only
**Location in Code**: `routes.py` lines 236-374 (render_super_admin_dashboard function)

---

### 🟠 Tenant Admin (1 Dashboard)

#### 1. **HR Manager Dashboard** (Accessible by Tenant Admin)
- **Route**: `/dashboard/hr-manager`
- **Template**: `hr_manager_dashboard.html`
- **Methods**: GET, POST
- **Features**:
  - Company-wise attendance statistics
  - Leave statistics by type
  - Overtime (OT) management and approvals
  - Payroll history (last 3 months)
  - Monthly statistics (MTD - Month-To-Date)
  - Yearly statistics (YTD - Year-To-Date)
  - Today's attendance summary
  - Today's leave summary
  - Today's OT summary
  - Pending OT approvals
  - Monthly and yearly breakdown

**Sub-Routes Available**:
- `/dashboard/hr-manager/ot-approval` - OT Approval Management
- `/dashboard/hr-manager/ot-attendance` - OT Attendance Records
- `/dashboard/hr-manager/generate-payroll` - Payroll Generation
- `/dashboard/hr-manager/payroll-reminder` - Payroll Reminders

**Access Restrictions**: Tenant Admin, HR Manager, Super Admin
**Location in Code**: `routes_hr_manager.py` lines 213-382

---

### 🟡 HR Manager (Multiple Dashboards - 5 Total)

#### 1. **HR Manager Dashboard** (Main)
- **Route**: `/dashboard/hr-manager`
- **Template**: `hr_manager_dashboard.html`
- **Same as Tenant Admin above**
- **Additional Sub-Dashboards**:

#### 2. **OT Approval Dashboard** (HR Manager Level 2)
- **Route**: `/ot/approval` 
- **Template**: `ot/approval_dashboard.html`
- **Features**:
  - Pending OT approvals for final level (HR)
  - Approval statistics
  - Rejected/approved counts
  - Approval level indication: "HR"
  - Final approval decision interface

**Location in Code**: `routes_ot.py` (lines 809+)
**Access**: HR Manager, Tenant Admin, Super Admin

#### 3. **OT Attendance Records**
- **Route**: `/dashboard/hr-manager/ot-attendance`
- **Template**: `hr_manager/ot_attendance.html`
- **Features**:
  - OT attendance records with pagination
  - Date range filtering (last 30 days default)
  - Page navigation

#### 4. **Payroll Generation Interface**
- **Route**: `/dashboard/hr-manager/generate-payroll`
- **Template**: `hr_manager/generate_payroll.html`
- **Features**:
  - Company selection
  - Month/Year selection
  - Payroll generation initiation

**Restriction**: Only Tenant Admin and Super Admin can generate
**HR Manager can view**: Yes, but cannot generate (403 if attempted)

#### 5. **Payroll Reminder**
- **Route**: `/dashboard/hr-manager/payroll-reminder`
- **Template**: `hr_manager/payroll_reminder.html`
- **Features**:
  - Pending payrolls for current month
  - Reminder notifications

**Location in Code**: `routes_hr_manager.py` lines 356-382

---

### 🔵 Manager (2 Dashboards)

#### 1. **OT Manager Approval Dashboard** (Level 1)
- **Route**: `/ot/manager-approval` or similar
- **Template**: `ot/manager_approval_dashboard.html`
- **Features**:
  - Pending OT approvals from team members (Level 1)
  - Manager-specific approval interface
  - Team statistics
  - Approval history

**Location in Code**: `routes_ot.py` (lines 567-807)
**Access**: Managers can approve Level 1 OT requests

#### 2. **General Dashboard**
- **Route**: `/dashboard`
- **Template**: `dashboard.html`
- **Features**:
  - Basic HR metrics
  - Team member activities
  - Pending leaves from team
  - Recent team activities
  - Attendance rate statistics
  - Pending claims/leaves count

**Location in Code**: `routes.py` lines 432-447

---

### 🟢 Employee (1 Dashboard)

#### 1. **General Dashboard** (Employee View)
- **Route**: `/dashboard`
- **Template**: `dashboard.html`
- **Features**:
  - Own leave history
  - Own recent activities
  - Personal leave status
  - Claim status
  - Attendance records

**Location in Code**: `routes.py` lines 449-462

---

## Additional Specialized Dashboards

### 📋 Compliance Dashboard
- **Template**: `templates/compliance/dashboard.html`
- **Status**: Template exists but no dedicated route found
- **Purpose**: Compliance tracking and reporting
- **Likely Access**: Tenant Admin, HR Manager

### 🏢 Tenant Admin Dashboard
- **Template**: `templates/tenant_admin_dashboard.html`
- **Status**: Template exists but no dedicated route found
- **Purpose**: Could be alternate interface for Tenant Admin
- **Note**: May need to be implemented as a route

---

## Route Hierarchy

```
/dashboard
├── Super Admin → super_admin_dashboard.html (Tenant & Company Analytics)
├── Tenant Admin → hr_manager_dashboard.html
├── HR Manager → hr_manager_dashboard.html
│   ├── /ot-approval → ot/approval_dashboard.html
│   ├── /ot-attendance → hr_manager/ot_attendance.html
│   ├── /generate-payroll → hr_manager/generate_payroll.html
│   └── /payroll-reminder → hr_manager/payroll_reminder.html
├── Manager → dashboard.html (General) + ot/manager_approval_dashboard.html
└── Employee → dashboard.html (General)

/ot
├── /manager-approval → ot/manager_approval_dashboard.html
└── /approval → ot/approval_dashboard.html
```

---

## Summary Table

| Role | Dashboard Count | Primary Dashboard | Sub-Dashboards |
|------|-----------------|-------------------|-----------------|
| Super Admin | 1 | Super Admin Dashboard | - |
| Tenant Admin | 1 | HR Manager Dashboard | 4 sub-routes |
| HR Manager | 5 | HR Manager Dashboard | OT Approval, OT Attendance, Payroll Gen, Payroll Reminder |
| Manager | 2 | General Dashboard | OT Manager Approval |
| Employee | 1 | General Dashboard | - |

---

## Files Reference

**Route Files**:
- `routes.py` - Main dashboard and general dashboard routes
- `routes_hr_manager.py` - HR Manager dashboard and sub-routes
- `routes_ot.py` - OT approval dashboards

**Template Files**:
- `templates/dashboard.html` - General dashboard
- `templates/super_admin_dashboard.html` - Super Admin dashboard
- `templates/hr_manager_dashboard.html` - HR Manager dashboard
- `templates/hr_manager/ot_approval.html` - OT approval for HR
- `templates/hr_manager/ot_attendance.html` - OT records
- `templates/hr_manager/generate_payroll.html` - Payroll generation
- `templates/hr_manager/payroll_reminder.html` - Payroll reminders
- `templates/ot/manager_approval_dashboard.html` - Manager OT approvals
- `templates/ot/approval_dashboard.html` - HR final OT approval
- `templates/compliance/dashboard.html` - Compliance (unused)
- `templates/tenant_admin_dashboard.html` - Tenant Admin (unused)

---

## Permission Checking Mechanism

**Decorator Used**: `@require_login` and role checks
**Role Check Condition Example**:
```python
if current_user.role.name not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
    flash('Access Denied', 'danger')
    return redirect(url_for('index'))
```

---

## Notes

1. **Dashboard Reuse**: Multiple roles can access the same dashboard (e.g., HR Manager Dashboard)
2. **Conditional Rendering**: Some dashboards conditionally display features based on role
3. **Unused Templates**: `tenant_admin_dashboard.html` and `compliance/dashboard.html` templates exist but don't have dedicated routes
4. **Company Filtering**: HR Manager dashboard filters data by company
5. **OT Workflow**: OT has a 2-level approval process (Manager → HR Manager)
6. **Payroll Access**: Only Tenant Admin and Super Admin can generate payroll
