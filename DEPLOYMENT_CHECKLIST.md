# 📋 Production Deployment Checklist

**Project:** HRMS (Human Resource Management System)  
**Deployment Date:** _______________  
**Deployed By:** _______________  
**Reviewed By:** _______________  

---

## ✅ Phase 1: Pre-Deployment (2-3 hours before)

### Code Readiness
- [ ] All features tested on development branch
- [ ] All bug fixes merged to development branch
- [ ] Code review completed and approved
- [ ] No console errors or warnings
- [ ] All API endpoints tested
- [ ] Environment variables verified

### Database Preparation
- [ ] Development database verified working
- [ ] Master data verified in development
  - [ ] Organizations configured
  - [ ] Roles defined
  - [ ] Designations created
  - [ ] Leave types set
  - [ ] Banks configured
- [ ] Database backup created: `dev_db_backup_$(date).sql`
- [ ] Production database credentials verified
- [ ] Database connection strings confirmed in render.yaml

### Infrastructure
- [ ] Production service created in Render
- [ ] Production PostgreSQL database created in Render
- [ ] Environment variables configured in Render
  - [ ] PROD_DATABASE_URL set
  - [ ] PROD_SESSION_SECRET generated
  - [ ] ENVIRONMENT = "production"
- [ ] Health check endpoint configured: `/health`
- [ ] Build and start commands verified

### Testing
- [ ] Run pre-deployment verification:
  ```bash
  python verify_prod_deployment.py --env dev
  ```
  - [ ] All checks passed ✅
- [ ] Local build test successful:
  ```bash
  ./build.sh
  ```
- [ ] Application starts locally without errors

---

## ✅ Phase 2: Database Migration (30-45 minutes before)

### Migration Execution
- [ ] Run full database migration:
  ```bash
  python db_migration_to_prod.py --mode full
  ```
  - [ ] Schema migration completed
  - [ ] Master data exported
  - [ ] Master data imported
  - [ ] Verification passed

- [ ] Verification completed:
  ```bash
  python verify_prod_deployment.py --env prod
  ```
  - [ ] All checks passed ✅
  - [ ] Master data visible in production DB
  - [ ] Tables created successfully
  - [ ] Indexes created successfully

### Backup Verification
- [ ] Master data export file saved: `master_data_*.sql`
- [ ] File location noted: _______________
- [ ] Backup accessible if rollback needed

---

## ✅ Phase 3: Code Deployment (15-30 minutes)

### Git Repository
- [ ] Develop branch has all updates
- [ ] Master branch pulled latest
- [ ] All commits are signed/verified
- [ ] Tag created for this release (optional):
  ```bash
  git tag -a v1.0.0 -m "Production release"
  git push origin v1.0.0
  ```

### Push to Master
- [ ] Merge develop to master locally:
  ```bash
  git checkout master
  git pull origin master
  git merge origin/development
  ```
  - [ ] No merge conflicts
  - [ ] Merge successful

- [ ] Push to master:
  ```bash
  git push origin master
  ```
  - [ ] Push successful (no errors)

### Render Deployment
- [ ] Monitor Render deployment:
  - [ ] Go to Render Dashboard: https://render.com/dashboard
  - [ ] Select: noltrion-hrm service
  - [ ] Watch: "Logs" tab for deployment progress

- [ ] Watch for key milestones:
  - [ ] Build started
  - [ ] Dependencies installed
  - [ ] Application built
  - [ ] Migrations applied (alembic upgrade head)
  - [ ] Service started successfully
  - [ ] Health check passed

- [ ] Deployment complete:
  - [ ] Status shows "Live" (green)
  - [ ] Last deployed time updated
  - [ ] No error logs in console

---

## ✅ Phase 4: Immediate Post-Deployment (5-10 minutes)

### Application Health
- [ ] Application loads without errors:
  ```bash
  curl -I https://noltrion-hrm.render.com
  ```
  - [ ] HTTP Status: 200 or 302 (redirect to login)

- [ ] Health check endpoint responds:
  ```bash
  curl https://noltrion-hrm.render.com/health
  ```
  - [ ] Response: `{"status": "healthy"}`

### Database Connectivity
- [ ] Application connects to production database
- [ ] No database connection errors in logs
- [ ] Verify with:
  ```bash
  python verify_prod_deployment.py --env prod --report
  ```

### Security Verification
- [ ] All API endpoints require authentication
- [ ] Session management working
- [ ] HTTPS enforced (no HTTP access)
- [ ] CSRF protection enabled

---

## ✅ Phase 5: Functional Testing (15-30 minutes)

### Authentication
- [ ] [ ] Login page loads
- [ ] [ ] Admin credentials work: `username` / `password`
- [ ] [ ] Session persists across pages
- [ ] [ ] Logout works correctly

### Dashboard
- [ ] [ ] Dashboard loads without errors
- [ ] [ ] All widgets display data
- [ ] [ ] Charts render correctly
- [ ] [ ] Navigation menu visible

### Master Data
- [ ] [ ] Organizations visible and accessible
- [ ] [ ] Roles displayed correctly
- [ ] [ ] Designations load in dropdowns
- [ ] [ ] Leave types accessible
- [ ] [ ] Banks available for payroll

### Core Features
- [ ] [ ] Employee management works
  - [ ] Can create new employee
  - [ ] Employee ID generation works
  - [ ] Can edit employee
  - [ ] Employee list displays correctly

- [ ] [ ] Payroll module works
  - [ ] Can create payroll
  - [ ] Calculations accurate
  - [ ] Can generate payslip

- [ ] [ ] Attendance tracking works
  - [ ] Can record attendance
  - [ ] Reports generate

- [ ] [ ] Leave management works
  - [ ] Can request leave
  - [ ] Can approve leave

### API Testing
- [ ] [ ] GET endpoints return data
- [ ] [ ] POST endpoints create records
- [ ] [ ] PUT endpoints update records
- [ ] [ ] DELETE endpoints remove records
- [ ] [ ] Error responses are appropriate

---

## ✅ Phase 6: Performance & Monitoring (10 minutes)

### Performance
- [ ] [ ] Pages load within 2-3 seconds
- [ ] [ ] No console errors (DevTools)
- [ ] [ ] No console warnings
- [ ] [ ] Database queries performant

### Render Monitoring
- [ ] [ ] CPU usage reasonable (<70%)
- [ ] [ ] Memory usage stable (<512MB)
- [ ] [ ] No out-of-memory errors
- [ ] [ ] Disk space available

### Logs Review
- [ ] [ ] No error messages in Render logs
- [ ] [ ] No critical warnings
- [ ] [ ] Application running normally
- [ ] [ ] Database operations logged normally

---

## ✅ Phase 7: Team Communication (5 minutes)

### Notifications
- [ ] [ ] Team lead notified of go-live
- [ ] [ ] Super admin user(s) informed
- [ ] [ ] Tenant admins notified if applicable
- [ ] [ ] Documentation updated if needed

### Documentation
- [ ] [ ] Deployment date recorded
- [ ] [ ] Version number noted
- [ ] [ ] Known issues documented (if any)
- [ ] [ ] Rollback procedure documented

### Signoff
- [ ] Deployed by: _______________
- [ ] Verified by: _______________
- [ ] Approved by: _______________
- [ ] Date/Time: _______________

---

## ⚠️ Phase 8: Rollback Plan (If Needed)

### Automatic Rollback Triggers
- [ ] Application won't start
- [ ] Database connection fails persistently
- [ ] Critical feature broken after 15 min testing
- [ ] Data corruption detected

### Manual Rollback Steps
1. [ ] Revert git commit:
   ```bash
   git checkout master
   git revert HEAD
   git push origin master
   ```

2. [ ] Render will automatically redeploy previous version

3. [ ] Monitor deployment completion

4. [ ] Verify application restored:
   ```bash
   curl https://noltrion-hrm.render.com/health
   ```

5. [ ] Restore database from backup (if needed):
   - Contact Render support or manually restore backup
   - Restore file: `dev_db_backup_*.sql`

6. [ ] Post-mortem review completed
   - Issue root cause identified
   - Fix prepared
   - Schedule new deployment

---

## 📊 Deployment Summary

| Item | Status | Notes |
|------|--------|-------|
| **Code Deployment** | ✅/❌ | |
| **Database Migration** | ✅/❌ | |
| **Health Check** | ✅/❌ | |
| **Core Features** | ✅/❌ | |
| **Data Integrity** | ✅/❌ | |
| **Performance** | ✅/❌ | |
| **Overall Status** | ✅/❌ | |

---

## 📝 Notes & Observations

```
[Space for deployment notes]




```

---

## 🔗 Important Contacts & Resources

| Resource | URL/Contact |
|----------|------------|
| Render Dashboard | https://render.com/dashboard |
| Application URL | https://noltrion-hrm.render.com |
| GitHub Repo | https://github.com/your-repo |
| Database Backup | `dev_db_backup_*.sql` |
| Master Data Export | `master_data_*.sql` |
| Migration Guide | PRODUCTION_DB_MIGRATION_GUIDE.md |
| Quick Start | PRODUCTION_DEPLOYMENT_QUICK_START.md |

---

## ✨ Success Criteria Met

By checking all items above, you've confirmed:

✅ Application deployed and running  
✅ Database migrated with schema and master data  
✅ Core functionality verified  
✅ Security measures verified  
✅ Performance acceptable  
✅ Team notified  
✅ Rollback plan ready  

## 🎉 Deployment Complete!

Your HRMS application is now live in production!

**Deployment completed on:** _______________  
**Expected availability:** Immediate  
**Estimated ROI:** User-friendly, efficient HR management system ready for organization-wide use  

---

**Questions?** Refer to:
- `PRODUCTION_DB_MIGRATION_GUIDE.md` - Detailed technical guide
- `PRODUCTION_DEPLOYMENT_QUICK_START.md` - Quick reference
- Render Dashboard - Logs and monitoring

**Congratulations on your production deployment! 🚀**