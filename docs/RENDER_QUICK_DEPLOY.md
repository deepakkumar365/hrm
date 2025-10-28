# ⚡ Render Quick Deploy Reference

## 🚀 Deploy to Production (3 Steps)

### **Step 1: Commit & Push**
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

### **Step 2: Render Auto-Deploys**
✅ Automatically runs migrations via `build.sh`  
✅ Creates all database tables  
✅ Starts application in production mode

### **Step 3: Verify**
Check logs for:
```
✅ Build completed successfully!
🌍 Running in PRODUCTION mode
```

---

## 🗄️ Database Migrations

### **Automatic (Default)**
Migrations run automatically during deployment.

### **Manual (If Needed)**
```bash
# Via Render Shell
flask db upgrade
```

---

## 🔍 Quick Troubleshooting

| Error | Solution |
|-------|----------|
| "relation does not exist" | Run `flask db upgrade` in Render Shell |
| "PROD_DATABASE_URL not set" | Check Render environment variables |
| "Multiple heads detected" | Run `flask db merge heads` locally, then push |
| Build fails | Check Render build logs for errors |

---

## 📊 Environment Variables (Render)

Set in `render.yaml`:
- ✅ `ENVIRONMENT=production`
- ✅ `PROD_SESSION_SECRET` (auto-generated)
- ✅ `PROD_DATABASE_URL` (your production DB)

---

## 🧪 Test Locally Before Deploy

```bash
# 1. Ensure development environment
ENVIRONMENT=development

# 2. Test migrations
flask db upgrade

# 3. Run application
python app.py

# 4. Verify no errors
```

---

## 🆘 Emergency Rollback

### **Rollback Code:**
Render Dashboard → Deploys → Previous Deploy → Redeploy

### **Rollback Database:**
```bash
flask db downgrade -1
```

---

## ✅ Deployment Checklist

- [ ] Migrations tested locally
- [ ] No migration conflicts
- [ ] `.env` not committed
- [ ] Code pushed to GitHub
- [ ] Render build successful
- [ ] Application accessible
- [ ] No errors in logs

---

## 📞 Quick Commands

```bash
# Check migration status
flask db current

# View migration history
flask db history

# Create new migration
flask db migrate -m "description"

# Apply migrations
flask db upgrade

# Rollback one migration
flask db downgrade -1
```

---

**🎯 One-Line Deploy:** `git add . && git commit -m "Deploy" && git push origin main`