# Fix: Clock In "Already Clocked In" Error on Next Day

## Problem
When a new day arrives (midnight), users were getting "Already clocked in for today" error when trying to clock in on the new day. This happened even though they had clocked in on the previous day.

## Root Cause
The system was using **inconsistent timezone logic** to determine the current date:

1. **Main attendance route** (`/attendance/mark` in routes.py):
   - Used employee's personal timezone (which often defaulted to UTC)
   - If employee had no timezone set, defaulted to 'UTC'
   - If company was in a different timezone (e.g., Asia/Kolkata = UTC+5:30), the date calculation would be wrong
   - Previous day's record would still be considered "today" on the next calendar day

2. **Mobile API** (`/api/attendance/mark` in routes_api.py):
   - Used `date.today()` which is the server's local date
   - Not timezone-aware at all

3. **OT Mark Attendance** (`/ot/mark` in routes_ot.py):
   - Used `datetime.now().date()` which is the server's local date
   - Same timezone issue as API

## Solution Implemented

### 1. Main Attendance Route (routes.py)
**Changed from:**
```python
employee_tz_str = current_user.employee_profile.timezone or 'UTC'
employee_tz = timezone(employee_tz_str)
now_utc = datetime.now(utc)
today = now_utc.astimezone(employee_tz).date()
current_time = now_utc.time()  # UTC time!
```

**Changed to:**
```python
timezone_str = current_user.company.timezone if current_user.company else 'UTC'
company_tz = timezone(timezone_str)
now_utc = datetime.now(utc)
today = now_utc.astimezone(company_tz).date()
current_time = now_utc.astimezone(company_tz).time()  # Company timezone time
```

**Benefits:**
- All employees in a company use the same timezone for date calculation
- Company timezone is authoritative, not employee's personal timezone
- Time values are also in company timezone, not UTC

### 2. Mobile API (routes_api.py)
**Changed from:**
```python
today = date.today()  # Server local date
now = datetime.now()  # No timezone info
```

**Changed to:**
```python
company = employee.company
timezone_str = company.timezone if company else 'UTC'
company_tz = timezone(timezone_str)
now_utc = datetime.now(utc)
today = now_utc.astimezone(company_tz).date()
current_time = now_utc.astimezone(company_tz)
```

**Additional fixes:**
- Fixed field names: `check_in`/`check_out` → `clock_in`/`clock_out`
- Set timezone field on attendance records
- Added consistency with main route

### 3. OT Mark Attendance (routes_ot.py)
**Changed from:**
```python
today = datetime.now().date()  # Server local date
```

**Changed to:**
```python
company = Company.query.get(company_id)
timezone_str = company.timezone if company else 'UTC'
company_tz = timezone(timezone_str)
now_utc = datetime.now(utc)
today = now_utc.astimezone(company_tz).date()
```

## Testing Instructions

1. **Verify Company Timezone is Set:**
   - Go to Settings/Tenant Configuration
   - Ensure your company has a timezone configured (e.g., `Asia/Kolkata`, `America/New_York`, etc.)

2. **Test Clock In on New Day:**
   - Clock in on Day 1 at 9:00 AM
   - Wait for Day 2 (or manually change system date)
   - Try to clock in on Day 2
   - **Expected:** Should create a new attendance record
   - **Should NOT see:** "Already clocked in for today" warning

3. **Test Multiple Days:**
   - Clock in/out on Day 1
   - Clock in/out on Day 2
   - Verify each day has its own attendance record in the database

4. **Test Mobile API:**
   - Use POST `/api/attendance/mark` with proper company timezone
   - Verify attendance records are created with correct dates

## Database Impact
- No schema changes required
- Existing attendance records remain unchanged
- Only new/updated records will have correct timezone-aware dates

## Files Modified
1. `routes.py` - Line 2361-2378 (attendance_mark function)
2. `routes_api.py` - Line 579-626 (mobile_api_mark_attendance function)
3. `routes_ot.py` - Line 211-217 (mark_ot_attendance function)

## Deployment Notes
- No migrations needed
- Can be deployed immediately
- Restart Flask application to apply changes
- Existing attendance records are not affected