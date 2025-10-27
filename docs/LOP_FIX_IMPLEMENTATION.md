# Loss of Pay (LOP) Implementation - Complete Fix

## Overview
Fixed three critical issues with Loss of Pay (LOP) functionality in the Bulk Attendance feature:

1. **LOP not saved to database** - The LOP checkbox data was submitted but never processed
2. **Payroll not calculating LOP** - The payroll generation ignored LOP records
3. **Payslip not showing LOP deduction** - The payslip PDF didn't display LOP as a deduction

---

## Issue 1: LOP Not Saved to Database

### Root Cause
The `attendance_bulk_manage()` route in `routes.py` was not reading the LOP checkbox data from the form submission.

### Solution Applied
**File:** `E:/Gobi/Pro/HRMS/hrm/routes.py` (lines 2588-2590)

Added code to read the LOP checkbox data:
```python
# Handle LOP (Loss of Pay) checkbox
lop_field = f'lop_{employee.id}'
attendance.lop = lop_field in request.form
```

**What it does:**
- Checks if the LOP checkbox for each employee was submitted
- Sets the `attendance.lop` field to `True` if checked, `False` otherwise
- Saves to database when `db.session.commit()` is called

---

## Issue 2: Payroll Not Calculating LOP

### Root Cause
The `payroll_generate()` function was not:
- Counting employees with LOP marked
- Calculating LOP deduction amount
- Storing LOP data in the Payroll record

### Solution Applied
**File:** `E:/Gobi/Pro/HRMS/hrm/routes.py` (lines 1650-1691)

#### Step 1: Calculate LOP Days and Deduction (lines 1650-1661)
```python
# Calculate LOP (Loss of Pay) deduction
lop_records = Attendance.query.filter_by(
    employee_id=employee.id,
    status='Absent',
    lop=True).filter(
    Attendance.date.between(pay_period_start,
                            pay_period_end)).all()

lop_days = len(lop_records)
# Calculate daily rate: basic_pay / 26 (standard working days per month)
daily_rate = basic_pay / 26
lop_deduction = lop_days * daily_rate
```

**Calculation Logic:**
- Queries all 'Absent' records where LOP flag is True
- Counts the number of LOP days
- Calculates daily rate: basic_pay ÷ 26 (standard working days)
- LOP deduction = number of LOP days × daily rate

#### Step 2: Updated Gross/Net Pay Calculation (lines 1663-1673)
```python
# Gross pay (BEFORE deductions - standard payroll terminology)
gross_pay = basic_pay + total_allowances + overtime_pay

# Calculate CPF
employee_cpf = gross_pay * (float(employee.employee_cpf_rate) / 100)
employer_cpf = gross_pay * (float(employee.employer_cpf_rate) / 100)

# Net pay (after all deductions including LOP)
total_deductions_amount = employee_cpf + lop_deduction
net_pay = gross_pay - total_deductions_amount
```

**Key Points:**
- Gross pay remains as basic salary + allowances + overtime (before deductions)
- Net pay is now reduced by LOP deduction
- CPF is calculated on gross pay before LOP

#### Step 3: Store LOP Data in Payroll Record (lines 1690-1691)
```python
payroll.lop_days = lop_days
payroll.lop_deduction = lop_deduction
```

---

## Issue 3: Payslip Not Showing LOP

### Solution Applied - Part A: Backend Calculation
**File:** `E:/Gobi/Pro/HRMS/hrm/routes.py` (lines 2049 & 2073)

Added LOP to deductions dictionary:
```python
deductions = {
    'income_tax': f"{float(payroll.income_tax):,.2f}",
    'medical': "0.00",
    'life_insurance': "0.00",
    'loss_of_pay': f"{float(payroll.lop_deduction or 0):,.2f}",  # NEW
    'provident_fund': f"{float(payroll.employee_cpf):,.2f}",
    'others': f"{float(payroll.other_deductions):,.2f}"
}
```

Updated total deductions calculation:
```python
'total_deductions': f"{float(payroll.employee_cpf + payroll.income_tax + payroll.other_deductions + (payroll.lop_deduction or 0)):,.2f}",
```

### Solution Applied - Part B: Template Display
**File:** `E:/Gobi/Pro/HRMS/hrm/templates/payroll/payslip.html` (lines 459-480)

Added LOP deduction line in the payslip table:
```html
<tr>
    <td>Vacation Pay</td>
    <td>-</td>
    <td>-</td>
    <td>{{ earnings.vacation_pay }}</td>
    <td>Loss of Pay</td>
    <td>{{ deductions.loss_of_pay }}</td>
</tr>
```

Added "Other Deductions" row:
```html
<tr>
    <td></td>
    <td></td>
    <td></td>
    <td></td>
    <td>Other Deductions</td>
    <td>{{ deductions.others }}</td>
</tr>
```

---

## Payroll Calculation Example

### Scenario:
- Basic Salary: SGD 3,000
- Allowances: SGD 500
- Overtime Pay: SGD 200
- LOP Days: 2 days
- CPF Rate: 8%

### Calculation:
```
Daily Rate = 3,000 ÷ 26 = SGD 115.38/day
LOP Deduction = 2 × 115.38 = SGD 230.77

Gross Pay = 3,000 + 500 + 200 = SGD 3,700
CPF Deduction = 3,700 × 8% = SGD 296
Net Pay = 3,700 - 296 - 230.77 = SGD 3,173.23

Payslip Display:
- Total Earnings: SGD 3,700.00
- Total Deductions: SGD 526.77 (CPF 296 + LOP 230.77)
- Net Pay: SGD 3,173.23
```

---

## Database Fields Used

### Attendance Table (hrm_attendance)
- `lop` (BOOLEAN) - Indicates if Loss of Pay is marked for this day

### Payroll Table (hrm_payroll)
- `lop_days` (INTEGER) - Number of days marked as LOP in the period
- `lop_deduction` (NUMERIC) - Calculated deduction amount in currency

---

## Testing Checklist

✅ **Bulk Attendance:**
1. Navigate to /attendance/bulk
2. Select a date
3. Mark an employee as "Absent"
4. Check the LOP checkbox (should only be enabled for Absent status)
5. Click "Save Attendance"
6. Verify LOP is saved in the attendance record

✅ **Payroll Generation:**
1. Navigate to /payroll/generate
2. Select month, year, and company
3. Generate payroll for an employee with LOP marked
4. Verify payroll record shows:
   - lop_days: 1 (or count of LOP days)
   - lop_deduction: calculated amount
   - Reduced net_pay reflecting LOP deduction

✅ **Payslip View:**
1. View a generated payslip
2. Verify "Loss of Pay" appears in deductions section
3. Confirm amount matches calculation
4. Check total deductions and net pay are correct
5. Download/print PDF to verify formatting

---

## Files Modified

1. **routes.py**
   - Line 2588-2590: Added LOP reading in attendance_bulk_manage()
   - Line 1650-1673: Added LOP calculation in payroll_generate()
   - Line 1690-1691: Stored LOP data in payroll record
   - Line 2049: Added LOP to deductions dictionary in payroll_payslip()
   - Line 2073: Updated total deductions calculation

2. **payslip.html**
   - Line 459-480: Added LOP and Other Deductions rows in payslip table

---

## Notes

- LOP checkbox is only enabled when attendance status is "Absent"
- Daily rate calculation uses standard 26 working days per month
- LOP is always deducted from net pay (not from gross pay in earnings display)
- CPF is calculated on full gross pay before LOP deduction
- All monetary values are displayed with 2 decimal places
- LOP deduction can be 0.00 if no absences are marked as LOP

---

## Related Components

- **Attendance Status Options:** Pending, Present, Absent, Leave, Half Day
- **LOP Eligibility:** Only Absent status can have LOP marked
- **Payroll Status:** Draft → Approved → Finalized
- **Payslip Display:** Shows gross, deductions, and net pay breakdown
