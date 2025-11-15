# OT Two-Tier Approval Workflow - Complete Implementation Guide

## 🎯 Overview

The OT (Overtime) Management system now implements a **complete two-tier approval workflow**:

```
LEVEL 1: Manager Approval          LEVEL 2: HR Manager Approval       FINAL: Payroll
=============================      ===========================        ==============

1. Employee marks OT
   (Draft Status)
        ↓
2. HR Manager submits to Manager
   (Creates OTRequest: pending_manager)
   (Creates OTApproval L1: pending_manager)
        ↓
3. Manager Reviews & Takes Action
   ├─ APPROVE → Status = "manager_approved"
   │   ├─ Creates OTApproval L2 (pending_hr)
   │   ├─ Visible to HR Manager
   │   └─ Can modify hours if needed
   │
   └─ REJECT → Status = "manager_rejected"
       └─ Back to Employee (OTAttendance = Draft)
            ↓
       (Employee re-marks & resubmits)
        ↓
4. HR Manager Reviews Manager-Approved OT
   ├─ APPROVE → Status = "hr_approved"
   │   ├─ OTRequest.approved_at = NOW
   │   ├─ Ready for PAYROLL ✓
   │   └─ Can modify hours if needed
   │
   └─ REJECT → Status = "hr_rejected"
       ├─ Back to Manager (OTApproval L1 = pending_manager)
       └─ Manager can re-review or reject again
            ↓
       (Manager re-reviews & resubmits if needed)
        ↓
5. Payroll Calculates
   (Only OT with status = "hr_approved")
   Hours × Employee_Hourly_Rate × OT_Type_Multiplier = Amount
```

---

## 📋 Workflow Status States

### OTAttendance Table (Employee-Side)
| Status | Meaning | Next Action | Who Can Modify |
|--------|---------|-------------|----------------|
| **Draft** | Employee marked OT, not yet in approval | Submit to Manager | HR Manager |
| **Submitted** | In approval workflow | Manager to approve/reject | Read-only |
| **Manager_Rejected** | Manager rejected - back to Draft | Employee re-marks | Employee |

### OTRequest Table (Workflow-Side)
| Status | Meaning | L1 Approval | L2 Approval | Next Step |
|--------|---------|------------|------------|-----------|
| **pending_manager** | Waiting for Manager | Pending | - | Manager approves/rejects |
| **manager_approved** | Manager approved ✓ | Approved | Pending | HR Manager approves/rejects |
| **manager_rejected** | Manager rejected ✗ | Rejected | - | Back to Employee |
| **hr_rejected** | HR rejected - back to Manager | Pending | Rejected | Manager re-reviews |
| **hr_approved** | FINAL ✓ Ready for Payroll | Approved | Approved | Calculate in Payroll |

### OTApproval Table (Approval History)
| Approval Level | Status | Approver | Action | Creates Next |
|----------------|--------|----------|--------|--------------|
| **1 (Manager)** | pending_manager | Employee's Manager | Approve/Reject | L2 (if approve) |
| **1 (Manager)** | manager_approved | Employee's Manager | - | OTApproval L2 |
| **1 (Manager)** | manager_rejected | Employee's Manager | - | Back to Employee |
| **2 (HR)** | pending_hr | HR Manager | Approve/Reject | - |
| **2 (HR)** | hr_approved | HR Manager | - | Ready for Payroll |
| **2 (HR)** | hr_rejected | HR Manager | - | Back to Manager (L1) |

---

## 👥 Role-Based Access & Actions

### Employee Role
```
✓ CAN DO:
  • Mark OT (Attendance > Mark OT Attendance)
  • View their own marked OT
  • View rejection feedback from Manager

✗ CANNOT DO:
  • See approval process
  • Approve/reject others' OT
  • Access OT Management section
```

### Manager Role (Employee's Reporting Manager)
```
✓ CAN DO:
  • View OT submitted to them (OT Management > Manager Approval Dashboard)
  • Approve OT → Forwards to HR Manager
  • Reject OT → Back to Employee to re-mark
  • Modify hours before approving
  • Add comments/feedback

✗ CANNOT DO:
  • Approve to Payroll (needs HR approval too)
  • Reject after HR approval
  • View OT from other companies
```

### HR Manager Role
```
✓ CAN DO:
  • Submit Employee OT to their Manager (OT Attendance page)
  • View Manager-Approved OT (OT Requests page)
  • View Payroll-Ready OT (OT Payroll Summary page)
  • Approve OT for Payroll → OT goes to Payroll
  • Reject OT → Back to Manager to re-review
  • Modify hours before final approval
  • Generate Payroll reports

✗ CANNOT DO:
  • Approve without Manager approval first (Two-tier required!)
  • Bypass Manager review
```

### Super Admin Role
```
✓ CAN DO:
  • Everything HR Manager can do
  • Access all companies' OT
  • View all approval levels
  • Override approvals if needed
```

---

## 🔄 Complete Workflow Example

### Scenario: Employee "John" marks OT, Manager "Sarah" approves, HR Manager "Lisa" finalizes

**Step 1: Employee Marks OT**
```
John (Employee)
  → Attendance > Mark OT Attendance
  → Date: 2024-01-15, Hours: 2.0, Type: "General OT"
  → Save
  
Result:
  • OTAttendance created (status: Draft)
  • Visible only to HR Manager
```

**Step 2: HR Manager Submits to Manager**
```
Lisa (HR Manager)
  → OT Management > OT Attendance
  → Click "Submit to Manager" on John's OT record
  
System Does:
  • Creates OTRequest (status: pending_manager)
  • Creates OTApproval L1 (approver: Sarah's User ID, status: pending_manager)
  • Updates OTAttendance (status: Submitted)
  • Sends notification to Sarah (if notifications configured)
  
Database State:
  OTAttendance.status = "Submitted"
  OTRequest.status = "pending_manager"
  OTApproval[L1].status = "pending_manager"
  OTApproval[L1].approver_id = Sarah.user_id
```

**Step 3: Manager Reviews & Approves**
```
Sarah (Manager) sees notification or checks:
  → OT Management > Manager Approval Dashboard
  → Sees John's pending OT (2.0 hours)
  → Clicks "Approve"
  → Optionally adds comment: "Approved - Project deadline"
  
System Does:
  • Updates OTApproval L1 (status: manager_approved)
  • Updates OTRequest (status: manager_approved)
  • Creates OTApproval L2 (approver: First HR Manager found, status: pending_hr)
  • Sends notification to HR Manager Lisa
  
Database State:
  OTApproval[L1].status = "manager_approved"
  OTRequest.status = "manager_approved"
  OTApproval[L2].status = "pending_hr"
  OTApproval[L2].approver_id = Lisa.user_id
```

**Step 4: HR Manager Reviews & Approves (FINAL)**
```
Lisa (HR Manager) sees:
  → OT Management > OT Requests
  → Filter by "manager_approved" status
  → Sees John's OT (Manager approved)
  → Clicks "Approve"
  
System Does:
  • Updates OTApproval L2 (status: hr_approved)
  • Updates OTRequest (status: hr_approved, approved_at: NOW)
  • OT is NOW READY FOR PAYROLL ✓
  
Database State:
  OTApproval[L2].status = "hr_approved"
  OTRequest.status = "hr_approved"
  OTRequest.approved_at = 2024-01-16 14:30:00
```

**Step 5: Payroll Calculates**
```
Lisa (HR Manager) or Payroll Officer:
  → OT Management > OT Payroll Summary
  → Select Month: January 2024
  
System Shows:
  • Only OT with status = "hr_approved"
  • John's OT: 2.0 hours
  • Type: General OT (1.5x multiplier)
  • Calculation: 2.0 × $15/hour × 1.5 = $45
  • Total OT amount in payroll
```

---

## 🔌 Route URLs Reference

```
📝 EMPLOYEE SIDE:
  POST   /ot/mark                      → Employee marks OT (creates Draft)

🔄 HR MANAGER SIDE (Workflow Start):
  GET    /ot/attendance               → View Draft OT to submit
  POST   /ot/submit-for-manager-approval/<id>  → Submit to Manager (L1)

👨‍💼 MANAGER SIDE (L1 Approval):
  GET    /ot/manager-approval         → View pending manager approvals
  POST   /ot/manager-approval         → Approve/Reject (takes action)

👩‍💼 HR MANAGER SIDE (L2 Approval):
  GET    /ot/requests                 → View manager-approved OT for HR review
  GET    /ot/approval                 → View pending HR approvals
  POST   /ot/approval                 → Approve/Reject (final decision)

💰 PAYROLL SIDE:
  GET    /ot/payroll-summary          → View HR-approved OT for payroll
```

---

## 🎯 Key Implementation Details

### 1. **Manager Assignment**
- Managers are identified by Employee.manager_id
- Manager must have:
  - Employee record with `is_manager = True`
  - User account created (`employee.user_id` is not null)
- If employee has no manager → Cannot submit for approval (Error shown)

### 2. **Company Isolation**
- All queries filter by company_id
- Manager can only see OT from their company
- HR Manager sees only their company (unless Super Admin)

### 3. **Rejection Flow - Manager Rejects**
```
Manager clicks REJECT
  ↓
OTApproval L1.status = "manager_rejected"
OTRequest.status = "manager_rejected"
OTAttendance.status = "Draft"  ← Reset to Draft!
  ↓
Employee sees their OT back to Draft
  ↓
Employee can edit and re-submit
```

### 4. **Rejection Flow - HR Rejects**
```
HR Manager clicks REJECT
  ↓
OTApproval L2.status = "hr_rejected"
OTRequest.status = "hr_rejected"
OTApproval L1.status = "pending_manager"  ← Reset!
  ↓
Manager sees OT back in pending state
  ↓
Manager can re-review, modify hours, or re-reject
```

### 5. **Hour Modification**
- Both Manager and HR Manager can modify hours before approving
- Modified hours stored in: `OTApproval.approved_hours` and `OTRequest.approved_hours`
- Used in Payroll calculations

### 6. **Payroll Calculation**
```
Only includes: OT with status = "hr_approved"
Formula:
  Amount = Hours × Employee_Hourly_Rate × OT_Type_Multiplier
  
Example:
  Hours: 2.0
  Hourly Rate: $15/hour (from Employee table)
  OT Type Multiplier: 1.5x (General OT)
  Amount: 2.0 × $15 × 1.5 = $45
```

---

## ⚠️ Common Issues & Solutions

### Issue: "Employee has no reporting manager assigned"
**Problem**: When submitting OT to Manager, system shows this error
**Solution**:
1. Go to Employees > Edit Employee > Reporting Manager
2. Assign a Manager to the employee
3. Ensure Manager is marked as `is_manager = True`
4. Ensure Manager has a User account

### Issue: Manager Approval Dashboard is empty
**Problem**: Manager sees no pending OT
**Solution**:
1. Verify manager has employee_profile with `is_manager = True`
2. Verify HR Manager submitted OT for this manager's team
3. Check that OTRequest.status = "pending_manager"

### Issue: OT appears after Manager rejects but Employee didn't re-mark
**Problem**: Employee's old draft is still visible
**Solution**: This is expected behavior - employee must re-mark with new data

### Issue: HR Manager sees no manager-approved OT in OT Requests
**Problem**: OT Requests page is empty even though Manager approved
**Solution**:
1. Check OTRequest.status = "manager_approved" (not "manager_rejected")
2. Refresh the page
3. Verify company filter matches the OT's company

---

## 🧪 Testing Checklist

- [ ] Employee can mark OT (creates Draft)
- [ ] HR Manager can submit Draft OT to Manager
- [ ] Manager receives OT in Manager Approval Dashboard
- [ ] Manager can Approve (creates L2 for HR)
- [ ] Manager can Reject (resets OTAttendance to Draft)
- [ ] HR Manager sees Manager-Approved OT in OT Requests
- [ ] HR Manager can Approve (status becomes "hr_approved")
- [ ] HR Manager can Reject (sends back to Manager)
- [ ] Payroll Summary shows only "hr_approved" OT
- [ ] Payroll calculates correct hours and amounts
- [ ] Company isolation works (can't see other company OT)
- [ ] Role-based access is enforced

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  EMPLOYEE (Mark OT)                                              │
│  Status: Draft                                                   │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ↓ HR Manager submits
┌─────────────────────────────────────────────────────────────────┐
│  OTREQUESTL1 MANAGER APPROVAL                                    │
│  Status: pending_manager                                         │
│  OTApproval[L1] → Manager (approver_id)                          │
└───┬─────────────────────────────────────────────────────────────┘
    │
    ├─ APPROVE ──→ Status: manager_approved → Create OTApproval[L2]
    │                                              │
    │                                              ↓
    │                          ┌──────────────────────────────────┐
    │                          │  OTREQUEST L2 HR APPROVAL       │
    │                          │  Status: pending_hr              │
    │                          │  OTApproval[L2] → HR Manager     │
    │                          └──┬───────────────────────────────┘
    │                             │
    │                             ├─ APPROVE → Status: hr_approved → PAYROLL ✓
    │                             │
    │                             └─ REJECT → Status: hr_rejected
    │                                              │
    │                                              ↓
    │                                   Reset OTApproval[L1]
    │                                   to pending_manager
    │
    └─ REJECT ──→ Status: manager_rejected
                        │
                        ↓ Reset Employee OT
               OTAttendance: Draft
                        │
                        ↓ Employee re-marks
                   Back to START
```

---

## 📞 Support & Questions

For issues or questions about the two-tier approval workflow:
1. Check the "Common Issues" section above
2. Verify employee has manager_id assigned
3. Check Manager has `is_manager = True` and User account
4. Verify company_id matches for all records
5. Check OTRequest and OTApproval status values

---

## Version Information
- **Implemented**: Two-Tier Approval Workflow
- **Date**: January 2024
- **Status**: ✅ PRODUCTION READY