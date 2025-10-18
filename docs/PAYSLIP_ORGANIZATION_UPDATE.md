# Payslip Organization Data Update

## Summary
Updated the payslip generation to properly display organization data (name, address, UEN) from the database and removed the manager name field from the payslip.

## Changes Made

### 1. Database Model Update (`models.py`)
**File:** `E:/Gobi/Pro/HRMS/hrm/models.py`

Added two new fields to the `Organization` model:
- `address` (Text field, nullable) - Organization's address
- `uen` (String(50), nullable) - Unique Entity Number

```python
class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=True)  # NEW
    uen = db.Column(db.String(50), nullable=True)  # NEW
    logo_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
```

### 2. Database Migration
**File:** `E:/Gobi/Pro/HRMS/hrm/migrations/versions/add_org_address_uen.py`

Created and applied a migration to add the new columns to the database:
- Migration ID: `add_org_address_uen`
- Status: ✅ Successfully applied

### 3. Routes Update (`routes.py`)
**File:** `E:/Gobi/Pro/HRMS/hrm/routes.py`
**Function:** `payroll_payslip(payroll_id)`

Updated the company data preparation to fetch from database:

**Before:**
```python
company_data = {
    'name': company.name,
    'address': 'N/A',  # Not in current model
    'uen': 'N/A',  # Not in current model
    'manager_name': 'N/A'  # Not in current model
}
```

**After:**
```python
company_data = {
    'name': company.name,
    'address': company.address or 'N/A',
    'uen': company.uen or 'N/A'
}
```

### 4. Template Update (`payslip.html`)
**File:** `E:/Gobi/Pro/HRMS/hrm/templates/payroll/payslip.html`

Removed the manager name field from the employee information table:

**Before:**
```html
<tr>
    <td class="label">Employee Name:</td>
    <td>{{ employee.name }}</td>
    <td class="label">Manager:</td>
    <td>{{ company.manager_name }}</td>
</tr>
```

**After:**
```html
<tr>
    <td class="label">Employee Name:</td>
    <td>{{ employee.name }}</td>
    <td class="label">Pay Date:</td>
    <td>{{ payroll.pay_date }}</td>
</tr>
```

Reorganized the employee information table to remove manager field and better utilize the space.

## How to Update Organization Data

To add or update organization address and UEN number, you can:

### Option 1: Using Python Shell
```python
from app import app, db
from models import Organization

with app.app_context():
    org = Organization.query.first()
    org.address = "123 Business Street, #01-01, Singapore 123456"
    org.uen = "201234567A"
    db.session.commit()
```

### Option 2: Using SQL
```sql
UPDATE organization 
SET address = '123 Business Street, #01-01, Singapore 123456',
    uen = '201234567A'
WHERE id = 1;
```

### Option 3: Create an Admin Interface
You can add an organization settings page in the admin panel to allow updating these fields through the UI.

## Testing

1. **Verify Database Changes:**
   ```sql
   SELECT id, name, address, uen FROM organization;
   ```

2. **Test Payslip Generation:**
   - Navigate to a payroll record
   - Click "View Payslip"
   - Verify that:
     - Company name displays correctly
     - Company address displays (or 'N/A' if not set)
     - UEN number displays (or 'N/A' if not set)
     - Manager name field is removed
     - Employee information is properly displayed

## Benefits

1. ✅ **Data Integrity:** Organization data now comes from the database instead of hardcoded values
2. ✅ **Maintainability:** Easy to update organization details without code changes
3. ✅ **Cleaner UI:** Removed unnecessary manager field from payslip
4. ✅ **Flexibility:** Address and UEN can be updated as needed per organization

## Next Steps (Optional)

1. Create an organization settings page in the admin panel
2. Add validation for UEN format (Singapore UEN format)
3. Add support for multiple organizations if needed
4. Add organization logo display on payslip

## Files Modified

1. `models.py` - Added address and uen fields to Organization model
2. `routes.py` - Updated payroll_payslip function to use database values
3. `templates/payroll/payslip.html` - Removed manager field, reorganized layout
4. `migrations/versions/add_org_address_uen.py` - New migration file (created)

## Status: ✅ COMPLETE

All changes have been successfully implemented and tested. The payslip now properly displays organization data from the database.