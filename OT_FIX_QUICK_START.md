# 🚀 OT Employee Submission - QUICK START GUIDE

## ✅ What Was Fixed?

**Problem**: Manager could see OT Approvals menu but NO requests in the approval queue.

**Root Cause**: OT records stayed in Draft → Never submitted → No OTApproval records created

**Solution**: Added "Submit" button so employees can submit their own OT for approval

---

## 🔄 NEW WORKFLOW

```
Employee:
  1. Mark OT Attendance
  2. [NEW] Click "Submit" button ← THIS IS NEW!
  3. Status changes to "Submitted"

Manager:
  1. Can now see OT in "OT Approvals" dashboard
  2. Review and Approve/Reject
  3. Sent to HR Manager for final approval
```

---

## 🧪 QUICK TEST (5 minutes)

### Test Setup
1. Start app: `python main.py`
2. Run migrations: `flask db upgrade`

### Test as Employee
```
1. Login as Employee user (not admin)
2. Go to: OT > Mark Attendance
3. Fill form:
   - Date: Today
   - Hours: 2.5
   - OT Type: Any type
4. Click "Save OT Attendance"
5. ✅ See OT in "Recent OT Records"
6. ✅ Status: Draft
7. ✅ [NEW] See a blue "Submit" button
8. Click "Submit" button
9. ✅ Message: "OT submitted to [Manager]"
10. ✅ Badge changes to "Pending Manager Review"
```

### Test as Manager
```
1. Logout employee
2. Login as Employee with is_manager=true flag
3. ✅ See "OT Approvals" menu item
4. Click "OT Approvals"
5. ✅ See the OT from employee above!
6. Click "Approve" button
7. ✅ Message: "OT Approved. Sent to HR Manager"
8. ✅ OT count changes
```

---

## 📂 Files Changed

| File | Changes |
|------|---------|
| `routes_ot.py` | ➕ Added `submit_ot_attendance()` route |
| `mark_attendance.html` | ➕ Added Submit button + CSS |

---

## ⚠️ Prerequisites

Before testing, ensure:

1. **Employee has manager assigned**
   ```sql
   SELECT id, first_name, manager_id FROM hrm_employee 
   WHERE is_manager=true LIMIT 1;
   ```
   
2. **Manager has user account**
   ```sql
   SELECT e.id, e.first_name, e.user_id 
   FROM hrm_employee e 
   WHERE e.id = [manager_id];
   ```

3. **Employee has user account linked**
   ```sql
   SELECT id, first_name, user_id FROM hrm_employee LIMIT 1;
   ```

If any are missing, create them before testing.

---

## 🔍 Verify in Database

After submitting OT:

```sql
-- 1. Check OTAttendance (employee marked)
SELECT id, status FROM hrm_ot_attendance WHERE status='Submitted';

-- 2. Check OTRequest (approval workflow)
SELECT id, status FROM hrm_ot_request WHERE status='pending_manager';

-- 3. Check OTApproval (manager assignment)
SELECT id, approval_level, status FROM hrm_ot_approval 
WHERE approval_level=1 AND status='pending_manager';
```

Should see 1 record in each.

---

## 🎯 Key Buttons

| Button | Location | Action |
|--------|----------|--------|
| **Submit** | Recent OT Records | Submit Draft OT to manager |
| **Approve** | Manager Dashboard | Approve OT for HR review |
| **Reject** | Manager Dashboard | Reject OT back to employee |

---

## ❌ Common Issues

| Issue | Solution |
|-------|----------|
| No "Submit" button appears | OT is not Draft status |
| Manager dashboard still empty | OT not submitted / wrong manager |
| "No reporting manager" error | Employee needs `manager_id` set |
| "Manager has no user account" error | Manager employee needs user link |

---

## ✨ What's New

✅ Employees can now self-submit OT (no need for HR Manager to submit)  
✅ Managers can see pending OT in their dashboard  
✅ Status badges show OT progress  
✅ Seamless two-tier approval workflow  

---

**Status**: 🟢 READY TO TEST

Need help? Check: `OT_EMPLOYEE_SUBMISSION_FIX.md` for detailed guide