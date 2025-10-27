# 🚀 Production Deployment Quick Start

## ⚡ 5-Minute Quick Start

### Step 1: Pre-Flight Check (1 minute)
```bash
# Verify environment setup
python verify_prod_deployment.py --env dev

# Expected: All checks should pass
# If any fail, fix before proceeding
```

### Step 2: Run Migration (2 minutes)
```bash
# Migrate schema and master data to production
python db_migration_to_prod.py --mode full

# This will:
# ✅ Connect to dev and prod databases
# ✅ Run Alembic migrations on prod
# ✅ Export master data from dev
# ✅ Import master data to prod
# ✅ Verify success
```

### Step 3: Deploy to Production (1 minute)
```bash
# Merge to master and push
git checkout master
git pull origin master
git merge origin/development
git push origin master

# Render will automatically:
# ✅ Detect push to master branch
# ✅ Build application
# ✅ Run migrations (alembic upgrade head)
# ✅ Start production service
```

### Step 4: Verify Production (1 minute)
```bash
# Check production deployment
curl https://your-prod-url.render.com/health

# Expected response:
# {"status": "healthy"}

# Then verify database
python verify_prod_deployment.py --env prod
```

---

## 📋 Complete Deployment Checklist

### Before Deployment
- [ ] Code reviewed and tested on development
- [ ] All features working on dev branch
- [ ] Master data verified in dev database
- [ ] Backup created of dev database
- [ ] Render production service is running
- [ ] Production database credentials verified

### During Migration
```bash
# Step 1: Verify development database
python verify_prod_deployment.py --env dev
# All checks should pass ✅

# Step 2: Run full migration
python db_migration_to_prod.py --mode full
# Monitor output for any errors

# Step 3: Merge to master
git checkout master
git merge origin/development
git push origin master

# Step 4: Monitor Render deployment
# Go to Render Dashboard → noltrion-hrm → Logs
# Watch for: "Migrations applied successfully"
```

### After Deployment
- [ ] Production app loads: `https://prod-url/`
- [ ] Login works with test admin account
- [ ] Master data visible (roles, designations, etc.)
- [ ] Employee creation works
- [ ] Payroll module accessible
- [ ] No error logs in Render dashboard
- [ ] Team notified of go-live

---

## 🔧 Common Scenarios

### Scenario 1: Fresh Production Database (First Time)
```bash
# 1. Verify dev has data
python verify_prod_deployment.py --env dev

# 2. Run full migration
python db_migration_to_prod.py --mode full

# 3. Deploy
git push origin master

# 4. Verify
python verify_prod_deployment.py --env prod
```

### Scenario 2: Production Database Exists (Data Update)
```bash
# If production database already exists with old data:

# 1. Backup production
pg_dump "your_prod_connection_string" > prod_backup.sql

# 2. Update master data only
python db_migration_to_prod.py --mode data-only

# 3. Deploy code
git push origin master
```

### Scenario 3: Schema Changes Only
```bash
# If only database schema changed (new migrations):

# 1. Run schema-only migration
python db_migration_to_prod.py --mode schema-only

# 2. Deploy
git push origin master
```

---

## ⚠️ Troubleshooting

### Problem: "Tables don't exist" error
```bash
# Solution: Re-run schema migration
python db_migration_to_prod.py --mode schema-only
```

### Problem: "Master data not visible"
```bash
# Solution: Re-import master data
python db_migration_to_prod.py --mode data-only
```

### Problem: Connection timeout
```bash
# Solution: Verify database connection
python verify_prod_deployment.py --env prod
# Check Render Dashboard for database status
```

### Problem: Need to rollback
```bash
# 1. Revert git commit
git revert HEAD

# 2. Push to master
git push origin master

# 3. Restore database backup
# Contact Render support for database restore
```

---

## 📊 Deployment Comparison

| Environment | URL | Database | Purpose |
|-------------|-----|----------|---------|
| **Development** | http://localhost:5000 | DEV_DATABASE_URL | Testing & development |
| **Production** | https://prod-url.render.com | PROD_DATABASE_URL | Live application |

---

## 🎯 Success Criteria

Your production deployment is successful when:

✅ Application loads without errors  
✅ Login functionality works  
✅ Master data (roles, designations) visible  
✅ Can create new employees  
✅ Payroll calculations work  
✅ Reports generate successfully  
✅ No database connection errors  
✅ All users can access their roles  

---

## 📞 Post-Deployment Support

If you encounter issues after deployment:

1. **Check Render Logs:**
   - Go to Render Dashboard → noltrion-hrm → Logs
   - Look for any error messages

2. **Check Database:**
   ```bash
   python verify_prod_deployment.py --env prod
   ```

3. **Check Application Health:**
   ```bash
   curl https://your-prod-url.render.com/health
   ```

4. **Review Documentation:**
   - PRODUCTION_DB_MIGRATION_GUIDE.md (detailed guide)
   - PRODUCTION_DEPLOYMENT_QUICK_START.md (this file)

---

## 🔗 Quick Reference Commands

```bash
# Verify environment
python verify_prod_deployment.py --env dev

# Full migration
python db_migration_to_prod.py --mode full

# Schema only
python db_migration_to_prod.py --mode schema-only

# Data only
python db_migration_to_prod.py --mode data-only

# Verify production
python verify_prod_deployment.py --env prod

# Git deployment
git push origin master
```

---

## ✨ You're Ready!

All scripts are ready. Follow the 5-minute quick start above, and your production deployment will be complete! 🎉

**Questions?** Review the detailed guide: `PRODUCTION_DB_MIGRATION_GUIDE.md`
