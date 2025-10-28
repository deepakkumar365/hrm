# Payroll Module - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Run Database Migration (Required)
```bash
# Navigate to project directory
cd E:/Gobi/Pro/HRMS/hrm

# Run migration
flask db upgrade
```

**Alternative (if flask db doesn't work):**
```bash
python -c "from app import app, db; from models import PayrollConfiguration; app.app_context().push(); db.create_all()"
```

---

### Step 2: Configure Employee Allowances

1. **Login as Admin**
2. **Navigate:** Payroll → Payroll Configuration
3. **For each employee:**
   - Click the **Edit** button (✏️)
   - Set allowances:
     - Transport Allowance: e.g., $200
     - Housing Allowance: e.g., $500
     - Meal Allowance: e.g., $150
     - Other Allowance: e.g., $100
   - Set OT Rate per Hour: e.g., $25
   - Click **Save** button (✓)

---

### Step 3: Generate Payroll

1. **Navigate:** Payroll → Generate Payroll
2. **Select Month:** e.g., January
3. **Select Year:** e.g., 2025
4. **Click:** "Load Employee Data"
5. **Review** the preview table
6. **Select** employees (or click "Select All")
7. **Click:** "Generate Payslips"
8. **Done!** Payroll records created

---

## 📋 What Each Page Does

### 1. Payroll Configuration (`/payroll/config`)
**Purpose:** Set up employee allowances and OT rates

**What you can do:**
- ✅ Edit base salary
- ✅ Set 4 different allowances per employee
- ✅ Set custom OT rate
- ✅ Search employees
- ✅ Save changes instantly (AJAX)

---

### 2. Generate Payroll (`/payroll/generate`)
**Purpose:** Create monthly payroll for employees

**What you see:**
- Base Salary
- Transport Allowance
- Housing Allowance
- Meal Allowance
- Other Allowance
- OT Hours (from attendance)
- OT Amount (calculated)
- Attendance Days
- CPF Deductions
- **Net Salary**

**What it does:**
- Fetches attendance records
- Calculates OT automatically
- Applies allowances from configuration
- Calculates CPF deductions
- Creates payroll records

---

### 3. Payslip Viewer (`/payroll`)
**Purpose:** View and manage generated payslips

**What you can do:**
- ✅ View all payroll records
- ✅ Filter by month/year
- ✅ View detailed payslip
- ✅ Approve payroll (Admin)
- ✅ Track status (Draft/Approved/Paid)

---

## 🔑 Access Levels

| Feature | Super Admin | Admin | HR Manager | Manager | User |
|---------|-------------|-------|------------|---------|------|
| Configure Allowances | ✅ | ✅ | ✅ | ❌ | ❌ |
| Generate Payroll | ✅ | ✅ | ✅ | ❌ | ❌ |
| View All Payslips | ✅ | ✅ | ✅ | ❌ | ❌ |
| View Team Payslips | ✅ | ✅ | ✅ | ✅ | ❌ |
| View Own Payslip | ✅ | ✅ | ✅ | ✅ | ✅ |
| Approve Payroll | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## 💡 Quick Tips

### Tip 1: Bulk Configuration
Configure allowances for multiple employees at once by:
1. Edit first employee
2. Save
3. Edit next employee
4. Repeat

### Tip 2: Preview Before Generate
Always click "Load Employee Data" to preview calculations before generating payroll.

### Tip 3: Check Attendance First
Ensure attendance records are marked for the month before generating payroll. OT hours come from attendance.

### Tip 4: Avoid Duplicates
The system automatically skips employees who already have payroll for the selected month.

### Tip 5: Draft Status
Generated payroll starts with "Draft" status. Review and approve before marking as paid.

---

## 🧮 Calculation Formula

```
Total Allowances = Transport + Housing + Meal + Other

OT Amount = OT Hours × OT Rate

Gross Pay = Base Salary + Total Allowances + OT Amount

Employee CPF = Gross Pay × (Employee CPF Rate ÷ 100)

Net Pay = Gross Pay - Employee CPF
```

**Example:**
```
Base Salary: $5,000
Transport: $200
Housing: $500
Meal: $150
Other: $100
OT Hours: 10
OT Rate: $25/hour

Total Allowances = $950
OT Amount = 10 × $25 = $250
Gross Pay = $5,000 + $950 + $250 = $6,200
Employee CPF (20%) = $6,200 × 0.20 = $1,240
Net Pay = $6,200 - $1,240 = $4,960
```

---

## ⚠️ Common Issues & Solutions

### Issue: "Table doesn't exist" error
**Solution:** Run the database migration (Step 1 above)

### Issue: Allowances not showing
**Solution:** Configure allowances in Payroll Configuration page first

### Issue: OT hours are zero
**Solution:** Mark attendance with OT hours for the month

### Issue: Can't save configuration
**Solution:** Check browser console for errors. Ensure you're logged in as Admin/HR Manager

### Issue: Duplicate payroll error
**Solution:** Payroll already exists for that employee and month. Check Payroll List.

---

## 📁 Files Modified/Created

### New Files:
- `templates/payroll/generate.html` - New payroll generation UI
- `migrations/versions/add_payroll_configuration.py` - Database migration
- `README_PAYROLL_MODULE.md` - Full documentation
- `PAYROLL_IMPLEMENTATION_SUMMARY.md` - Implementation details
- `PAYROLL_QUICK_START.md` - This file

### Modified Files:
- `models.py` - Added PayrollConfiguration model
- `routes.py` - Added 4 new routes
- `templates/payroll/config.html` - Rewritten with new features

---

## 🎯 Workflow Example

**Scenario:** Generate January 2025 payroll for all employees

1. **Configure (One-time setup):**
   - Go to Payroll Configuration
   - Set allowances for each employee
   - Set OT rates

2. **Mark Attendance (Monthly):**
   - Employees mark attendance daily
   - Include OT hours if applicable

3. **Generate Payroll (Monthly):**
   - Go to Generate Payroll
   - Select January 2025
   - Load employee data
   - Review preview
   - Select all employees
   - Generate payslips

4. **Review & Approve:**
   - Go to Payroll List
   - Filter by January 2025
   - Review each payroll
   - Click Approve

5. **Employees View:**
   - Employees login
   - Go to Payroll
   - View their payslip

---

## 📞 Need Help?

1. **Full Documentation:** See `README_PAYROLL_MODULE.md`
2. **Implementation Details:** See `PAYROLL_IMPLEMENTATION_SUMMARY.md`
3. **Test Checklist:** See testing section in README

---

## ✅ Pre-Launch Checklist

Before using in production:

- [ ] Database migration completed
- [ ] Test with 2-3 employees first
- [ ] Verify calculations are correct
- [ ] Configure allowances for all employees
- [ ] Test payroll generation
- [ ] Test payslip viewing
- [ ] Test approval workflow
- [ ] Test role-based access
- [ ] Backup database

---

**Ready to use!** 🎉

Start with Step 1 (Database Migration) and follow the guide above.