# Automatic Database Migration on Startup

## Overview
The application now includes automatic database migration capability that runs during the build/deployment phase. This ensures that all required database tables are created without manual intervention.

## How It Works

### Table Existence Check
When the application starts, it automatically checks if required database tables exist:
- `hrm_users`
- `hrm_employees`
- `hrm_roles`

### Automatic Migration
If tables don't exist and `AUTO_MIGRATE_ON_STARTUP` is enabled:
1. The app detects missing tables during startup
2. Runs Flask-Migrate `upgrade` command automatically
3. All pending migrations are applied
4. Default data is initialized

### One-Time Execution
- Migrations only run once per application startup (tracked via `_migrations_applied` flag)
- Prevents duplicate migration attempts
- Safe for container restarts and deployments

## Configuration

### Enable Auto-Migration (Recommended for Deployment)
```bash
# In .env file
AUTO_MIGRATE_ON_STARTUP=true
```

### Disable Auto-Migration (Manual Control)
```bash
# In .env file
AUTO_MIGRATE_ON_STARTUP=false
```

When disabled, manually run:
```bash
flask db upgrade
```

## Use Cases

### ✅ Docker/Kubernetes Deployment
```dockerfile
# Dockerfile
ENV AUTO_MIGRATE_ON_STARTUP=true
# App will auto-migrate on container startup
```

### ✅ CI/CD Pipeline
```yaml
# .github/workflows/deploy.yml or similar
env:
  AUTO_MIGRATE_ON_STARTUP: "true"
# Migrations run automatically during deployment
```

### ✅ Development Environment
```bash
# .env for development
AUTO_MIGRATE_ON_STARTUP=true
# Developers get clean DB on app restart
```

### ❌ Production (Cautious Approach)
For production with high availability:
```bash
# Manually run migrations before deployment
flask db upgrade

# Then deploy with AUTO_MIGRATE_ON_STARTUP=false
# to prevent race conditions in multi-instance setups
```

## Related Environment Variables

### FLASK_SKIP_DB_INIT
- Default: `not set` (migrations run)
- Set to `1` to completely skip initialization and migrations
- Use when migrations are handled separately

```bash
# Skip all initialization
FLASK_SKIP_DB_INIT=1
```

## Behavior Matrix

| AUTO_MIGRATE | Tables Exist | Result |
|---|---|---|
| true | Yes | Skip migrations, run default data |
| true | No | Run migrations, run default data |
| false | Yes | Skip migrations, run default data |
| false | No | Error message, skip default data |

## Error Handling

If migrations fail:
1. Application startup will fail with error details
2. Check migration files in `migrations/versions/`
3. Fix the migration file
4. Restart the application

## Monitoring

Check the application logs for:

### ✅ Success Messages
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

### ⚠️ Warning Messages
```
⚠️  Database tables not found.
   To auto-run migrations on startup, set: AUTO_MIGRATE_ON_STARTUP=true
```

## Migration Files Location
All migration scripts are in: `migrations/versions/`

Python migrations (recommended): `*.py` files
SQL migrations (legacy): `*.sql` files

## Best Practices

1. **Always backup production database** before enabling auto-migration
2. **Test in staging environment** first with AUTO_MIGRATE_ON_STARTUP=true
3. **Use version control** for all migration files
4. **Review migration changes** before deploying to production
5. **Monitor logs** during first deployment with auto-migration enabled

## Troubleshooting

### Tables Won't Create
1. Check database connectivity
2. Verify DEV_DATABASE_URL or PROD_DATABASE_URL is correct
3. Check database user has CREATE TABLE permissions
4. Try manual migration: `flask db upgrade`

### Migrations Fail
1. Review error message in logs
2. Check migrations/versions/*.py for syntax errors
3. Try to create tables manually if needed
4. Contact DBA for production issues

### Duplicate Execution
1. Should not happen - tracked via _migrations_applied flag
2. If it does, restart the application
3. Check for concurrent deployment issues

## Related Commands

```bash
# Manual migration operations
flask db upgrade              # Apply migrations
flask db downgrade           # Rollback migrations
flask db current             # Show current version
flask db history             # Show migration history
flask db revision -m "description"  # Create new migration
flask db migrate -m "description"   # Auto-generate migration
```

## Deployment Checklist

- [ ] Backup production database
- [ ] Review pending migrations
- [ ] Set AUTO_MIGRATE_ON_STARTUP=true in deployment config
- [ ] Deploy application
- [ ] Monitor logs for success messages
- [ ] Verify all tables created correctly
- [ ] Test critical functionality
- [ ] Monitor performance after deployment