# HR Manager - OT Approval User Guide

## Quick Start

### Access the OT Approval Dashboard

1. **Login** as HR Manager
2. **Navigate** to: Main Menu → **OT Management** → **Approval Dashboard**
3. You'll see all OT requests pending your approval

---

## Understanding the OT Approval Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│ OT Approval Dashboard                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  📊 Status: 3 Pending Requests                             │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Employee: Rajesh Kumar                              │  │
│  │  ID: EMP-2024-001 | Dept: Engineering               │  │
│  │                                           ⏳ Pending  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                      │  │
│  │  Hours Requested:  3.5 hrs                          │  │
│  │  OT Type:          Weekend Overtime                 │  │
│  │  Requested On:     15 Jan 2024                      │  │
│  │                                                      │  │
│  │  Reason: Project deadline - database optimization   │  │
│  │                                                      │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │  Comments:  [              Text area              ] │  │
│  │  Modified Hours: [         Optional input         ]  │  │
│  │                                                      │  │
│  │  [✓ Approve]  [✗ Reject]  [✎ Modify Hours]        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  More requests below...                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step: Approving an OT Request

### Option 1: Simple Approval (No Changes)

1. **Review** the OT request details
   - Check: Hours, Date, OT Type, Reason
   - Verify: Employee eligibility

2. **Leave comments empty** (optional)

3. **Click "Approve" button**
   - ✓ Status changes to **"APPROVED"**
   - ✓ OT is now ready for **Payroll**
   - ✓ Employee gets notification

---

### Option 2: Approval with Comments

1. **Review** the OT request

2. **Add comments** (e.g., "Approved as per project deadline")

3. **Click "Approve" button**
   - ✓ Your comments are saved
   - ✓ Status changes to **"APPROVED"**
   - ✓ OT is ready for **Payroll**

---

### Option 3: Approval with Modified Hours

1. **Review** the OT request

2. **Click "Modify Hours" button**
   - The "Modified Hours" field becomes active

3. **Enter new hours** (e.g., 2.5 instead of 3.5)

4. **Optionally add comments** (e.g., "Reduced due to company policy")

5. **Click "Approve" button**
   - ✓ New hours are saved
   - ✓ Status changes to **"APPROVED"**
   - ✓ OT is ready for **Payroll** with modified hours

---

## Step-by-Step: Rejecting an OT Request

### When to Reject

- Employee didn't have pre-approval
- Overtime not needed/expected
- Hours exceed policy
- Invalid OT type
- Any other reason

### How to Reject

1. **Review** the OT request

2. **Add rejection comment** (REQUIRED - Explain why)
   - "This was not pre-approved"
   - "Exceeds company OT limit"
   - "Project deadline was met"
   - Be clear and professional!

3. **Click "Reject" button**
   - ✓ Your rejection comment is saved
   - ✓ Status changes to **"REJECTED"**
   - ✓ Request goes **back to Manager**
   - ✓ Manager sees your feedback

---

## Understanding Previous Comments

### When You See a "Previous Comments" Box

```
┌────────────────────────────────────────────────────┐
│  ⚠️  Previous Comments                             │
│  "This was not pre-approved by the department     │
│   Please get approval from your team lead first"   │
│  - HR Manager (14 Jan 2024)                       │
└────────────────────────────────────────────────────┘
```

**This means**:
- The Manager rejected this OT before
- The Employee/Manager is re-submitting it
- You need to decide: Approve or reject again?

### How to Handle Re-submissions

1. **Read the previous comments** to understand the issue
2. **Check if the issue is resolved**
3. **Decide**:
   - If resolved → **Approve**
   - If not resolved → **Reject** with new feedback
   - If unsure → **Add comment** asking for clarification before approving

---

## Important Rules

### ✓ DO:
- [x] Add comments when rejecting (always!)
- [x] Review the employee details carefully
- [x] Verify the OT type is valid
- [x] Check dates make sense
- [x] Be clear in your feedback

### ✗ DON'T:
- [ ] Approve without reviewing
- [ ] Reject without comments
- [ ] Modify hours without explaining why
- [ ] Approve invalid OT types
- [ ] Ignore previous rejection comments

---

## OT Workflow Timeline

```
1. Employee marks OT attendance (Draft) 
   ↓
2. Employee or HR submits for approval 
   ↓
3. MANAGER Level Approval
   - Manager reviews: Approve ✓ or Reject ✗
   - If rejected → Goes back to employee
   - If approved → Sends to HR Manager
   ↓
4. HR MANAGER Level Approval ← YOU ARE HERE
   ├─ [YOUR ACTION] Review and Approve/Reject
   ├─ If approved → Ready for Payroll ✓
   └─ If rejected → Back to Manager for review
   ↓
5. Payroll Processing
   - HR/Payroll uses approved OT hours
   - Calculates OT payment
   - Includes in salary
```

---

## Quick Reference

| Action | Field | Visible? |
|--------|-------|----------|
| **Review Reason** | Reason box (blue) | ✓ Yes, always |
| **Previous Feedback** | Previous Comments box (yellow) | ✓ If exists |
| **Add Your Feedback** | Comments textarea | ✓ Always |
| **Change Hours** | Modified Hours field | ✓ Click "Modify Hours" |
| **Approve** | Approve button | ✓ Always |
| **Reject** | Reject button | ✓ Always |

---

## Common Scenarios

### Scenario 1: Manager Approved, Now You Need to Approve

**What you see**:
- OT details with hours and reason
- Blue box with original employee reason
- No previous comments

**What to do**:
- Review the details
- Approve if everything looks good

**Expected result**: Status → "APPROVED", Ready for payroll ✓

---

### Scenario 2: Rejected Before, Employee Re-submitted

**What you see**:
- OT details
- **Yellow box** with "Previous Comments" showing why it was rejected
- New submission attempt

**What to do**:
1. Read the previous rejection reason
2. Check if it's been addressed
3. Approve or Reject accordingly

**Expected result**: 
- If fixed → Status → "APPROVED" ✓
- If not fixed → Status → "REJECTED" with new feedback

---

### Scenario 3: Hours Look Wrong

**What you see**:
- OT hours seem excessive for the task
- Maybe 8 hours for a 2-hour meeting?

**What to do**:
1. Add a comment asking for clarification (optional)
2. Click "Modify Hours" button
3. Change to reasonable hours (e.g., 2 hours)
4. Add comment: "Adjusted to actual overtime worked"
5. Click Approve

**Expected result**: Status → "APPROVED" with modified hours ✓

---

## Troubleshooting

### Problem: Can't see OT details

**Solution**: 
- Refresh the page (F5)
- Clear browser cache
- Contact IT support

### Problem: Can't click Approve/Reject buttons

**Solution**:
- Make sure you filled in required fields
- Check if browser has JavaScript enabled
- Try a different browser

### Problem: Approval doesn't save

**Solution**:
- Check internet connection
- Look for error message at top of page
- Try again
- Contact IT support

### Problem: Status hasn't changed after approval

**Solution**:
- Refresh page to see updated status
- Wait a few seconds and refresh
- Check if you saw confirmation message
- Contact IT support if still not working

---

## Tips for Efficiency

1. **Batch Processing**: Process multiple OT requests at once
   - Review all pending
   - Quick approve/reject decisions
   - Add brief comments
   - Move to next batch

2. **Template Comments**: Use consistent feedback
   - "Approved as per policy"
   - "Requires manager approval first"
   - "Exceeds monthly limit"

3. **Regular Review**: Check dashboard daily
   - Keep processing time short
   - Improve employee experience
   - Timely payroll processing

4. **Clear Feedback**: When rejecting
   - Explain the reason clearly
   - Tell them what to do next
   - Reference policy if applicable

---

## Need Help?

- **Email**: hr@company.com
- **Phone**: 1234-5678
- **In-App Help**: Click help icon (?)
- **FAQs**: [Link to HR Policies]

---

## Changelog - Fixed Issues

**Latest Update**: OT Approval Workflow Fixes
- ✓ Fixed: Approval status now updates correctly
- ✓ Fixed: Previous rejection comments now visible
- ✓ Fixed: All OT details display correctly
- ✓ Improved: User interface clarity
- ✓ Improved: Workflow efficiency

**Status**: All features working ✓
