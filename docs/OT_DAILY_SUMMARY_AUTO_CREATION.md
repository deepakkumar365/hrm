# OT Daily Summary Auto-Creation Feature

## Overview
When a **Manager approves an OT request**, the system now **automatically creates an OTDailySummary record** in the Payroll Summary Grid. This allows HR Managers to immediately see and manage the 12 allowance fields for approved OT records.

---

## Feature Details

### What Changed
Previously, the OT workflow and the Payroll Summary Grid were disconnected:
- **OT Approval**: Employee → Manager → HR Manager (just for approval)
- **Payroll Grid**: HR Manager had to manually add employees using "Add New" button

Now they are **integrated**:
- When a Manager approves an OT → **Automatically added to Payroll Summary Grid**
- HR Manager can immediately see all approved OT records with hours pre-filled
- HR Manager then fills in the 12 allowance fields and saves

### Complete New Workflow

```
1. Employee marks OT (AKSL093)
   └─ Status: Draft

2. Employee submits for Manager approval
   └─ OTRequest created
   └─ OTApproval Level 1 created (pending_manager)

3. Manager (AKSL092) APPROVES
   ├─ OTApproval Level 1 → "manager_approved"
   ├─ OTApproval Level 2 created (pending_hr)
   └─ ✅ OTDailySummary AUTO-CREATED
       ├─ ot_hours: Pre-filled from approved hours
       ├─ ot_amount: Auto-calculated (hours × rate)
       ├─ All 12 allowances: 0 (ready to edit)
       └─ Status: Draft

4. HR Manager logs in
   ├─ Goes to: OT Management > Payroll Summary (Grid)
   ├─ Filters by date (today or any date)
   └─ SEES: AKSL093 row with OT info

5. HR Manager UPDATES ALLOWANCES
   ├─ Enters values for 12 allowance fields:
   │  ├─ KD & CLAIM
   │  ├─ TRIPS
   │  ├─ SINPOST
   │  ├─ SANDSTONE
   │  ├─ SPX
   │  ├─ PSLE
   │  ├─ MANPOWER
   │  ├─ STACKING
   │  ├─ DISPOSE
   │  ├─ NIGHT
   │  ├─ PH
   │  └─ SUN
   ├─ Total Allowances auto-calculates
   ├─ Grand Total auto-calculates
   └─ Clicks SAVE

6. HR Manager MAY ALSO approve OT in HR Approval Dashboard
   └─ If modified hours, OTDailySummary updates accordingly
```

---

## How It Works

### 1. Automatic OTDailySummary Creation (When Manager Approves)

**File**: `routes_ot.py` - Lines 663-717

When a Manager approves an OT request:
```python
# Get employee and their OT rate
employee = Employee.query.get(ot_request.employee_id)

# Get OT rate from PayrollConfiguration
ot_rate = employee.payroll_config.ot_rate_per_hour or employee.hourly_rate

# Calculate OT amount
approved_hours = ot_request.approved_hours or ot_request.requested_hours
ot_amount = approved_hours × ot_rate

# Create or update OTDailySummary
ot_summary = OTDailySummary(
    employee_id=ot_request.employee_id,
    company_id=ot_request.company_id,
    ot_request_id=ot_request.id,  # Link back to OT request
    ot_date=ot_request.ot_date,
    ot_hours=approved_hours,
    ot_rate_per_hour=ot_rate,
    ot_amount=ot_amount,
    status='Draft',  # Ready for HR Manager
    created_by=current_user.username
)
```

### 2. OT Rate Calculation Priority

The system uses this priority for OT rate:
1. **PayrollConfiguration.ot_rate_per_hour** (if set for employee)
2. **Employee.hourly_rate** (fallback)
3. **0** (if neither is set)

**⚠️ Important**: Ensure your employees have their hourly rates configured in **Payroll Configuration**.

### 3. HR Manager Updates Allowances

In the **Payroll Summary Grid** (`/ot/daily-summary`):
- HR Manager filters by date
- Sees all Draft OT records for that date
- Edits the 12 allowance fields (all numeric inputs)
- Clicks SAVE to update each row
- Totals calculate automatically

**Data Saved in OTDailySummary**:
```
- kd_and_claim
- trips
- sinpost
- sandstone
- spx
- psle
- manpower
- stacking
- dispose
- night
- ph
- sun
- total_allowances (sum of all 12)
- total_amount (ot_amount + total_allowances)
```

### 4. HR Manager Approval with Hour Modifications

**File**: `routes_ot.py` - Lines 856-864

If HR Manager modifies the OT hours in the approval dashboard:
```python
# If modified hours provided
if modified_hours:
    # Update OTDailySummary hours and amount
    ot_summary.ot_hours = modified_hours
    ot_summary.ot_amount = modified_hours × ot_rate
    ot_summary.modified_by = current_user.username
    ot_summary.modified_at = datetime.now()
```

### 5. HR Manager Rejection

**File**: `routes_ot.py` - Lines 884-891

If HR Manager rejects an OT:
```python
# Mark OTDailySummary as Rejected (keep audit trail)
ot_summary.status = 'Rejected'
ot_summary.notes = f'Rejected by HR Manager: {comments}'
```

The Payroll Summary Grid will then hide rejected records (only shows Draft/Submitted).

---

## Data Flow Diagram

```
OTAttendance (Draft)
       ↓
   Employee submits
       ↓
OTRequest (pending_manager) + OTApproval L1
       ↓
Manager APPROVES
       ↓
OTApproval L1 (manager_approved) + OTApproval L2 (pending_hr)
       ↓
    ✅ OTDailySummary CREATED ← (AUTO)
       ├─ ot_hours ✓
       ├─ ot_amount ✓
       ├─ all allowances = 0
       └─ status = Draft
       ↓
HR Manager Views Grid
       ↓
HR Manager EDITS 12 Allowances
       ↓
HR Manager SAVES
       ↓
OTDailySummary UPDATED
       ├─ kd_and_claim ✓
       ├─ trips ✓
       ├─ ... (all 12 fields)
       ├─ total_allowances ✓
       └─ total_amount ✓
       ↓
(Optional) HR Manager APPROVES in dashboard
       ↓
OTRequest (hr_approved)
```

---

## Usage Instructions

### Step 1: Ensure Employees Have Hourly Rates

Go to **Masters → Payroll Configuration** and set the **OT Rate per Hour** for each employee.

If not set, the system will use the employee's hourly rate from their Employee Profile.

### Step 2: Manager Approves OT

1. Employee marks OT
2. Employee submits for approval
3. Manager goes to **OT Management → Manager Approval**
4. Manager clicks **APPROVE**
   - ✅ Automatically creates OTDailySummary record
   - ✅ OT hours and amount pre-filled
   - ✅ Ready for HR Manager

### Step 3: HR Manager Updates Allowances

1. HR Manager logs in
2. Goes to **OT Management → Payroll Summary (Grid)**
3. Selects **date** from "Filter by Date" picker
4. **Sees** all approved OT records for that date
   - Employee name
   - OT Hours (pre-filled)
   - OT Amount (pre-calculated)
   - Empty 12 allowance fields
5. **Enters values** for each allowance column
   - Totals update automatically
6. **Clicks SAVE** on each row
   - Values are persisted to database

### Step 4: Review & Export (Optional)

HR Manager can then:
- Go to **Payroll Summary (List View)** to see all records
- Go to **OT Payroll Summary** to see HR-approved records
- Export data for payroll processing

---

## Database Changes

### OTDailySummary Model

The model already has all required fields:

```python
class OTDailySummary(db.Model):
    # Core fields
    employee_id → Link to Employee
    company_id → Link to Company
    ot_request_id → Link to OTRequest (NEW: Now populated)
    
    # OT Information
    ot_date → Date of OT
    ot_hours → Hours (auto-filled from manager approval)
    ot_rate_per_hour → Rate (auto-filled from PayrollConfiguration)
    ot_amount → Calculated (auto-filled from manager approval)
    
    # 12 Allowance Fields (to be filled by HR Manager)
    kd_and_claim, trips, sinpost, sandstone, spx, psle,
    manpower, stacking, dispose, night, ph, sun
    
    # Totals (auto-calculated)
    total_allowances → Sum of all 12 fields
    total_amount → ot_amount + total_allowances
    
    # Status & Audit
    status → Draft, Submitted, Approved, Rejected, Finalized
    created_by, created_at
    modified_by, modified_at
    finalized_by, finalized_at
```

### Table Index

```sql
-- Unique constraint on (employee_id, ot_date)
-- This prevents duplicate entries for same employee on same date
UNIQUE CONSTRAINT (employee_id, ot_date)
```

---

## Features & Benefits

✅ **Automatic Integration**: No manual "Add New" required for approved OTs  
✅ **Data Integrity**: OT hours & rates auto-populated, less manual entry  
✅ **Real-time Totals**: 12 allowance fields calculate totals instantly  
✅ **Audit Trail**: All changes tracked (created_by, modified_by, timestamps)  
✅ **Rejection Handling**: Rejected OTs marked as "Rejected", hidden from grid  
✅ **Multi-tenant**: Company-level access control enforced  
✅ **Hour Modifications**: HR Manager can modify hours, OTDailySummary updates automatically  

---

## Troubleshooting

### OT Not Appearing in Grid

**Issue**: Approved OT doesn't appear in Payroll Summary Grid

**Causes & Solutions**:

1. **Wrong Status**
   - Check that OTDailySummary.status = 'Draft' or 'Submitted'
   - Rejected records won't show

2. **Wrong Date**
   - Ensure grid filter matches OT date
   - Filter by correct date using "Filter by Date" picker

3. **Wrong Company**
   - If HR Manager is from Company A, can only see Company A's OTs
   - Verify employee is assigned to same company as HR Manager

4. **Missing OT Rate**
   - Ensure employee has OT rate in PayrollConfiguration
   - Or set employee's hourly_rate in Employee Profile
   - If both missing, OT amount will be 0

5. **Database Issues**
   - Run: `python create_ot_daily_summary_table.py`
   - This recreates the table if needed

### OT Amount Shows 0.00

**Cause**: OT rate is 0 or not configured

**Solution**:
1. Go to **Masters → Payroll Configuration**
2. Find the employee
3. Set **OT Rate per Hour** to correct value
4. Manager re-approves the OT
5. OTDailySummary will update with correct amount

### Can't Edit Allowance Fields

**Cause**: OTDailySummary status is not 'Draft' or 'Submitted'

**Solution**:
1. Check OTDailySummary.status
2. If 'Rejected', it was rejected by HR Manager
3. Have manager re-approve the OT to create new record

---

## Backend Changes Summary

### Modified Files

**routes_ot.py**
- Lines 663-717: Added auto-creation of OTDailySummary when manager approves
- Lines 856-864: Added update of OTDailySummary when HR Manager modifies hours
- Lines 884-891: Added status change to 'Rejected' when HR Manager rejects
- Lines 1103-1104: Added filter to exclude rejected records from daily summary grid

### New Code Logic

1. **Manager Approval Handler** (Line 663)
   - When status = 'approve'
   - Get employee's OT rate
   - Calculate OT amount
   - Check for existing OTDailySummary
   - Create new or update existing
   - Log all actions

2. **HR Approval Handler with Hour Modifications** (Line 856)
   - When modified_hours provided
   - Update OTDailySummary.ot_hours
   - Recalculate ot_amount
   - Update timestamps

3. **HR Rejection Handler** (Line 884)
   - When status = 'reject'
   - Mark OTDailySummary as 'Rejected'
   - Add HR Manager's comments
   - Keep record for audit trail

4. **Grid Query Filter** (Line 1104)
   - Only show records with status in ['Draft', 'Submitted']
   - Hide rejected records
   - Improves UX by showing only active records

---

## Configuration Requirements

### Required for This Feature to Work

1. ✅ **Employee has hourly_rate or PayrollConfiguration.ot_rate_per_hour**
   - Location: Masters → Payroll Configuration
   - Or: Employees → Edit → Hourly Rate

2. ✅ **Manager has access to /ot/manager-approval route**
   - Role: Manager, HR Manager, Tenant Admin, or Super Admin

3. ✅ **HR Manager has access to /ot/daily-summary route**
   - Role: HR Manager, Tenant Admin, or Super Admin

4. ✅ **OTDailySummary table exists**
   - Created automatically on first use
   - Or run: `python create_ot_daily_summary_table.py`

---

## Testing Checklist

- [ ] Employee creates OT for Date X
- [ ] Employee submits for approval
- [ ] Manager views approval dashboard
- [ ] Manager APPROVES OT
- [ ] Check database: OTDailySummary record created?
  - `SELECT * FROM hrm_ot_daily_summary WHERE employee_id=X AND ot_date='Date X'`
- [ ] Verify: ot_hours and ot_amount are populated
- [ ] HR Manager logs in
- [ ] HR Manager goes to OT Management > Payroll Summary (Grid)
- [ ] HR Manager filters by Date X
- [ ] HR Manager SEES employee OT record in grid
- [ ] HR Manager enters allowance values
- [ ] HR Manager clicks SAVE
- [ ] Verify: Record saved in database
- [ ] Verify: Totals calculated correctly

---

## Quick Summary

**Before (Disconnected)**:
1. OT Approval Flow (separate)
2. HR Manager manually adds employees to grid

**After (Integrated)** ✅:
1. Manager approves OT → Automatically appears in grid
2. HR Manager updates allowance fields
3. All OT data flows seamlessly from approval to payroll

**Result**: Faster OT processing, fewer manual steps, reduced errors! 🚀