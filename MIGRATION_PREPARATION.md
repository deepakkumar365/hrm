# 🚀 PRODUCTION DATABASE MIGRATION GUIDE

## Overview
This guide prepares you to migrate development database data to production safely and efficiently.

---

## ⚠️ CRITICAL REQUIREMENTS

### Before Starting:
1. ✅ **Backup Production Database** - Take a complete backup first
2. ✅ **Backup Development Database** - Keep development data safe
3. ✅ **Database Credentials Ready** - Both DEV_DATABASE_URL and PROD_DATABASE_URL in .env
4. ✅ **Network Access** - Ensure both databases are accessible
5. ✅ **Sufficient Disk Space** - For backup and migration files
6. ✅ **No Active Users** - Stop the application before migration
7. ✅ **Python Environment** - Activate venv with required packages

---

## 📋 PRE-MIGRATION CHECKLIST

```
Environment Setup:
  ☐ Confirm .env file has DEV_DATABASE_URL
  ☐ Confirm .env file has PROD_DATABASE_URL
  ☐ Confirm .env file has DEV_SESSION_SECRET
  ☐ Confirm .env file has PROD_SESSION_SECRET
  ☐ Python 3.11+ installed
  ☐ PostgreSQL client tools available
  ☐ All requirements.txt packages installed

Database Verification:
  ☐ Development database is accessible
  ☐ Production database is accessible
  ☐ Production database is EMPTY or backed up
  ☐ Network connectivity tested

Backup Preparation:
  ☐ Development DB backup created: dev_backup_YYYYMMDD.sql
  ☐ Production DB backup created (if migrating to existing DB)
  ☐ Backup files stored in safe location
  ☐ Backup verification completed

Application Status:
  ☐ Development server stopped
  ☐ Production server stopped
  ☐ No active database connections
  ☐ Check for any running transactions: none
```

---

## 🔧 MIGRATION MODES

### Mode 1: FULL MIGRATION (Recommended for First Time)
```bash
python db_migration_to_prod.py --mode full
```
**Includes:**
- Schema migration (via Alembic)
- Master data export and import
- Full validation and verification

**Duration:** 5-15 minutes depending on data volume

**Best For:** Initial setup, complete data migration

---

### Mode 2: SCHEMA ONLY
```bash
python db_migration_to_prod.py --mode schema-only
```
**Includes:**
- Database schema creation only
- No data transferred

**Duration:** 1-3 minutes

**Best For:** Testing schema compatibility, dry runs

---

### Mode 3: DATA ONLY
```bash
python db_migration_to_prod.py --mode data-only
```
**Includes:**
- Master data export from development
- Master data import to production
- Assumes schema already exists

**Duration:** 2-10 minutes depending on data volume

**Best For:** Re-running failed migrations, incremental updates

---

## 📊 DATA MIGRATION FLOW

```
Development DB
    ├─ organization
    ├─ role
    ├─ designation
    ├─ leave_type
    ├─ bank
    ├─ overtime_group
    ├─ compliance_requirement
    └─ document_type
                ↓
        [EXPORT to master_data_TIMESTAMP.sql]
                ↓
        [IMPORT to Production DB]
                ↓
Production DB
    ├─ organization
    ├─ role
    ├─ designation
    ├─ leave_type
    ├─ bank
    ├─ overtime_group
    ├─ compliance_requirement
    └─ document_type
```

---

## 🚀 STEP-BY-STEP MIGRATION

### Step 1: Verify Environment Variables
```bash
# Check that .env contains:
# DEV_DATABASE_URL=postgresql://user:pass@host:port/dev_db
# PROD_DATABASE_URL=postgresql://user:pass@host:port/prod_db
# DEV_SESSION_SECRET=your-dev-secret
# PROD_SESSION_SECRET=your-prod-secret
```

### Step 2: Test Database Connectivity
```bash
python verify_migration.py
```

### Step 3: Create Backups
```bash
# Development backup
pg_dump $DEV_DATABASE_URL > dev_backup_$(date +%Y%m%d_%H%M%S).sql

# Production backup (if exists)
pg_dump $PROD_DATABASE_URL > prod_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Step 4: Run Verification Script
```bash
python verify_prod_migration.py
```

### Step 5: Execute Migration
```bash
# Option A: Full migration
python db_migration_to_prod.py --mode full

# Option B: Schema only (for testing)
python db_migration_to_prod.py --mode schema-only

# Option C: Data only (if schema exists)
python db_migration_to_prod.py --mode data-only
```

### Step 6: Verify Migration Success
```bash
python verify_prod_migration.py
```

### Step 7: Post-Migration Tasks
```bash
# 1. Reset all user passwords
python prod_password_management.py
# Choose option 4 to reset all users

# 2. Verify users can login
python test_login_credentials.py

# 3. Check application startup
ENVIRONMENT=production python main.py
```

---

## ✅ POST-MIGRATION VALIDATION

### Data Integrity Checks
```bash
# Verify table counts
SELECT table_name, row_count 
FROM production_db;

# Check foreign key constraints
SELECT constraint_name 
FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY';

# Verify indexes
SELECT indexname FROM pg_indexes 
WHERE schemaname = 'public';
```

### Application Checks
```bash
# 1. Users can login
# 2. Organizations visible
# 3. Designations available
# 4. Leave types configured
# 5. Payroll settings intact
# 6. Reports generate correctly
```

---

## 🔄 ROLLBACK PROCEDURE

If migration fails or data is corrupted:

### Rollback to Development
```bash
# Stop production application
# Restore from backup
psql $PROD_DATABASE_URL < prod_backup_YYYYMMDD_HHMMSS.sql

# Verify restoration
python verify_prod_migration.py

# Restart application
ENVIRONMENT=production python main.py
```

### Restart Migration
```bash
# After fixing issues, run:
python db_migration_to_prod.py --mode full --retry
```

---

## 📝 IMPORTANT NOTES

### What Gets Migrated
✅ Organization configurations  
✅ User roles and permissions  
✅ Designations/Job titles  
✅ Leave types and settings  
✅ Bank details  
✅ Overtime groups  
✅ Compliance requirements  
✅ Document types  

### What Does NOT Get Migrated
❌ User passwords (will be reset - see password guide)  
❌ Employee profiles and personal data (manual transfer required)  
❌ Attendance records (if not in master data)  
❌ Payroll entries (manual verification required)  
❌ Leave applications (manual assessment)  
❌ Session data (cleared automatically)  

### Password Management After Migration
After data migration, run:
```bash
python prod_password_management.py
# Choose option 4: Reset ALL users to default password
# All users will need to change password on first login
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Connection refused" error
**Solution:**
```bash
# Check PostgreSQL service is running
# Verify database URL in .env
# Test connection: psql $PROD_DATABASE_URL
```

### Issue: "Foreign key constraint failed"
**Solution:**
```bash
# Check for data inconsistencies
# Run in order: parent tables first
# Use: python verify_prod_migration.py --detailed
```

### Issue: "Permission denied" error
**Solution:**
```bash
# Verify database user has:
# - CREATE TABLE
# - CREATE SCHEMA
# - INSERT privileges
# Grant if needed: ALTER USER db_user WITH CREATEDB;
```

### Issue: "Out of disk space"
**Solution:**
```bash
# Free up space on server
# Reduce backup retention
# Run migration with smaller chunks
```

---

## 📞 SUPPORT & VERIFICATION

### Quick Status Check
```bash
python verify_prod_migration.py --quick
```

### Detailed Report
```bash
python verify_prod_migration.py --detailed
```

### Database Statistics
```bash
python verify_prod_migration.py --stats
```

---

## ⏱️ MIGRATION TIMELINE

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| Pre-Migration | Backups & Verification | 30 min | ☐ |
| Migration | Schema & Data Transfer | 10 min | ☐ |
| Post-Migration | Validation & Testing | 20 min | ☐ |
| Final | User Setup & Go-Live | 15 min | ☐ |
| **Total** | **All Steps** | **~75 min** | ☐ |

---

## ✨ SUCCESS INDICATORS

✅ All tables present in production  
✅ Data counts match between dev and prod  
✅ No foreign key violations  
✅ Application starts without errors  
✅ Users can login with temporary password  
✅ All organization data visible  
✅ Payroll module accessible  
✅ Reports generate correctly  

---

**Last Updated:** 2024  
**Version:** 1.0  
**Migration Ready:** YES ✅