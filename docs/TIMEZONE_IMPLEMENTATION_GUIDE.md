# Timezone Implementation Guide - Company-Level Configuration

## Overview

This document describes the timezone implementation at the company level. When marking attendance or overtime (OT), the current time shown in the system will be displayed in the logged-in user's company's local timezone.

## What Was Implemented

### 1. **Database Schema Changes**
- **File**: `migrations/versions/add_company_timezone.py`
- **Change**: Added `timezone` column to `hrm_company` table
- **Default Value**: `UTC`
- **Data Type**: `VARCHAR(50)` - Accepts IANA timezone identifiers

### 2. **Company Model Update**
- **File**: `models.py`
- **Changes**:
  - Added `timezone` field to Company class
  - Updated `to_dict()` method to include timezone
  - Timezone is stored and retrieved as IANA identifier (e.g., 'Asia/Singapore')

### 3. **API Routes Update**
- **File**: `routes_tenant_company.py`
- **Changes**:
  - Updated `create_company()` endpoint to accept timezone parameter
  - Updated `update_company()` endpoint to accept timezone parameter
  - Timezone defaults to 'UTC' if not provided

### 4. **UI/Template Update**
- **File**: `templates/masters/company_view.html`
- **Changes**:
  - Added timezone badge display in company information section
  - Added timezone dropdown selector in edit company modal
  - Updated JavaScript functions to handle timezone field

### 5. **Timezone Utilities Module**
- **File**: `timezone_utils.py` (NEW)
- **Functions**:
  - `get_company_timezone(company)` - Get timezone for a company
  - `convert_utc_to_company_timezone(utc_datetime, company)` - Convert UTC time to company timezone
  - `convert_company_timezone_to_utc(local_datetime, company)` - Convert local time to UTC for storage
  - `get_current_time_in_company_timezone(company)` - Get current time in company's timezone
  - `format_time_for_display(datetime_obj, format_str)` - Format datetime for display
  - `get_timezone_offset_str(company)` - Get timezone offset string
  - `validate_timezone(timezone_str)` - Validate timezone identifier

## How to Use

### Setup

1. **Run the migration** to add timezone column:
```bash
flask db upgrade
```

2. **Set timezone for existing companies** (optional - they default to UTC):
```bash
# Via UI: Navigate to Company Details → Edit Company → Select Timezone
# Via API: PUT /api/companies/<company_id> with timezone parameter
```

### In Your Code

#### Example 1: Display Current Time in Company Timezone (Attendance Marking)

```python
from timezone_utils import get_current_time_in_company_timezone, format_time_for_display
from models import Company, User
from flask_login import current_user

# Get user's company
user_company = current_user.employee_profile.company

# Get current time in company's timezone
current_time = get_current_time_in_company_timezone(user_company)

# Format for display
display_time = format_time_for_display(current_time, "%Y-%m-%d %H:%M:%S")

print(f"Current time in {user_company.name}: {display_time}")
```

#### Example 2: Store Time in UTC, Display in Company Timezone

```python
from datetime import datetime
from timezone_utils import convert_utc_to_company_timezone, get_company_timezone
from models import Attendance, Company

# User submits attendance - time comes as local input
user_submitted_time = datetime.now()  # This is in user's local system time

# Get user's company
company = user.employee_profile.company

# Convert to UTC for storage
from timezone_utils import convert_company_timezone_to_utc
utc_time = convert_company_timezone_to_utc(user_submitted_time, company)

# Store in database
attendance = Attendance(
    employee_id=employee_id,
    attendance_date=utc_time.date(),
    check_in_time=utc_time,
    is_active=True
)
db.session.add(attendance)
db.session.commit()

# When displaying, convert back to company timezone
display_time = convert_utc_to_company_timezone(attendance.check_in_time, company)
print(f"Check-in time: {display_time.strftime('%Y-%m-%d %H:%M:%S')}")
```

#### Example 3: In Templates

```html
{% extends "base.html" %}
{% block content %}
<div class="container">
    <h2>Mark Attendance</h2>
    
    <!-- Display current company timezone -->
    <div class="alert alert-info">
        <strong>Company Timezone:</strong> {{ current_user.employee_profile.company.timezone or 'UTC' }}
    </div>
    
    <!-- Display current time in company timezone -->
    <div class="form-group">
        <label>Current Time (Company Timezone):</label>
        <input type="text" class="form-control" id="currentTime" readonly>
    </div>
    
    <!-- Time input -->
    <div class="form-group">
        <label>Check-in Time:</label>
        <input type="time" class="form-control" id="checkInTime" required>
    </div>
</div>

<script>
// Get current time in company timezone via AJAX
fetch('/api/current-time-in-company-timezone', {
    method: 'GET'
})
.then(response => response.json())
.then(data => {
    document.getElementById('currentTime').value = data.current_time;
});
</script>
{% endblock %}
```

#### Example 4: In Routes (Attendance/OT Marking)

```python
from flask import jsonify, request
from flask_login import current_user, login_required
from timezone_utils import get_current_time_in_company_timezone, format_time_for_display
from models import Attendance, Company, Employee
from datetime import datetime
from app import db

@app.route('/api/mark-attendance', methods=['POST'])
@login_required
def mark_attendance():
    """Mark attendance with timezone consideration"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        check_in_notes = data.get('notes', '')
        
        # Get employee and company
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'success': False, 'error': 'Employee not found'}), 404
        
        company = employee.company
        
        # Get current time in company's timezone
        current_time_company_tz = get_current_time_in_company_timezone(company)
        
        # Convert to UTC for storage (important!)
        from timezone_utils import convert_company_timezone_to_utc
        current_time_utc = convert_company_timezone_to_utc(
            current_time_company_tz.replace(tzinfo=None), 
            company
        )
        
        # Create attendance record
        attendance = Attendance(
            employee_id=employee_id,
            attendance_date=current_time_utc.date(),
            check_in_time=current_time_utc,
            notes=check_in_notes,
            is_active=True
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        # Return formatted time for display
        display_time = format_time_for_display(current_time_company_tz)
        
        return jsonify({
            'success': True,
            'message': f'Attendance marked at {display_time}',
            'timezone': company.timezone,
            'current_time': display_time
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
```

## Supported Timezones

Common supported timezones include:
- **UTC** - Coordinated Universal Time (default)
- **Asia/Singapore, Asia/Hong_Kong, Asia/Tokyo, Asia/Bangkok, Asia/Manila, Asia/Jakarta, Asia/Kolkata, Asia/Dubai**
- **America/New_York, America/Chicago, America/Los_Angeles, America/Denver, America/Toronto**
- **Europe/London, Europe/Paris, Europe/Berlin, Europe/Amsterdam, Europe/Istanbul**
- **Australia/Sydney, Australia/Melbourne**
- **Pacific/Auckland, Pacific/Fiji**

Full list of IANA timezones can be accessed via:
```python
from timezone_utils import get_all_timezones
all_timezones = get_all_timezones()
```

## Key Points

### Storage Strategy
- **Store everything in UTC** in the database for consistency
- **Display in company timezone** when showing to users
- This ensures data consistency and allows for timezone changes without data migration

### When to Use Which Function

| Function | Use Case |
|----------|----------|
| `get_current_time_in_company_timezone()` | Get current time for display |
| `convert_utc_to_company_timezone()` | Convert stored UTC time to display format |
| `convert_company_timezone_to_utc()` | Convert user input/local time to UTC for storage |
| `format_time_for_display()` | Format datetime for display |
| `get_timezone_offset_str()` | Get offset for display (e.g., "+08:00") |

### Migration Considerations

If you need to apply timezone to new time-based features:

1. **For Attendance**: Update the attendance marking endpoints to use `get_current_time_in_company_timezone()`
2. **For OT (Overtime)**: Update OT marking routes to use `convert_utc_to_company_timezone()` and `convert_company_timezone_to_utc()`
3. **For Reports**: Use `convert_utc_to_company_timezone()` when displaying historical data
4. **For Payroll**: Ensure payroll calculations consider company timezone for date-based calculations

## Testing

### Test Timezone Configuration

```python
# Test basic functions
from timezone_utils import validate_timezone, get_timezone_object
from pytz import UTC

# Validate timezone
assert validate_timezone('Asia/Singapore') == True
assert validate_timezone('Invalid/Timezone') == False

# Get timezone object
tz = get_timezone_object('Asia/Singapore')
assert tz.zone == 'Asia/Singapore'

print("✅ Timezone utilities working correctly!")
```

### Test Conversion

```python
from datetime import datetime
from timezone_utils import (
    convert_utc_to_company_timezone,
    convert_company_timezone_to_utc,
    get_current_time_in_company_timezone
)
from models import Company

# Create test company with Singapore timezone
company = Company(
    name='Test Company',
    code='TST',
    timezone='Asia/Singapore'
)

# Test conversions
utc_time = datetime(2025, 1, 24, 12, 0, 0)  # 12:00 UTC
sg_time = convert_utc_to_company_timezone(utc_time, company)
print(f"UTC: {utc_time}, Singapore: {sg_time}")
# Expected: UTC: 2025-01-24 12:00:00+00:00, Singapore: 2025-01-24 20:00:00+08:00

print("✅ Timezone conversions working correctly!")
```

## Troubleshooting

### Issue: "Unknown timezone error"
- Check that the timezone string uses IANA format (e.g., 'Asia/Singapore', not 'Singapore')
- Validate using `validate_timezone()`

### Issue: Time is off by several hours
- Ensure times are stored in UTC in the database
- Always convert user input to UTC before storing
- Convert to company timezone only for display

### Issue: Daylight Saving Time issues
- IANA timezones handle DST automatically
- No special handling needed

## Future Enhancements

1. **Employee-level timezone override** - Allow employees to set their own timezone preference
2. **Timezone dropdown in attendance UI** - Let users select timezone during marking
3. **Report timezone selector** - Let managers view reports in different timezones
4. **Timezone audit trail** - Track timezone changes for compliance

## API Endpoints

### Get current time in company timezone

```
GET /api/current-time-in-company-timezone
Response: {
    "success": true,
    "timezone": "Asia/Singapore",
    "current_time": "2025-01-24 20:30:45",
    "utc_time": "2025-01-24 12:30:45"
}
```

### List all supported timezones

```
GET /api/supported-timezones
Response: {
    "success": true,
    "timezones": [
        "UTC",
        "Asia/Singapore",
        "Asia/Hong_Kong",
        ...
    ]
}
```

## References

- [IANA Timezone Database](https://www.iana.org/time-zones)
- [Python pytz Documentation](https://pypi.org/project/pytz/)
- [UTC Time Explanation](https://en.wikipedia.org/wiki/Coordinated_Universal_Time)