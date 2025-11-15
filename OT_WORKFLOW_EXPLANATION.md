# OT (Overtime) Management Workflow Explanation

## Current System Architecture

There are **4 main tables** in the OT system:

1. **OTType** - Configuration (Regular OT, Weekend OT, Holiday OT, etc.)
2. **OTAttendance** - Employee marks their OT entry (with date, hours, type)
3. **OTRequest** - Formal OT approval request (currently NOT USED in routes)
4. **OTApproval** - Approval records and history

---

## Complete OT Workflow Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 1: EMPLOYEE MARKS OT ATTENDANCE                           │
│  ─────────────────────────────────────────                       │
│  Menu: Attendance > Mark OT Attendance                           │
│  ✓ Select Date, OT Type, Hours/Time                             │
│  ✓ Add Notes                                                     │
│  ✓ Saves to: hrm_ot_attendance table                           │
│  Status: "Draft"                                                 │
│                                                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 2: HR MANAGER SUBMITS FOR APPROVAL (MISSING IN CURRENT)   │
│  ─────────────────────────────────────────────────────────────   │
│  Menu: OT Management > OT Attendance                             │
│  ✗ NO SUBMIT BUTTON - THIS FUNCTIONALITY IS MISSING!            │
│  ✗ Need to click "Submit for Approval" to convert to OTRequest  │
│  ✗ This should create OTApproval records                        │
│                                                                   │
│  What SHOULD happen:                                             │
│  • Convert OTAttendance (Draft) → OTRequest + OTApproval        │
│  • Update OTAttendance.status = "Submitted"                      │
│  • Create OTApproval record with status = "pending"              │
│                                                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 3: MANAGER/ADMIN REVIEWS OT REQUEST                       │
│  ─────────────────────────────────────────                       │
│  Menu: OT Management > OT Requests                               │
│  • View pending OT requests (from OTApproval table)              │
│  • Filter by status: Pending, Approved, Rejected                │
│  • Shows employee name, date, requested hours                   │
│  ✗ CURRENTLY EMPTY (no OTApproval records exist)                │
│                                                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 4: MANAGER APPROVES/REJECTS VIA APPROVAL DASHBOARD        │
│  ─────────────────────────────────────────────────────────────  │
│  Menu: OT Management > Approval Dashboard                        │
│  ✓ See pending OT approvals                                     │
│  ✓ Click "Approve", "Reject", or "Modify Hours"                 │
│  ✓ Add comments/reason                                          │
│  ✓ Updates OTApproval.status & notifies employee                │
│  ✗ CURRENTLY EMPTY (no OTApproval records exist)                │
│                                                                   │
│  Possible Actions:                                               │
│  • ✓ Approve: OTApproval.status = "approved"                   │
│  • ✗ Reject: OTApproval.status = "rejected"                    │
│  • ⚠ Modify: Adjust approved hours if needed                    │
│                                                                   │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                   │
│  STEP 5: CALCULATE & VIEW OT PAYROLL SUMMARY                    │
│  ─────────────────────────────────────────                       │
│  Menu: OT Management > OT Payroll Summary                        │
│  ✓ View approved OT by employee                                 │
│  ✓ Group by OT Type (with rate multipliers)                     │
│  ✓ Calculate OT salary = approved_hours × hourly_rate × rate    │
│  ✗ CURRENTLY EMPTY (no OTApproval records)                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why You See Empty Data

**OT Requests, Approval Dashboard, and OT Payroll Summary are all EMPTY because:**

❌ **Missing Link:** There's NO route/functionality to convert `OTAttendance (Draft)` → `OTApproval (Pending)`

**Current State:**
- ✅ OTAttendance records are being created
- ❌ OTApproval records are NOT being created
- ❌ No link between the two

**What's Missing:**
- No "Submit for Approval" button in OT Attendance page
- No code to create OTApproval records from OTAttendance

---

## How to See Data (Current Workaround)

Until the "Submit for Approval" feature is implemented, you can:

### Option A: Directly Create Test OTApproval Records (Database)
```sql
-- Create test OTApproval record
INSERT INTO hrm_ot_approval (ot_request_id, approver_id, status, comments)
VALUES (1, 1, 'pending', 'Test approval');
```

### Option B: Use OT Attendance Only
- ✅ Mark OT: Works (creates OTAttendance records)
- ✅ View OT Attendance: Works (see all marked OTs)
- ❌ Approval workflow: Not implemented yet

---

## Data Access Bug (Additional Issue)

**Found Issue in routes_ot.py:**

Lines 183, 209, 248, 265, 316, 356 use:
```python
current_user.company_id  # ❌ This doesn't exist!
```

**Should be:**
```python
current_user.employee_profile.company_id  # ✅ Correct path
```

This is why HR Managers can't see employee lists in the filters!

---

## Summary: What's Working vs What's Missing

| Feature | Status | Issue |
|---------|--------|-------|
| OT Types Management | ✅ Fixed | Company access fixed |
| Mark OT Attendance | ✅ Works | Employees can mark |
| View OT Attendance | ⚠️ Partial | Uses wrong company_id path |
| OT Requests | ❌ Empty | No OTApproval records created |
| Approval Dashboard | ❌ Empty | No OTApproval records |
| OT Payroll Summary | ❌ Empty | No OTApproval records |

---

## Next Steps (Recommendations)

1. **Immediate (Fix Bugs):**
   - Fix all `current_user.company_id` → `current_user.employee_profile.company_id`
   - This is blocking HR Managers from filtering data

2. **Short-term (Implement Missing Workflow):**
   - Add "Submit for Approval" button in OT Attendance page
   - Create route to convert OTAttendance → OTApproval
   - This will populate the Requests & Approval Dashboard

3. **Integration:**
   - Link approved OT to payroll system for salary calculation
   - Add notifications for approvers
   - Add reports for OT trends by employee/department
