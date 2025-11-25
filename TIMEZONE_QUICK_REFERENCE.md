# ⏰ Timezone Implementation - Quick Reference

## 📋 What Was Done

Added company-level timezone configuration to display attendance/OT times in the company's local timezone.

## 🆕 New Files Created

| File | Purpose |
|------|---------|
| `timezone_utils.py` | Core timezone utility functions |
| `routes_timezone.py` | Timezone-related API endpoints |
| `migrations/versions/add_company_timezone.py` | Database migration |
| `docs/TIMEZONE_IMPLEMENTATION_GUIDE.md` | Comprehensive guide |
| `docs/TIMEZONE_DEPLOYMENT_CHECKLIST.md` | Deployment guide |

## ✏️ Files Modified

| File | Changes |
|------|---------|
| `models.py` | Added `timezone` field to Company model |
| `routes_tenant_company.py` | Updated create/update company to handle timezone |
| `templates/masters/company_view.html` | Added timezone display and selector |
| `main.py` | Added import for `routes_timezone` |

## 🚀 Quick Start

### 1. Run Migration
```bash
flask db upgrade
```

### 2. Configure Company Timezone
**Via UI**: Companies → Edit Company → Select Timezone

**Via API**:
```bash
curl -X PUT http://localhost:5000/api/companies/<id>/timezone \
  -H "Content-Type: application/json" \
  -d '{"timezone": "Asia/Singapore"}'
```

### 3. Use in Your Code
```python
from timezone_utils import (
    get_current_time_in_company_timezone,
    convert_utc_to_company_timezone,
    convert_company_timezone_to_utc
)

# Get current time in company timezone
company = current_user.employee_profile.company
current_time = get_current_time_in_company_timezone(company)

# Convert UTC to company timezone for display
display_time = convert_utc_to_company_timezone(utc_datetime, company)

# Convert company timezone to UTC for storage
utc_time = convert_company_timezone_to_utc(local_datetime, company)
```

## 📍 Supported Timezones

**Common ones**:
- UTC (default)
- Asia/Singapore, Asia/Hong_Kong, Asia/Tokyo, Asia/Bangkok, Asia/Manila, Asia/Jakarta
- America/New_York, America/Los_Angeles, America/Toronto
- Europe/London, Europe/Paris, Europe/Berlin
- Australia/Sydney, Australia/Melbourne

**Get all**: `from timezone_utils import get_all_timezones()`

## 🔌 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/supported-timezones` | GET | List all timezones |
| `/api/current-time-in-company-timezone` | GET | Get current time in user's company tz |
| `/api/timezone/<company_id>` | GET | Get company timezone info |
| `/api/validate-timezone` | POST | Validate timezone string |
| `/api/timezone-comparison` | POST | Compare time across timezones |
| `/api/companies/<id>/timezone` | GET/PUT | Get/Update company timezone |
| `/api/my-timezone` | GET | Get user's company timezone |

## 💡 Common Patterns

### Pattern 1: Display Attendance Time
```python
# In route handler
attendance = Attendance.query.get(id)
company = attendance.employee.company

# Convert UTC to company timezone
display_time = convert_utc_to_company_timezone(attendance.check_in_time, company)
return jsonify({
    'time': display_time.strftime('%Y-%m-%d %H:%M:%S'),
    'timezone': company.timezone
})
```

### Pattern 2: Mark Attendance
```python
# Get current time in company timezone
company_time = get_current_time_in_company_timezone(company)

# Convert to UTC for storage
from timezone_utils import convert_company_timezone_to_utc
utc_time = convert_company_timezone_to_utc(company_time.replace(tzinfo=None), company)

# Save to database
attendance = Attendance(
    employee_id=emp_id,
    check_in_time=utc_time  # Stored as UTC
)
db.session.add(attendance)
db.session.commit()
```

### Pattern 3: In Templates
```html
<!-- Display company timezone info -->
<div class="timezone-badge">
  Timezone: <strong>{{ current_user.employee_profile.company.timezone }}</strong>
</div>

<!-- Display time from company timezone -->
<p>Current Time: <span id="currentTime"></span></p>

<script>
fetch('/api/current-time-in-company-timezone')
  .then(r => r.json())
  .then(data => {
    document.getElementById('currentTime').textContent = data.current_time;
  });
</script>
```

## ✅ Key Points to Remember

| Point | Important |
|-------|-----------|
| **Store Times** | Always in UTC in database |
| **Display Times** | Always convert to company timezone |
| **Existing Data** | Treated as UTC (no migration needed) |
| **Default Timezone** | UTC (for backward compatibility) |
| **Timezone Format** | IANA identifiers (e.g., 'Asia/Singapore') |
| **Daylight Saving** | Handled automatically by pytz |

## 🐛 Debugging

### Check Timezone for Company
```python
from models import Company
company = Company.query.first()
print(f"Timezone: {company.timezone}")
```

### Test Timezone Conversion
```python
from timezone_utils import convert_utc_to_company_timezone
from datetime import datetime

company = Company.query.first()
utc_time = datetime(2025, 1, 24, 12, 0, 0)
company_time = convert_utc_to_company_timezone(utc_time, company)
print(f"UTC: {utc_time}, Company: {company_time}")
```

### Validate Timezone String
```python
from timezone_utils import validate_timezone

print(validate_timezone('Asia/Singapore'))  # True
print(validate_timezone('Invalid/TZ'))      # False
```

## 📚 Documentation

| Document | Content |
|----------|---------|
| `TIMEZONE_IMPLEMENTATION_GUIDE.md` | Detailed guide with examples |
| `TIMEZONE_IMPLEMENTATION_SUMMARY.md` | Summary of changes |
| `TIMEZONE_DEPLOYMENT_CHECKLIST.md` | Deployment steps |
| `TIMEZONE_QUICK_REFERENCE.md` | This file |

## ⚡ Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| pytz not found | `pip install pytz` |
| Migration fails | Run `flask db upgrade` |
| Timezone not updating | Restart Flask app |
| Time still in UTC | Use `convert_utc_to_company_timezone()` |
| Wrong timezone in DB | Check Company model has timezone value |

## 🔄 Data Flow

```
User Input (Local Time)
    ↓
convert_company_timezone_to_utc()
    ↓
Store in Database (UTC)
    ↓
Retrieve from Database
    ↓
convert_utc_to_company_timezone()
    ↓
Display to User (Company Timezone)
```

## 📊 Example Use Cases

### Use Case 1: Attendance System
```
1. Employee clicks "Mark Attendance"
2. System gets current time in company timezone
3. Time is displayed: "2025-01-24 20:30:45"
4. System converts to UTC and stores: "2025-01-24 12:30:45"
5. When displaying: Shows as "20:30:45" (company timezone)
```

### Use Case 2: OT Marking
```
1. Employee marks OT in Singapore (UTC+8)
2. Local time: 18:00
3. Stored as UTC: 10:00
4. Display to manager: 18:00 (Singapore time)
5. Payroll system uses UTC: 10:00 for calculations
```

### Use Case 3: Multi-Location Reporting
```
1. Company A (Singapore, UTC+8): Shows 20:00
2. Company B (London, UTC+0): Shows 12:00
3. Company C (NYC, UTC-5): Shows 07:00
All stored as same UTC time: 12:00
```

## 🎯 Next Steps

1. **Deploy**: Run migration and deploy code
2. **Configure**: Set timezone for each company
3. **Update Routes**: Use timezone in attendance/OT routes
4. **Test**: Verify times display correctly
5. **Monitor**: Watch for timezone-related issues

## 🔗 Related Features

- Attendance marking - Should use company timezone for current time
- OT marking - Should use company timezone for current time  
- Leave calculations - Could use company timezone for date boundaries
- Payroll processing - Should respect company timezone
- Reports - Should display in company timezone

## 📞 Quick Links

- **Migration**: `migrations/versions/add_company_timezone.py`
- **Utilities**: `timezone_utils.py`
- **Routes**: `routes_timezone.py`
- **Model**: `models.py` (Company class)
- **Template**: `templates/masters/company_view.html`
- **Guide**: `docs/TIMEZONE_IMPLEMENTATION_GUIDE.md`

---

**Last Updated**: 2025-01-24  
**Version**: 1.0  
**Status**: Ready for Production