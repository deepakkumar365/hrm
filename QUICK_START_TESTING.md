# 🚀 Quick Start Testing Guide - HRMS Enhancements

## 📋 Overview

This guide will help you quickly test all the new enhancements implemented for the HRMS Admin Module.

**Total Testing Time:** ~30 minutes  
**Prerequisites:** Application running, database migrated

---

## 🔧 Step 1: Start the Application (5 minutes)

### Option A: Using PowerShell

```powershell
# Navigate to project directory
Set-Location "E:/Gobi/Pro/HRMS/hrm"

# Activate virtual environment (if using venv)
.\venv\Scripts\Activate.ps1

# Run database migrations
flask db upgrade

# Start the application
python main.py
```

### Option B: Using PyCharm

1. Open PyCharm
2. Open project: `E:/Gobi/Pro/HRMS/hrm`
3. Right-click on `main.py`
4. Select "Run 'main'"

### Verify Application Started

**Expected Output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**Open Browser:**
```
http://localhost:5000
```

---

## 👤 Step 2: Login Credentials

Use these credentials for testing:

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Super Admin | `superadmin` | `admin123` | Full access |
| Admin | `admin` | `admin123` | Full access |
| HR Manager | `manager` | `admin123` | Reports only |
| Employee | `user` | `admin123` | Limited access |

---

## ✅ Step 3: Quick Feature Tests (20 minutes)

### Test 1: Password Reset (2 minutes)

1. **Login:** `superadmin` / `admin123`
2. **Navigate:** Admin → Employees
3. **Action:** Click key icon (🔑) for any employee
4. **Verify:** Modal opens with employee name
5. **Action:** Click "Reset Password"
6. **Verify:** Success message with temporary password (e.g., "John123")

**✅ Pass Criteria:** Temporary password displayed, format is `{FirstName}123`

---

### Test 2: Employee ID Generation (2 minutes)

1. **Navigate:** Admin → Employees → Add New
2. **Verify:** "Employee ID" field is first field
3. **Verify:** "Generate" button appears next to field
4. **Action:** Click "Generate" button
5. **Verify:** Employee ID auto-filled (format: `EMPYYYYMMDDHHMMSS`)
6. **Verify:** Success message appears

**✅ Pass Criteria:** Unique Employee ID generated, field is editable

---

### Test 3: Removed Sections (1 minute)

**Employee View:**
1. **Navigate:** Admin → Employees → View (any employee)
2. **Verify:** "Salary & Benefits" section is NOT present

**Employee Form:**
1. **Navigate:** Admin → Employees → Add New
2. **Verify:** "Banking Details" section is NOT present

**✅ Pass Criteria:** Both sections completely removed

---

### Test 4: Reports Menu (3 minutes)

1. **Navigate:** Click "Reports" in top navigation
2. **Verify:** Dropdown shows:
   - All Reports
   - ─────────────
   - Employee History
   - Payroll Configuration
   - Attendance Report

3. **Action:** Click "All Reports"
4. **Verify:** Page shows 3 report cards + placeholder

**✅ Pass Criteria:** Reports menu visible, all links work

---

### Test 5: Employee History Report (2 minutes)

1. **Navigate:** Reports → Employee History
2. **Verify:** Table displays with columns:
   - Employee ID, Name, Email, Department, Role, Join Date, Exit Date, Manager, Status
3. **Verify:** Summary statistics at bottom
4. **Action:** Click "Export CSV"
5. **Verify:** CSV file downloads

**✅ Pass Criteria:** Report displays data, CSV export works

---

### Test 6: Payroll Configuration Report (2 minutes)

1. **Navigate:** Reports → Payroll Configuration
2. **Verify:** Table displays with columns:
   - Employee ID, Name, Basic Salary, Allowances, Employer CPF, Employee CPF, Gross Salary, Net Salary, Remarks
3. **Verify:** Footer row shows totals
4. **Action:** Click "Export CSV"
5. **Verify:** CSV downloads

**✅ Pass Criteria:** Report shows CPF columns, totals calculate correctly

---

### Test 7: Attendance Report with Filters (3 minutes)

1. **Navigate:** Reports → Attendance Report
2. **Verify:** Date filter form displays
3. **Action:** Click "Today" button
4. **Verify:** Start and end dates set to today
5. **Action:** Click "This Week" button
6. **Verify:** Dates set to current week
7. **Action:** Click "This Month" button
8. **Verify:** Dates set to current month
9. **Action:** Click "Filter" button
10. **Verify:** Table displays attendance records
11. **Verify:** Summary statistics show counts

**✅ Pass Criteria:** Quick filters work, data displays correctly

---

### Test 8: Attendance Default Date (1 minute)

1. **Navigate:** Attendance → View Records
2. **Verify:** Date filter is pre-filled with today's date
3. **Verify:** Today's attendance records display

**✅ Pass Criteria:** Date defaults to today automatically

---

### Test 9: Payroll Status Colors (1 minute)

1. **Navigate:** Payroll → Generate Payroll
2. **Verify:** Status badges display with colors:
   - **Approved** = Green with ✓ icon
   - **Paid** = Green with 💵 icon
   - **Pending** = Yellow with 🕐 icon
   - **Draft** = Gray with 📄 icon
3. **Verify:** "Approve" button shows text label (not just icon)

**✅ Pass Criteria:** Colors correct, icons display, caption visible

---

### Test 10: Payroll Configuration - New Columns (2 minutes)

1. **Navigate:** Payroll → Configuration
2. **Verify:** Table shows new columns:
   - Employer CPF
   - Employee CPF
   - Net Salary
   - Remarks
3. **Action:** Click "Edit" for any employee
4. **Verify:** New fields become editable (blue border)
5. **Action:** Enter values:
   - Employer CPF: `500`
   - Employee CPF: `400`
   - Net Salary: `3500`
   - Remarks: `Test`
6. **Action:** Click "Save"
7. **Verify:** Success message appears
8. **Action:** Refresh page
9. **Verify:** Values saved correctly

**✅ Pass Criteria:** New columns display, values save successfully

---

### Test 11: Bank Info Modal (3 minutes)

1. **Navigate:** Payroll → Configuration
2. **Verify:** "Bank Info" button (🏛️ icon) appears in Actions column
3. **Action:** Click "Bank Info" for any employee
4. **Verify:** Modal opens with title showing employee name
5. **Verify:** Form fields present:
   - Bank Account Name (required)
   - Bank Account Number (required)
   - Bank Code (optional)
   - PayNow Number (optional)

6. **Action:** Fill in form:
   - Bank Account Name: `Test User`
   - Bank Account Number: `1234567890`
   - Bank Code: `DBSSSGSG`
   - PayNow Number: `+65 9123 4567`

7. **Action:** Click "Save"
8. **Verify:** Loading spinner appears
9. **Verify:** Success toast notification
10. **Verify:** Modal closes

11. **Action:** Click "Bank Info" again
12. **Verify:** Previously saved data is pre-populated

**✅ Pass Criteria:** Modal works, data saves and loads correctly

---

## 🔐 Step 4: Role-Based Access Test (5 minutes)

### Test as Employee (User Role)

1. **Logout** from Admin account
2. **Login:** `user` / `admin123`
3. **Verify:** Reports menu is NOT visible
4. **Verify:** Cannot access `/reports` URL directly (should redirect or show error)
5. **Navigate:** Admin → Employees (if accessible)
6. **Verify:** Password Reset button is NOT visible

**✅ Pass Criteria:** Employee cannot access admin features

### Test as HR Manager

1. **Logout** from Employee account
2. **Login:** `manager` / `admin123`
3. **Verify:** Reports menu IS visible
4. **Navigate:** Reports → Employee History
5. **Verify:** Can view report
6. **Navigate:** Payroll → Configuration
7. **Verify:** Can view but may have limited edit access

**✅ Pass Criteria:** HR Manager can view reports but has limited admin access

---

## 📊 Step 5: Data Verification (Optional - 5 minutes)

### Check Database Directly

```powershell
# Connect to PostgreSQL
psql -U postgres -d hrms_db

# Check bank info table
SELECT * FROM hrm_employee_bank_info LIMIT 5;

# Check payroll config with new columns
SELECT employee_id, employer_cpf, employee_cpf, net_salary, remarks 
FROM hrm_payroll_configuration LIMIT 5;

# Exit
\q
```

**✅ Pass Criteria:** Data exists in database tables

---

## 🎯 Quick Test Summary

After completing all tests, verify:

- [ ] ✅ Password Reset works
- [ ] ✅ Employee ID generation works
- [ ] ✅ Salary & Banking sections removed
- [ ] ✅ Reports menu accessible
- [ ] ✅ All 3 reports display correctly
- [ ] ✅ CSV exports work
- [ ] ✅ Date filters work
- [ ] ✅ Attendance defaults to today
- [ ] ✅ Payroll status colors correct
- [ ] ✅ New payroll columns work
- [ ] ✅ Bank Info modal works
- [ ] ✅ Role-based access enforced

---

## 🐛 Common Issues & Quick Fixes

### Issue: Application won't start

**Solution:**
```powershell
# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process if needed
taskkill /PID <PID> /F

# Restart application
python main.py
```

### Issue: Migrations fail

**Solution:**
```powershell
# Check current migration
flask db current

# Stamp to latest
flask db stamp head

# Run upgrade
flask db upgrade
```

### Issue: JavaScript not working

**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Check browser console for errors (F12)

### Issue: 404 errors on new routes

**Solution:**
1. Verify `routes_enhancements.py` is imported in `main.py`
2. Restart Flask application
3. Check route registration: `flask routes | grep reports`

### Issue: Database connection error

**Solution:**
```powershell
# Check PostgreSQL service
Get-Service postgresql*

# Start service if stopped
Start-Service postgresql-x64-14
```

---

## 📝 Test Results Template

Copy this template to record your test results:

```
HRMS Enhancement Testing - [Date]
Tester: [Your Name]

✅ = Pass | ❌ = Fail | ⚠️ = Partial

[ ] Test 1: Password Reset
[ ] Test 2: Employee ID Generation
[ ] Test 3: Removed Sections
[ ] Test 4: Reports Menu
[ ] Test 5: Employee History Report
[ ] Test 6: Payroll Configuration Report
[ ] Test 7: Attendance Report with Filters
[ ] Test 8: Attendance Default Date
[ ] Test 9: Payroll Status Colors
[ ] Test 10: Payroll Configuration - New Columns
[ ] Test 11: Bank Info Modal
[ ] Test 12: Role-Based Access

Issues Found:
1. [Description]
2. [Description]

Overall Status: [PASS / FAIL / NEEDS REVIEW]

Notes:
[Additional comments]
```

---

## 🎓 Tips for Efficient Testing

1. **Use Multiple Browser Tabs**
   - Tab 1: Admin view
   - Tab 2: Employee view
   - Tab 3: Database console

2. **Keep Developer Console Open**
   - Press F12 in browser
   - Monitor Network tab for API calls
   - Check Console tab for JavaScript errors

3. **Test in Order**
   - Follow the test sequence above
   - Each test builds on previous ones
   - Don't skip tests

4. **Document Everything**
   - Take screenshots of issues
   - Note exact steps to reproduce
   - Record error messages

5. **Test Edge Cases**
   - Empty forms
   - Invalid data
   - Long text in fields
   - Special characters

---

## 📞 Need Help?

**Documentation:**
- `DEPLOYMENT_CHECKLIST.md` - Full deployment guide
- `FRONTEND_IMPLEMENTATION_SUMMARY.md` - Frontend details
- `USER_CREDENTIALS_SUMMARY.md` - Login credentials

**Support:**
- Check browser console for errors
- Review Flask logs in terminal
- Search error messages in documentation

---

## ✅ Testing Complete!

Once all tests pass:

1. **Document Results**
   - Fill in test results template
   - Note any issues found
   - Suggest improvements

2. **Report to Team**
   - Share results with Business Analyst (Nagaraj)
   - Discuss any issues with developers
   - Schedule UAT if needed

3. **Prepare for Production**
   - Review deployment checklist
   - Plan deployment window
   - Prepare rollback plan

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Estimated Testing Time:** 30 minutes

**Happy Testing! 🎉**