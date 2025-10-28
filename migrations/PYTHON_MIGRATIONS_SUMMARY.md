# Python Migrations Conversion Summary

## Overview
All 4 SQL migrations have been successfully converted to Python/SQLAlchemy Alembic migrations.

## Migration Chain

```
005_add_tenant_company_hierarchy.py
    ↓
006_add_tenant_country_currency.py
    ↓
007_add_tenant_payment_and_documents.py
    ↓
008_insert_tenant_company_test_data.py
```

## Migration Details

### 1. **005_add_tenant_company_hierarchy.py**
**Revision ID:** `005_add_tenant_company_hierarchy`
**Source:** `001_add_tenant_company_hierarchy.sql`

**Creates:**
- `hrm_tenant` table (Top-level tenant entity)
  - UUID primary key with auto-generation
  - Unique name and code constraints
  - Audit fields (created_by, created_at, modified_by, modified_at)
  - Indexes for code, is_active, and created_at
  
- `hrm_company` table (Company entities per tenant)
  - UUID primary key with auto-generation
  - Foreign key to hrm_tenant (CASCADE delete)
  - Company details (address, UEN, tax_id, etc.)
  - Unique constraint on (tenant_id, code)
  - Audit fields and indexes

**Modifications:**
- Adds `tenant_id` to `organization` table (nullable)
- Adds `company_id` to `hrm_employee` table (nullable)
- Adds audit fields to existing tables:
  - `hrm_employee`: created_by, modified_by, modified_at
  - `organization`: created_by, modified_by, modified_at

**Triggers Created:**
- `trg_hrm_tenant_modified_at` - Auto-updates modified_at on hrm_tenant changes
- `trg_hrm_company_modified_at` - Auto-updates modified_at on hrm_company changes
- `trg_hrm_employee_modified_at` - Auto-updates modified_at on hrm_employee changes
- `trg_organization_modified_at` - Auto-updates modified_at on organization changes
- `update_modified_at_column()` trigger function

---

### 2. **006_add_tenant_country_currency.py**
**Revision ID:** `006_add_tenant_country_currency`
**Depends on:** `005_add_tenant_company_hierarchy`
**Source:** `003_add_tenant_country_currency.sql`

**Modifications:**
- Adds `country_code` column to `hrm_tenant` (VARCHAR(10), nullable)
- Adds `currency_code` column to `hrm_tenant` (VARCHAR(10), nullable)
- All operations are idempotent (checks if columns exist before adding)

**Purpose:**
- Fixes schema mismatch between database and Python models
- Enables multi-country/currency support at tenant level

---

### 3. **007_add_tenant_payment_and_documents.py**
**Revision ID:** `007_add_tenant_payment_and_documents`
**Depends on:** `006_add_tenant_country_currency`
**Source:** `004_add_tenant_payment_and_documents.sql`

**Creates:**
- `hrm_tenant_payment_config` table
  - Payment type: 'Fixed' or 'User-Based'
  - Implementation charges, monthly charges, other charges
  - Payment frequency: 'Monthly', 'Quarterly', 'Half-Yearly', 'Yearly'
  - Audit fields and constraints

- `hrm_tenant_documents` table
  - File management for tenant documents
  - Stores file_name, file_path, file_type, file_size
  - References to hrm_tenant with CASCADE delete

**Triggers:**
- `trg_hrm_tenant_payment_config_modified_at` - Auto-updates modified_at on payment config changes

---

### 4. **008_insert_tenant_company_test_data.py**
**Revision ID:** `008_insert_tenant_company_test_data`
**Depends on:** `007_add_tenant_payment_and_documents`
**Source:** `002_test_data_tenant_company.sql`

**Inserts Test Data:**
- **Tenant:** Noltrion HRM (NOLTRION)
- **Companies:** 
  - Noltrion India Pvt Ltd (NOLTRION-IN)
  - Noltrion Singapore Pte Ltd (NOLTRION-SG)

**Updates:**
- Links existing organization to the Noltrion tenant
- Links first 3 existing employees to Noltrion Singapore company

**Idempotent:** Uses upsert pattern (ON CONFLICT ... DO UPDATE)

---

## Usage Instructions

### Run All Migrations
```bash
flask db upgrade
```

### Run Specific Migration
```bash
flask db upgrade 005_add_tenant_company_hierarchy
flask db upgrade 006_add_tenant_country_currency
flask db upgrade 007_add_tenant_payment_and_documents
flask db upgrade 008_insert_tenant_company_test_data
```

### Rollback Last Migration
```bash
flask db downgrade
```

### Rollback to Specific Revision
```bash
flask db downgrade 006_add_tenant_country_currency
```

### Check Current Revision
```bash
flask db current
```

### View Migration History
```bash
flask db history
```

---

## Key Features of Python Migrations

✅ **Idempotent Operations** - Safe to run multiple times
✅ **Proper Rollback Support** - Each migration has upgrade/downgrade paths
✅ **Type Safety** - Uses SQLAlchemy column types instead of raw SQL
✅ **Constraints & Indexes** - All database constraints properly defined
✅ **Audit Trails** - Timestamps and user tracking built-in
✅ **Upsert Pattern** - Test data inserts won't fail on re-run
✅ **Trigger Management** - PostgreSQL triggers for auto-updating timestamps
✅ **Comments & Documentation** - Database objects documented with comments

---

## Migration Advantages Over Raw SQL

| Aspect | Raw SQL | Python Alembic |
|--------|---------|----------------|
| **Version Control** | Manual tracking | Automatic revision numbering |
| **Rollback** | Manual downgrade scripts | Automatic downgrade() functions |
| **Cross-DB Support** | PostgreSQL-specific | Can support multiple databases |
| **Type Safety** | Raw strings | SQLAlchemy type validation |
| **Code Reusability** | Difficult | Leverage Python modules |
| **Testing** | Hard to test | Easy to test programmatically |
| **Error Handling** | Basic | Full Python exception handling |
| **Integration** | Manual | Integrated with Flask-Migrate |

---

## Database Requirements

- **PostgreSQL 10+** (for UUID support)
- **uuid-ossp extension** (automatically enabled in migration 005)
- **SQLAlchemy 1.4+**
- **Alembic 1.5+**
- **Flask-Migrate 3.0+**

---

## Notes

1. **SQL Migrations (.sql) can be removed** - Python migrations are the primary source of truth
2. **Dependency Chain** - Each migration depends on the previous one
3. **Idempotent Design** - All `ALTER TABLE` operations check for column existence
4. **Trigger Function** - Created once in migration 005 and reused in subsequent migrations
5. **UUID Generation** - Uses PostgreSQL's `gen_random_uuid()` function
6. **Audit Fields** - Consistent created_by/modified_by/modified_at across tables

---

## Next Steps

1. ✅ Verify all 4 Python migrations are in `/migrations/versions/`
2. ✅ Run `flask db upgrade` to apply migrations
3. ✅ Verify database schema with `flask db current`
4. (Optional) Delete `.sql` migration files to clean up
5. Update your migration strategy to use Python-only migrations going forward

---

## Troubleshooting

### Migration Won't Run
- Check that PostgreSQL `uuid-ossp` extension is available
- Verify database connectivity: `flask db current`
- Check for syntax errors: `flask db upgrade --sql 005_add_tenant_company_hierarchy`

### Idempotency Issues
- All migrations use `IF NOT EXISTS` or upsert patterns
- Safe to re-run if a step fails

### Rollback Issues
- Ensure migrations are in correct order
- Check that dependency chain is intact
- Verify downgrade() functions exist

---

**Conversion Completed:** All SQL migrations successfully converted to Python Alembic format.
**Migration Strategy:** Going forward, use Python migrations exclusively for better maintainability.