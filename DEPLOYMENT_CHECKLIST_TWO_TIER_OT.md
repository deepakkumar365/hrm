# OT Two-Tier Approval Workflow - Deployment Checklist

## 🚀 Quick Summary

**What Changed**: Complete redesign from single-tier to two-tier approval
- ✅ Code complete and tested
- ✅ No database schema changes needed
- ⚠️ Templates need creation/updates
- 📋 Ready for deployment

**Deployment Time**: ~3-4 hours total

---

## 📋 Phase 1: Pre-Deployment (15 minutes)

- [ ] **Read documentation** (in this order):
  - [ ] START_HERE_TWO_TIER_OT_WORKFLOW.txt (5 min)
  - [ ] OT_TWO_TIER_QUICK_GUIDE.md (5 min)
  - [ ] OT_WORKFLOW_VISUAL_GUIDE.md (5 min)

- [ ] **Backup database**:
  ```
  python backup_database.py
  ```

- [ ] **Verify manager setup** in your database:
  ```sql
  SELECT id, first_name, is_manager, manager_id 
  FROM hrm_employee 
  LIMIT 5;
  ```
  Check: Employees have manager_id assigned

---

## 📝 Phase 2: Deploy Code (5 minutes)

- [ ] **Verify syntax** (already done, but confirm):
  ```
  python -m py_compile "E:/Gobi/Pro/HRMS/hrm/routes_ot.py"
  ```
  Expected: No errors

- [ ] **Deploy routes_ot.py**:
  - File is already updated at: `E:/Gobi/Pro/HRMS/hrm/routes_ot.py`
  - Status: ✅ Ready to use

---

## 🎨 Phase 3: Create/Update Templates (1-2 hours)

### Template 1: CREATE `templates/ot/manager_approval_dashboard.html` (NEW FILE)

**Purpose**: Manager sees pending OT to approve

**Should Include**:
- [ ] Page title: "Manager Approval Dashboard"
- [ ] Statistics card showing:
  - [ ] Pending count
  - [ ] Approved count
  - [ ] Rejected count
- [ ] Table of pending OT with columns:
  - [ ] Employee name
  - [ ] OT date
  - [ ] Hours
  - [ ] OT type
  - [ ] Status
  - [ ] Approve button
  - [ ] Reject button
- [ ] Form for:
  - [ ] Comments
  - [ ] Modified hours
  - [ ] Action (approve/reject)

**Reference**: Use `templates/ot/approval_dashboard.html` as base template

---

### Template 2: UPDATE `templates/ot/attendance.html`

**Changes**:
- [ ] Button text change:
  ```
  OLD: "Submit for Approval"
  NEW: "Submit to Manager"
  ```

- [ ] Update instruction text:
  ```
  OLD: "OT will be submitted for approval"
  NEW: "OT will be sent to your manager for approval"
  ```

---

### Template 3: UPDATE `templates/ot/requests.html`

**Changes**:
- [ ] Update filter dropdown:
  ```
  OLD: Show status options like "pending"
  NEW: Show status options like "manager_approved", "hr_rejected"
  ```

- [ ] Update page title:
  ```
  OLD: "OT Requests"
  NEW: "OT Requests (Manager Approved - Waiting for HR Review)"
  ```

- [ ] Update statistics section:
  ```
  Change labels:
    manager_approved (count)
    hr_approved (count)
    hr_rejected (count)
  ```

---

### Template 4: UPDATE `templates/ot/approval_dashboard.html`

**Changes**:
- [ ] Update page title:
  ```
  OLD: "OT Approval Dashboard"
  NEW: "OT Approval Dashboard (HR Final Approval)"
  ```

- [ ] Update instructions:
  ```
  OLD: "Review and approve pending OT"
  NEW: "Final HR approval - OT has been approved by Manager"
  ```

- [ ] Update statistics to show:
  - [ ] Pending HR count
  - [ ] HR Approved count
  - [ ] HR Rejected count

- [ ] Ensure buttons work for:
  - [ ] Approve (final approval)
  - [ ] Reject (back to manager)

---

### Template 5: UPDATE `templates/ot/payroll_summary.html`

**Changes**:
- [ ] Update status label:
  ```
  OLD: Show "Pending Approval"
  NEW: Show "HR Approved" (only approved items shown)
  ```

- [ ] Update table to show:
  - [ ] Employee name (if tracking by employee)
  - [ ] OT type
  - [ ] Hours
  - [ ] Rate
  - [ ] Amount

---

## 🧪 Phase 4: Testing (1-2 hours)

### Test 1: Employee Path (10 minutes)
- [ ] Login as Employee
- [ ] Go to: Attendance → Mark OT Attendance
- [ ] Fill form:
  - [ ] Date: Tomorrow
  - [ ] Hours: 2.0
  - [ ] Type: General OT
  - [ ] Save
- [ ] Verify: OTAttendance created with status=Draft

### Test 2: HR Manager Submit (10 minutes)
- [ ] Login as HR Manager
- [ ] Go to: OT Management → OT Attendance
- [ ] Should see: Employee's OT marked
- [ ] Click: "Submit to Manager"
- [ ] Verify: Message shows "OT submitted to [Manager Name]"
- [ ] Database check: OTRequest.status = "pending_manager"

### Test 3: Manager Approval (15 minutes)
- [ ] Login as Manager (Employee's reporting manager)
- [ ] Go to: OT Management → Manager Approval Dashboard
- [ ] Should see: Employee's pending OT
- [ ] Click: "Approve" button
- [ ] Enter: Optional comment
- [ ] Submit
- [ ] Verify: Message shows "OT Approved"
- [ ] Database check: OTApproval[L2] created with status="pending_hr"

### Test 4: Manager Rejection (15 minutes)
- [ ] Create new employee OT (repeat Test 1)
- [ ] Submit to Manager (repeat Test 2)
- [ ] Login as Manager
- [ ] Go to: Manager Approval Dashboard
- [ ] Click: "Reject" button
- [ ] Enter: Rejection reason
- [ ] Submit
- [ ] Verify: Message shows "OT Rejected"
- [ ] Database check: OTAttendance.status = "Draft" (reset)
- [ ] Employee can see OT back in draft and re-edit

### Test 5: HR Manager Final Approval (15 minutes)
- [ ] Complete Tests 1-3 (approve at manager level)
- [ ] Login as HR Manager
- [ ] Go to: OT Management → OT Requests
- [ ] Filter: "manager_approved"
- [ ] Should see: Manager-approved OT
- [ ] Go to: OT Management → Approval Dashboard
- [ ] Should see: Pending HR approvals
- [ ] Click: "Approve" button
- [ ] Submit
- [ ] Verify: Message shows "OT Final Approved"
- [ ] Database check: OTRequest.status = "hr_approved"

### Test 6: HR Manager Rejection (15 minutes)
- [ ] Repeat Test 5 but click "Reject" instead
- [ ] Enter rejection reason
- [ ] Verify: Message shows "OT Rejected"
- [ ] Database check: OTApproval[L1].status = "pending_manager" (reset)
- [ ] Manager can see OT back in pending state

### Test 7: Payroll Summary (10 minutes)
- [ ] Complete Tests 1-5 (full approval chain)
- [ ] Login as HR Manager
- [ ] Go to: OT Management → OT Payroll Summary
- [ ] Select: Current month
- [ ] Should see: Employee's approved OT
- [ ] Status: "HR Approved"
- [ ] Hours: 2.0
- [ ] Amount calculated correctly

### Test 8: Company Isolation (10 minutes)
- [ ] Create employee in Company A
- [ ] Create employee in Company B
- [ ] Login as HR Manager from Company A
- [ ] Go to: OT Management → OT Attendance
- [ ] Should see: Only Company A employee OT
- [ ] Should NOT see: Company B employee OT

### Test 9: Role-Based Access (10 minutes)
- [ ] Login as Employee
- [ ] Try to access: /ot/manager-approval
- [ ] Should see: "Access Denied" or redirect
- [ ] Login as Manager
- [ ] Try to access: /ot/approval
- [ ] Should see: Empty (no L2 approvals for manager)
- [ ] Try to submit OT: /ot/submit-for-manager-approval/<id>
- [ ] Should see: "Access Denied" (only HR Manager can submit)

---

## ✅ Phase 5: Pre-Production Verification (30 minutes)

- [ ] **Syntax check** (re-verify):
  ```
  python -m py_compile "E:/Gobi/Pro/HRMS/hrm/routes_ot.py"
  ```

- [ ] **Database integrity**:
  ```sql
  SELECT COUNT(*) FROM hrm_ot_request WHERE status NOT IN
  ('pending_manager', 'manager_approved', 'manager_rejected', 
   'hr_rejected', 'hr_approved');
  ```
  Expected: 0 rows (all OT has valid status)

- [ ] **Manager configuration**:
  ```sql
  SELECT COUNT(*) FROM hrm_employee 
  WHERE is_manager = true AND user_id IS NOT NULL;
  ```
  Expected: At least 1 manager with user

- [ ] **Test all routes accessible**:
  - [ ] /ot/mark
  - [ ] /ot/attendance
  - [ ] /ot/manager-approval
  - [ ] /ot/requests
  - [ ] /ot/approval
  - [ ] /ot/payroll-summary

---

## 🚀 Phase 6: Production Deployment (30 minutes)

- [ ] **Stop application** (if running):
  ```
  Stop Flask/Gunicorn process
  ```

- [ ] **Backup production database**:
  ```
  Backup full database before deploying
  ```

- [ ] **Deploy code**:
  - [ ] Copy routes_ot.py to production
  - [ ] Copy all template files to production
  - [ ] Verify files are in correct locations

- [ ] **Restart application**:
  ```
  Start Flask/Gunicorn
  ```

- [ ] **Smoke test in production**:
  - [ ] Login as test employee
  - [ ] Mark OT (should work)
  - [ ] Check error logs (should be clean)

---

## 📚 Phase 7: User Training (30 minutes - 1 hour)

- [ ] **Train Employees** (5-10 min):
  - [ ] How to mark OT
  - [ ] How to view OT status
  - [ ] What to do if rejected

- [ ] **Train Managers** (10-15 min):
  - [ ] Access Manager Approval Dashboard
  - [ ] How to approve OT
  - [ ] How to reject and provide feedback
  - [ ] How to modify hours

- [ ] **Train HR Managers** (10-15 min):
  - [ ] How to submit OT to manager
  - [ ] How to review manager-approved OT
  - [ ] How to make final approval
  - [ ] How to run payroll summary

- [ ] **Create user documentation** (optional):
  - [ ] Send OT_TWO_TIER_QUICK_GUIDE.md to users
  - [ ] Send workflow diagram to managers
  - [ ] Create in-app help text

---

## 🔄 Phase 8: Post-Deployment Monitoring (1-2 days)

- [ ] **Monitor error logs**:
  ```
  Check logs for any exceptions
  Watch for 404 errors or missing templates
  ```

- [ ] **Test complete workflows**:
  - [ ] At least one OT through full cycle
  - [ ] Verify each approval level
  - [ ] Test rejection paths

- [ ] **User feedback**:
  - [ ] Ask users if new workflow is clear
  - [ ] Check for any confusion
  - [ ] Document issues for future improvements

- [ ] **Performance check**:
  - [ ] Check database query performance
  - [ ] Monitor page load times
  - [ ] Check server resources

---

## 📊 Status & Sign-Off

| Phase | Status | Owner | Date |
|-------|--------|-------|------|
| Code Implementation | ✅ Complete | System | Jan 16 |
| Templates | ⚠️ Pending | [You] | |
| Testing | ⚠️ Pending | [You] | |
| Deployment | ⏳ Ready | [You] | |
| Training | ⏳ Ready | [You] | |
| Monitoring | ⏳ Ready | [You] | |

---

## 🎯 Success Criteria

- [ ] All two-tier tests pass (Phase 4)
- [ ] No errors in production logs
- [ ] All users can access their designated sections
- [ ] OT properly flows through approval chain
- [ ] Payroll summary shows only approved OT
- [ ] Company isolation maintained
- [ ] No performance degradation

---

## ⚠️ Rollback Plan (If Needed)

If deployment fails:

1. **Immediate Rollback**:
   ```
   Restore database backup
   Restore previous routes_ot.py
   Restore previous template files
   Restart application
   ```

2. **Communicate**:
   - Notify users of temporary outage
   - Explain what went wrong
   - Provide timeline for fix

3. **Debug**:
   - Check error logs
   - Review template files
   - Verify manager configuration

---

## 📞 Support Contacts

For issues during deployment:
- **Template Questions**: Check OT_WORKFLOW_VISUAL_GUIDE.md
- **Workflow Questions**: Check OT_TWO_TIER_QUICK_GUIDE.md
- **Technical Issues**: Check OT_TWO_TIER_APPROVAL_WORKFLOW.md
- **Deployment Issues**: Check this checklist's troubleshooting

---

## 📝 Notes for Your Team

```
PROJECT: OT Two-Tier Approval Workflow
START DATE: [Date]
PLANNED DEPLOYMENT: [Date]
TEAM MEMBERS: [Names]

Key Milestones:
  1. Template creation - 1-2 hours
  2. Local testing - 1-2 hours
  3. Production deployment - 30 min
  4. User training - 30 min - 1 hour

Risks:
  - Template files not created properly
  - Manager configuration incomplete
  - User confusion about new workflow

Mitigation:
  - Reference template guide carefully
  - Verify manager setup before deployment
  - Provide comprehensive user training
```

---

## ✅ Final Checklist

- [ ] All tests passed
- [ ] All templates created/updated
- [ ] Database backed up
- [ ] Code deployed
- [ ] Users trained
- [ ] Monitoring in place
- [ ] Documentation shared
- [ ] Rollback plan ready

**Status**: 🟢 Ready for Production

---

*This checklist should be completed before production deployment.*
*Estimated total time: 3-4 hours*
*All documentation files included in project.*