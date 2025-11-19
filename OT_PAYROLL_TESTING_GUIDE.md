# OT Payroll Sync Fix - Testing Guide

## Quick Test Scenario

### Prerequisites
- At least one employee with `hourly_rate` set in Employee Master
- OT requests that have been **approved** (hr_approved status)
- OT Daily Summary records with allowances entered

---

## Test 1: OT Payroll Summary - Rate/Hour Field

**Path**: OT Management > Payroll Summary

**Steps**:
1. Navigate to OT Management > Payroll Summary
2. Select Month/Year with approved OT requests
3. Look at the summary table

**Expected Results**:
- ✅ Column header shows "Rate/Hour" (not "Avg Rate/Hour")
- ✅ Rate/Hour column displays Employee's actual hourly_rate (e.g., ₹500.00)
- ✅ OT Amount is calculated as: Hours × Rate/Hour (e.g., 10 × 500 = ₹5,000)
- ✅ Currency shows as ₹ (Indian Rupee)

**Example**:
```
OT Type    | Count | Hours  | Rate/Hour | Amount
General    | 2     | 10.00  | ₹500.00   | ₹5,000.00
Weekend    | 1     | 5.00   | ₹750.00   | ₹3,750.00
           |       |        |           |
TOTAL      | 3     | 15.00  | -         | ₹8,750.00
```

---

## Test 2: OT Allowances in Payroll Grid

**Path**: Payroll > Generate Payroll

**Prerequisites for this test**:
1. Create/Approve OT requests in OT Management
2. HR Manager enters OT Daily Summary for those OT dates
   - Navigate to: OT > Daily Summary
   - For each approved OT date, click "Allowances" button
   - Enter values for: KD & CLAIM, TRIPS, SINPOST, etc.
   - Save changes

**Steps**:
1. Navigate to Payroll > Generate Payroll
2. Select Company, Month (same month as OT Daily Summary), Year
3. Click "Load Data"
4. Look at the "Allow" column in the table

**Expected Results**:
- ✅ "Allow" column shows total allowances (config + OT combined)
- ✅ For employees with OT allowances: value should be **higher** than before
- ✅ Formula example:
  - Config Allowances (Transport+Housing+Meal+Other+Levy) = $100
  - OT Allowances (KD & CLAIM, TRIPS, etc.) = $150
  - Total Shown in Allow column = $250

**Example Before Fix**:
```
Employee | Allow (Old)
John     | $100        ← Missing OT allowances
Mary     | $100        ← Missing OT allowances
```

**Example After Fix**:
```
Employee | Allow (New)
John     | $250        ← Config ($100) + OT ($150) ✓
Mary     | $100        ← Config only (no OT allowances)
```

---

## Test 3: Payroll Generation with OT Allowances

**Path**: Payroll > Generate Payroll

**Steps**:
1. Load employee data (as in Test 2)
2. Select employees with OT allowances
3. Click "Generate Payslips"
4. Go to Payroll > Payroll List
5. View the generated payroll record

**Expected Results**:
- ✅ Payroll record created successfully
- ✅ Allowances field includes both config and OT allowances
- ✅ Gross Pay = Basic + Allowances (both types) + OT Amount
- ✅ Net Pay calculated correctly with combined allowances

---

## Test 4: API Response Validation

**Technical Test** (for developers):

**Endpoint**: `/api/payroll/preview?company_id=<id>&month=<m>&year=<y>`

**Steps**:
1. Open Browser DevTools > Network tab
2. Load Payroll > Generate Payroll page
3. Select company/month/year and click "Load Data"
4. In Network tab, find the API call to `/api/payroll/preview`
5. Click on it and check Response JSON

**Expected in Response**:
```json
{
  "success": true,
  "employees": [
    {
      "id": 1,
      "name": "John Doe",
      "basic_salary": 1000,
      "config_allowances": 100,
      "ot_allowances": 150,
      "total_allowances": 250,
      "ot_amount": 500,
      "gross_salary": 1750,
      "net_salary": 1400
    }
  ]
}
```

**Verify**:
- ✅ `config_allowances` field present
- ✅ `ot_allowances` field present
- ✅ `total_allowances` = config + ot (250 = 100 + 150)
- ✅ OT Daily Summary data included

---

## Troubleshooting

### Issue: Rate/Hour shows as ₹0.00

**Cause**: Employee doesn't have `hourly_rate` set in Master

**Solution**:
1. Go to Employees > Employee List
2. Edit the employee
3. Set the "Hourly Rate" / "Rate/Hour" field
4. Save
5. Retry

### Issue: OT Allowances column still shows old value

**Cause**: Browser cache not cleared

**Solution**:
1. Press Ctrl+Shift+Delete (Windows) or Cmd+Shift+Delete (Mac)
2. Clear browser cache
3. Reload page
4. Or use Ctrl+F5 to hard refresh

### Issue: Allowances field blank in Payroll grid

**Cause**: Employee has no config allowances AND no OT Daily Summary records

**Solution**:
1. Check if employee has payroll config setup
2. Check if OT Daily Summary exists for that month
3. If yes, check the API response (Test 4 above)

### Issue: OT Amount shows 0

**Cause**: OT Daily Summary records don't have ot_amount populated

**Solution**:
1. Check OT Daily Summary > Daily Summary Grid
2. Make sure OT hours and rate/hr are filled
3. OT Amount should auto-calculate (Hours × Rate)
4. Save the record
5. Reload Payroll page

---

## Data Flow Verification

### Step 1: Verify OT Daily Summary has data
```
Path: OT > Daily Summary
Look for: Records with ot_date in selected month, ot_amount > 0, total_allowances > 0
```

### Step 2: Verify API returns correct data
```
DevTools > Network > /api/payroll/preview
Check: ot_allowances field has correct value
Check: total_allowances = config_allowances + ot_allowances
```

### Step 3: Verify Payroll Grid displays correctly
```
Path: Payroll > Generate Payroll
Check: Allow column = total_allowances from API
Check: OT Amt column = ot_amount from API
```

### Step 4: Verify Payroll record created correctly
```
Path: Payroll > List
Check: allowances field = config_allowances + ot_allowances
Check: Gross = basic + allowances + overtime_pay
```

---

## Regression Testing

Make sure these still work:

- [ ] Payroll generation without any OT allowances works
- [ ] OT Summary shows correct totals
- [ ] Config allowances still editable in Payroll grid
- [ ] Payslip generation works with new allowance data
- [ ] OT approval workflow unaffected
- [ ] Multiple employees with different OT scenarios display correctly

---

## Support

If issues persist:
1. Check the server logs for errors
2. Verify OTDailySummary table has data for the month
3. Ensure Employee.hourly_rate is populated
4. Check that OTApproval status is 'hr_approved'