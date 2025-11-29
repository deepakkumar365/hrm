# Timezone Offset Display Implementation

## Overview
This document describes the implementation of displaying timezone information in offset format (e.g., "+8:00", "-5:00") on the "Attendance > Mark Attendance" page, along with a live current time display based on the logged user's company configuration.

## Changes Made

### 1. Backend Changes: `routes.py` (Line 2446-2485)

#### What Changed:
Updated the `attendance_mark()` route to provide timezone offset and current datetime information to the template.

#### Before:
```python
    return render_template('attendance/form.html',
                           today_attendance=today_attendance,
                           company_timezone=company_timezone)
```

#### After:
```python
    # Get timezone offset in format like "+8:00" or "-5:00"
    if company:
        timezone_offset = get_timezone_offset_str(company)
        # Get current datetime in company timezone
        current_datetime_company_tz = datetime.now(utc).astimezone(company_tz_obj)
    
    return render_template('attendance/form.html',
                           today_attendance=today_attendance,
                           company_timezone=company_timezone,
                           timezone_offset=timezone_offset,
                           current_datetime_company_tz=current_datetime_company_tz)
```

#### New Variables Passed:
- **`timezone_offset`** (str): Timezone offset like "+8:00", "-5:00", "+5:30"
- **`current_datetime_company_tz`** (datetime): Current datetime in company's timezone

#### Utility Function Used:
- **`get_timezone_offset_str(company)`** from `timezone_utils.py`: Converts timezone name to UTC offset format

---

### 2. Frontend Changes: `templates/attendance/form.html`

#### Change 2a: Display Timezone Label (Line 795-798)

**BEFORE:**
```html
<div class="clock-label" style="margin-top: 0.4rem; font-size: 0.55rem; opacity: 0.9;" id="timezoneLabel">{{ company_timezone }}</div>
```

**AFTER:**
```html
<div class="clock-label" style="margin-top: 0.4rem; font-size: 0.55rem; opacity: 0.9;" id="timezoneLabel">
    <span id="timezoneNameLabel">{{ company_timezone }}</span>
    <span id="timezoneOffsetLabel" style="margin-left: 0.3rem; font-weight: 600;">{{ timezone_offset }}</span>
</div>
```

**What Changed:**
- Split timezone display into two parts
- Shows both timezone name (e.g., "Asia/Singapore") and offset (e.g., "+8:00")
- Offset is now bolded for emphasis

---

#### Change 2b: Add JavaScript Variables (Line 1064-1066)

**BEFORE:**
```javascript
    // Update live clock based on selected timezone
    function updateLiveClock() {
        const timezone = document.getElementById('timezoneDropdown').value || '{{ company_timezone }}';
        const timeStr = getTimeInTimezone(timezone);
        document.getElementById('digitalClock').textContent = timeStr;
    }
```

**AFTER:**
```javascript
    // Company timezone from backend
    const companyTimezone = '{{ company_timezone }}' || 'UTC';
    const timezoneOffset = '{{ timezone_offset }}' || '+00:00';
    
    // Update live clock based on company timezone
    function updateLiveClock() {
        const timeStr = getTimeInTimezone(companyTimezone);
        document.getElementById('digitalClock').textContent = timeStr;
    }
```

**What Changed:**
- Added global variables for timezone and offset
- Removed dependency on dropdown (which doesn't exist)
- Clock now uses company timezone directly

---

#### Change 2c: Update `updateGreeting()` Function (Line 1079-1081)

**BEFORE:**
```javascript
    function updateGreeting() {
        const timezone = document.getElementById('timezoneDropdown').value || '{{ company_timezone }}';
```

**AFTER:**
```javascript
    function updateGreeting() {
        const timezone = companyTimezone;
```

**What Changed:**
- Uses global variable instead of dropdown
- Greeting is now based on company timezone

---

#### Change 2d: Simplify DOMContentLoaded (Line 1202-1216)

**BEFORE:**
```javascript
    document.addEventListener('DOMContentLoaded', function() {
        // Auto-select company timezone
        const companyTimezone = '{{ company_timezone }}';
        const timezoneDropdown = document.getElementById('timezoneDropdown');
        if (companyTimezone && timezoneMap[companyTimezone]) {
            timezoneDropdown.value = companyTimezone;
        }
        
        // Initial updates
        updateClock();
        updateGreeting();
        updateDate();
        updateStatus();
        getLocation();

        // Update clock every second with timezone awareness
        setInterval(function() {
            updateClock();
            updateGreeting();
        }, 1000);
        
        // Add event listener for timezone changes
        timezoneDropdown.addEventListener('change', updateTimezone);
    });
```

**AFTER:**
```javascript
    document.addEventListener('DOMContentLoaded', function() {
        // Initial updates
        updateClock();
        updateGreeting();
        updateDate();
        updateStatus();
        getLocation();

        // Update clock every second with timezone awareness
        setInterval(function() {
            updateClock();
            updateGreeting();
        }, 1000);
    });
```

**What Changed:**
- Removed all references to non-existent dropdown
- Removed event listener registration
- Cleaner, simpler initialization code

---

## Visual Result

### On Attendance Mark Page:
The user will now see:

```
Current Time: 14:35:42
Asia/Singapore +8:00
```

Where:
- **"14:35:42"** updates every second (live clock)
- **"Asia/Singapore"** shows the company timezone name
- **"+8:00"** shows the UTC offset for that timezone

If the company was in New York, it would show:
```
Current Time: 02:35:42
America/New_York -5:00
```

---

## Technical Details

### Timezone Offset Format
The offset format follows ISO 8601 standard:
- **Positive offset**: "+HH:MM" (e.g., "+8:00" for Singapore, "+5:30" for India)
- **Negative offset**: "-HH:MM" (e.g., "-5:00" for New York, "-8:00" for Los Angeles)

### How It Works
1. Backend fetches the company timezone (e.g., "Asia/Singapore")
2. Converts to UTC offset format using `get_timezone_offset_str()` from `timezone_utils.py`
3. Passes both the timezone name and offset to the template
4. JavaScript uses the timezone name to get the current time using browser's `Intl.DateTimeFormat` API
5. Clock updates every second using the company's timezone

### Browser Compatibility
- Uses JavaScript `Intl.DateTimeFormat` API which is supported in all modern browsers
- Automatically handles daylight saving time transitions

---

## Files Modified

1. **`routes.py`** - Updated `attendance_mark()` route (lines 2446-2485)
2. **`templates/attendance/form.html`** - Updated timezone display and JavaScript (lines 795-798, 1064-1216)

## Verification Steps

1. Log in as an employee
2. Navigate to "Attendance > Mark Attendance"
3. Verify:
   - Live clock updates every second
   - Shows correct current time in company timezone
   - Shows both timezone name and UTC offset
   - Greeting updates based on company timezone time