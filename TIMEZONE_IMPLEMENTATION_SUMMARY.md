# Timezone Implementation - Quick Summary

## 🎯 What Was Done

Implemented company-level timezone configuration to display attendance and OT times in the company's local timezone instead of UTC/server time.

## 📝 Files Modified/Created

### 1. **Database Model** (`models.py`)
- Added `timezone` field to Company model
- Default value: `'UTC'`
- Updated `Company.to_dict()` method

### 2. **Database Migration** (NEW)
- **File**: `migrations/versions/add_company_timezone.py`
- Adds timezone column to hrm_company table with UTC default

### 3. **API Routes** (`routes_tenant_company.py`)
- Updated `create_company()` - accepts timezone parameter
- Updated `update_company()` - accepts timezone parameter in updatable_fields

### 4. **Timezone Utilities** (NEW)
- **File**: `timezone_utils.py`
- Comprehensive timezone utility functions:
  - `convert_utc_to_company_timezone()` - UTC → Company timezone (for display)
  - `convert_company_timezone_to_utc()` - Company timezone → UTC (for storage)
  - `get_current_time_in_company_timezone()` - Get current time in company timezone
  - `get_company_timezone()` - Get timezone for a company
  - `format_time_for_display()` - Format datetime for UI
  - `validate_timezone()` - Validate timezone strings
  - `get_all_timezones()` - List all supported timezones

### 5. **Frontend Template** (`templates/masters/company_view.html`)
- Added timezone badge display in company information section
- Added timezone dropdown selector in edit company modal
- Updated JavaScript functions to handle timezone field

### 6. **Documentation** (NEW)
- **File**: `docs/TIMEZONE_IMPLEMENTATION_GUIDE.md`
- Comprehensive guide with examples and usage patterns

## 🚀 How to Use

### Step 1: Run Migration
```bash
flask db upgrade
```

### Step 2: Configure Company Timezone
Navigate to: **Companies → Select Company → Edit → Timezone Dropdown**

### Step 3: Use in Your Code

```python
from timezone_utils import get_current_time_in_company_timezone, convert_utc_to_company_timezone
from models import Company
from flask_login import current_user

# Get user's company
company = current_user.employee_profile.company

# Get current time in company's timezone
current_time = get_current_time_in_company_timezone(company)
print(current_time)  # 2025-01-24 20:30:45+08:00 (for Singapore)

# Convert UTC time to company timezone for display
from datetime import datetime
utc_time = datetime.now()
company_time = convert_utc_to_company_timezone(utc_time, company)
```

### Step 4: Update Your Attendance/OT Routes

For **attendance marking** or **OT marking**, use:

```python
from timezone_utils import (
    get_current_time_in_company_timezone,
    convert_company_timezone_to_utc
)

# Store in UTC
company = user.employee_profile.company
company_time = get_current_time_in_company_timezone(company)
utc_time = convert_company_timezone_to_utc(company_time.replace(tzinfo=None), company)

# Save to database
attendance.check_in_time = utc_time  # Stored as UTC

# Display to user (convert back to company timezone)
display_time = convert_utc_to_company_timezone(attendance.check_in_time, company)
```

## 📊 Supported Timezones

- **UTC** (default)
- **Asia**: Singapore, Hong Kong, Tokyo, Bangkok, Manila, Jakarta, Kolkata, Dubai
- **Americas**: New York, Chicago, Los Angeles, Denver, Toronto
- **Europe**: London, Paris, Berlin, Amsterdam, Istanbul
- **Australia/Pacific**: Sydney, Melbourne, Auckland, Fiji

See `timezone_utils.py` for full list or use `get_all_timezones()` function.

## ⚡ Key Design Decisions

1. **Store in UTC**: All times stored in database as UTC for consistency
2. **Display in Company Timezone**: Converted to company timezone for UI display
3. **IANA Identifiers**: Using standard IANA timezone strings (e.g., 'Asia/Singapore')
4. **Backward Compatible**: Existing companies default to UTC, no data migration needed
5. **No Data Loss**: Timezone changes don't require re-processing historical data

## 🔍 What Happens When

| Action | Storage | Display |
|--------|---------|---------|
| User marks attendance at 2 PM (Singapore) | Stores as 6 AM UTC | Shows as 2 PM Singapore |
| System logs OT entry | Stores as UTC | Shows in company timezone |
| Generate report | Reads from UTC storage | Converts to company timezone |

## ✅ Testing Checklist

- [ ] Run migration: `flask db upgrade`
- [ ] Navigate to Company Edit and verify timezone dropdown
- [ ] Select a company and change timezone
- [ ] Verify timezone is saved and displays in company view
- [ ] Import timezone_utils and test functions:
  ```python
  from timezone_utils import validate_timezone
  print(validate_timezone('Asia/Singapore'))  # Should be True
  ```
- [ ] Update attendance/OT routes to use timezone utilities
- [ ] Test attendance/OT marking shows correct time

## 📖 Full Documentation

See: `docs/TIMEZONE_IMPLEMENTATION_GUIDE.md`

For detailed examples, API endpoints, and troubleshooting guide.

## 🔗 Related Code

- Model: `models.Company` (line 164-227)
- Routes: `routes_tenant_company.py` (lines 429-540)
- Utils: `timezone_utils.py`
- Template: `templates/masters/company_view.html`
- Migration: `migrations/versions/add_company_timezone.py`

## ⚠️ Important Notes

1. **Always convert to UTC before storing** times in the database
2. **Always convert from UTC to company timezone** when displaying
3. **Use pytz timezones** - they handle DST automatically
4. **Test with different timezones** before deploying to production
5. **Existing data is not affected** - already stored times remain as UTC

## 🛠️ Next Steps

1. Run migration to add timezone column
2. Set timezone for each company
3. Update attendance/OT marking routes to use timezone utilities
4. Update templates to display times using company timezone
5. Test end-to-end with different timezones

## 📞 Questions?

Refer to the comprehensive guide in `docs/TIMEZONE_IMPLEMENTATION_GUIDE.md` for:
- Detailed usage examples
- API endpoint documentation
- Troubleshooting section
- Testing procedures