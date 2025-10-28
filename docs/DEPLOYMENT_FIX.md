# Fixing the "column hrm_users.role does not exist" Error on Render

## Problem Summary

Your Render deployment is failing with this error:
```
psycopg2.errors.UndefinedColumn: column hrm_users.role does not exist
```

This happens because your production database has an **old schema** with a `role` column (string), but your current code expects `role_id` (foreign key) and uses a relationship to the `Role` table.

## Root Cause

The production database on Render was created with an older version of your User model that had:
- A `role` column (String field)

But your current model has:
- A `role_id` column (Foreign Key to Role table)
- A `role` relationship (not a column)

## Solution Options

### Option 1: Automated Fix (Recommended)

I've created a migration and build script that will automatically fix this on deployment.

**Steps:**
1. Commit the new files:
   - `migrations/versions/remove_role_column_from_users.py` (migration to remove old column)
   - `build.sh` (build script that runs migrations)
   - Updated `render.yaml` (uses the build script)

2. Push to your Git repository:
   ```bash
   git add .
   git commit -m "Fix: Remove old role column from hrm_users table"
   git push
   ```

3. Render will automatically:
   - Run the build script
   - Execute the migration
   - Remove the old `role` column
   - Start your application

### Option 2: Manual Fix via Render Shell

If you need to fix it immediately without redeploying:

1. Go to your Render dashboard
2. Open the Shell for your web service
3. Run the fix script:
   ```bash
   python fix_production_schema.py
   ```

4. Restart your service

### Option 3: Direct Database Fix

If you have direct access to your PostgreSQL database:

1. Connect to your Render PostgreSQL database
2. Run this SQL command:
   ```sql
   ALTER TABLE hrm_users DROP COLUMN IF EXISTS role;
   ```

3. Restart your Render web service

## Verification

After applying any of the above fixes, verify that:

1. Your application starts without errors
2. You can log in successfully
3. User roles are working correctly (they should use `role_id` and the `role` relationship)

## What Changed

### Old Schema (Production)
```python
class User(db.Model):
    # ...
    role = db.Column(db.String(50))  # Old: direct string column
```

### New Schema (Current Code)
```python
class User(db.Model):
    # ...
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))  # New: foreign key
    role = db.relationship('Role', back_populates='users')      # New: relationship
```

## Files Created

1. **migrations/versions/remove_role_column_from_users.py**
   - Migration that safely removes the old `role` column
   - Checks if column exists before attempting to drop it

2. **build.sh**
   - Build script for Render
   - Installs dependencies and runs migrations automatically

3. **fix_production_schema.py**
   - Manual script to fix the schema
   - Can be run directly on Render shell

4. **DEPLOYMENT_FIX.md** (this file)
   - Documentation of the issue and solutions

## Prevention

To prevent this issue in the future:

1. Always run migrations on production after schema changes
2. Use the build script approach (Option 1) for automatic migration execution
3. Test migrations locally before deploying
4. Keep your local and production schemas in sync

## Need Help?

If you encounter any issues:
1. Check the Render logs for detailed error messages
2. Verify that all migrations have been applied: `flask db current`
3. Check the database schema: Run `fix_production_schema.py` to see current columns
4. Ensure your DATABASE_URL environment variable is correctly set

## Next Steps

Choose one of the solution options above and apply it. **Option 1 (Automated Fix)** is recommended as it will prevent similar issues in the future by automatically running migrations on every deployment.