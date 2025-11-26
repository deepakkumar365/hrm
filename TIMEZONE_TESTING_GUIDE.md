# 🧪 Timezone Display Testing Guide

## Quick Start - Test in 5 Minutes

### Step 1: Open Browser & Login (1 min)
1. Open your HRMS application in browser
2. Login with your employee account
3. Navigate to: **OT Management → Mark OT Attendance**

### Step 2: Verify Live Clock Display (1 min)
Look for the **colorful clock display** in the form:
```
┌─────────────────────────────────────┐
│ Current Time in India - Kolkata (IST)│
│          06:51 AM                     │
└─────────────────────────────────────┘
```

✅ **Expected Behavior:**
- Clock shows actual local time (e.g., 06:51 AM NOT "UTC+5:30")
- Clock updates every second (watch the seconds change)
- Background is purple gradient
- Text is white and easy to read

❌ **If you see issues:**
- Clock shows `--:-- --` → Check browser console (F12)
- Time doesn't match your timezone → Change timezone dropdown
- Clock doesn't update → Refresh page

### Step 3: Check Auto-Selected Timezone (1 min)
Below the live clock, look for:
```
Timezone dropdown with company timezone pre-selected
Help text: "🌍 Your company timezone: Asia/Singapore"
```

✅ **Expected Behavior:**
- Timezone dropdown already has a timezone selected (not blank)
- Help text shows your company's timezone
- Example: If company is in India, should show "Asia/Kolkata"

### Step 4: Test "Set In" Button (1 min)
1. Click the **"Set In"** button (with ▶️ icon)
2. Look at the **"In Time"** field above the buttons
3. Should automatically populate with current time (e.g., 06:51)

✅ **Expected Behavior:**
- Time field shows: **06:51** (or current time in 24-hour format)
- NOT showing decimal format like "06.51" or "UTC+5:30"
- Button has subtle animation when clicked

❌ **If you see:**
- Time field stays empty → Check browser console for errors
- Time shows UTC time instead of local → Timezone not set correctly
- Time shows different value each click → This is normal (current time updates)

### Step 5: Test Console Logs (1 min)
1. Open **Developer Console** (F12 key)
2. Click **"Set In"** button again
3. Look for message in Console tab:
```
✅ Set ot_in_time to 06:51 (06:51 AM) in Asia/Kolkata
```

✅ **Expected Console Output:**
- Green checkmark (✅)
- Shows field name: `ot_in_time`
- Shows time in 24-hour: `06:51`
- Shows 12-hour format: `(06:51 AM)`
- Shows timezone: `Asia/Kolkata`

---

## Detailed Testing Scenarios

### Scenario 1: India Employee Testing

**Setup:**
- Company timezone: `Asia/Kolkata`
- Current IST time: 06:51 AM
- Browser timezone: Any timezone

**Test Steps:**
```
1. Open Mark OT Attendance page
2. Verify clock shows "06:51 AM" (not "UTC+5:30")
3. Timezone dropdown should show "Asia/Kolkata" selected
4. Click "Set In" → In Time field shows "06:51"
5. Console shows: "...in Asia/Kolkata"
```

**Success Criteria:**
- ✅ All times shown in 12-hour format (HH:MM AM/PM)
- ✅ Clock updates every second
- ✅ Timezone dropdown pre-selected with company timezone
- ✅ Console logs show correct timezone

---

### Scenario 2: Singapore Employee Testing

**Setup:**
- Company timezone: `Asia/Singapore`
- Current SGT time: 02:21 PM
- Browser timezone: Any timezone

**Test Steps:**
```
1. Open Mark OT Attendance page
2. Verify clock shows "02:21 PM" (not "UTC+8")
3. Timezone dropdown should show "Asia/Singapore" selected
4. Click "Set Out" → Out Time field shows "14:21"
5. Console shows: "...in Asia/Singapore"
```

**Success Criteria:**
- ✅ Singapore time displayed correctly (12-hour format)
- ✅ Timezone dropdown shows Singapore timezone
- ✅ Time conversion working accurately

---

### Scenario 3: Timezone Switching Test

**Test Steps:**
```
1. Open Mark OT Attendance
2. Note current time in live clock (e.g., "06:51 AM" for India)
3. Click timezone dropdown
4. Change to different timezone (e.g., "Asia/Singapore")
5. Watch live clock update
```

**Expected:**
- Clock time changes when you switch timezone
- Example: India (IST) 06:51 AM → Singapore (SGT) 09:21 AM (2.5 hours difference)

**Calculation Example:**
```
India (UTC+5:30): 06:51 AM
Add 2.5 hours
Singapore (UTC+8): 09:21 AM ✅
```

---

### Scenario 4: Mark OT with Timezone

**Test Steps:**
```
1. Open Mark OT Attendance
2. Select OT Date: Today
3. Click "Set In" → captures current time in employee's timezone
4. Click "Set Out" → captures current time + time buffer
5. Enter OT Hours or keep In/Out times
6. Select OT Type
7. Click "Mark OT"
```

**Verification:**
```sql
-- Check database to verify timezone was saved
SELECT id, ot_date, ot_in_time, ot_out_time, timezone 
FROM hrm_ot_attendance 
WHERE employee_id = 'YOUR_ID' 
ORDER BY created_at DESC 
LIMIT 1;
```

---

## Troubleshooting Guide

### Problem 1: Clock Shows "--:-- --"

**Possible Causes:**
1. JavaScript error in browser
2. Timezone value not set correctly
3. Browser doesn't support Intl API

**Solution:**
```
1. Press F12 to open Developer Tools
2. Click "Console" tab
3. Look for red error messages
4. Refresh page (Ctrl+R)
5. Check if timezone dropdown has a value selected
```

### Problem 2: Timezone Dropdown is Blank

**Possible Cause:**
- Backend not passing `company_timezone` variable

**Solution:**
```python
# Check that routes_ot.py has this code:
company = Company.query.get(company_id)
company_timezone = company.timezone if company and company.timezone else 'Asia/Singapore'

# And passes it to template:
return render_template('ot/mark_attendance.html',
    ...
    company_timezone=company_timezone)
```

### Problem 3: Time Doesn't Update in Clock

**Possible Cause:**
- JavaScript setInterval not running
- Browser performance issue

**Solution:**
```
1. Refresh page
2. Wait 2 seconds for initial clock display
3. Watch for second-by-second changes
4. Check console for any JavaScript errors
5. Try different browser
```

### Problem 4: "Set In" Button Doesn't Work

**Possible Cause:**
1. OT Types not configured
2. JavaScript error
3. Button is disabled

**Solution:**
```
1. Check if OT Types are configured in Masters > OT Types
2. Open console (F12) to check for errors
3. Verify timezone dropdown has a value
4. Check if buttons are disabled (grey out appearance)
```

### Problem 5: Database Doesn't Have Timezone Column

**Solution:**
```sql
-- Check if column exists:
SELECT column_name FROM information_schema.columns 
WHERE table_name = 'hrm_company';

-- If timezone column missing, add it:
ALTER TABLE hrm_company
ADD COLUMN timezone VARCHAR(50) NOT NULL DEFAULT 'UTC';
```

---

## Browser Console Testing

### View All Console Logs

1. Press **F12** to open Developer Tools
2. Click **"Console"** tab
3. Try clicking "Set In" and "Set Out" buttons
4. Should see messages like:
```
✅ Set ot_in_time to 06:51 (06:51 AM) in Asia/Kolkata
✅ Set ot_out_time to 09:15 (09:15 AM) in Asia/Kolkata
```

### Common Console Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `Cannot read property 'value' of null` | Timezone dropdown missing | Check HTML for `id="ot_timezone"` |
| `Intl.DateTimeFormat is not a function` | Old browser | Update browser to latest version |
| `undefined is not an object` | JavaScript syntax error | Check template file for typos |

---

## Performance Testing

### Check Page Load Time
```
1. Open Network tab (F12 > Network)
2. Refresh page
3. Note the load time
4. Should load in < 2 seconds
5. Live clock should start updating immediately
```

### Check Clock Update Frequency
```
1. Open Console tab
2. Add manual logging: document.body.style.opacity = 0.99;
3. Watch the console for messages
4. Clock should update every 1 second (not too fast, not too slow)
```

---

## Data Verification Checklist

After marking an OT record, verify the data:

```
✅ In Time shows correct time in your timezone
✅ Out Time shows correct time in your timezone
✅ Duration calculation is accurate
✅ OT Type is selected correctly
✅ Notes are saved (if provided)
✅ Status shows "Draft"
✅ Employee name matches
✅ OT Date matches selected date
```

---

## Quick Test Command (Python)

Run the verification script:
```bash
python verify_timezone_implementation.py
```

This will check:
- ✅ Backend files contain timezone code
- ✅ Frontend files have live clock
- ✅ Database has timezone column
- ✅ All features are implemented

---

## Next Steps After Testing

### If All Tests Pass ✅
1. **Deploy to Production**
   ```bash
   git add .
   git commit -m "feat: Implement timezone display for Attendance & OT modules"
   git push
   ```

2. **Update Company Timezone Settings**
   - Go to Tenant Configuration
   - Set each company's timezone
   - Verify employees see correct timezone

3. **Inform Employees**
   - Announce: "OT Module now displays times in your local timezone"
   - Provide testing instructions
   - Create help document

### If Tests Fail ❌
1. Check console for JavaScript errors (F12 > Console)
2. Verify all files were edited correctly
3. Restart Flask development server
4. Clear browser cache (Ctrl+Shift+Delete)
5. Re-run verification script

---

## Support & Questions

**For questions about:**
- **Time Display Format** → Check if showing "06:51 AM" (12-hour with period)
- **Timezone Selection** → Verify dropdown auto-selects company timezone
- **Clock Updates** → Check if updates every second (not faster/slower)
- **Database Storage** → Check if timezone saved with OT record

**Debug Tips:**
1. Always check browser console (F12)
2. Refresh page completely (Ctrl+Shift+R)
3. Try different browser to isolate issues
4. Check server logs for backend errors
