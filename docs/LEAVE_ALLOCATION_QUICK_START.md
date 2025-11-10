# Leave Allocation Configuration - Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites
- ✅ Database migration completed
- ✅ You are a Super Admin, Tenant Admin, or HR Manager

### Quick Setup Steps

#### **Step 1: Run Database Migration** (2 minutes)

```bash
# Navigate to project directory
cd D:/Projects/HRMS/hrm

# Run migration
python -m flask db upgrade

# Verify migration
python -m flask db current
```

**Expected Output:**
```
(venv) $ python -m flask db current
Info  [alembic.migration] Context impl PostgreSQLImpl.
INFO  [alembic.migration] Will assume transactional DDL.
Leave Allocation and Employee Groups Migration → leave_allocation_001
```

---

#### **Step 2: Create Employee Groups** (2 minutes)

1. **Open HRMS Dashboard**
2. **Navigate to:** Masters → Employee Groups
3. **Click:** "Add Employee Group"
4. **Fill Form:**
   ```
   Group Name: Senior Management
   Category:   Department
   Description: Senior level managers and leaders
   ```
5. **Click:** Create Employee Group
6. **Repeat for other groups** (e.g., Support Team, Engineering, etc.)

---

#### **Step 3: Assign Employees to Groups** (1 minute)

1. **Navigate to:** Employees
2. **Select an Employee**
3. **Edit Profile**
4. **Set:** Employee Group = "Senior Management"
5. **Save**

---

### Optional: Configure Leave Allocations

#### **Option A: By Designation**

1. **Navigate to:** Leave Management → Allocation → Designation
2. **Select Company** (top-left dropdown)
3. **Click:** "Add Allocation"
4. **Fill Form:**
   ```
   Designation: Manager
   Leave Type:  Annual Leave
   Total Days:  20
   ```
5. **Save**

**Result:** All Managers now get 20 Annual Leave days

---

#### **Option B: By Employee Group**

1. **Navigate to:** Leave Management → Allocation → Employee Group
2. **Select Company** (top-left dropdown)
3. **Click:** "Add Allocation"
4. **Fill Form:**
   ```
   Employee Group: Senior Management
   Leave Type:     Annual Leave
   Total Days:     22
   ```
5. **Save**

**Result:** All employees in Senior Management get 22 Annual Leave days

---

#### **Option C: Individual Override**

1. **Navigate to:** Leave Management → Allocation → Employee
2. **Search** for specific employee
3. **Create Override** with custom days and reason

---

## 📋 What You Can Now Do

✅ **Configure leave days per designation**
- E.g., "Manager gets 20 days, Staff gets 15 days"

✅ **Configure leave days per employee group**
- E.g., "Marketing team gets 15 casual leave days"

✅ **Override for individual employees**
- E.g., "John Smith gets 25 days (senior contributor)"

✅ **Support multiple companies**
- Each company has independent configuration

✅ **Track audit trail**
- See who created/modified each configuration

---

## 🔑 Key Navigation

```
📊 Dashboard
├── Masters
│   └── Employee Groups ← Create/manage groups
├── Leave Management
│   ├── Configuration ← Configure leave types (existing)
│   └── Allocation
│       ├── Designation ← Configure by job title
│       ├── Employee Group ← Configure by group
│       └── Employee ← Override for individuals
└── Employees
    └── [Edit Profile] ← Assign employee group
```

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Can access "Employee Groups" in Masters menu
- [ ] Can create new employee groups
- [ ] Can assign employee groups to employees
- [ ] Can configure designation-based allocations
- [ ] Can configure employee group-based allocations
- [ ] Can see all allocations in respective list views
- [ ] Can edit and delete allocations
- [ ] Data shows company context correctly

---

## 🐛 Common Issues

### Issue: "Page Not Found" when accessing Employee Groups
**Solution:** Restart Flask application after migration
```bash
# Stop current Flask server (Ctrl+C)
# Run migration again
python -m flask db upgrade
# Start Flask
python main.py
```

### Issue: Cannot see new columns in employee form
**Solution:** Clear browser cache (Ctrl+Shift+Delete) and refresh

### Issue: Migration fails with "table already exists"
**Solution:** Migration has already run. Check with:
```bash
python -m flask db current
```

### Issue: "Permission denied" error
**Solution:** Ensure you're logged in as Tenant Admin or HR Manager

---

## 📚 Learn More

For detailed documentation, see: `LEAVE_ALLOCATION_CONFIGURATION.md`

---

## 🎯 Common Configuration Examples

### Example 1: Simple Designation-Based System
```
Senior Manager    → Annual: 20 days, Sick: 10 days, Casual: 5 days
Manager           → Annual: 18 days, Sick: 10 days, Casual: 5 days
Staff             → Annual: 15 days, Sick: 10 days, Casual: 5 days
```

### Example 2: Group-Based with Mixed Allocation
```
Engineering Team     → Special: 5 days (for conferences)
Support Team         → Annual: 15 days (flexible)
Human Resources      → Annual: 20 days (administrative duty)
```

### Example 3: Hybrid Approach
```
Use Designations for: Annual Leave (standardized across company)
Use Groups for: Casual Leave (varies by team)
Use Overrides for: Executive exceptions or special cases
```

---

## ⚙️ Configuration Best Practices

1. **Start with Designations**
   - Define standard leave allocation by job title
   - Easier to maintain

2. **Add Groups for Exceptions**
   - Use when certain teams need different allocation
   - E.g., field teams might need more casual leave

3. **Use Overrides Sparingly**
   - Document the reason clearly
   - Use for genuine exceptions only

4. **Review Annually**
   - Check if allocations match company policy
   - Update for new designations or groups

---

## 🆘 Need Help?

1. **Check documentation:** See `LEAVE_ALLOCATION_CONFIGURATION.md`
2. **Review application logs:** Check console for error messages
3. **Verify database:** Run `python verify_db.py`
4. **Reset if needed:** Admin can re-run migration with cleanup

---

**Last Updated:** 2024  
**Version:** 1.0