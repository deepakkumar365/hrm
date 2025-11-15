# OT Two-Tier Approval System - Quick User Guide

## 📱 Who Does What?

### 👤 EMPLOYEE
```
1. Go to: Attendance → Mark OT Attendance
2. Fill in: Date, Hours, OT Type, Notes
3. Click: Save

That's it! You just marked OT.
Status: DRAFT (waiting for manager review)
```

### 👨‍💼 MANAGER
```
1. Go to: OT Management → Manager Approval Dashboard
2. See: All OT submitted to you
3. Review: Employee name, hours, date, reason
4. Choose:
   • "Approve" - Send to HR for final approval
   • "Reject" - Send back to employee to re-mark

Notes:
  • Can modify hours if needed
  • Can add approval comments
  • Cannot skip HR approval - two steps required!
```

### 👩‍💼 HR MANAGER
```
Step 1: Submit Employee OT to Manager
  1. Go to: OT Management → OT Attendance
  2. See: All employee OT marked (Draft status)
  3. Click: "Submit to Manager"
  
Step 2: Review Manager-Approved OT
  1. Go to: OT Management → OT Requests
  2. Filter: Show "Manager Approved" OT
  3. Review: What manager approved
  
Step 3: Final Approval for Payroll
  1. Go to: OT Management → Approval Dashboard
  2. See: All pending HR approvals
  3. Choose:
     • "Approve" - Ready for payroll ✓
     • "Reject" - Back to manager to re-review

Step 4: Check Payroll
  1. Go to: OT Management → OT Payroll Summary
  2. See: Only "approved" OT ready for payroll
  3. Review: Hours, rates, amounts
```

---

## 🔄 The Flow in Simple Terms

```
EMPLOYEE MARKS OT
        ↓
        Waiting for Manager... (Manager Approval)
        ↓
MANAGER APPROVES
        ↓
        Waiting for HR... (HR Approval)
        ↓
HR APPROVES
        ↓
✓ READY FOR PAYROLL
        ↓
PAYROLL CALCULATES PAY
```

---

## ⏱️ Timeline Example

**John's OT on Jan 15:**

```
Jan 15, 4 PM    → John marks OT: 2 hours
Jan 16, 9 AM    → HR Manager Lisa submits to Manager
Jan 16, 10 AM   → Manager Sarah sees pending OT
Jan 16, 10:15   → Sarah approves, Lisa gets notified
Jan 16, 10:30   → Lisa approves (FINAL)
Jan 16, 10:31   → OT added to Jan payroll ✓
```

---

## ✅ What Happens If Rejected?

### If Manager Rejects:
```
Manager says NO
        ↓
Employee's OT goes back to DRAFT
        ↓
Employee can edit and re-mark
        ↓
Re-submit to Manager (same process)
```

### If HR Rejects:
```
HR Manager says NO
        ↓
Goes BACK to Manager for review
        ↓
Manager can:
  • Modify hours and re-approve
  • Reject again
  • Add comments about why HR rejected
        ↓
Back to HR (same process)
```

---

## 🆘 Troubleshooting

### "I can't submit OT to Manager"
**Check**: Does the employee have a manager assigned?
- Employee profile → Reporting Manager field
- If empty → Assign a manager first

### "No one to send the OT to"
**Check**: Is the manager configured correctly?
- Manager must have: is_manager = ✓ (checkbox marked)
- Manager must have: User Account created

### "I don't see pending OT"
**Manager**: 
- Go to Manager Approval Dashboard
- Refresh the page
- Check filter is set to "pending"

**HR Manager**:
- Go to OT Requests → filter "manager_approved"
- Or go to Approval Dashboard → filter "pending_hr"

### "Hours look wrong in Payroll"
**Check**: Was final approval given by HR?
- Only HR-approved OT shows in Payroll Summary
- OT not approved yet? Status must be "HR Approved"

---

## 📊 Status Meanings

```
DRAFT               → Marked by employee, not submitted yet
SUBMITTED           → HR submitted to Manager
PENDING MANAGER     → Waiting for Manager approval
MANAGER APPROVED    → Manager said yes, now at HR
MANAGER REJECTED    → Manager said no, back to employee
PENDING HR          → Waiting for HR approval
HR APPROVED         → ✓ FINAL - Ready for payroll
HR REJECTED         → Back to Manager to re-review
```

---

## ⏰ Quick Reference - Who Sees What?

```
EMPLOYEE
  ✓ See: Own OT marks (Draft)
  ✓ See: Rejection comments from Manager
  ✗ Cannot: See approval process

MANAGER
  ✓ See: OT from their team
  ✓ See: Pending OT to approve
  ✓ Do: Approve/Reject/Modify hours
  ✗ Cannot: See all OT (only their team)

HR MANAGER
  ✓ See: All Draft OT to submit
  ✓ See: Manager-approved OT
  ✓ See: OT pending final approval
  ✓ See: Ready-for-payroll OT
  ✓ Do: Everything - submit, approve, reject, modify
```

---

## 🎯 Key Points

1. **TWO Approvals Required**: Manager + HR
   - Can't skip manager approval
   - Can't approve to payroll without both levels

2. **Rejection Can Happen Twice**:
   - Manager rejects → Employee re-marks
   - HR rejects → Manager re-reviews

3. **Only Approved OT Goes to Payroll**:
   - Status must be "HR Approved"
   - Payroll Summary shows only approved

4. **Manager Assignment Required**:
   - Every employee needs a manager
   - Manager must have User account + is_manager flag

5. **Comments Trail**:
   - Each approval level can add comments
   - Comments preserved through rejections

---

## 📞 Common Questions

**Q: Can I approve OT without going through Manager?**
A: No - two-tier system requires Manager approval first, then HR approval.

**Q: What if Manager is absent?**
A: OT stays pending. Assign an alternate manager or escalate to HR.

**Q: Can I modify hours?**
A: Yes, both Manager and HR can modify hours before approving.

**Q: How long does approval take?**
A: Depends on manager/HR workload. Usually same day, max 1-2 days.

**Q: If rejected, do I lose the OT record?**
A: No - you can edit and resubmit. OT record is preserved.

**Q: When does payroll include my OT?**
A: Only when HR Manager approves (after Manager approves).

---

## 🚀 Quick Start - For Each Role

### EMPLOYEE (2 clicks):
```
1. Attendance → Mark OT Attendance
2. Fill form & Save
```

### MANAGER (1 click):
```
1. OT Management → Manager Approval Dashboard
2. Approve or Reject pending OT
```

### HR MANAGER (3 steps):
```
1. OT Management → OT Attendance → Submit to Manager
2. OT Management → OT Requests → Review Manager Approvals
3. OT Management → Approval Dashboard → Final Approve/Reject
```

---

## 📋 Implementation Status

✅ Two-Tier Approval Complete
✅ Manager Dashboard Added
✅ HR Approval Workflow Ready
✅ Payroll Integration Complete
✅ Company Isolation Enabled
✅ Role-Based Access Enforced

**Status**: 🟢 LIVE AND READY TO USE

---

*For technical questions, contact System Administrator*