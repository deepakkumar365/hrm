# Timezone Implementation - Deployment Checklist

## Pre-Deployment

### Code Review
- [ ] Review `timezone_utils.py` - Check all utility functions
- [ ] Review `routes_timezone.py` - Check all new API endpoints
- [ ] Review `routes_tenant_company.py` changes - Verify timezone field handling
- [ ] Review `models.py` changes - Verify Company model has timezone field
- [ ] Review `templates/masters/company_view.html` - Check UI updates

### Dependencies
- [ ] Verify `pytz` is installed: `pip list | grep pytz`
- [ ] If not installed: `pip install pytz`
- [ ] Update `requirements.txt` to include `pytz` if not already present

### Database Backup
- [ ] **IMPORTANT**: Create backup of production database
- [ ] Export current company data to JSON
- [ ] Document current timezone settings (if any)

---

## Deployment Steps

### Step 1: Deploy Code
- [ ] Deploy all modified files to production:
  - [ ] `models.py`
  - [ ] `routes_tenant_company.py`
  - [ ] `routes_timezone.py` (NEW)
  - [ ] `timezone_utils.py` (NEW)
  - [ ] `templates/masters/company_view.html`
  - [ ] `main.py`

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
# or if pytz not in requirements.txt:
pip install pytz
```

### Step 3: Run Database Migration
```bash
# Backup database first!
flask db upgrade
```

**Expected Output**:
```
✅ Added timezone column to hrm_company table
   - Default value: UTC
   - Used for: Display attendance and OT times in company's local timezone
```

### Step 4: Verify Migration
```bash
# Check that column was added
python verify_schema.py

# OR run this SQL query:
# SELECT * FROM hrm_company LIMIT 1;
# Verify it has 'timezone' column
```

### Step 5: Verify API Endpoints
```bash
# Test timezone endpoints
curl http://localhost:5000/api/supported-timezones
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:5000/api/current-time-in-company-timezone
```

### Step 6: Test UI
- [ ] Login to system
- [ ] Navigate to: **Companies → Select a Company → Edit**
- [ ] Verify **Timezone** dropdown appears
- [ ] Verify timezone options are available
- [ ] Select a timezone and save
- [ ] Verify timezone displays in company view

---

## Post-Deployment

### Configuration
- [ ] Set timezone for each company:
  1. Go to Company View
  2. Click Edit
  3. Select appropriate timezone
  4. Click Update Company

### Testing

#### Test 1: Verify Timezone Utility Functions
```bash
python3 << 'EOF'
from timezone_utils import validate_timezone, get_all_timezones

# Test timezone validation
assert validate_timezone('Asia/Singapore') == True
assert validate_timezone('Invalid/TZ') == False

# Test getting all timezones
timezones = get_all_timezones()
assert len(timezones) > 100
assert 'UTC' in timezones
assert 'Asia/Singapore' in timezones

print("✅ All timezone utility tests passed!")
EOF
```

#### Test 2: Verify Database Schema
```bash
python3 << 'EOF'
from app import db, app
from models import Company

with app.app_context():
    # Get a company
    company = Company.query.first()
    if company:
        print(f"Company: {company.name}")
        print(f"Timezone: {company.timezone}")
        print(f"✅ Timezone column verified!")
    else:
        print("No companies found")
EOF
```

#### Test 3: Test API Endpoints
```bash
# Test supported timezones endpoint
curl -s http://localhost:5000/api/supported-timezones | head -20

# Test validate timezone endpoint
curl -s -X POST http://localhost:5000/api/validate-timezone \
  -H "Content-Type: application/json" \
  -d '{"timezone": "Asia/Singapore"}'

# Should return: {"success": true, "valid": true, ...}
```

#### Test 4: Test Timezone Conversion
```bash
python3 << 'EOF'
from timezone_utils import (
    convert_utc_to_company_timezone,
    convert_company_timezone_to_utc,
    get_current_time_in_company_timezone
)
from datetime import datetime
from models import Company
from app import app

with app.app_context():
    # Get a test company
    company = Company.query.first()
    if company:
        # Test current time
        current = get_current_time_in_company_timezone(company)
        print(f"Current time in {company.timezone}: {current}")
        
        # Test UTC to company conversion
        utc_time = datetime(2025, 1, 24, 12, 0, 0)
        company_time = convert_utc_to_company_timezone(utc_time, company)
        print(f"UTC 2025-01-24 12:00:00 → {company.timezone}: {company_time}")
        
        print("✅ Timezone conversion tests passed!")
EOF
```

### Integration Tests

#### Test 5: Mark Attendance with Timezone
If attendance routes are updated:

```bash
# Step 1: Get current user's company timezone
curl -s -H "Authorization: Bearer <TOKEN>" \
  http://localhost:5000/api/my-timezone

# Step 2: Mark attendance
curl -s -X POST \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"employee_id": 1, "notes": "Test"}' \
  http://localhost:5000/api/mark-attendance

# Verify time is recorded correctly in company timezone
```

#### Test 6: OT Marking with Timezone
If OT routes are updated:

```bash
# Test OT marking (endpoint may vary)
curl -s -X POST \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-01-24", "hours": 2}' \
  http://localhost:5000/api/mark-overtime

# Verify time is in company timezone
```

---

## Monitoring

### Performance Impact
- [ ] Monitor database query performance - timezone column shouldn't impact queries
- [ ] Check API response times - new timezone endpoints should be fast
- [ ] Monitor memory usage - pytz library adds minimal overhead

### Logs to Watch
```bash
# Check application logs for timezone-related errors
tail -f logs/app.log | grep -i timezone

# Check for migration errors
tail -f logs/migration.log
```

### User Reports
- [ ] Employees confirm attendance shows correct local time
- [ ] Time differences align with company timezone
- [ ] No data loss or time discrepancies

---

## Rollback Plan

If issues occur:

### Rollback Option 1: Simple Rollback
```bash
# Revert migration (if critical issues)
flask db downgrade

# Revert code changes
git revert <commit-hash>

# Restart application
```

### Rollback Option 2: Manual Fix
If migration can't be reverted:

```bash
# Keep timezone column but don't use it
# Set all companies back to 'UTC'
UPDATE hrm_company SET timezone = 'UTC' WHERE timezone IS NOT NULL;

# Comment out timezone-related code in routes
# Redeploy without timezone features
```

### Rollback Option 3: Restore from Backup
```bash
# Restore database from backup
pg_restore -d hrms_db backup_before_tz.sql

# Revert code
git checkout HEAD -- models.py routes_tenant_company.py
```

---

## Troubleshooting

### Issue 1: Migration Fails with "Column Already Exists"
**Cause**: Timezone column already exists
**Solution**: 
```bash
# Check if column exists
SELECT column_name FROM information_schema.columns 
WHERE table_name='hrm_company' AND column_name='timezone';

# If it exists, update migration revision marker
flask db stamp <latest_revision>
```

### Issue 2: pytz Not Found Error
**Cause**: pytz library not installed
**Solution**:
```bash
pip install pytz
# Verify installation
python3 -c "import pytz; print('✅ pytz installed')"
```

### Issue 3: Timezone Changes Not Reflecting
**Cause**: Application cache or browser cache
**Solution**:
- [ ] Restart Flask application
- [ ] Clear browser cache
- [ ] Verify database change:
  ```sql
  SELECT company_name, timezone FROM hrm_company;
  ```

### Issue 4: Time Off by Several Hours
**Cause**: Timezone not applied to display code
**Solution**:
- [ ] Verify attendance/OT routes use timezone conversion
- [ ] Check that UTC → Company timezone conversion is applied
- [ ] Verify company has correct timezone configured

---

## Success Criteria

✅ **Deployment is successful when:**

- [ ] Migration completes without errors
- [ ] All timezone endpoints are accessible
- [ ] Company timezone can be configured in UI
- [ ] Database schema includes timezone column
- [ ] Timezone utility functions work correctly
- [ ] Current time displays in company timezone
- [ ] Attendance/OT times show in company timezone
- [ ] No data loss or corruption
- [ ] Performance metrics unchanged
- [ ] User acceptance tests pass

---

## Notification

### Notify Users After Deployment
**Message Template**:

```
Subject: System Update - Timezone Configuration for Attendance

Dear Users,

We have deployed an important update to the HRM system:

🕐 TIMEZONE CONFIGURATION
Company administrators can now set their company's timezone. 
This ensures that when you mark attendance or overtime, 
the time displayed is in your company's local timezone instead of UTC.

📍 What to Do:
- Timezone Admin: Set your company timezone in Company Settings
- Employees: No action needed - system will use company timezone

⚙️ Current Default: UTC (if timezone not configured)

For support or questions, contact your HR Administrator.

---
System Team
```

---

## Documentation

### Update Internal Documentation
- [ ] Update HRM System Documentation with timezone feature
- [ ] Create FAQ for timezone configuration
- [ ] Add timezone screenshots to user guide
- [ ] Document supported timezones list

### Create Knowledge Base Articles
- [ ] "How to Configure Company Timezone"
- [ ] "Why Timezone Matters for Attendance"
- [ ] "Timezone Troubleshooting Guide"

---

## Follow-Up Tasks

### Short Term (Next 1-2 weeks)
- [ ] Monitor for timezone-related issues
- [ ] Gather user feedback
- [ ] Document any discovered issues

### Medium Term (Next 1-2 months)
- [ ] Integrate timezone into reports
- [ ] Add timezone to payroll calculations
- [ ] Implement employee timezone preferences

### Long Term (Next 3-6 months)
- [ ] Audit all time-based features for timezone compliance
- [ ] Implement timezone in leave calculations
- [ ] Add timezone conversion to export features

---

## Sign-Off

**Deployment Date**: _______________

**Deployed By**: _______________

**Verified By**: _______________

**Notes**:
```




```

---

## Contact & Support

**For Issues During Deployment**:
- Check: `docs/TIMEZONE_IMPLEMENTATION_GUIDE.md`
- Review: `TIMEZONE_IMPLEMENTATION_SUMMARY.md`
- Test: `timezone_utils.py` functions
- API Documentation: `routes_timezone.py` comments

**Emergency Contacts**:
- Database Admin: _______________
- System Admin: _______________
- Developer Lead: _______________