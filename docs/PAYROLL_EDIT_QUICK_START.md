# Quick Start: Payroll Generate - Inline Editing

## 🎯 What's New?

The Payroll Generate page now allows you to **edit and save payroll data directly** without waiting to generate payslips!

✅ **Edit individual cells** in the table  
✅ **Save single rows** one at a time  
✅ **Save all changes** at once with bulk save  
✅ **Auto-calculated** totals (Gross & Net Salary)  
✅ **Visual indicators** for unsaved changes  

---

## 📋 Step-by-Step Guide

### 1️⃣ Load Employee Data

```
1. Go to: Payroll → Generate
2. Select Company dropdown
3. Select Month dropdown
4. Select Year dropdown
5. Click "Load Employee Data" button
   → Table loads with employees
```

### 2️⃣ Edit a Cell

**Click anywhere on the payroll values** to edit:

```
Editable columns:
• Base Salary (₱)
• Allowances (₱)
• OT Hours
• OT Amount (₱)
• Attendance Days
• Absent Days
• LOP Days
• Other Deductions (₱)
```

**When you click:**
- Input field appears
- Current value is selected
- Edit the value

**After editing:**
- Press **Enter** → Save to browser
- Press **Escape** → Cancel edit
- Click outside → Save to browser

### 3️⃣ Row Turns Yellow

After editing a cell:
- Row background turns **yellow** 🟨
- **"Unsaved"** badge appears
- **Save button** appears in the row

### 4️⃣ Save Individual Row

**Option A - Save One Row:**

```
1. Make your edits in the row cells
2. Click the "Save" button (blue button)
3. Spinner appears (saving...)
4. "Saved!" message shows
5. Row returns to normal (white background)
6. Data saved to database ✅
```

**Option B - Save Multiple Rows at Once:**

```
1. Edit multiple employee rows
   → Each shows "Unsaved" badge
2. Click "Save All Unsaved Changes" button (bottom left)
3. Confirm the number of rows
4. All rows save automatically
5. All show "Saved!" message ✅
```

### 5️⃣ Generate Payslips (After Editing)

Once your edits are saved:

```
1. Select employees via checkboxes ☑️
2. Click "Generate Payslips" button
   → Creates payslip records with your edited data
3. Redirects to Payroll list
```

**OR skip this** if you just wanted to **save payroll data without payslips**.

---

## 💡 Tips & Tricks

### Smart Auto-Calculation
After you edit any field, these calculate automatically:
- **Gross Salary** = Base + Allowances + OT Amount
- **Net Salary** = Gross - CPF - Deductions

You don't need to calculate manually! ✨

### Keyboard Shortcuts
```
Enter  → Save cell and move next
Escape → Cancel current edit
Tab    → Move to next field (and save current)
```

### Batch Operations
```
Edit Employee 1 → row shows "Unsaved"
Edit Employee 2 → row shows "Unsaved"
Edit Employee 3 → row shows "Unsaved"
     ↓
"Save All Unsaved Changes" button appears ← Click here!
     ↓
All 3 rows save at once
```

### Visual Indicators
| Visual | Meaning |
|--------|---------|
| 🟩 Gray hover | Cell is editable |
| 🟨 Yellow edit | Currently editing |
| 🟨 Yellow row | Row has unsaved changes |
| 🔵 Save button | Click to save this row |
| 📌 "Unsaved" badge | This row not saved yet |
| ✅ "Saved!" message | Row saved successfully |

---

## ⚠️ Important Notes

### Before You Start
- ✅ You must have **Admin** or **HR Manager** role
- ✅ Company, Month, and Year must be selected
- ✅ Employees must be active in the system

### Save Behavior
- **Browser memory**: Changes appear immediately in the table
- **Database**: Only saved when you click "Save" button
- **Lost on refresh**: Unsaved changes lost if you refresh page
- **No auto-save**: Manual save required (not automatic)

### Editing Rules
- ✅ Can edit any payroll field
- ✅ Values must be 0 or positive
- ✅ Decimal values allowed (up to 2 places)
- ✅ Days must be whole numbers

---

## 🔍 Common Tasks

### Task: Fix OT Hours for one employee
```
1. Load data for the month
2. Find the employee row
3. Click the "OT Hours" cell
4. Change the value to correct hours
5. Press Enter
6. Click Save button on that row
7. Done! ✅
```

### Task: Update allowances for all employees
```
1. Load data for the month
2. For each employee:
   - Click allowance cell
   - Edit value
   - Press Enter
3. After all edits, click "Save All Unsaved Changes"
4. Confirm and wait for saving
5. All done! ✅
```

### Task: Fix attendance and recalculate
```
1. Load data for the month
2. Click "Attendance Days" cell
3. Change to correct number of days
4. Press Enter (Auto-calc updates Gross & Net Salary!)
5. Click Save
6. Done! ✅
```

---

## ❓ FAQ

**Q: Will my edits be lost?**  
A: Only if you don't click the Save button before closing/refreshing the page.

**Q: Can I edit before loading data?**  
A: No, you must load employees first by selecting Company/Month/Year.

**Q: What if saving fails?**  
A: You'll see an error message. Changes remain in the table for retry.

**Q: Can I save without generating payslips?**  
A: Yes! Save your payroll data, then close the page. You can generate payslips later.

**Q: Do I need to select employees to save payroll?**  
A: No, you can save any employee's data regardless of checkbox selection.

**Q: What happens to my edits after generating payslips?**  
A: Your edited data is used to create the payslips. The data is preserved.

---

## 🚀 Ready to Go!

You're all set! Start editing payroll:

1. Navigate to **Payroll → Generate**
2. Select your filters
3. Click "Load Employee Data"
4. Click cells to edit
5. Hit Save
6. All done! ✅

Need help? Contact your HR Manager or Admin.

---

**Version**: 1.0 | **Last Updated**: January 2025