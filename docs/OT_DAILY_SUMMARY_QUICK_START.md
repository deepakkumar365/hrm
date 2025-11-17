# OT Daily Summary - Quick Start Guide

## What's New? 🎉

**OT records are now AUTOMATICALLY added to the Payroll Summary Grid when a Manager approves them!**

No more manual "Add New" button - the system does it for you.

---

## 5-Minute Workflow

### Step 1: Employee Creates OT
- Employee goes to: **OT Management → Mark OT Attendance**
- Enters OT date, hours, and reason
- Submits for manager approval

### Step 2: Manager Approves (AUTO-MAGIC HAPPENS HERE ✨)
- Manager goes to: **OT Management → Manager Approval**
- Reviews the OT request
- Clicks **APPROVE**
- **✅ System automatically creates OT record in Payroll Summary Grid**

### Step 3: HR Manager Updates Allowances
1. HR Manager logs in
2. Goes to: **OT Management → Payroll Summary (Grid)**
3. Selects **date** using "Filter by Date" selector
4. **SEES** all approved OT records for that date with hours pre-filled
5. **ENTERS values** for 12 allowance columns:
   - KD & CLAIM
   - TRIPS
   - SINPOST
   - SANDSTONE
   - SPX
   - PSLE
   - MANPOWER
   - STACKING
   - DISPOSE
   - NIGHT
   - PH
   - SUN
6. **Totals auto-calculate** as you type
7. **CLICKS SAVE** on the row

### Step 4: Done! 🎉
- OT data is ready for payroll processing
- All 12 allowances are captured
- Grand total calculated automatically

---

## What You'll See

### Payroll Summary Grid Now Shows:

| Employee | OT Hours | OT Rate | OT Amount | KD & Claim | Trips | ... | 12 Fields | Total Allow | Grand Total | Save |
|----------|----------|---------|-----------|------------|-------|-----|-----------|-------------|-------------|------|
| AKSL093  | 5.00     | 25.00   | 125.00    | [Input]    | [In]  | ... | [Input]   | Auto ↓      | Auto ↓      | [✓]  |

---

## Key Points

✅ **Automatic**: No manual "Add New" needed  
✅ **Pre-filled**: OT hours and amount already there  
✅ **Editable**: All 12 allowance fields ready for input  
✅ **Smart Totals**: Total allowances and grand total calculate automatically  
✅ **Audit Trail**: All changes tracked with user and timestamp  

---

## Important Prerequisites

### 1. Employee Hourly Rate Must Be Set

Before manager can approve OT, ensure the employee has an hourly rate:

**Option A: Payroll Configuration** (Recommended)
1. Go to: **Masters → Payroll Configuration**
2. Find employee AKSL093
3. Set **"OT Rate per Hour"** (e.g., 25.00)
4. Save

**Option B: Employee Profile**
1. Go to: **Employees → Edit → [Employee Name]**
2. Set **"Hourly Rate"** (e.g., 25.00)
3. Save

If neither is set → OT Amount will show **0.00**

### 2. User Roles

| Action | Required Role |
|--------|---------------|
| Mark OT | Any employee (except Super Admin) |
| Approve OT (Manager Level) | Manager, HR Manager, Tenant Admin, Super Admin |
| Update Allowances (HR Grid) | HR Manager, Tenant Admin, Super Admin |

---

## Troubleshooting

### Q: OT doesn't appear in grid after manager approves?

**A: Check these:**
1. **Date filter** - Is it set to the same date as the OT?
2. **Status** - Approved OTs should have status = "Draft"
3. **Company** - Are you and the employee in the same company?
4. **OT Rate** - Does the employee have an hourly rate? If 0, amount will be 0

### Q: OT Amount shows 0.00?

**A: Set the employee's hourly rate:**
1. Go to: **Masters → Payroll Configuration**
2. Find the employee
3. Set **"OT Rate per Hour"** to correct amount (e.g., 25.00)
4. Manager re-approves the OT
5. OT amount will recalculate

### Q: Can't edit the allowance fields?

**A: Check OTDailySummary status:**
- Only "Draft" records are editable
- If "Rejected" → Manager needs to re-approve
- If "Finalized" → Can't edit (it's locked)

### Q: Where do I see the final OT totals?

**A: Multiple places:**
- **Payroll Summary (Grid)** - Daily view with editable allowances
- **Payroll Summary (List View)** - All OT records in list format
- **OT Payroll Summary** - Only HR-Approved OTs ready for payroll processing

---

## Common Scenarios

### Scenario 1: Manager Modifies Hours After Approval

**What happens:**
1. Manager approves OT with 5 hours
2. OTDailySummary created with 5 hours and amount = 5 × 25 = 125
3. Later, Manager reviews in HR Approval Dashboard
4. Manager changes hours to 6 hours
5. **✅ System auto-updates OTDailySummary to 6 hours and amount = 150**

### Scenario 2: HR Manager Rejects OT

**What happens:**
1. OTDailySummary status changes to "Rejected"
2. Record hidden from Payroll Summary Grid
3. OT goes back to Manager for review
4. Manager re-approves → New OTDailySummary created
5. HR Manager can update allowances again

### Scenario 3: Multiple OTs for Same Employee on Same Day

**What happens:**
- Each OT is separate row in the grid
- If you try to add second OT for same employee/date
- System updates the existing row (one row per employee per day)

---

## Data Flow

```
Employee marks OT
         ↓
Employee submits for approval
         ↓
Manager reviews & approves
         ↓
✅ OTDailySummary AUTO-CREATED
         ↓
HR Manager filters date
         ↓
HR Manager SEES OT in grid with hours pre-filled
         ↓
HR Manager enters allowance values
         ↓
HR Manager clicks SAVE
         ↓
OTDailySummary UPDATED with all 12 allowances
         ↓
Ready for payroll processing!
```

---

## Database Table Reference

### OTDailySummary Table Structure

```sql
-- Primary Key & Foreign Keys
id (Primary Key)
employee_id (FK → Employee)
company_id (FK → Company)
ot_request_id (FK → OTRequest) ← NEW: Now auto-populated

-- OT Information
ot_date (Date)
ot_hours (Numeric) ← Auto-filled from manager approval
ot_rate_per_hour (Numeric) ← Auto-filled from employee config
ot_amount (Numeric) ← Auto-calculated

-- 12 Allowance Fields (filled by HR Manager)
kd_and_claim, trips, sinpost, sandstone, spx, psle,
manpower, stacking, dispose, night, ph, sun

-- Totals (Auto-calculated)
total_allowances ← Sum of all 12 fields
total_amount ← ot_amount + total_allowances

-- Status & Audit
status (Draft, Submitted, Approved, Rejected, Finalized)
created_by, created_at
modified_by, modified_at
finalized_by, finalized_at
```

---

## Pro Tips 💡

1. **Batch Processing**: Have all employees submit OT → Manager approves all → HR Manager updates all on same date
2. **Standard Allowances**: If most employees get same allowance amounts, use Copy feature in grid
3. **Hourly Rate Strategy**: 
   - Set standard OT rate in Payroll Configuration for all employees
   - Override only for special cases (managers, contractors, etc.)
4. **Export**: Download final grid as Excel for record-keeping
5. **Approvals**: You can approve the OT later in HR Approval Dashboard if needed

---

## Files Modified

- **routes_ot.py** - Added auto-creation logic for OTDailySummary
- **models.py** - OTDailySummary model (no changes needed)

## New Documentation

- `OT_DAILY_SUMMARY_AUTO_CREATION.md` - Detailed technical documentation
- `OT_DAILY_SUMMARY_QUICK_START.md` - This file

---

## Need Help?

| Issue | File | Line |
|-------|------|------|
| How does auto-creation work? | routes_ot.py | 663-717 |
| How do HR Manager updates work? | routes_ot.py | 1056-1181 |
| What happens on rejection? | routes_ot.py | 884-891 |
| How is data filtered? | routes_ot.py | 1103-1104 |

---

**That's it! Your OT workflow is now seamlessly integrated.** 🚀