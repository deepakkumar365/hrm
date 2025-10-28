# Quick Start: Python Migrations

## 🎯 What Was Done

4 SQL migrations have been converted to Python Alembic migrations:

| File | Type | Purpose |
|------|------|---------|
| **005_add_tenant_company_hierarchy.py** | Schema | Create tenant/company hierarchy + audit fields |
| **006_add_tenant_country_currency.py** | Schema | Add country/currency columns |
| **007_add_tenant_payment_and_documents.py** | Schema | Create payment config & documents tables |
| **008_insert_tenant_company_test_data.py** | Data | Insert test data (Noltrion tenant/companies) |

---

## 🚀 Getting Started

### 1. Apply All Migrations
```bash
cd c:\Repo\hrm
flask db upgrade
```

### 2. Check Migration Status
```bash
flask db current
```
**Expected Output:**
```
e6e02c1e87aa  08_insert_tenant_company_test_data
```

### 3. View Migration History
```bash
flask db history
```

---

## 📋 Migration Details

### Migration Chain
```
005_add_tenant_company_hierarchy
    ↓ (depends on)
006_add_tenant_country_currency
    ↓ (depends on)
007_add_tenant_payment_and_documents
    ↓ (depends on)
008_insert_tenant_company_test_data
```

### What Each Migration Creates

#### 005 - Tenant & Company Hierarchy
**Tables Created:**
- `hrm_tenant` - Top-level tenant
- `hrm_company` - Companies under tenant

**Columns Added:**
- `organization.tenant_id`
- `hrm_employee.company_id`
- Audit fields to both tables

**Triggers Created:**
- Auto-update `modified_at` on changes

#### 006 - Country & Currency
**Columns Added to `hrm_tenant`:**
- `country_code` (e.g., 'SG', 'US', 'IN')
- `currency_code` (e.g., 'SGD', 'USD', 'INR')

#### 007 - Payment & Documents
**Tables Created:**
- `hrm_tenant_payment_config` - Billing configuration
- `hrm_tenant_documents` - Document storage

#### 008 - Test Data
**Data Inserted:**
- Tenant: Noltrion HRM (code: NOLTRION)
- Companies: Noltrion India, Noltrion Singapore
- Sample employee links

---

## 📁 File Locations

**New Python Migrations:**
```
c:\Repo\hrm\migrations\versions\
  ├── 005_add_tenant_company_hierarchy.py
  ├── 006_add_tenant_country_currency.py
  ├── 007_add_tenant_payment_and_documents.py
  └── 008_insert_tenant_company_test_data.py
```

**Documentation:**
```
c:\Repo\hrm\migrations\
  ├── PYTHON_MIGRATIONS_SUMMARY.md (Complete reference)
  ├── SQL_TO_PYTHON_CONVERSION_GUIDE.md (Conversion patterns)
  └── QUICK_START_PYTHON_MIGRATIONS.md (This file)
```

**Original SQL Migrations (can be archived/deleted):**
```
c:\Repo\hrm\migrations\versions\
  ├── 001_add_tenant_company_hierarchy.sql
  ├── 002_test_data_tenant_company.sql
  ├── 003_add_tenant_country_currency.sql
  └── 004_add_tenant_payment_and_documents.sql
```

---

## 🔍 Verification

### Check if Migrations Exist
```bash
ls c:\Repo\hrm\migrations\versions\00*.py
```

### View Generated SQL (without running)
```bash
flask db upgrade --sql 005_add_tenant_company_hierarchy
```

### Test Specific Migration
```bash
flask db upgrade 006_add_tenant_country_currency
```

### Verify Database Schema
```bash
# Check tables exist
flask shell
>>> from app import db
>>> from sqlalchemy import inspect
>>> inspector = inspect(db.engine)
>>> inspector.get_table_names()
['hrm_tenant', 'hrm_company', 'hrm_tenant_payment_config', 'hrm_tenant_documents', ...]
```

---

## ⏮️ Rollback Operations

### Rollback Last Migration
```bash
flask db downgrade
```

### Rollback to Specific Migration
```bash
flask db downgrade 007_add_tenant_payment_and_documents
```

### Rollback All Custom Migrations
```bash
# Find the migration before 005
flask db downgrade 2be68655c2bb_merge_payroll_and_enhancements
```

---

## 🔧 Common Tasks

### Create New Migration
```bash
# Auto-detect schema changes
flask db migrate -m "Add new column to users"

# Manual migration
flask db revision -m "Custom migration description"
```

### Show Current Revision
```bash
flask db current
```

### Show All Revisions
```bash
flask db history
```

### Check Migration Status Without Applying
```bash
flask db upgrade --sql
```

---

## ⚠️ Important Notes

1. **Migration Chain Matters** - Migrations depend on each other in order
2. **Idempotent** - Safe to re-run if something fails
3. **Backup First** - Always backup database before running migrations in production
4. **Test Rollback** - Test `downgrade()` in test environment first
5. **One-Way Data** - Migration 008 (test data) is one-way (data won't rollback to empty state)

---

## 🐛 Troubleshooting

### Error: "sqlalchemy.exc.OperationalError"
**Solution:** Ensure PostgreSQL is running and database exists
```bash
flask db current
```

### Error: "ModuleNotFoundError: No module named 'alembic'"
**Solution:** Install Flask-Migrate
```bash
pip install Flask-Migrate
```

### Error: "UUID extension not available"
**Solution:** Migration 005 creates it automatically, but if needed manually:
```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### Migration Won't Downgrade
**Solution:** Check `downgrade()` function is defined properly
```bash
flask db downgrade --sql 005_add_tenant_company_hierarchy
```

### Alembic Branches Detected
**Solution:** Clean up alembic version table
```bash
flask db merge --rev-id merged
flask db upgrade
```

---

## 📚 Reference Documentation

| Document | Purpose |
|----------|---------|
| `PYTHON_MIGRATIONS_SUMMARY.md` | Complete migration reference |
| `SQL_TO_PYTHON_CONVERSION_GUIDE.md` | Learn conversion patterns |
| `QUICK_START_PYTHON_MIGRATIONS.md` | Quick reference (this file) |

---

## ✅ Checklist

Before committing to production:

- [ ] All 4 migrations created in `migrations/versions/`
- [ ] `flask db upgrade` runs successfully
- [ ] Database tables created correctly
- [ ] Test data inserted (if needed)
- [ ] `flask db downgrade` tested and works
- [ ] Database backed up
- [ ] Application starts without errors
- [ ] All tests pass
- [ ] SQL migration files archived or deleted

---

## 📞 Need Help?

1. **Check PYTHON_MIGRATIONS_SUMMARY.md** - Full migration reference
2. **Check SQL_TO_PYTHON_CONVERSION_GUIDE.md** - How conversions work
3. **Review the migration files** - Each has detailed comments
4. **Run `flask db current`** - Check current state
5. **Test in dev environment first** - Always test before production

---

**Conversion Status:** ✅ Complete  
**Ready for Production:** ✅ Yes (after testing)  
**Last Updated:** 2024