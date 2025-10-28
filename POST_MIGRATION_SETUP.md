# 🎯 POST-MIGRATION SETUP & GO-LIVE GUIDE

## Overview
This guide covers everything needed after database migration to get production running smoothly.

---

## 📋 POST-MIGRATION CHECKLIST

### Immediately After Migration (Within 5 minutes)

- [ ] Verify migration script completed successfully
- [ ] Check for any error messages
- [ ] Confirm production database has data (run verification script)
- [ ] Review migration log file
- [ ] Create timestamp backup of the successful migration

### Before Starting Application (Next 15 minutes)

- [ ] Reset all user passwords to temporary default
- [ ] Verify at least one user can login with temporary password
- [ ] Check database is accessible from application server
- [ ] Verify environment variables are set correctly
- [ ] Confirm ENVIRONMENT variable is set to 'production'

### Before Go-Live (Next 30 minutes)

- [ ] Test application startup
- [ ] Verify all pages load without errors
- [ ] Test user login with multiple user types
- [ ] Check organization/company visibility
- [ ] Verify payroll module is accessible
- [ ] Check if reports generate correctly
- [ ] Review application logs for any warnings

---

## 🔐 STEP 1: PASSWORD MANAGEMENT

### Why This is Critical
After migration, users from development database need a known password to login in production.

### Option A: Reset All Users to Same Password (Recommended)

**Best for:** Initial setup when you want all users to have access immediately

```bash
# Run interactive tool
python prod_password_management.py

# Choose Option 4: Reset ALL users
# Enter temporary password: Noltrion@123
# Confirm: yes

# Result: All users now have Noltrion@123
```

**What happens next:**
- Users login with temporary password
- System forces password change on first login
- Users create their own secure passwords

### Option B: Reset Specific Users

**Best for:** Setting up individual admin accounts

```bash
# Run interactive tool
python prod_password_management.py

# Choose Option 3: Reset specific user
# Enter username: superadmin
# Enter new password: YourSecurePassword123!
# Confirm: yes
```

### Option C: Verify Current Passwords (Testing)

```bash
# Run verification
python test_login_credentials.py

# This tests if all users can login
# Helps identify any password issues
```

### Password Best Practices

✅ DO:
- Use strong passwords (12+ characters)
- Include uppercase, lowercase, numbers, symbols
- Force password change on first login
- Log all password reset operations
- Inform users of temporary password securely

❌ DON'T:
- Use simple passwords (123456, password, etc.)
- Share passwords via email or chat
- Store passwords in plain text
- Use same password for all users
- Forget to make users change password

---

## 🚀 STEP 2: APPLICATION STARTUP

### Pre-Startup Verification

```bash
# Verify environment variables
echo $ENVIRONMENT          # Should be: production
echo $PROD_DATABASE_URL    # Should be: postgresql://...
echo $PROD_SESSION_SECRET  # Should be set

# If any are missing, update .env file
```

### Start Application on Local Machine

**Windows (PowerShell):**
```powershell
# Set production environment
$env:ENVIRONMENT = "production"

# Start application
python main.py

# Expected output:
# [INFO] Running in PRODUCTION mode
# [INFO] Starting HRMS Application...
# * Running on http://127.0.0.1:5000
```

**Linux/Mac:**
```bash
export ENVIRONMENT=production
python main.py

# Expected output:
# [INFO] Running in PRODUCTION mode
# [INFO] Starting HRMS Application...
# * Running on http://127.0.0.1:5000
```

### Start Application on Render/Cloud

1. Go to your deployment dashboard
2. Re-enable or restart the service
3. Set environment variables:
   - `ENVIRONMENT=production`
   - `PROD_DATABASE_URL=postgresql://...`
   - `PROD_SESSION_SECRET=your-secret`
4. Wait for deployment to complete (2-3 minutes)
5. Check deployment logs for errors

### Startup Troubleshooting

**Error: "PROD_DATABASE_URL not set"**
```bash
# Solution: Add to .env file
PROD_DATABASE_URL=postgresql://user:pass@host:port/database
```

**Error: "Cannot connect to database"**
```bash
# Solution: Verify connection
psql $PROD_DATABASE_URL -c "SELECT 1"

# If fails, check:
# - Database is running
# - Credentials are correct
# - Network connectivity
# - Firewall rules
```

**Error: "Permission denied"**
```bash
# Solution: Database user needs privileges
# Contact database admin to grant:
# - CONNECT
# - CREATE
# - SELECT, INSERT, UPDATE, DELETE
```

---

## ✅ STEP 3: LOGIN & FUNCTIONALITY TESTING

### Test User Login

**In browser, go to:**
```
http://localhost:5000/login    (if local)
https://your-app.com/login     (if deployed)
```

**Test with multiple user types:**

1. **Super Admin Login**
   - Username: `superadmin`
   - Password: `Noltrion@123` (or your set password)
   - Expected: See admin dashboard

2. **Manager Login**
   - Username: `manager`
   - Password: `Noltrion@123` (or your set password)
   - Expected: See manager dashboard

3. **Employee Login**
   - Username: `employee`
   - Password: `Noltrion@123` (or your set password)
   - Expected: See employee dashboard

4. **Tenant Admin Login**
   - Username: `tenantadmin`
   - Password: `Noltrion@123` (or your set password)
   - Expected: See tenant admin dashboard

### Verify Force Password Change

On first login after migration:
1. User attempts login
2. System forces password change dialog
3. User enters new password
4. Login successful with new password

### Test Core Features

After login, verify:

**Organizations:**
- [ ] Organizations visible in dropdown
- [ ] Can switch between organizations
- [ ] All organization settings intact

**User Management:**
- [ ] Can view all users
- [ ] Can create new users
- [ ] Can edit user details
- [ ] Can disable/enable users
- [ ] Roles are correctly assigned

**Payroll Module:**
- [ ] Payroll menu visible
- [ ] Can view payroll entries
- [ ] Can create payroll
- [ ] Salary slip generation works

**Attendance:**
- [ ] Can mark attendance
- [ ] Can bulk upload attendance
- [ ] Attendance reports work

**Leave Management:**
- [ ] Leave types are available
- [ ] Can apply for leave
- [ ] Can approve/reject leaves

**Reports:**
- [ ] Reports section accessible
- [ ] Can generate sample reports
- [ ] Excel export works

---

## 📊 STEP 4: DATA VERIFICATION

### Verify Master Data

```bash
# Run verification script
python verify_prod_migration.py --detailed

# Should show:
# ✅ Organizations: X records
# ✅ Roles: X records
# ✅ Designations: X records
# ✅ Leave Types: X records
# ✅ Banks: X records
# ✅ Users: X records
```

### Manual Verification Steps

**Check Organizations:**
```sql
-- Run this in database
SELECT COUNT(*) as org_count FROM organization;
SELECT name FROM organization LIMIT 5;
```

**Check Users:**
```sql
SELECT COUNT(*) as user_count FROM hrm_users;
SELECT username, email, is_active FROM hrm_users LIMIT 5;
```

**Check Roles:**
```sql
SELECT COUNT(*) as role_count FROM role;
SELECT name FROM role;
```

**Check Data Integrity:**
```sql
-- Foreign keys should reference valid records
SELECT COUNT(*) FROM hrm_users WHERE organization_id NOT IN (SELECT id FROM organization);
-- Should return 0 (no orphaned records)
```

### Identify Missing Data

If data seems incomplete:

1. Compare record counts between dev and prod
2. Export missing data from development
3. Manually import into production
4. Or restore backup and retry migration

---

## 🔍 STEP 5: APPLICATION LOGS REVIEW

### Where Logs Are Located

**Local Machine:**
```
E:\Gobi\Pro\HRMS\hrm\logs\app.log
E:\Gobi\Pro\HRMS\hrm\logs\error.log
```

**Render/Cloud:**
```
Dashboard → Logs → View logs
```

### What to Look For

✅ Good Signs:
```
[INFO] Connected to database successfully
[INFO] All tables initialized
[WARNING] (optional, non-critical)
```

❌ Problems to Watch For:
```
[ERROR] Database connection failed
[ERROR] Foreign key constraint violation
[ERROR] Import error (missing dependencies)
[CRITICAL] Application failed to start
```

### Fix Common Errors

**Error: "relation 'xyz' does not exist"**
- Migration didn't complete fully
- Run: `python db_migration_to_prod.py --mode full`

**Error: "could not connect to database"**
- Check PROD_DATABASE_URL
- Verify database is running
- Test connection: `psql $PROD_DATABASE_URL -c "SELECT 1"`

**Error: "permission denied"**
- Database user lacks privileges
- Contact database admin

---

## 🔄 STEP 6: ROLLBACK PROCEDURE (If Needed)

### When to Rollback

- Application won't start
- Critical data missing
- Users can't login
- Major functionality broken

### How to Rollback

**Option 1: Restore from Backup**
```bash
# Stop application
# Restore production database from backup
psql $PROD_DATABASE_URL < prod_backup_YYYYMMDD_HHMMSS.sql

# Restart application
python main.py
```

**Option 2: Re-run Migration**
```bash
# Fix the issue that caused failure
# Clear production database (if possible)
# Run migration again
python db_migration_to_prod.py --mode full
```

**Option 3: Use Development Database**
```bash
# Temporarily point to development database
# Edit .env: DATABASE_URL=$DEV_DATABASE_URL
# Restart application
# Identify root cause
# Fix and retry migration
```

---

## 📞 STEP 7: USER COMMUNICATION

### Notify Users Before Go-Live

**Email Template:**
```
Subject: HRMS System Upgrade - Temporary Password Required

Dear Users,

We have successfully upgraded our HRMS system to production. 
Please follow these steps to access the new system:

1. Go to: https://your-app.com
2. Login with your username and temporary password: Noltrion@123
3. You will be prompted to change your password on first login
4. Create a strong, unique password
5. You're ready to use the system!

If you experience any issues:
- Check browser compatibility (Chrome/Firefox recommended)
- Clear browser cache (Ctrl+Shift+Delete)
- Contact IT Support

Thank you!
```

### Provide Login Instructions

**Quick Reference Card:**
```
┌─────────────────────────────────────┐
│  HRMS LOGIN QUICK REFERENCE         │
├─────────────────────────────────────┤
│ URL: https://your-app.com/login     │
│ Username: [Your username]           │
│ Password: Noltrion@123 (temp)       │
│                                     │
│ Note: You must change your password │
│ on first login!                     │
│                                     │
│ Support: it-support@company.com     │
└─────────────────────────────────────┘
```

### Setup Support Team

- [ ] Document all user accounts and default passwords
- [ ] Create password reset procedures
- [ ] Setup support ticket system
- [ ] Document common issues and solutions
- [ ] Establish escalation procedures

---

## ✨ GO-LIVE CHECKLIST

### Final Verification (Before Opening to Users)

```
Infrastructure:
  ☐ Application deployed and running
  ☐ Database connected and accessible
  ☐ All services started
  ☐ SSL certificates valid (HTTPS working)

Functionality:
  ☐ Login works for all user types
  ☐ Dashboard loads correctly
  ☐ All menus visible and accessible
  ☐ Core modules functional (Payroll, Attendance, etc.)
  ☐ Reports generate successfully

Data:
  ☐ Master data migrated (Organizations, Roles, etc.)
  ☐ User accounts created
  ☐ No data corruption detected
  ☐ Foreign key relationships intact

Security:
  ☐ Passwords reset to temporary values
  ☐ Force password change enabled
  ☐ SSL/TLS configured
  ☐ Session timeouts set
  ☐ Error messages don't expose sensitive info

Documentation:
  ☐ User instructions provided
  ☐ Support team trained
  ☐ Runbooks created
  ☐ Escalation procedures defined

Go-Live Approval:
  ☐ Project manager approval
  ☐ Technical lead approval
  ☐ Business owner approval
  ☐ All stakeholders informed
```

---

## 📈 STEP 8: POST-GO-LIVE MONITORING

### Monitor First 24 Hours

- [ ] Check application performance metrics
- [ ] Monitor error logs regularly
- [ ] Be available for user support
- [ ] Track user feedback
- [ ] Document any issues

### Daily Tasks (First Week)

- [ ] Review application logs
- [ ] Check database performance
- [ ] Verify backups are running
- [ ] Monitor user adoption
- [ ] Address reported issues

### Weekly Tasks (First Month)

- [ ] Analyze user metrics
- [ ] Review system performance
- [ ] Optimize slow queries
- [ ] Schedule maintenance window (if needed)
- [ ] Plan next phase improvements

---

## 🎓 TRAINING & DOCUMENTATION

### User Training

Provide training on:
- [ ] How to login with temporary password
- [ ] How to change password
- [ ] Basic navigation
- [ ] Common tasks (mark attendance, apply leave, etc.)
- [ ] How to get help

### Support Documentation

Maintain documentation for:
- [ ] Troubleshooting guide
- [ ] FAQ
- [ ] Known issues and workarounds
- [ ] Contact information
- [ ] Escalation procedures

---

## 🚨 COMMON ISSUES & SOLUTIONS

### Issue: Users can't login

**Cause:** Password not reset after migration  
**Solution:**
```bash
python prod_password_management.py
# Choose option 4 to reset all passwords
```

### Issue: Application crashes on startup

**Cause:** Database connection issue  
**Solution:**
```bash
# Check database is running and accessible
psql $PROD_DATABASE_URL -c "SELECT 1"
# Verify .env has correct credentials
```

### Issue: Reports show no data

**Cause:** Data not migrated properly  
**Solution:**
```bash
python verify_prod_migration.py --detailed
# Check what data is missing
# Restore from backup and retry migration
```

### Issue: Users see old data

**Cause:** Cache not cleared  
**Solution:**
```bash
# Clear browser cache (Ctrl+Shift+Delete)
# Restart application
python main.py
```

---

## ✅ SUCCESS CRITERIA

Migration is successful when:

✅ Application starts without errors  
✅ Users can login with temporary password  
✅ All master data is visible (organizations, roles, etc.)  
✅ Payroll module accessible and functional  
✅ Reports generate correctly  
✅ No database integrity issues  
✅ All foreign key constraints satisfied  
✅ Performance acceptable  
✅ Backups running automatically  
✅ Support team trained and ready  

---

## 📚 REFERENCE DOCUMENTS

- MIGRATION_PREPARATION.md - Pre-migration guide
- MIGRATION_QUICK_START.txt - Step-by-step quick guide
- PASSWORD_MANAGEMENT_GUIDE.md - Password management details
- TROUBLESHOOTING_GUIDE.md - Detailed troubleshooting

---

## 📞 SUPPORT CONTACT

For issues during post-migration setup:
- [ ] Check application logs
- [ ] Review troubleshooting guide
- [ ] Run verification scripts
- [ ] Contact technical support with:
  - Error message
  - Application logs
  - Steps to reproduce

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** Ready for Production Go-Live ✅