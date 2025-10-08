# 🚀 Quick Start Guide - Flask HRMS

## ✅ Status: FULLY OPERATIONAL

All critical issues have been resolved. The application is ready to use!

---

## 📋 What Was Fixed

1. ✅ **Circular Import Errors** - Resolved
2. ✅ **Database Initialization Issues** - Fixed
3. ✅ **Missing Database Tables** - Created (18 tables)
4. ✅ **Default Data** - Initialized (4 users, 4 roles, 1 organization)
5. ✅ **Password Authentication** - Working

---

## 🏃 Quick Start (Development)

### 1. Start the Application
```bash
cd E:/Gobi/Pro/HRMS/hrm
python app.py
```

### 2. Access the Application
```
URL: http://localhost:5000
```

### 3. Login with Default Credentials
```
Username: superadmin
Password: admin123
```

---

## 👥 Default User Accounts

| Username | Email | Password | Role |
|----------|-------|----------|------|
| `superadmin` | superadmin@hrm.com | `admin123` | SUPER_ADMIN |
| `admin` | admin@hrm.com | `admin123` | ADMIN |
| `manager` | manager@hrm.com | `admin123` | HR_MANAGER |
| `user` | user@hrm.com | `admin123` | EMPLOYEE |

⚠️ **Change these passwords immediately in production!**

---

## 🗄️ Database Status

### Tables Created: 18
```
✓ hrm_users              ✓ hrm_employee
✓ hrm_departments        ✓ hrm_attendance
✓ hrm_leave              ✓ hrm_payroll
✓ hrm_payroll_configuration
✓ hrm_appraisal          ✓ hrm_claim
✓ hrm_compliance_report  ✓ hrm_employee_documents
✓ hrm_work_schedules     ✓ hrm_working_hours
✓ hrm_tenant             ✓ hrm_company
✓ organization           ✓ role
✓ alembic_version
```

### Default Data:
- **4 Users** (superadmin, admin, manager, user)
- **4 Roles** (SUPER_ADMIN, ADMIN, HR_MANAGER, EMPLOYEE)
- **1 Organization** (Default Organization)

---

## 🛠️ Useful Commands

### Database Management
```bash
# Run migrations
flask db upgrade

# Check migration status
flask db current

# View migration history
flask db history

# Rollback one migration
flask db downgrade -1
```

### Verification Scripts
```bash
# Check database tables
python check_tables.py

# Test initialization
python test_initialization.py

# Reset default passwords
python reset_default_passwords.py

# Run full verification
python final_verification.py
```

### Application Management
```bash
# Start development server
python app.py

# Start with specific environment
ENVIRONMENT=development python app.py
ENVIRONMENT=production python app.py
```

---

## 🔧 Troubleshooting

### Issue: "relation does not exist" error
**Solution:**
```bash
flask db upgrade
python app.py
```

### Issue: Can't login with default credentials
**Solution:**
```bash
python reset_default_passwords.py
```

### Issue: Circular import error
**Solution:** Already fixed! If it reoccurs, check that model imports in `seed.py` are inside functions, not at module level.

### Issue: Application won't start
**Solution:**
```bash
# Check if tables exist
python check_tables.py

# Run full verification
python final_verification.py
```

---

## 📁 Important Files

### Configuration
- `app.py` - Main application file
- `.env` - Environment variables (create from `.env.example`)
- `config.py` - Configuration settings

### Database
- `models.py` - Database models
- `migrations/` - Alembic migration files

### Authentication
- `auth.py` - User authentication and default user creation
- `routes.py` - Application routes

### Utilities
- `check_tables.py` - Check database tables
- `test_initialization.py` - Test database initialization
- `reset_default_passwords.py` - Reset default user passwords
- `final_verification.py` - Complete system verification

### Documentation
- `ISSUE_RESOLUTION_SUMMARY.md` - Detailed resolution summary
- `QUICK_START.md` - This file
- `RENDER_DEPLOYMENT_GUIDE.md` - Production deployment guide

---

## 🚀 Production Deployment (Render)

### Prerequisites
1. GitHub repository connected to Render
2. PostgreSQL database created on Render
3. Environment variables configured in `render.yaml`

### Deployment Steps
```bash
# 1. Commit changes
git add .
git commit -m "Deploy HRMS application"
git push origin main

# 2. Render automatically:
#    - Runs build.sh
#    - Installs dependencies
#    - Runs migrations
#    - Starts application

# 3. Verify deployment
#    - Check Render build logs
#    - Check application logs
#    - Test login functionality
```

### Post-Deployment
1. Visit your Render URL
2. Login with `superadmin` / `admin123`
3. **Change default passwords immediately!**
4. Configure organization settings
5. Add real users

---

## 🔐 Security Checklist

- [ ] Change all default passwords
- [ ] Update `SESSION_SECRET` in production
- [ ] Enable SSL/HTTPS
- [ ] Configure CORS properly
- [ ] Set up database backups
- [ ] Enable application logging
- [ ] Configure rate limiting
- [ ] Review user permissions

---

## 📊 System Requirements

### Development
- Python 3.11+
- PostgreSQL 12+
- 2GB RAM minimum
- 1GB disk space

### Production (Render)
- Web Service (Python 3.11)
- PostgreSQL database
- Environment variables configured
- Build command: `./build.sh`
- Start command: `gunicorn app:app`

---

## 🆘 Getting Help

### Check Logs
```bash
# Application logs
tail -f logs/app.log

# Database logs
flask db current
flask db history
```

### Run Diagnostics
```bash
python final_verification.py
```

### Common Solutions
1. **Database issues** → Run `flask db upgrade`
2. **Login issues** → Run `python reset_default_passwords.py`
3. **Import errors** → Check Python path and dependencies
4. **Migration issues** → Check `flask db current` and `flask db history`

---

## ✅ Verification Checklist

Before going to production, verify:

- [ ] All tests pass: `python final_verification.py`
- [ ] Database tables created: `python check_tables.py`
- [ ] Default users exist: `python test_initialization.py`
- [ ] Login works with default credentials
- [ ] Migrations are up to date: `flask db current`
- [ ] Environment variables are set correctly
- [ ] Application starts without errors
- [ ] No circular import errors

---

## 🎉 Success!

Your Flask HRMS application is now:
- ✅ Fully operational
- ✅ Database initialized
- ✅ Default users created
- ✅ Ready for development
- ✅ Ready for production deployment

**Happy coding! 🚀**

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** Production Ready