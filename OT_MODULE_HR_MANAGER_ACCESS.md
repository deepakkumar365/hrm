# 🔐 OT Management Module - HR Manager Access Control

## 📋 HR Manager Permissions Summary

An **HR Manager** in this system has the following access levels for the Overtime Management module:

| Component | Access Level | Description |
|-----------|--------------|-------------|
| Employee OT Attendance | **Editable** | Can view/manage all employees' OT records |
| OT Requests | **Editable** | Can view, approve, and reject OT requests |
| OT Approval Dashboard | **Editable** | Full access to review pending requests |
| OT Payroll Summary | **View Only** | Can view OT payment summaries for payroll |
| OT Type Management | **Hidden** | Cannot create/edit OT types (Super Admin only) |

---

## 🎯 What HR Manager CAN See

### 1. **OT Attendance Overview** (`/ot/attendance`)
- ✅ View all employees' OT attendance records
- ✅ See daily OT hours summary
- ✅ View OT status (Draft, Submitted, Approved)
- ✅ Filter by employee, date range, OT type
- ✅ See geolocation data for each OT entry

**Screen shows:**
```
Weekly OT Summary
- Employee: John Doe
- Regular OT: 10 hours (1.25x)
- Weekend OT: 5 hours (1.5x)
- Holiday OT: 3 hours (2.0x)
- Sunday OT: 2 hours (1.75x)
- Total: 20 hours
```

---

### 2. **OT Requests Dashboard** (`/ot/requests`)
- ✅ View all pending OT requests from employees
- ✅ See request details (employee, date, hours, reason)
- ✅ Access to approve/reject individual requests
- ✅ Add approval comments
- ✅ Bulk approve/reject operations
- ✅ Search and filter capabilities

**Statistics visible:**
```
OT Requests Dashboard
- Pending Requests: 12
- Total Hours Pending: 45.5 hours
- Approved This Month: 8 requests (32 hours)
- Rejected This Month: 2 requests (8 hours)
```

---

### 3. **Approval Dashboard** (`/ot/approvals`)
- ✅ See all pending OT approval requests
- ✅ View employee details (name, department, manager)
- ✅ Review OT type and hours requested
- ✅ Access to approve with modified hours
- ✅ Reject with reason/comments
- ✅ View approval history

**Dashboard layout:**
```
Pending Approvals
┌─────────────────────────────────────────────────┐
│ Employee: Sarah Johnson | Dept: Sales          │
│ OT Type: Weekend OT | Hours: 8.0               │
│ Reason: Project completion                      │
│ [Approve] [Reject] [View Details]              │
└─────────────────────────────────────────────────┘
```

---

### 4. **Payroll OT Summary** (`/ot/payroll-summary`)
- ✅ View monthly OT hours by type (READ-ONLY)
- ✅ See total OT amounts (calculated for payroll)
- ✅ Access daily logs of OT entries
- ✅ Download summary reports
- ✅ View breakdown by employee and OT type

**Payroll view:**
```
Monthly OT Summary - January 2024

Employee: John Doe
┌──────────────┬───────┬──────────┬─────────┐
│ OT Type      │ Hours │ Amount   │ Status  │
├──────────────┼───────┼──────────┼─────────┤
│ General OT   │ 10.0  │ ₹1,250   │ Synced  │
│ Weekend OT   │ 5.0   │ ₹937.50  │ Synced  │
│ Holiday OT   │ 3.0   │ ₹1,500   │ Synced  │
│ Sunday OT    │ 2.0   │ ₹700     │ Synced  │
├──────────────┼───────┼──────────┼─────────┤
│ TOTAL        │ 20.0  │ ₹4,387.50│ Ready   │
└──────────────┴───────┴──────────┴─────────┘
```

---

## 🚫 What HR Manager CANNOT See

| Feature | Access | Reason |
|---------|--------|--------|
| Create OT Types | ❌ Hidden | Only Super Admin/Tenant Admin |
| Edit OT Rate Multipliers | ❌ Hidden | System configuration only |
| Delete OT Records | ❌ Hidden | Audit trail protection |
| Modify Approved OT (History) | ❌ Hidden | Prevents tampering |
| Configure OT Policies | ❌ Hidden | Tenant Admin responsibility |
| Access Other Company's OT | ❌ Hidden | Data isolation |

---

## 📊 Default Role-Based Access Matrix

```
╔═══════════════════════════════════════════════════════════════════╗
║          OT Module Access by Role                                 ║
╠════════════════════╦════════════╦════════════╦═════════╦══════════╣
║ Feature            ║ Super Admin║ Tenant Adm ║ HR Mgr  ║ Employee ║
╠════════════════════╬════════════╬════════════╬═════════╬══════════╣
║ OT Attendance      ║ Editable   ║ Editable   ║ Editable║ Editable*║
║ OT Requests        ║ Editable   ║ Editable   ║ Editable║ Editable*║
║ Approval Dashboard ║ Editable   ║ Editable   ║ Editable║ Hidden   ║
║ Payroll Summary    ║ Editable   ║ Editable   ║ View    ║ Hidden   ║
║ OT Type Mgmt       ║ Editable   ║ Editable   ║ Hidden  ║ Hidden   ║
║ Rate Multipliers   ║ Editable   ║ Editable   ║ Hidden  ║ Hidden   ║
║ Company Settings   ║ Editable   ║ Editable   ║ Hidden  ║ Hidden   ║
║ Audit Logs         ║ View Only  ║ View Only  ║ Hidden  ║ Hidden   ║
╚════════════════════╩════════════╩════════════╩═════════╩══════════╝

* Employees can only see their own records
```

---

## 🔐 API Endpoints Access for HR Manager

```python
# HR Manager CAN access these endpoints:

GET    /ot/attendance              # View OT attendance page
GET    /ot/request                 # View OT requests form
GET    /ot/approvals               # View approval dashboard (MAIN)
POST   /ot/approve/<request_id>    # Approve OT request (MAIN)
POST   /ot/reject/<request_id>     # Reject OT request (MAIN)
GET    /ot/payroll-summary         # View payroll OT summary (READ-ONLY)

# HR Manager CANNOT access these endpoints:

POST   /ot/types                   # Create OT Type (403 Forbidden)
PUT    /ot/types/<type_id>         # Edit OT Type (403 Forbidden)
DELETE /ot/types/<type_id>         # Delete OT Type (403 Forbidden)
POST   /ot/settings                # Edit OT Settings (403 Forbidden)
GET    /ot/audit-logs              # View audit logs (403 Forbidden)
```

---

## 🎬 Sample HR Manager Workflow

### **Scenario: Approving Employee OT Requests**

**Step 1: HR Manager logs in and sees dashboard**
```
Dashboard → HR Manager Menu → Attendance → Overtime Management
```

**Step 2: Navigate to OT Approvals**
```
/ot/approvals
Shows: 5 pending requests, 32 total hours pending
```

**Step 3: Review pending request**
```
Request Details:
- Employee: Sarah Johnson (Sales Department)
- Date: January 15, 2024
- OT Type: Weekend OT (1.5x multiplier)
- Hours: 8.0
- Reason: "Project deadline completion"
- Base Salary: ₹50,000
- Calculated Amount: ₹937.50

[Approve] [Modify Hours] [Reject]
```

**Step 4: Approve with optional modifications**
```
Action: Approve
Approved Hours: 8.0 (keep original)
Comments: "Approved - Project deadline confirmed"
[Submit Approval]
```

**Step 5: Auto-sync to Payroll**
```
✅ OT automatically synced to January 2024 payroll
✅ Amount: ₹937.50 added to payroll
✅ Audit trail recorded
```

---

## 🔄 Data Visibility by Company

HR Managers can **ONLY** see:
- ✅ OT records of their own company
- ✅ Their own company's employees
- ✅ Their company's OT types and settings

HR Managers **CANNOT** see:
- ❌ Other companies' OT records (data isolation)
- ❌ Other companies' employees' OT
- ❌ Inter-company OT comparisons

---

## 📈 OT Metrics Visible to HR Manager

HR Managers have access to these analytics:

```
OT Dashboard Metrics:
├─ Total OT Hours (Month)
├─ Total OT Amount (Month)
├─ OT by Type (breakdown)
├─ OT by Department
├─ Employee with Most OT
├─ Approval Rate (Approved vs Total)
├─ Average OT Hours per Employee
├─ OT Trend (month-on-month)
└─ Pending Approvals
```

---

## 🚀 Implementation Recommendation

To enable proper access control for OT module, update `routes_ot.py` with:

```python
# Employee routes (own records only)
@ot_bp.route('/attendance', methods=['GET'])
@login_required
def attendance_page():
    # Employees see only their own records
    # HR Managers see all employees

# Manager approval routes
@ot_bp.route('/approvals', methods=['GET'])
@require_role(['HR Manager', 'Admin', 'Super Admin'])
def approval_dashboard():
    # HR Manager can see all pending requests
    # Other roles cannot access

# Payroll integration
@ot_bp.route('/payroll-summary', methods=['GET'])
@require_role(['HR Manager', 'Admin', 'Super Admin'])  
def get_payroll_ot_summary():
    # HR Manager has READ-ONLY access
    # Others cannot see
```

---

## 🎯 Key Features for HR Manager

| Feature | Availability | Notes |
|---------|--------------|-------|
| **Bulk Approve** | ✅ Yes | Select multiple and approve together |
| **Bulk Reject** | ✅ Yes | Select multiple and reject together |
| **Export to Excel** | ✅ Yes | Download approval requests |
| **Filter by Date** | ✅ Yes | Date range filtering |
| **Filter by Employee** | ✅ Yes | Search specific employee |
| **Filter by OT Type** | ✅ Yes | General/Weekend/Holiday/Sunday |
| **Search Box** | ✅ Yes | Find requests quickly |
| **Approval History** | ✅ Yes | See past approvals |
| **Rejection Reasons** | ✅ Yes | Document why rejected |
| **Edit Hours** | ✅ Yes | Modify approved hours before submission |

---

## ⚙️ Default Configuration

**HR Manager access should be configured as:**

1. **Automatic Approvals**: Disabled (requires manual review)
2. **Maximum OT per Day**: 12 hours (can adjust)
3. **Approval Timeout**: 7 days (requests auto-expire if not approved)
4. **Notification on Request**: Yes (HR Manager gets notified)
5. **Email Summary**: Daily digest of pending requests
6. **View History**: Last 90 days of approvals

---

## 🔍 Audit Trail

All HR Manager actions are logged:
```
[2024-01-15 10:30:45] HR Manager: john_smith
  Action: Approved OT Request #1245
  Employee: Sarah Johnson
  Hours: 8.0
  Amount: ₹937.50
  Reason: "Approved for project deadline"
  Status: Success ✅
```

---

## 📞 Access Control Summary

**To grant HR Manager access to OT module:**

```sql
-- Update access control matrix
UPDATE role_access_control
SET hr_manager_access = 'Editable'
WHERE module_name = 'Overtime'
AND menu_name IN ('OT Attendance', 'OT Requests', 'OT Approval');

UPDATE role_access_control
SET hr_manager_access = 'View Only'
WHERE module_name = 'Overtime'
AND menu_name = 'OT Payroll Summary';
```

---

**Questions?** Check the main `OT_MODULE_DEPLOYMENT_GUIDE.md` for full implementation details.