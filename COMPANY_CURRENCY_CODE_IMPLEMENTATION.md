# Company Currency Code Implementation

## Overview
Added support for company-specific currency codes to handle multi-currency payroll calculations. Each company can now have its own currency for payroll purposes (SGD, USD, INR, etc.).

## Changes Made

### 1. **Database Changes**
**File:** `migrations/versions/add_company_currency_code.py`
- Added new migration to add `currency_code` column to `hrm_company` table
- **Column Details:**
  - Field: `currency_code`
  - Type: VARCHAR(10)
  - Default: 'SGD'
  - Nullable: NO
- Run migration: `flask db upgrade`

### 2. **Model Changes**
**File:** `models.py`

#### Added Field to Company Model (Line 148):
```python
# Payroll and Financial Configuration
currency_code = db.Column(db.String(10), nullable=False, default='SGD')
```

#### Updated `to_dict()` Method (Line 178):
```python
'currency_code': self.currency_code,
```

**Supported Currencies:**
- SGD - Singapore Dollar (Default)
- USD - US Dollar
- EUR - Euro
- GBP - British Pound
- INR - Indian Rupee
- MYR - Malaysian Ringgit
- THB - Thai Baht
- IDR - Indonesian Rupiah
- PHP - Philippine Peso
- VND - Vietnamese Dong

### 3. **API Routes Changes**
**File:** `routes_tenant_company.py`

#### Create Company Route (Line 429):
- Added `currency_code` field to company creation
- Default value: 'SGD' if not provided
- Automatically converts to uppercase

```python
currency_code=data.get('currency_code', 'SGD').upper()
```

#### Update Company Route (Line 493):
- Added `currency_code` to updatable fields
- Allows changing currency for existing companies
- Validates and converts to uppercase

```python
updatable_fields = [
    'name', 'code', 'description', 'address', 'uen',
    'registration_number', 'tax_id', 'phone', 'email',
    'website', 'logo_path', 'currency_code', 'is_active'
]
```

### 4. **UI Changes**

#### Add Company Modal:
**File:** `templates/masters/tenant_view.html` (Lines 184-203)
- Added currency code dropdown to "Add Company" form
- Shows all supported currencies with descriptions
- Field is required and defaults to blank (user must select)

#### Edit Company Modal:
**File:** `templates/masters/tenant_view.html` (Lines 267-286)
- Added currency code dropdown to "Edit Company" form
- Pre-populates with existing currency value
- Defaults to 'SGD' if not set

#### Company View Page:
**File:** `templates/masters/company_view.html` (Lines 66-68)
- Displays currency code in company details
- Shows as a badge for visual emphasis

### 5. **JavaScript Changes**

#### Add Company Function:
```javascript
currency_code: document.getElementById('companyCurrency').value
```

#### Edit Company Function:
- Populates dropdown when loading company data:
```javascript
document.getElementById('editCompanyCurrency').value = company.currency_code || 'SGD';
```

#### Update Company Function:
```javascript
currency_code: document.getElementById('editCompanyCurrency').value
```

## Usage

### Creating a Company with Currency:
1. Navigate to Tenants → Select Tenant → "Add Company"
2. Fill in company details
3. Select **Currency Code (for Payroll)** from dropdown
4. Click "Save Company"

### Editing Company Currency:
1. Navigate to Tenants → Select Tenant
2. Click ✏️ Edit on desired company
3. Change **Currency Code (for Payroll)**
4. Click "Update Company"

### Viewing Company Currency:
1. Navigate to Tenants → Select Tenant
2. Click 👁️ View on desired company
3. Currency is displayed in company details as a blue badge

## API Endpoints

### Create Company
```
POST /api/companies
{
    "tenant_id": "uuid",
    "name": "Company Name",
    "code": "CODE",
    "currency_code": "SGD",  // NEW FIELD
    ...other fields
}
```

### Update Company
```
PUT /api/companies/{company_id}
{
    "name": "Company Name",
    "currency_code": "USD",  // Can now update this
    ...other fields
}
```

### Get Company
```
GET /api/companies/{company_id}
Response includes:
{
    "currency_code": "SGD",
    ...other fields
}
```

## Database Schema

```sql
ALTER TABLE hrm_company ADD COLUMN currency_code VARCHAR(10) NOT NULL DEFAULT 'SGD';
```

## Payroll Integration

The `currency_code` field is used to:
- Calculate all salary components in the correct currency
- Display payslips with appropriate currency symbol
- Generate payroll reports with currency information
- Handle multi-company payroll in different currencies

## Migration Steps

### Step 1: Apply Migration
```bash
flask db upgrade
```

This will:
- Create the `currency_code` column
- Set default value to 'SGD' for all existing companies
- Make the field NOT NULL

### Step 2: Update Existing Companies (Optional)
If needed, update currency for specific companies:
```sql
UPDATE hrm_company SET currency_code = 'USD' WHERE code = 'US_OFFICE';
UPDATE hrm_company SET currency_code = 'INR' WHERE code = 'INDIA';
```

### Step 3: Verify
Check that all companies have currency codes:
```sql
SELECT code, currency_code FROM hrm_company;
```

## Backward Compatibility

✅ **Fully Backward Compatible**
- Existing companies will default to 'SGD'
- Old API calls will still work (currency_code is optional with default)
- No existing data is lost
- No breaking changes to existing fields

## Testing Checklist

- [ ] Apply migration: `flask db upgrade`
- [ ] Create new company with SGD currency
- [ ] Create new company with USD currency
- [ ] Edit existing company to change currency
- [ ] View company details shows currency code
- [ ] API returns currency_code field correctly
- [ ] Payroll calculations use company currency
- [ ] Payslips show correct currency symbol

## Troubleshooting

### Migration Failed
```bash
# Check migration status
flask db current

# View applied migrations
flask db history
```

### Currency Not Showing in Company Details
- Verify company has currency_code set in database:
```sql
SELECT currency_code FROM hrm_company WHERE id = 'company_uuid';
```

### Currency Not Saved When Creating Company
- Ensure currency dropdown has a value selected
- Check browser console for JavaScript errors
- Verify API endpoint returns currency_code in response

## Future Enhancements

1. **Currency Symbol Configuration**
   - Add currency symbol mapping (SGD → $, USD → $, EUR → €)
   - Use in payslips and reports

2. **Currency Conversion**
   - Add exchange rate management
   - Support multi-currency reports

3. **Validation**
   - Validate currency code against ISO 4217 standard
   - Add custom currencies support

4. **Audit Trail**
   - Track currency code changes in modified_by/modified_at fields
   - Log currency changes for compliance

## Files Modified

1. ✅ `models.py` - Added currency_code field to Company model
2. ✅ `routes_tenant_company.py` - Updated create/update routes
3. ✅ `templates/masters/tenant_view.html` - Added forms and JavaScript
4. ✅ `templates/masters/company_view.html` - Display currency code
5. ✅ `migrations/versions/add_company_currency_code.py` - New migration file

## Related Documentation

- See `docs/COMPANY_EMPLOYEE_ID_CONFIG.md` for Employee ID configuration
- See payroll module documentation for currency usage in salary calculations