# OT Draft Save Feature - Complete Guide

## Overview

This feature allows employees to **save their OT "Set In" time as a draft** without immediately submitting the full OT record. The draft persists across page refreshes, allowing users to update the "Set Out" time later and submit when ready.

---

## What Was Added

### Backend (routes_ot.py)

#### 1. **Save OT Draft Endpoint** - `/api/ot/save-draft` (POST)
Saves OT attendance as draft with only Set In date and OT date. This allows partial data to be saved without requiring Set Out.

**Request Format:**
```json
{
  "ot_date": "2025-09-15",
  "ot_in_time": "18:30",
  "ot_type_id": 1,
  "notes": "Optional notes"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OT Set In time saved as draft successfully!",
  "ot_date": "2025-09-15",
  "ot_in_time": "18:30"
}
```

**Validations:**
- ✅ OT date is required
- ✅ Set In time is required
- ✅ OT Type is required (can be added later if needed)
- ✅ Date cannot be in the future
- ✅ Employee profile must exist

#### 2. **Get OT Draft Endpoint** - `/api/ot/get-draft` (GET)
Retrieves existing OT draft for a specific date to populate the form.

**Request:**
```
GET /api/ot/get-draft?ot_date=2025-09-15
```

**Response (if draft exists):**
```json
{
  "success": true,
  "ot_date": "2025-09-15",
  "ot_id": 123,
  "status": "Draft",
  "ot_in_time": "18:30",
  "ot_out_time": null,
  "ot_hours": null,
  "ot_type_id": 1,
  "notes": "Optional notes"
}
```

**Response (if no draft exists):**
```json
{
  "success": false,
  "message": "No draft found"
}
```

---

### Frontend (mark_attendance.html)

#### 1. **Save Draft Button**
Added a new **amber/orange "SAVE DRAFT"** button to the form:
- Located between the form fields and Submit button
- Shows loading state while saving
- Displays success/error messages
- Styled with gradient: `#f59e0b` to `#d97706`

#### 2. **Save Draft Function** - `saveDraft()`
JavaScript function that:
- Validates Set In time is provided
- Calls `/api/ot/save-draft` endpoint
- Shows loading spinner while saving
- Displays success/error notification
- Logs to browser console

**Validation checks:**
- OT date required
- Set In time required
- OT Type required
- Date cannot be future

#### 3. **Load Draft Function** - `loadDraft(otDate)`
JavaScript function that:
- Calls `/api/ot/get-draft` endpoint
- Populates form fields with saved draft data
- Auto-switches to correct mode (time or hours)
- Shows info notification when draft is loaded
- Silently ignores if no draft exists
- Logs loaded data to browser console

#### 4. **Auto-Load on Page Load**
When the page loads:
1. Loads draft for today's date (if exists)
2. Sets up listener for date changes
3. Auto-loads draft when user changes the OT date

---

## How It Works - Step by Step

### Scenario: Employee Working Overtime

**Step 1: Open Mark OT Form**
```
Dashboard → Mark OT
```

**Step 2: Fill Set In Time**
1. Select OT Date (e.g., 2025-09-15)
2. Select OT Type (e.g., "Weekday OT")
3. Click "Set In" button or manually enter time
   - Example: 18:30

**Step 3: Save as Draft**
1. Click **"SAVE DRAFT"** button
2. Form shows: "OT Set In time saved as draft successfully!"
3. Data is saved to database
4. Browser console shows: `[DRAFT SAVED] {ot_date: "2025-09-15", ot_in_time: "18:30", ...}`

**Step 4: Leave/Refresh Page**
- Navigate to other menus
- Refresh the page
- Close and reopen the form
- **All draft data persists!**

**Step 5: Return Later to Complete**
1. Open Mark OT again
2. Select same date (2025-09-15)
3. **Draft auto-loads!**
   - Set In time: 18:30 (populated)
   - OT Type: Selected (populated)
   - Notes: Restored (if any)
4. Now set "Set Out" time (e.g., 21:30)
5. Click "Submit Attendance" to finalize

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Employee Opens Form                       │
├─────────────────────────────────────────────────────────────┤
│  loadDraft(todayDate) called automatically                  │
│  ↓                                                            │
│  fetch(/api/ot/get-draft?ot_date=2025-09-15)               │
│  ↓                                                            │
│  If draft exists:                                            │
│    - ot_in_time → Populate field                             │
│    - ot_out_time → Populate field                            │
│    - ot_hours → Populate field                               │
│    - ot_type_id → Populate select                            │
│    - Show "Draft loaded" info notification                   │
│  Else:                                                        │
│    - Show blank form (normal behavior)                       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  Employee Clicks "Save Draft"                │
├─────────────────────────────────────────────────────────────┤
│  saveDraft() called                                          │
│  ↓                                                            │
│  Validate fields:                                            │
│    - OT date ✅                                              │
│    - Set In time ✅                                          │
│    - OT Type ✅                                              │
│  ↓                                                            │
│  fetch(POST /api/ot/save-draft)                             │
│  ↓                                                            │
│  Backend saves to DB:                                        │
│    - OTAttendance.ot_date = 2025-09-15                      │
│    - OTAttendance.ot_in_time = 18:30                        │
│    - OTAttendance.status = "Draft"                          │
│  ↓                                                            │
│  Response: success = true                                    │
│  ↓                                                            │
│  Show: "OT Set In time saved as draft successfully!"        │
│  Log: [DRAFT SAVED] {ot_date, ot_in_time, ...}             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            Employee Changes Date or Refreshes Page           │
├─────────────────────────────────────────────────────────────┤
│  User changes OT Date to 2025-09-16                          │
│  ↓                                                            │
│  loadDraft("2025-09-16") triggered                           │
│  ↓                                                            │
│  fetch(/api/ot/get-draft?ot_date=2025-09-16)               │
│  ↓                                                            │
│  If draft for 16th exists → Load it                         │
│  If no draft for 16th → Show blank form                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Changes

**No database schema changes required!**

The feature uses the existing `OTAttendance` table:
- `ot_date` - Date of overtime
- `ot_in_time` - Set In time (can be NULL initially)
- `ot_out_time` - Set Out time (can be NULL for drafts)
- `ot_hours` - OT hours (can be NULL for drafts)
- `ot_type_id` - Type of overtime
- `status` - Already set to 'Draft'
- `notes` - Optional notes
- `created_at` - Auto-set
- `modified_at` - Updated when draft is saved

---

## Testing Guide

### Test 1: Save a Draft
1. Go to **Dashboard → Mark OT**
2. Select today's date
3. Select an OT Type
4. Click "Set In" button (or enter manually)
5. Enter notes (optional)
6. Click **"SAVE DRAFT"** button
7. ✅ See success message: "OT Set In time saved as draft successfully!"
8. Check browser console (F12): Should see `[DRAFT SAVED]` with data

### Test 2: Verify Draft Persists After Refresh
1. After saving draft (from Test 1)
2. Refresh the page (F5)
3. Same date should be selected
4. ✅ All draft fields should be populated
5. ✅ Info message: "Draft loaded for 2025-09-15. You can now add Set Out time and submit."

### Test 3: Complete Draft Submission
1. From the loaded draft (from Test 2)
2. Click "Set Out" button or enter manually
3. Click **"Submit Attendance"** button
4. ✅ Form submits successfully
5. ✅ Status changes from Draft to Submitted

### Test 4: Multiple Dates
1. Select date 1 (e.g., 2025-09-15)
2. Set In time: 18:30
3. Save Draft
4. Change date to 2025-09-14
5. Set In time: 19:00
6. Save Draft
7. Change date to 2025-09-15
8. ✅ Should see 18:30 loaded (not 19:00)

### Test 5: Navigate Away
1. Save a draft
2. Click Dashboard or other menu
3. Return to **Mark OT**
4. ✅ Draft still loaded for today's date

---

## Browser Console Logs

When using the feature, check browser console (F12 → Console) for these logs:

**When saving draft:**
```
[DRAFT SAVED] {ot_date: "2025-09-15", ot_in_time: "18:30", ot_type_id: 1, ...}
```

**When loading draft:**
```
[DRAFT LOADED] {ot_date: "2025-09-15", ot_in_time: "18:30", ot_out_time: null, ...}
✅ Loaded Set In: 18:30
✅ Loaded OT Type ID: 1
✅ Loaded Notes: Your notes here
```

**When no draft exists:**
```
No draft found for this date (this is normal): ...
```

---

## API Reference

### POST /api/ot/save-draft

**Purpose:** Save OT attendance as draft with Set In time only

**Request:**
```bash
curl -X POST http://localhost:5000/api/ot/save-draft \
  -H "Content-Type: application/json" \
  -d '{
    "ot_date": "2025-09-15",
    "ot_in_time": "18:30",
    "ot_type_id": 1,
    "notes": "Working on project X"
  }'
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "OT Set In time saved as draft successfully!",
  "ot_date": "2025-09-15",
  "ot_in_time": "18:30"
}
```

**Error Responses:**
```json
// 400 - Missing required fields
{
  "success": false,
  "message": "Set In time is required"
}

// 403 - Employee profile not found
{
  "success": false,
  "message": "Employee profile required"
}

// 500 - Server error
{
  "success": false,
  "message": "Error saving draft: ..."
}
```

### GET /api/ot/get-draft

**Purpose:** Get existing OT draft for a specific date

**Request:**
```bash
curl http://localhost:5000/api/ot/get-draft?ot_date=2025-09-15
```

**Success Response (200):**
```json
{
  "success": true,
  "ot_date": "2025-09-15",
  "ot_id": 123,
  "status": "Draft",
  "ot_type_id": 1,
  "notes": "Working on project X",
  "ot_in_time": "18:30",
  "ot_out_time": null,
  "ot_hours": null
}
```

**No Draft Response (404):**
```json
{
  "success": false,
  "message": "No draft found"
}
```

---

## Features Summary

| Feature | Details |
|---------|---------|
| **Save Draft** | Save Set In time without Set Out - persists across refreshes |
| **Auto-Load Draft** | Automatically loads when you select the same date |
| **Partial Completion** | Can save with only Set In, complete later with Set Out |
| **Multiple Drafts** | Can have drafts for multiple different dates |
| **Error Handling** | Validates all inputs before saving |
| **User Feedback** | Shows success/error notifications and console logs |
| **Date Validation** | Prevents future dates |
| **No Schema Changes** | Uses existing OTAttendance table |

---

## Troubleshooting

### Q: Draft isn't loading when I select the date
**A:** Check browser console (F12). If you see "No draft found...", it means no draft exists for that date. This is normal - drafts are only created when you click "Save Draft".

### Q: I saved a draft but it disappeared after page refresh
**A:** Check the browser console for errors. The draft should auto-load. If it's not:
1. Verify you clicked "Save Draft" (not "Clear Form")
2. Check that the same date is selected
3. Check database: `SELECT * FROM hrm_ot_attendance WHERE employee_id = X AND ot_date = '2025-09-15';`

### Q: Set Out time isn't loading from draft
**A:** Set Out is optional for drafts. Only Set In is required. Add Set Out time and click "Save Draft" again, then refresh to verify it saves.

### Q: Getting "Employee profile required" error
**A:** Make sure you're logged in as an employee (not Super Admin). Navigate to Dashboard → Mark OT as a regular employee.

### Q: Console shows error when loading draft
**A:** This is normal if no draft exists. The loadDraft function catches the error silently. If you're getting a different error, check the browser console details.

---

## Files Modified

1. **D:/DEV/HRM/hrm/routes_ot.py**
   - Added `save_ot_draft()` endpoint (POST /api/ot/save-draft)
   - Added `get_ot_draft()` endpoint (GET /api/ot/get-draft)

2. **D:/DEV/HRM/hrm/templates/ot/mark_attendance.html**
   - Added "SAVE DRAFT" button
   - Added `saveDraft()` JavaScript function
   - Added `loadDraft()` JavaScript function
   - Modified DOMContentLoaded to auto-load drafts
   - Added date change listener

---

## Future Enhancements

Possible improvements:
- [ ] Add undo/discard draft functionality
- [ ] Show list of all drafts for past dates
- [ ] Auto-save draft periodically while editing
- [ ] Add draft expiration after X days
- [ ] Show draft status indicator in recent OT records list
- [ ] Allow draft duplication for quick creation

---

## Support

If you encounter any issues:
1. Check browser console (F12) for error messages
2. Verify employee profile exists
3. Ensure you're not Super Admin
4. Check database for draft records
5. Review backend logs in server console