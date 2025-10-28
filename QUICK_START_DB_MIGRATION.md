# Quick Start: Database Migration Auto-Run

## TL;DR

✅ **Database tables now auto-create during app startup**

### For Developers
```bash
# Just run the app - migrations happen automatically
python main.py
# or
flask run

# Logs will show:
# ✅ Database tables exist - skipping migrations
# ✅ Default users created successfully!
```

### For DevOps/Deployment
```bash
# Set this in production environment
AUTO_MIGRATE_ON_STARTUP=true

# Deploy
docker build -t myapp .
docker run myapp
# Tables automatically created on first run
```

## Configuration

### Enable Auto-Migration (Recommended)
```bash
AUTO_MIGRATE_ON_STARTUP=true  # .env or environment variable
```

### Disable Auto-Migration (Manual Control)
```bash
AUTO_MIGRATE_ON_STARTUP=false
# Then run manually before starting app:
flask db upgrade
```

## What Happens?

### First Run (No Tables)
1. App starts
2. Detects tables don't exist
3. Runs `flask db upgrade` automatically
4. Creates all tables from migrations
5. Initializes default data
6. App is ready ✅

### Subsequent Runs (Tables Exist)
1. App starts
2. Detects tables exist
3. Skips migrations
4. Initializes default data
5. App is ready ✅

## Common Scenarios

### 🐳 Docker Deployment
```dockerfile
ENV AUTO_MIGRATE_ON_STARTUP=true
# Tables auto-create on container start
```

### 💻 Local Development
```bash
# In .env file (already set):
AUTO_MIGRATE_ON_STARTUP=true

# Just start the app:
flask run
# Migrations run automatically
```

### 🚀 Production Deployment
```bash
# Option 1: Auto-migrate on startup (simple)
AUTO_MIGRATE_ON_STARTUP=true

# Option 2: Manual migration (controlled)
AUTO_MIGRATE_ON_STARTUP=false
# Run before deployment:
flask db upgrade
```

## Manual Migration (if needed)

```bash
# Apply all pending migrations
flask db upgrade

# Rollback one migration
flask db downgrade

# Check current status
flask db current

# View history
flask db history
```

## Troubleshooting

### Tables won't create?
```bash
# 1. Check database connection
ping-db.py

# 2. Verify environment variable
echo $AUTO_MIGRATE_ON_STARTUP  # Should be "true"

# 3. Try manual migration
flask db upgrade

# 4. Check logs for errors
# Look for 🔴 error messages
```

### App starts but tables missing?
```bash
# Check if AUTO_MIGRATE_ON_STARTUP is set
# If not:
AUTO_MIGRATE_ON_STARTUP=true flask run

# Or add to .env:
AUTO_MIGRATE_ON_STARTUP=true
```

## Migration Files

Located in: `migrations/versions/`

- Python migrations: `*.py` files
- SQL migrations: `*.sql` files (legacy)

## When to Disable Auto-Migration

```bash
# Multi-instance production with load balancer
# (prevent concurrent migration race conditions)
AUTO_MIGRATE_ON_STARTUP=false
# Then migrate separately before deployment:
flask db upgrade
```

## Files Changed

- ✅ `routes.py` - Added migration checker
- ✅ `.env` - Added AUTO_MIGRATE_ON_STARTUP=true
- ✅ `.env.example` - Documented the variable
- ✅ `render.yaml` - Enabled for production
- ✅ `build.sh` - Added comments

## Log Messages

### ✅ Success
```
✅ Database tables exist - skipping migrations
✅ Default users created successfully!
✅ Default master data created successfully!
```

### 📦 Running Migrations
```
📦 Database tables not found. Running migrations...
✅ Migrations completed successfully!
```

### ⚠️ Warning
```
⚠️  Database tables not found.
   To auto-run migrations on startup, set: AUTO_MIGRATE_ON_STARTUP=true
```

## More Information

- Full guide: `docs/DATABASE_MIGRATION_AUTO_RUN.md`
- Implementation details: `IMPLEMENTATION_SUMMARY_DB_MIGRATION.md`
- Flask-Migrate docs: https://flask-migrate.readthedocs.io/

## Need Help?

1. Check the logs (look for 🔴, ⚠️, or 📦 messages)
2. Read `docs/DATABASE_MIGRATION_AUTO_RUN.md`
3. Try manual migration: `flask db upgrade`
4. Check database connectivity and permissions