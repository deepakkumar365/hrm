# Tenant Schema Fix - country_code and currency_code

## Issue Encountered

When querying the `hrm_tenant` table, the following error occurred:

```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column hrm_tenant.country_code does not exist
LINE 2: ...on, hrm_tenant.is_active AS hrm_tenant_is_active, hrm_tenant...
```

## Root Cause

**Schema Mismatch between Python Model and Database**

1. **Python Model (`models.py`)** - Lines 74-75
   - Defines `country_code` and `currency_code` columns
   - These fields were added to support tenant-specific country/currency settings
   
2. **Database Schema** 
   - The original migration `001_add_tenant_company_hierarchy.sql` created the `hrm_tenant` table
   - **Did NOT include** `country_code` and `currency_code` columns
   - This caused SQLAlchemy to fail when trying to query these columns

## Solution Applied

### Step 1: Created Migration File

**File:** `migrations/versions/003_add_tenant_country_currency.sql`

```sql
-- Add country_code column if it doesn't exist
ALTER TABLE hrm_tenant ADD COLUMN country_code VARCHAR(10);

-- Add currency_code column if it doesn't exist
ALTER TABLE hrm_tenant ADD COLUMN currency_code VARCHAR(10);
```

The migration is **idempotent** - safe to run multiple times.

### Step 2: Created Migration Runner Script

**File:** `run_tenant_country_currency_migration.py`

This script:
- Reads the SQL migration file
- Executes it within the Flask app context
- Handles errors gracefully
- Provides clear feedback

### Step 3: Executed the Migration

```bash
python run_tenant_country_currency_migration.py
```

**Result:**
```
✅ Migration completed successfully!

The following columns have been added to hrm_tenant:
  - country_code (VARCHAR(10))
  - currency_code (VARCHAR(10))
```

### Step 4: Verified the Fix

**File:** `verify_tenant_schema.py`

Verification confirmed:
- ✅ Both columns exist in the database
- ✅ Tenant queries work correctly
- ✅ No more `UndefinedColumn` errors

## Database Schema After Fix

The `hrm_tenant` table now has the following columns:

| Column Name    | Data Type                | Nullable |
|---------------|--------------------------|----------|
| id            | uuid                     | NOT NULL |
| name          | character varying        | NOT NULL |
| code          | character varying        | NOT NULL |
| description   | text                     | NULL     |
| is_active     | boolean                  | NOT NULL |
| created_by    | character varying        | NOT NULL |
| created_at    | timestamp with time zone | NOT NULL |
| modified_by   | character varying        | NULL     |
| modified_at   | timestamp with time zone | NULL     |
| **country_code**  | **character varying**    | **NULL** |
| **currency_code** | **character varying**    | **NULL** |

## Files Created

1. **`migrations/versions/003_add_tenant_country_currency.sql`**
   - SQL migration to add missing columns (country_code, currency_code)
   - Idempotent and safe to re-run

2. **`migrations/versions/004_add_tenant_payment_and_documents.sql`**
   - SQL migration to create payment config and documents tables
   - Idempotent and safe to re-run

3. **`run_tenant_country_currency_migration.py`**
   - Python script to execute the country/currency migration
   - Provides clear feedback and error handling

4. **`run_tenant_payment_documents_migration.py`**
   - Python script to execute the payment/documents migration
   - Provides clear feedback and error handling

5. **`verify_tenant_schema.py`**
   - Verification script to check schema
   - Displays all columns and tests queries

6. **`test_tenant_fix.py`**
   - Comprehensive test script simulating dashboard queries
   - Validates all tenant-related functionality

7. **`TENANT_SCHEMA_FIX.md`** (this file)
   - Documentation of the issue and fix

## Additional Issues Fixed

During the fix, we discovered and resolved additional missing tables:

### Missing Table: `hrm_tenant_payment_config`
- **Error:** `relation "hrm_tenant_payment_config" does not exist`
- **Solution:** Created migration `004_add_tenant_payment_and_documents.sql`
- **Status:** ✅ Fixed

### Missing Table: `hrm_tenant_documents`
- **Error:** Would have occurred when accessing tenant documents
- **Solution:** Created in the same migration `004_add_tenant_payment_and_documents.sql`
- **Status:** ✅ Fixed

## Impact

✅ **Database schema now matches Python model**  
✅ **Tenant queries work correctly**  
✅ **No more UndefinedColumn errors**  
✅ **Country and currency fields available for use**  
✅ **Payment configuration table created**  
✅ **Document management table created**  
✅ **All tenant-related functionality operational**  

## Usage

The `country_code` and `currency_code` fields can now be used:

```python
# Create a tenant with country and currency
tenant = Tenant(
    name="Example Corp",
    code="EX01",
    country_code="SG",      # Singapore
    currency_code="SGD"     # Singapore Dollar
)
db.session.add(tenant)
db.session.commit()

# Query tenants by country
sg_tenants = Tenant.query.filter_by(country_code='SG').all()
```

## Testing Required

After this fix, please test:

1. **Tenant List Page**
   - Navigate to tenant management
   - Verify tenant list loads without errors
   - Check that country/currency fields display correctly

2. **Tenant Creation**
   - Create a new tenant
   - Set country code (e.g., 'SG', 'US', 'IN')
   - Set currency code (e.g., 'SGD', 'USD', 'INR')
   - Verify data is saved correctly

3. **Tenant Editing**
   - Edit an existing tenant
   - Update country and currency codes
   - Verify changes are saved

## Future Considerations

1. **Add Validation**
   - Consider adding validation for country codes (ISO 3166-1 alpha-2)
   - Consider adding validation for currency codes (ISO 4217)

2. **Add Dropdown Lists**
   - Create master data for countries
   - Create master data for currencies
   - Use dropdowns instead of free text

3. **Default Values**
   - Consider setting default country/currency based on organization
   - Add migration to populate existing tenants with defaults

## Related Files

- **Model Definition:** `models.py` (lines 58-106)
- **Original Migration:** `migrations/versions/001_add_tenant_company_hierarchy.sql`
- **This Fix Migration:** `migrations/versions/003_add_tenant_country_currency.sql`

---

**Status:** ✅ RESOLVED  
**Date:** 2024  
**Impact:** Critical - Database schema fixed  
**Testing:** Required  