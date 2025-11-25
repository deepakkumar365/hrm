# 📂 Timezone Implementation - File Structure

## 📋 Complete File Listing

### 🆕 **NEW FILES CREATED** (3)

```
hrm/
├── timezone_utils.py                           ⭐ NEW
│   ├── get_company_timezone()
│   ├── convert_utc_to_company_timezone()
│   ├── convert_company_timezone_to_utc()
│   ├── get_current_time_in_company_timezone()
│   ├── format_time_for_display()
│   ├── get_timezone_offset_str()
│   ├── validate_timezone()
│   ├── get_all_timezones()
│   └── SUPPORTED_TIMEZONES list
│
├── routes_timezone.py                          ⭐ NEW
│   ├── /api/supported-timezones (GET)
│   ├── /api/current-time-in-company-timezone (GET)
│   ├── /api/timezone/<company_id> (GET)
│   ├── /api/validate-timezone (POST)
│   ├── /api/timezone-comparison (POST)
│   ├── /api/companies/<id>/timezone (GET/PUT)
│   └── /api/my-timezone (GET)
│
└── migrations/versions/
    └── add_company_timezone.py                 ⭐ NEW
        ├── upgrade()   - Add timezone column
        └── downgrade() - Remove timezone column
```

### ✏️ **MODIFIED FILES** (5)

```
hrm/
├── models.py                                   📝 MODIFIED
│   └── Company class (line ~190-195)
│       ├── timezone = db.Column(...)
│       └── Updated to_dict() method
│
├── routes_tenant_company.py                    📝 MODIFIED
│   ├── create_company() (line ~466)
│   │   └── Added: timezone=data.get('timezone', 'UTC')
│   │
│   └── update_company() (line ~507)
│       └── Added 'timezone' to updatable_fields
│
├── templates/masters/company_view.html         📝 MODIFIED
│   ├── Line ~71:  Added timezone badge
│   ├── Lines ~268-296: Added timezone dropdown
│   ├── Line ~333: JavaScript - populate timezone
│   └── Line ~362: JavaScript - include timezone in update
│
├── main.py                                      📝 MODIFIED
│   └── Line ~40: import routes_timezone
│
└── app.py                                       ✅ NO CHANGES
    └── (No changes needed - pytz is standard library)
```

### 📚 **DOCUMENTATION FILES** (4 + this file)

```
docs/
├── TIMEZONE_IMPLEMENTATION_GUIDE.md            📖 NEW
│   ├── Overview & features
│   ├── Detailed usage guide
│   ├── Code examples (4 comprehensive examples)
│   ├── Supported timezones list
│   ├── Key points table
│   ├── Testing guide
│   ├── Troubleshooting section
│   ├── Future enhancements
│   └── API endpoint documentation
│
└── TIMEZONE_DEPLOYMENT_CHECKLIST.md            📖 NEW
    ├── Pre-deployment checklist
    ├── Deployment steps (6 steps)
    ├── Post-deployment testing (6 tests)
    ├── Monitoring guidelines
    ├── Rollback plan (3 options)
    ├── Troubleshooting (4 scenarios)
    └── Success criteria checklist

root/
├── TIMEZONE_QUICK_REFERENCE.md                 📖 NEW
│   ├── What was done
│   ├── Quick start (3 steps)
│   ├── Supported timezones
│   ├── API endpoints table
│   ├── Common patterns (3 patterns)
│   ├── Key points table
│   ├── Debugging guide
│   ├── Data flow diagram
│   ├── Use cases (3 scenarios)
│   └── Quick links
│
├── TIMEZONE_IMPLEMENTATION_SUMMARY.md          📖 NEW
│   ├── What was done
│   ├── Files created/modified list
│   ├── How to use (4 steps)
│   ├── Supported timezones
│   ├── Key design decisions
│   ├── Testing checklist
│   ├── Next steps
│   └── References
│
├── IMPLEMENTATION_COMPLETE.md                  📖 NEW
│   ├── Deliverables summary
│   ├── What this solves
│   ├── How to deploy
│   ├── Architecture overview
│   ├── Component checklist
│   ├── API endpoints list
│   ├── Code examples (3)
│   ├── Testing guide
│   ├── Benefits table
│   ├── Important notes
│   ├── Maintenance guide
│   ├── Documentation map
│   ├── Learning path
│   └── Success criteria
│
└── TIMEZONE_FILE_STRUCTURE.md                  📖 NEW (THIS FILE)
    └── Complete file structure and relationships
```

---

## 📊 File Dependencies

### Core Dependency Flow

```
                    ┌─────────────────┐
                    │   main.py       │
                    │ (imports all)   │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ↓                   ↓                   ↓
    ┌─────────┐      ┌───────────────┐   ┌──────────────┐
    │ routes  │      │ routes_       │   │ routes_      │
    │         │      │ tenant_       │   │ timezone     │
    │         │      │ company       │   │              │
    └────┬────┘      └────┬──────────┘   └──────┬───────┘
         │                 │                     │
         │                 ↓                     │
         │         ┌──────────────┐              │
         └────────→│  models.py   │←─────────────┘
                   │ (Company)    │
                   └──────┬───────┘
                          │
                          ↓
                  ┌──────────────────┐
                  │ timezone_utils   │
                  │ (Core library)   │
                  └──────────────────┘
                          │
                          ↓
                   ┌──────────────┐
                   │   pytz       │
                   │  (External)  │
                   └──────────────┘
                          │
                          ↓
                   ┌──────────────┐
                   │  Database    │
                   │  (UTC times) │
                   └──────────────┘
```

### Import Chain

```
main.py
  ├─ import routes_timezone
  │   └─ from timezone_utils import ...
  │       └─ import pytz
  │
  ├─ import routes_tenant_company
  │   ├─ from models import Company
  │   └─ (can use timezone_utils)
  │
  └─ import routes (and others)
      └─ can use timezone_utils
```

---

## 🔄 Function Relationships

### Core Functions in `timezone_utils.py`

```
get_company_timezone(company)
    └─→ Returns: string (IANA timezone identifier)

get_timezone_object(timezone_str)
    └─→ Returns: pytz.timezone object

convert_utc_to_company_timezone(utc_datetime, company)
    ├─ Calls: get_timezone_object()
    └─→ Returns: localized datetime in company timezone

convert_company_timezone_to_utc(local_datetime, company)
    ├─ Calls: get_timezone_object()
    └─→ Returns: UTC datetime

get_current_time_in_company_timezone(company)
    ├─ Calls: convert_utc_to_company_timezone()
    └─→ Returns: current time in company timezone

format_time_for_display(datetime_obj, format_str)
    └─→ Returns: formatted string for display

validate_timezone(timezone_str)
    └─→ Returns: boolean (True if valid)

get_all_timezones()
    └─→ Returns: list of all IANA timezones

get_timezone_offset_str(company)
    └─→ Returns: offset string (e.g., "+08:00")
```

---

## 🌐 API Endpoint Structure

### In `routes_timezone.py`

```
Timezone Utilities
  GET  /api/supported-timezones
       └─ Returns: list of all timezones
  
  GET  /api/current-time-in-company-timezone
       └─ Returns: current time in user's company tz
  
  POST /api/validate-timezone
       └─ Validates: timezone string
  
  POST /api/timezone-comparison
       └─ Compares: time across multiple timezones

Company Timezone Management
  GET  /api/timezone/<company_id>
       └─ Gets: timezone info for company
  
  PUT  /api/companies/<id>/timezone
       └─ Updates: company timezone
  
  GET  /api/my-timezone
       └─ Gets: user's company timezone
```

### In `routes_tenant_company.py`

```
Company CRUD (Updated to handle timezone)
  POST /api/companies
       ├─ New parameter: timezone
       └─ Default: 'UTC'
  
  PUT  /api/companies/<uuid:company_id>
       ├─ Updated field: timezone
       └─ Handles: timezone updates
```

---

## 🗄️ Database Schema

### Before Migration

```sql
CREATE TABLE hrm_company (
    id UUID PRIMARY KEY,
    tenant_id UUID,
    name VARCHAR(255),
    code VARCHAR(50),
    currency_code VARCHAR(10),
    -- ... other fields
    is_active BOOLEAN,
    created_at DATETIME,
    modified_at DATETIME
);
```

### After Migration

```sql
CREATE TABLE hrm_company (
    id UUID PRIMARY KEY,
    tenant_id UUID,
    name VARCHAR(255),
    code VARCHAR(50),
    currency_code VARCHAR(10),
    timezone VARCHAR(50) DEFAULT 'UTC',  ← NEW COLUMN
    -- ... other fields
    is_active BOOLEAN,
    created_at DATETIME,
    modified_at DATETIME
);
```

---

## 📦 Dependencies

### Required Libraries
```
pytz              ← For timezone handling (IANA database)
```

### Existing Flask Dependencies
```
Flask
Flask-SQLAlchemy
Flask-Login
sqlalchemy
```

### Import Map
```
timezone_utils.py
  ├─ from datetime import datetime, timezone
  ├─ import pytz
  └─ from flask import current_app

routes_timezone.py
  ├─ from flask import jsonify, request
  ├─ from flask_login import login_required, current_user
  ├─ from datetime import datetime
  ├─ import pytz
  ├─ from app import app
  ├─ from models import Company, Employee
  ├─ from timezone_utils import (multiple functions)
  └─ from auth import require_role

models.py (Company class)
  ├─ from datetime import datetime
  ├─ from app import db
  └─ No new imports needed

routes_tenant_company.py
  ├─ (existing imports)
  └─ (timezone_utils imported only where used)
```

---

## 🔗 Integration Points

### When Adding Timezone to Attendance

```python
# In routes.py or routes_ot.py or similar
from timezone_utils import (
    get_current_time_in_company_timezone,
    convert_company_timezone_to_utc
)

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    company = current_user.employee_profile.company
    
    # Get current time in company tz
    current_time = get_current_time_in_company_timezone(company)
    
    # Convert to UTC for storage
    utc_time = convert_company_timezone_to_utc(
        current_time.replace(tzinfo=None), 
        company
    )
    
    # Save to database
    attendance = Attendance(
        check_in_time=utc_time
    )
    db.session.add(attendance)
    db.session.commit()
```

### When Displaying Attendance

```python
# In route returning data to frontend
from timezone_utils import convert_utc_to_company_timezone

attendance = Attendance.query.get(id)
company = attendance.employee.company

# Convert from UTC to company tz
display_time = convert_utc_to_company_timezone(
    attendance.check_in_time, 
    company
)

return jsonify({
    'time': display_time.strftime('%Y-%m-%d %H:%M:%S'),
    'timezone': company.timezone
})
```

---

## 📋 Testing File Locations

### Unit Tests (Can be placed in)
```
tests/
├── test_timezone_utils.py
│   ├── test_validate_timezone()
│   ├── test_convert_utc_to_company()
│   ├── test_convert_company_to_utc()
│   └── test_format_time_for_display()
│
└── test_routes_timezone.py
    ├── test_get_supported_timezones()
    ├── test_validate_timezone_endpoint()
    └── test_timezone_comparison()
```

### Integration Tests (Can be placed in)
```
tests/
└── test_integration_timezone.py
    ├── test_company_timezone_creation()
    ├── test_company_timezone_update()
    ├── test_attendance_with_timezone()
    └── test_timezone_api_endpoints()
```

---

## 📈 File Size Reference

| File | Size | Type |
|------|------|------|
| `timezone_utils.py` | ~6 KB | Code |
| `routes_timezone.py` | ~8 KB | Code |
| `add_company_timezone.py` | ~2 KB | Migration |
| `company_view.html` | +50 lines | Template |
| `TIMEZONE_IMPLEMENTATION_GUIDE.md` | ~15 KB | Docs |
| `TIMEZONE_DEPLOYMENT_CHECKLIST.md` | ~12 KB | Docs |
| `TIMEZONE_QUICK_REFERENCE.md` | ~8 KB | Docs |
| `TIMEZONE_IMPLEMENTATION_SUMMARY.md` | ~5 KB | Docs |
| `IMPLEMENTATION_COMPLETE.md` | ~12 KB | Docs |
| **Total** | **~70 KB** | - |

---

## 🚀 Deployment File Checklist

### Must Deploy
- [x] `timezone_utils.py` → `hrm/timezone_utils.py`
- [x] `routes_timezone.py` → `hrm/routes_timezone.py`
- [x] Migration → `hrm/migrations/versions/add_company_timezone.py`
- [x] Updated `models.py` → `hrm/models.py`
- [x] Updated `routes_tenant_company.py` → `hrm/routes_tenant_company.py`
- [x] Updated `templates/masters/company_view.html`
- [x] Updated `main.py` → `hrm/main.py`

### Should Deploy
- [x] All documentation files (for reference)
- [x] This structure file (for reference)

### Optional
- [ ] Test files (if creating comprehensive test suite)
- [ ] Example usage scripts (for training)

---

## 🔍 Finding Things

| Looking for... | Location |
|---|---|
| Timezone conversion logic | `timezone_utils.py` |
| API endpoints | `routes_timezone.py` |
| Database changes | `migrations/versions/add_company_timezone.py` |
| UI for timezone selection | `templates/masters/company_view.html` |
| Company model changes | `models.py` (line ~190-195) |
| Usage examples | `TIMEZONE_IMPLEMENTATION_GUIDE.md` |
| Deployment steps | `TIMEZONE_DEPLOYMENT_CHECKLIST.md` |
| Quick reference | `TIMEZONE_QUICK_REFERENCE.md` |

---

## 🎓 Learning Resources by Role

### For Python Developer
1. Start: `TIMEZONE_QUICK_REFERENCE.md`
2. Review: `timezone_utils.py`
3. Study: `TIMEZONE_IMPLEMENTATION_GUIDE.md`
4. Implement: Add timezone to your routes

### For Frontend Developer
1. Start: `TIMEZONE_IMPLEMENTATION_SUMMARY.md`
2. Review: `templates/masters/company_view.html`
3. Study: API endpoint documentation
4. Implement: Update your templates

### For DevOps Engineer
1. Start: `TIMEZONE_DEPLOYMENT_CHECKLIST.md`
2. Review: Migration file
3. Plan: Pre-deployment backup
4. Execute: Deployment steps

### For Product Manager
1. Start: `IMPLEMENTATION_COMPLETE.md`
2. Review: Benefits section
3. Plan: User communication
4. Monitor: Deployment success

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] All files exist in correct locations
- [ ] `timezone_utils.py` can be imported
- [ ] `routes_timezone.py` is loaded by Flask
- [ ] Database migration completes
- [ ] `hrm_company.timezone` column exists
- [ ] Company timezone dropdown appears in UI
- [ ] API endpoints respond correctly
- [ ] No import errors in logs
- [ ] Existing tests still pass
- [ ] No performance degradation

---

**This structure document helps with:**
- ✅ Understanding how files connect
- ✅ Finding specific code
- ✅ Planning implementation
- ✅ Coordinating with team
- ✅ Troubleshooting issues

**Last Updated**: 2025-01-24