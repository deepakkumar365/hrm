# OT Payroll Summary - Test Checklist ✅

## Pre-Testing Setup

### Database & Migration
- [ ] App started successfully without errors
- [ ] Migration auto-ran on startup (check logs for "Migration completed")
- [ ] Database table `hrm_ot_daily_summary` created
- [ ] All indexes created successfully

### User Setup
- [ ] Logged in as HR Manager, Tenant Admin, or Super Admin
- [ ] User has valid employee profile with company assigned
- [ ] PayrollConfiguration exists for test employees (with ot_rate_per_hour)

---

## Feature Tests

### 1. Navigation & Access Control

#### Test 1.1: Menu Navigation
- [ ] Navigate to OT Management menu
- [ ] See "Payroll Summary (Grid)" option (new)
- [ ] Click link successfully loads page
- [ ] Page title shows "OT Payroll Summary"

#### Test 1.2: Access Control - HR Manager
- [ ] Log in as HR Manager
- [ ] Can access OT Payroll Summary grid
- [ ] Can only see own company's records (if Tenant Admin, see all)

#### Test 1.3: Access Control - Regular Employee
- [ ] Log in as regular employee
- [ ] Try to access /ot/daily-summary
- [ ] Get "Access Denied" message
- [ ] Redirected to dashboard

#### Test 1.4: Access Control - Manager (Non-HR)
- [ ] Log in as reporting manager (not HR)
- [ ] Try to access /ot/daily-summary
- [ ] Get "Access Denied" message

---

### 2. Date Filter & Display

#### Test 2.1: Date Filter
- [ ] Page loads with today's date by default
- [ ] Click date picker, select different date
- [ ] Grid refreshes with records for selected date
- [ ] URL updates with ?date=YYYY-MM-DD parameter

#### Test 2.2: No Records Scenario
- [ ] Select date with no OT records
- [ ] Display "No OT Records" message with icon
- [ ] Show "Add New" button in message
- [ ] Statistics show 0 across all cards

#### Test 2.3: With Records Scenario
- [ ] Select date with OT records
- [ ] Grid displays all employees with OT on that date
- [ ] Columns display correctly
- [ ] Statistics cards show accurate totals

---

### 3. Grid Display & Columns

#### Test 3.1: Column Headers
- [ ] All 21 columns visible and properly aligned
- [ ] Column headers clear and readable
- [ ] Table has sticky header (scrolls with body)
- [ ] No horizontal scroll issues on desktop

#### Test 3.2: Employee Data
- [ ] Employee name displays correctly
- [ ] Employee ID shows
- [ ] Department name shows
- [ ] All rows have unique employee identifiers

#### Test 3.3: OT Data
- [ ] OT Hours column shows correct values
- [ ] OT Rate/Hr shows (read-only)
- [ ] OT Amount shows calculated value
- [ ] All numeric columns aligned right

#### Test 3.4: Allowance Columns
- [ ] All 12 allowance columns visible
  - KD & CLAIM
  - TRIPS
  - SINPOST
  - SANDSTONE
  - SPX
  - PSLE
  - MANPOWER
  - STACKING
  - DISPOSE
  - NIGHT
  - PH
  - SUN
- [ ] All columns display current values
- [ ] Columns are input fields (editable)

#### Test 3.5: Total & Summary Columns
- [ ] Total Allowances shows sum of all allowance columns
- [ ] Grand Total shows OT Amount + Total Allowances
- [ ] Both columns update in real-time as user edits

---

### 4. Statistics Cards

#### Test 4.1: Summary Cards
- [ ] "Total Records" card shows count of employees
- [ ] "Total OT Hours" card shows sum of all hours
- [ ] "Total OT Amount" card shows sum of OT amounts
- [ ] "Total Allowances" card shows sum of allowances
- [ ] "Grand Total" card shows final payable amount

#### Test 4.2: Card Styling
- [ ] Cards are visually distinct with different colors
- [ ] Values are large and readable
- [ ] Labels are clear

---

### 5. Edit OT Hours

#### Test 5.1: Edit OT Hours Field
- [ ] Click on OT Hours input field
- [ ] Field becomes editable (cursor visible)
- [ ] Type new hours value (e.g., 3.5)
- [ ] Field accepts decimal values

#### Test 5.2: Auto-Calculate OT Amount
- [ ] Change OT Hours from 2.0 to 3.0
- [ ] OT Amount automatically updates
- [ ] Calculation correct: 3.0 × OT Rate = new OT Amount
- [ ] No manual save needed for calculation
- [ ] Grand Total updates automatically

#### Test 5.3: Validation
- [ ] Negative values not accepted (min="0")
- [ ] Decimal values accepted (step="0.5")
- [ ] Very large values accepted (no max limit)
- [ ] Empty values handled gracefully

---

### 6. Edit Allowance Fields

#### Test 6.1: Edit Single Allowance
- [ ] Click on KD & CLAIM field
- [ ] Type value (e.g., 500)
- [ ] Field accepts decimal values
- [ ] Move to next field (tab key)

#### Test 6.2: Auto-Calculate Total Allowances
- [ ] Set KD & CLAIM = 500
- [ ] Set TRIPS = 200
- [ ] Set SINPOST = 150
- [ ] Total Allowances updates: 500+200+150 = 850
- [ ] Calculation automatic, no manual entry needed

#### Test 6.3: Update Grand Total
- [ ] As allowances update, Grand Total updates
- [ ] Formula: OT Amount + Total Allowances
- [ ] Displayed in Grand Total column
- [ ] Color-coded (amber/orange) for visibility

#### Test 6.4: Edit Multiple Allowances
- [ ] Edit all 12 allowance columns
- [ ] Verify all updates are captured
- [ ] Total Allowances sums correctly
- [ ] No data loss during editing

---

### 7. Save Functionality

#### Test 7.1: Save Button Click
- [ ] Click "Save" button on a row
- [ ] Button shows "Saving..." state
- [ ] Button becomes disabled during save
- [ ] Save completes (shows "Save" again)

#### Test 7.2: Save Success
- [ ] Save returns success message
- [ ] Totals remain correct after save
- [ ] Data persists in database
- [ ] No page reload needed

#### Test 7.3: Save Multiple Records
- [ ] Edit record 1 and save
- [ ] Edit record 2 and save
- [ ] Edit record 3 and save
- [ ] All records save independently
- [ ] No conflicts between saves

#### Test 7.4: Save Validation
- [ ] Try to save with invalid data
- [ ] Error message displayed
- [ ] Save button not disabled on error
- [ ] Can retry after fixing data

---

### 8. Add New Record

#### Test 8.1: Open Add New Modal
- [ ] Click "Add New" button
- [ ] Modal dialog opens
- [ ] Modal has proper title and close button
- [ ] Modal appears centered on screen

#### Test 8.2: Select Employee
- [ ] Modal loads with employee dropdown
- [ ] Employee list shows all active employees
- [ ] Employees show: Name (ID)
- [ ] Can select any employee

#### Test 8.3: Select Date
- [ ] Date field shows current selected date
- [ ] Can change date in modal
- [ ] Date picker shows calendar

#### Test 8.4: Create Record
- [ ] Select employee
- [ ] Select date
- [ ] Click "Add Record"
- [ ] Record created successfully
- [ ] Modal closes
- [ ] New row appears in grid
- [ ] OT rate pre-populated from payroll config

#### Test 8.5: Duplicate Prevention
- [ ] Try to add same employee for same date
- [ ] Get error: "Record already exists"
- [ ] Record not duplicated

#### Test 8.6: Cancel Add New
- [ ] Click "Cancel" button in modal
- [ ] Modal closes without saving
- [ ] No record created

---

### 9. Calendar View

#### Test 9.1: Open Calendar Modal
- [ ] Click calendar icon (📅) on employee row
- [ ] Modal opens with employee name
- [ ] Modal title shows: "Daily Breakdown - [Employee Name]"

#### Test 9.2: Calendar Display
- [ ] Calendar shows current month
- [ ] Days of week headers visible
- [ ] All days of month visible
- [ ] Days aligned in grid correctly

#### Test 9.3: Calendar Data
- [ ] Days with OT show in green background
- [ ] Days with OT show: Date number, OT hours, OT total amount
- [ ] Days without OT show blank
- [ ] Previous month dates (empty cells) at start
- [ ] Next month dates (empty cells) at end

#### Test 9.4: Calendar Details
- [ ] Click on a day with OT data
- [ ] Shows breakdown: Hours, Amount, Allowances, Total
- [ ] All values correct for that day
- [ ] Multiple records on same day shown correctly

#### Test 9.5: Close Calendar Modal
- [ ] Click close button (X)
- [ ] Modal closes
- [ ] Grid still visible and unchanged

---

### 10. Real-Time Calculations

#### Test 10.1: OT Amount Calculation
- [ ] OT Hours: 2.5
- [ ] OT Rate: 200
- [ ] OT Amount should be: 500 ✓
- [ ] Edit OT Hours to 3.0
- [ ] OT Amount updates to: 600 ✓

#### Test 10.2: Allowances Calculation
- [ ] KD&CLAIM: 300
- [ ] TRIPS: 200
- [ ] SINPOST: 100
- [ ] SANDSTONE: 150
- [ ] SPX: 50
- [ ] Others: 0
- [ ] Total Allowances: 800 ✓

#### Test 10.3: Grand Total Calculation
- [ ] OT Amount: 600
- [ ] Total Allowances: 800
- [ ] Grand Total: 1400 ✓
- [ ] Edit any value, Grand Total updates ✓

#### Test 10.4: Complex Scenario
```
Initial:
- OT Hours: 2.0
- OT Rate: 250
- OT Amount: 500
- All allowances: 0
- Total Allowances: 0
- Grand Total: 500

Edit 1: Increase OT Hours to 4.0
- OT Amount updates to 1000
- Grand Total updates to 1000

Edit 2: Add allowances
- KD&CLAIM: 400, TRIPS: 300, NIGHT: 200
- Total Allowances: 900
- Grand Total updates to 1900

Edit 3: Reduce OT Hours to 3.0
- OT Amount updates to 750
- Grand Total updates to 1650
```
- [ ] All calculations correct at each step

---

### 11. Performance & UI

#### Test 11.1: Page Load
- [ ] Page loads within 2 seconds
- [ ] No console errors
- [ ] All elements render correctly
- [ ] Loader indicator appears then disappears

#### Test 11.2: Grid Performance
- [ ] Grid scrolls smoothly horizontally
- [ ] Grid scrolls smoothly vertically
- [ ] No lag when editing fields
- [ ] No lag when clicking buttons

#### Test 11.3: Responsive Design
- [ ] Page works on desktop (1920x1080)
- [ ] Page works on tablet (1024x768)
- [ ] Grid has horizontal scrollbar on mobile
- [ ] All buttons clickable on touch devices

#### Test 11.4: Styling & Colors
- [ ] Summary cards styled correctly
- [ ] Grid rows alternate colors (striped)
- [ ] Hover effect on rows
- [ ] Buttons have hover effects
- [ ] Input fields have focus styles

---

### 12. Data Persistence

#### Test 12.1: Save & Reload
- [ ] Edit records and save
- [ ] Refresh page
- [ ] Data persists (still shows saved values)
- [ ] No data loss on reload

#### Test 12.2: Multi-User Scenario
- [ ] User A edits record 1
- [ ] User A saves
- [ ] User B views same record
- [ ] User B sees User A's changes
- [ ] Timestamp shows when User A modified

#### Test 12.3: Concurrent Edits
- [ ] User A opens record 1
- [ ] User B opens same record 1
- [ ] User A edits and saves
- [ ] User B sees updated values
- [ ] No data conflicts

---

### 13. Error Handling

#### Test 13.1: Invalid Date
- [ ] Enter invalid date format
- [ ] Show appropriate error message
- [ ] Page still functional

#### Test 13.2: Network Error
- [ ] Simulate network failure during save
- [ ] Show error message
- [ ] Allow retry

#### Test 13.3: Server Error
- [ ] Simulate server 500 error
- [ ] Show user-friendly error message
- [ ] Don't show technical details to user

#### Test 13.4: Missing Data
- [ ] Try to save with missing OT rate
- [ ] Show validation error
- [ ] Prevent incomplete save

---

### 14. Audit Trail

#### Test 14.1: Created By
- [ ] Create new record
- [ ] Check created_by field = current username
- [ ] Check created_at timestamp = current time

#### Test 14.2: Modified By
- [ ] Update existing record
- [ ] Check modified_by field = current username
- [ ] Check modified_at timestamp = update time

#### Test 14.3: Audit Trail Accuracy
- [ ] Multiple edits tracked correctly
- [ ] Timestamps accurate
- [ ] Username matches logged-in user

---

### 15. Data Validation Rules

#### Test 15.1: Numeric Fields
- [ ] OT Hours: Min 0, max unlimited
- [ ] All allowances: Min 0, max unlimited
- [ ] Decimal values accepted (2 places)
- [ ] Negative values rejected

#### Test 15.2: Required Fields
- [ ] Employee required for new record
- [ ] Date required for new record
- [ ] Cannot save with missing values

#### Test 15.3: Unique Constraints
- [ ] Cannot create duplicate employee/date combo
- [ ] Get error if trying to duplicate
- [ ] Duplicate prevented automatically

---

### 16. Integration Tests

#### Test 16.1: With PayrollConfiguration
- [ ] Employee with OT rate shows correct rate
- [ ] Employee without OT rate shows 0
- [ ] OT amount calculated using PayrollConfiguration rate

#### Test 16.2: With OTRequest
- [ ] New OTDailySummary links to OTRequest (if exists)
- [ ] Can create without OTRequest (manual entry)
- [ ] Reference maintained in database

#### Test 16.3: With Employee Records
- [ ] Employee name displays correctly
- [ ] Employee ID displays correctly
- [ ] Department displays correctly
- [ ] Deleted employees not shown

#### Test 16.4: With Company Filtering
- [ ] Tenant Admin sees all companies' records
- [ ] HR Manager sees only own company
- [ ] Super Admin sees all records

---

## Performance Benchmarks

### Target Performance
- [ ] Page load time: < 2 seconds
- [ ] Grid render: < 1 second
- [ ] Save operation: < 500ms
- [ ] Calendar load: < 300ms

### Load Testing
- [ ] Test with 100 rows of data
- [ ] Test with 1000 rows of data
- [ ] Grid remains responsive
- [ ] No memory leaks

---

## Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Browser DevTools Tests

#### Test Console
- [ ] No JavaScript errors
- [ ] No console warnings
- [ ] No network errors

#### Test Network Tab
- [ ] All API calls successful (200 status)
- [ ] No failed requests
- [ ] Reasonable response times

#### Test Application Tab
- [ ] LocalStorage working (if used)
- [ ] Session data persists

---

## Final Checklist

### Ready for Production?
- [ ] All feature tests pass
- [ ] All edge cases handled
- [ ] Error messages user-friendly
- [ ] Performance acceptable
- [ ] Security validated
- [ ] Data integrity verified
- [ ] Documentation complete
- [ ] User tested and approved

### Sign-Off
- [ ] QA Testing: __________ Date: ______
- [ ] UAT Testing: __________ Date: ______
- [ ] Production Deploy: __________ Date: ______

---

## Notes & Issues Found

```
Issue #1: [Description]
Status: [ ] Open [ ] Fixed [ ] Wontfix
Details: ...

Issue #2: [Description]
Status: [ ] Open [ ] Fixed [ ] Wontfix
Details: ...
```

---

**Test Date**: __________
**Tested By**: __________
**Environment**: [ ] Development [ ] Staging [ ] Production
**Result**: [ ] Pass [ ] Fail [ ] Partial

---

## Sign-Off

- **QA Lead**: _________________ Date: _______
- **Project Manager**: _________________ Date: _______
- **Product Owner**: _________________ Date: _______