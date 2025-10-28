# Production Database Migration Guide

## 📋 Overview

This guide provides step-by-step instructions to safely migrate your HRMS database from **Development** to **Production** on Render with PostgreSQL.

**Current Setup:**
- **Dev Database:** DEV_DATABASE_URL (from render.yaml)
- **Prod Database:** PROD_DATABASE_URL (from render.yaml)
- **Migration Tools:** Alembic + Custom Scripts
- **Master Data:** Companies, Roles, Designations, Leave Types, etc.

---

## 🎯 Migration Strategy

### Phase 1: Pre-Deployment Checklist
- [ ] All development testing complete
- [ ] Code merged to `origin/master`
- [ ] Render deployment configured
- [ ] Production database credentials verified
- [ ] Backup of development database created

### Phase 2: Schema Migration (Tables & Structure)
- [ ] Run Alembic migrations on production
- [ ] Verify all tables created
- [ ] Verify all indexes created

### Phase 3: Master Data Migration
- [ ] Export master data from development
- [ ] Import master data to production
- [ ] Verify data integrity

### Phase 4: Post-Deployment Validation
- [ ] Test login functionality
- [ ] Test all CRUD operations
- [ ] Verify master data is accessible
- [ ] Monitor error logs

---

## 🚀 Step-by-Step Migration Process

### Step 1: Verify Render Environment Setup

#### 1.1 Check Render.yaml Configuration
```bash
# Verify your render.yaml has both database URLs
cat render.yaml
```

**Expected Output:**
```yaml
envVars:
  - key: PROD_DATABASE_URL
    value: postgresql://... (production connection string)
  - key: DEV_DATABASE_URL
    value: postgresql://... (development connection string)
```

#### 1.2 Get Production Database Credentials
1. Go to Render Dashboard: https://render.com
2. Navigate to: **PostgreSQL** → **noltrion-db** (or your prod DB)
3. Copy the **External Database URL**
4. Verify it matches `PROD_DATABASE_URL` in render.yaml

---

### Step 2: Backup Development Database

#### 2.1 Create Backup (Recommended)
```bash
# Option A: Using pg_dump (from your local machine)
# Format: pg_dump "postgresql://user:password@host:port/dbname" > backup.sql

pg_dump "postgresql://noltrion_dev:password@dev-host:5432/noltrion_dev" > dev_db_backup_$(date +%Y%m%d).sql

# Option B: Using Render's built-in backup
# Go to Render Dashboard → PostgreSQL → Backups → Create Backup
```

**Save the backup file safely** in case rollback is needed.

---

### Step 3: Initialize Production Database Schema

#### 3.1 Run Alembic Migrations on Production
```bash
# Method 1: Render Web Service Environment (Automatic)
# The build.sh script includes: alembic upgrade head
# This runs automatically when you deploy to Render

# Method 2: Manual from Local Machine
# Set production database URL and run:
export DATABASE_URL="postgresql://noltrion_admin:password@dpg-xxxxx.render.com:5432/noltrion_hrm?sslmode=require"
alembic upgrade head
```

**Verification:**
```bash
# After migration, verify tables exist in production
python verify_prod_schema.py
```

---

### Step 4: Migrate Master Data

#### 4.1 Run Data Migration Script
```bash
# Export master data from development
python export_master_data.py --env dev --output master_data.sql

# Import to production
python import_master_data.py --env prod --input master_data.sql
```

**Or use the comprehensive script:**
```bash
python db_migration_to_prod.py --mode full
```

---

### Step 5: Deploy to Production

#### 5.1 Merge to Master Branch
```bash
# On your local machine
git checkout master
git pull origin master
git merge origin/development
git push origin master
```

#### 5.2 Render Auto-Deployment Triggers
- Render detects push to `master` branch
- Runs build process: `./build.sh`
- Executes: `alembic upgrade head` (schema setup)
- Starts: `gunicorn -c gunicorn.conf.py main:app`

---

### Step 6: Post-Deployment Validation

#### 6.1 Verify Production Deployment
```bash
# Check health endpoint
curl https://your-production-url.render.com/health

# Should return: {"status": "healthy"}
```

#### 6.2 Verify Database Tables
```python
# Run verification script
python verify_prod_deployment.py
```

**Expected Output:**
```
✓ Production database connection: SUCCESS
✓ Total tables found: 32
✓ Master data verified:
  - Organizations: 5
  - Roles: 8
  - Designations: 12
  - Leave Types: 6
✓ All indexes created: SUCCESS
```

#### 6.3 Manual Testing
1. **Login Test:** https://your-prod-url/login
   - Use test admin account
   - Verify session works
   
2. **Master Data Check:**
   - Dashboard → Settings → Check organizations loaded
   - Dashboard → Masters → Check designations loaded
   
3. **Employee Operations:**
   - Create new employee
   - Verify ID generation works
   - Check employee appears in list

---

## 🔧 Troubleshooting

### Issue: Tables Not Created in Production

**Symptoms:**
```
ERROR: relation "hrm_users" does not exist
```

**Solution:**
```bash
# Option 1: Re-run migrations
export DATABASE_URL="your_prod_database_url"
alembic upgrade head

# Option 2: Use initialization script
python initialize_prod_database.py
```

---

### Issue: Master Data Not Visible

**Symptoms:**
- Designations dropdown is empty
- Roles not showing in role management

**Solution:**
```bash
# Run master data import
python import_master_data.py --env prod --regenerate

# Verify data
SELECT COUNT(*) FROM role;
SELECT COUNT(*) FROM designation;
```

---

### Issue: Connection Timeout to Production DB

**Symptoms:**
```
FATAL: no pg_hba.conf entry for host "x.x.x.x"
```

**Solution:**
1. Verify PROD_DATABASE_URL in render.yaml is correct
2. Check production DB firewall settings:
   - Render Dashboard → PostgreSQL → Security
   - Ensure "Allow public access" is enabled
3. Test connection:
   ```bash
   psql "postgresql://noltrion_admin:password@host:5432/noltrion_hrm?sslmode=require"
   ```

---

## 📊 Database Comparison

### Development vs Production

| Aspect | Development | Production |
|--------|-------------|-----------|
| **URL** | DEV_DATABASE_URL | PROD_DATABASE_URL |
| **Host** | dev-postgres.render.com | oregon-postgres.render.com |
| **Database** | noltrion_dev | noltrion_hrm |
| **Schema** | Same (Alembic managed) | Same (Alembic managed) |
| **Master Data** | Full test data | Master data only |
| **Employee Records** | Test employees | Real employees |

---

## ⚠️ Important Considerations

### Database Size
- **Backup size:** ~50-100MB (depending on employee records)
- **Restore time:** ~2-5 minutes

### SSL/TLS Connection
- Production requires `?sslmode=require` in connection string
- Handled automatically in render.yaml

### Backup Strategy
- **Manual backup** before each deployment
- **Render's automated backups** (7-day retention)
- Keep offline backups for critical data

### Rollback Plan
If production deployment fails:
1. Restore from backup: `psql < dev_db_backup_YYYYMMDD.sql`
2. Revert master branch: `git revert [commit-hash]`
3. Re-push to trigger Render redeploy

---

## 🎯 Migration Checklist

```
PRE-MIGRATION
[ ] Code tested on development branch
[ ] All migrations run successfully on dev
[ ] Master data verified in dev
[ ] Backup created of dev database
[ ] Render production service configured

DURING MIGRATION
[ ] Merge code to master branch
[ ] Monitor Render deployment logs
[ ] Verify production build completes
[ ] Check application health endpoint

POST-MIGRATION
[ ] Production database accessible
[ ] All tables created
[ ] Master data imported
[ ] Application login works
[ ] Employee creation tested
[ ] Error logs clear of DB errors
[ ] Team notified of go-live
```

---

## 📞 Support & Resources

### Useful Commands

```bash
# Check migration status
alembic current

# List all migrations
alembic history

# See recent migrations
alembic history --rev-range =1..@+3

# Verify production schema
python verify_prod_schema.py

# Export master data
python export_master_data.py --env prod

# Check database size
SELECT pg_size_pretty(pg_database_size('noltrion_hrm'));
```

### Render Dashboard
- https://render.com/dashboard
- PostgreSQL instances under "Services"

### PostgreSQL Tools
- **DBeaver:** Free GUI tool for database management
- **pgAdmin:** Web-based PostgreSQL management
- **psql:** Command-line PostgreSQL client

---

## 🔗 Related Files

- **Migration Scripts:** `db_migration_to_prod.py`
- **Verification Script:** `verify_prod_deployment.py`
- **Master Data Export:** `export_master_data.py`
- **Environment Setup:** `render.yaml`
- **Alembic Config:** `migrations/alembic.ini`

---

**Last Updated:** 2024
**Status:** Production Ready