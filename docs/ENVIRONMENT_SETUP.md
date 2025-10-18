# 🌍 Environment Configuration Guide

## Overview

Your HRMS application now supports **dual-environment configuration** within a single `.env` file. You can easily switch between Development and Production environments by changing a single variable.

---

## 📁 `.env` File Structure

```env
# =========================
# 🌱 Development Settings
# =========================
DEV_DATABASE_URL=postgresql://noltrion_admin:xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y@dpg-d2kq4015pdvs739uk9h0-a.oregon-postgres.render.com/pgnoltrion

# =========================
# 🚀 Production Settings
# =========================
PROD_DATABASE_URL=postgresql://noltrion_admin:1UzH1rVxlnimPf1qvyLEnuEeOnrybn7f@dpg-d3ii4fruibrs73cukdtg-a.oregon-postgres.render.com:5432/noltrion_hrm?sslmode=require

# =========================
# 🔧 Other Configuration
# =========================
PGDATABASE=pgnoltrion
PGHOST=dpg-d2kq4015pdvs739uk9h0-a.oregon-postgres.render.com
PGPASSWORD=xa5ZvROhUAN6IkVHwB4jqacjV2r9gJ5y
PGPORT=5432
PGUSER=noltrion_admin
SESSION_SECRET="your-secret-key-here"

# =========================
# ⚙️ Environment Switch
# =========================
ENVIRONMENT=development
```

---

## 🔄 How to Switch Environments

### Switch to Development Mode
Edit `.env` file and set:
```env
ENVIRONMENT=development
```

The application will use: `DEV_DATABASE_URL`

### Switch to Production Mode
Edit `.env` file and set:
```env
ENVIRONMENT=production
```

The application will use: `PROD_DATABASE_URL`

---

## 🚀 Quick Start

### 1. For Local Development
```bash
# In .env file
ENVIRONMENT=development

# Start the application
python app.py
# or
flask run
```

**Output:**
```
🌍 Running in DEVELOPMENT mode
```

### 2. For Production Deployment
```bash
# In .env file
ENVIRONMENT=production

# Start the application
python app.py
# or
gunicorn app:app
```

**Output:**
```
🌍 Running in PRODUCTION mode
```

---

## 🔐 Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `DEV_DATABASE_URL` | Development database connection string | `postgresql://user:pass@localhost/dev_db` |
| `PROD_DATABASE_URL` | Production database connection string | `postgresql://user:pass@host/prod_db` |
| `ENVIRONMENT` | Controls which database to use | `development` or `production` |
| `SESSION_SECRET` | Flask session encryption key | Random secure string |
| `PGDATABASE` | PostgreSQL database name (optional) | `pgnoltrion` |
| `PGHOST` | PostgreSQL host (optional) | `dpg-xxx.oregon-postgres.render.com` |
| `PGPASSWORD` | PostgreSQL password (optional) | Your password |
| `PGPORT` | PostgreSQL port (optional) | `5432` |
| `PGUSER` | PostgreSQL username (optional) | `noltrion_admin` |

---

## 🛡️ Security Best Practices

### ✅ DO:
- ✅ Keep `.env` file in `.gitignore` (never commit to Git)
- ✅ Use strong, unique passwords for production
- ✅ Use SSL/TLS for production database connections (`?sslmode=require`)
- ✅ Rotate credentials regularly
- ✅ Use environment variables on production servers (not `.env` files)

### ❌ DON'T:
- ❌ Never commit `.env` to version control
- ❌ Never share production credentials in chat/email
- ❌ Never use development credentials in production
- ❌ Never hardcode credentials in source code

---

## 🧪 Testing Environment Configuration

### Test Development Mode
```bash
# Set environment
echo "ENVIRONMENT=development" >> .env

# Test connection
python -c "from app import app, db; app.app_context().push(); print('✅ Connected to:', app.config['SQLALCHEMY_DATABASE_URI'])"
```

### Test Production Mode
```bash
# Set environment
echo "ENVIRONMENT=production" >> .env

# Test connection
python -c "from app import app, db; app.app_context().push(); print('✅ Connected to:', app.config['SQLALCHEMY_DATABASE_URI'])"
```

---

## 🐛 Troubleshooting

### Issue: "DEV_DATABASE_URL is not set"
**Solution:** Ensure `.env` file contains `DEV_DATABASE_URL` variable

### Issue: "PROD_DATABASE_URL is not set"
**Solution:** Ensure `.env` file contains `PROD_DATABASE_URL` variable

### Issue: Application connects to wrong database
**Solution:** Check `ENVIRONMENT` variable in `.env` file

### Issue: Changes not taking effect
**Solution:** Restart the application after modifying `.env` file

---

## 📊 Database Connection Strings Format

### PostgreSQL Format:
```
postgresql://username:password@host:port/database?options
```

### Example with SSL:
```
postgresql://user:pass@host.com:5432/dbname?sslmode=require
```

### Local PostgreSQL:
```
postgresql://postgres:password@localhost:5432/hrm_dev
```

### SQLite (for testing):
```
sqlite:///hrm.db
```

---

## 🔧 Advanced Configuration

### Using Environment Variables (Production Recommended)

Instead of using `.env` file in production, set environment variables directly:

**Linux/Mac:**
```bash
export ENVIRONMENT=production
export PROD_DATABASE_URL="postgresql://..."
export SESSION_SECRET="..."
```

**Windows PowerShell:**
```powershell
$env:ENVIRONMENT="production"
$env:PROD_DATABASE_URL="postgresql://..."
$env:SESSION_SECRET="..."
```

**Docker:**
```yaml
environment:
  - ENVIRONMENT=production
  - PROD_DATABASE_URL=postgresql://...
  - SESSION_SECRET=...
```

**Render.com / Heroku:**
Set environment variables in the dashboard under "Environment Variables" section.

---

## 📝 Migration Between Environments

### Scenario: Migrate from Dev to Production

1. **Backup Development Database:**
   ```bash
   pg_dump -h localhost -U dev_user -d dev_db > backup.sql
   ```

2. **Switch to Production:**
   ```env
   ENVIRONMENT=production
   ```

3. **Run Migrations:**
   ```bash
   flask db upgrade
   ```

4. **Verify Connection:**
   ```bash
   python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
   ```

---

## 🎯 Deployment Checklist

Before deploying to production:

- [ ] Set `ENVIRONMENT=production` in `.env` or environment variables
- [ ] Verify `PROD_DATABASE_URL` is correct
- [ ] Test database connection
- [ ] Run database migrations (`flask db upgrade`)
- [ ] Verify SSL is enabled (`?sslmode=require`)
- [ ] Check application logs for "🌍 Running in PRODUCTION mode"
- [ ] Test critical features (login, payroll, etc.)
- [ ] Set up database backups
- [ ] Configure monitoring and alerts

---

## 📞 Support

If you encounter issues:

1. Check application logs for error messages
2. Verify `.env` file syntax (no extra spaces, quotes)
3. Test database connection manually using `psql` or database client
4. Ensure firewall allows database connections
5. Check database credentials are correct

---

## 🔄 Rollback Plan

If production deployment fails:

1. **Immediate Rollback:**
   ```env
   ENVIRONMENT=development
   ```

2. **Restart Application:**
   ```bash
   # Stop current process
   # Start with development settings
   python app.py
   ```

3. **Investigate Issues:**
   - Check logs
   - Verify database connectivity
   - Test migrations

---

## ✅ Summary

✅ **Single `.env` file** for both environments  
✅ **Easy switching** with `ENVIRONMENT` variable  
✅ **Secure** - credentials separated by environment  
✅ **Flexible** - supports local, staging, and production  
✅ **Safe** - automatic validation and error messages  

**Current Setup:**
- 🌱 Development: Uses `DEV_DATABASE_URL`
- 🚀 Production: Uses `PROD_DATABASE_URL`
- ⚙️ Switch: Change `ENVIRONMENT` variable

---

**Ready to deploy!** 🎉