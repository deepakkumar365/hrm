# 🚀 Environment Switch - Quick Reference Card

## 📋 Current Configuration

```
✅ Development Database: Configured
✅ Production Database: Configured  
✅ Environment Switch: Active
✅ Default Mode: Development
```

---

## ⚡ Quick Commands

### Check Current Environment
```bash
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('Current:', os.getenv('ENVIRONMENT'))"
```

### Switch to Development
```bash
# Edit .env file, change:
ENVIRONMENT=development
```

### Switch to Production
```bash
# Edit .env file, change:
ENVIRONMENT=production
```

### Verify Active Database
```bash
python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'][:60])"
```

---

## 🎯 One-Line Environment Switch

### PowerShell (Windows)
```powershell
# Switch to Development
(Get-Content .env) -replace 'ENVIRONMENT=production', 'ENVIRONMENT=development' | Set-Content .env

# Switch to Production
(Get-Content .env) -replace 'ENVIRONMENT=development', 'ENVIRONMENT=production' | Set-Content .env
```

### Bash (Linux/Mac)
```bash
# Switch to Development
sed -i 's/ENVIRONMENT=production/ENVIRONMENT=development/' .env

# Switch to Production
sed -i 's/ENVIRONMENT=development/ENVIRONMENT=production/' .env
```

---

## 📊 Environment Comparison

| Feature | Development | Production |
|---------|-------------|------------|
| **Database** | `DEV_DATABASE_URL` | `PROD_DATABASE_URL` |
| **Host** | dpg-d2kq4015pdvs739uk9h0-a | dpg-d3ii4fruibrs73cukdtg-a |
| **Database Name** | pgnoltrion | noltrion_hrm |
| **SSL Mode** | Not specified | Required (`?sslmode=require`) |
| **Purpose** | Testing & Development | Live Production Data |

---

## 🔐 Security Reminder

⚠️ **NEVER:**
- Commit `.env` to Git
- Share production credentials
- Use production DB for testing
- Mix development and production data

✅ **ALWAYS:**
- Keep `.env` in `.gitignore`
- Use separate databases for dev/prod
- Test in development first
- Backup before production changes

---

## 🧪 Testing Checklist

Before switching to production:

- [ ] Backup production database
- [ ] Test all features in development
- [ ] Run database migrations in development
- [ ] Verify no breaking changes
- [ ] Check application logs
- [ ] Test user authentication
- [ ] Test payroll calculations
- [ ] Verify file uploads work
- [ ] Test all critical workflows

---

## 🚨 Emergency Rollback

If production fails:

```bash
# 1. Immediately switch back to development
# Edit .env:
ENVIRONMENT=development

# 2. Restart application
# Stop current process (Ctrl+C)
python app.py

# 3. Check logs
tail -f logs/app.log
```

---

## 📞 Quick Support

**Issue:** Wrong database connected  
**Fix:** Check `ENVIRONMENT` variable in `.env`

**Issue:** Connection refused  
**Fix:** Verify database URL and credentials

**Issue:** Changes not applied  
**Fix:** Restart application after `.env` changes

---

## 🎯 Current Setup Summary

```
📁 .env File Structure:
├── 🌱 Development Settings (DEV_DATABASE_URL)
├── 🚀 Production Settings (PROD_DATABASE_URL)
├── 🔧 Other Configuration (SESSION_SECRET, etc.)
└── ⚙️ Environment Switch (ENVIRONMENT)

🔄 How It Works:
1. Application reads ENVIRONMENT variable
2. If "production" → uses PROD_DATABASE_URL
3. If "development" → uses DEV_DATABASE_URL
4. Logs current mode on startup

✅ Status: Ready to use!
```

---

**For detailed documentation, see:** `ENVIRONMENT_SETUP.md`