# OT Draft Save Feature - Quick Start

## 🎯 What's New?

**NEW BUTTON: "SAVE DRAFT"** in Mark OT Attendance form

Allows employees to:
- ✅ Save "Set In" time without "Set Out"
- ✅ Come back later to add "Set Out" time
- ✅ Data persists after page refresh
- ✅ No data loss when navigating away

---

## 🚀 How to Use

### Step 1: Open Mark OT Form
**Dashboard → Mark OT**

### Step 2: Set Your In Time
1. Select OT Date
2. Select OT Type
3. Click "Set In" button or enter time manually
4. (Optional) Add notes

### Step 3: Click "SAVE DRAFT" Button
- **New amber/orange button** between form and submit
- Shows success message: "OT Set In time saved as draft successfully!"
- Data saved to database

### Step 4: Leave Safely
- Navigate away
- Refresh page
- Close browser
- **Draft persists!**

### Step 5: Return to Complete
1. Open Mark OT again
2. Select same date
3. **Draft auto-loads!** (info message shows)
4. Add "Set Out" time
5. Click "Submit Attendance"

---

## 📍 Where to Find the Button

```
┌─────────────────────────────────────────┐
│  Mark OT Attendance Form                 │
├─────────────────────────────────────────┤
│  [OT Date Input]                         │
│  [OT Type Dropdown]                      │
│  [Set In Time]                           │
│  [Set Out Time]                          │
│  [OT Hours]                              │
│  [Notes TextArea]                        │
├─────────────────────────────────────────┤
│ [SAVE DRAFT] [SUBMIT] [CLEAR FORM]      │  ← New button!
└─────────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Details |
|---------|---------|
| **Automatic Load** | When you select a date, draft auto-loads if it exists |
| **Validation** | Requires Set In time + OT Type before saving |
| **Error Messages** | Clear feedback if something goes wrong |
| **Console Logs** | Browser console (F12) shows [DRAFT SAVED] and [DRAFT LOADED] |
| **Multiple Drafts** | Can have drafts for different dates |
| **No Submission Required** | Save without being "Submitted" status |

---

## 🧪 Quick Test

1. **Save a Draft:**
   - Go to Mark OT
   - Set In: 18:30
   - OT Type: Weekday OT
   - Click "SAVE DRAFT"
   - ✅ Success message shown

2. **Refresh Page:**
   - Press F5
   - ✅ All fields still populated
   - ✅ Info message: "Draft loaded for..."

3. **Complete It:**
   - Set Out: 21:30
   - Click "Submit Attendance"
   - ✅ Form submits successfully

---

## 📱 Visual Indicators

**SAVE DRAFT Button:**
- Color: Amber/Orange gradient
- Icon: Floppy disk
- Text: "SAVE DRAFT"
- Position: Left of "Submit Attendance" button

**Success Message (Green):**
```
✅ OT Set In time saved as draft successfully!
```

**Draft Loaded Message (Blue Info):**
```
ℹ️  Draft loaded for 2025-09-15. You can now add Set Out time and submit.
```

---

## 🔍 Debug: Check Browser Console

Press **F12** and look for:

**When saving:**
```
[DRAFT SAVED] {ot_date: "2025-09-15", ot_in_time: "18:30", ...}
```

**When loading:**
```
[DRAFT LOADED] {ot_date: "2025-09-15", ot_in_time: "18:30", ...}
✅ Loaded Set In: 18:30
✅ Loaded OT Type ID: 1
```

---

## ⚠️ Things to Know

- ✅ **Works**: Save with only Set In time, no Set Out required
- ✅ **Works**: Data persists after page refresh
- ✅ **Works**: Change date and see corresponding draft
- ❌ **Doesn't Work**: Future dates (system prevents)
- ❌ **Doesn't Work**: Without OT Type selected
- ❌ **Doesn't Work**: Without Set In time

---

## 🆘 Troubleshooting

**Q: Draft didn't save**
- Check browser console for errors
- Verify Set In time is entered
- Verify OT Type is selected

**Q: Draft didn't load after refresh**
- Check if same date is selected
- Check browser console (F12)
- Verify draft was actually saved (not just form filled)

**Q: Getting error message**
- Read the error message carefully
- Check browser console for details
- Verify all required fields are filled

---

## 📞 Need More Info?

See full documentation: **OT_DRAFT_SAVE_FEATURE.md**

Contains:
- Complete API reference
- Data flow diagrams
- Detailed test cases
- Troubleshooting guide
- Future enhancements