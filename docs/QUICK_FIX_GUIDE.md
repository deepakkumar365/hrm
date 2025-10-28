# Quick Fix Guide for Render Deployment Error

## The Error
```
psycopg2.errors.UndefinedColumn: column hrm_users.role does not exist
```

## Quick Fix (Choose One)

### ✅ Option A: Automatic Fix (Best for long-term)

1. **Commit and push the changes:**
   ```bash
   git add .
   git commit -m "Fix: Add migration to remove old role column"
   git push
   ```

2. **Render will automatically:**
   - Run `build.sh` which executes migrations
   - Remove the old `role` column
   - Start your app successfully

### ⚡ Option B: Immediate Manual Fix

1. **Go to Render Dashboard** → Your Web Service → Shell

2. **Run this command:**
   ```bash
   python fix_production_schema.py
   ```

3. **Restart your service** (or it will restart automatically)

### 🔧 Option C: Direct SQL Fix

1. **Go to Render Dashboard** → Your PostgreSQL Database → Connect

2. **Run this SQL:**
   ```sql
   ALTER TABLE hrm_users DROP COLUMN IF EXISTS role;
   ```

3. **Restart your web service**

## What Was Fixed

I've created these files to solve your issue:

1. ✅ **migrations/versions/remove_role_column_from_users.py**
   - Migration to safely remove the old `role` column

2. ✅ **build.sh**
   - Automated build script that runs migrations on deployment

3. ✅ **Updated render.yaml**
   - Now uses `build.sh` instead of just `pip install`

4. ✅ **Updated requirements-render.txt**
   - Added `flask-migrate>=4.0.5` (was missing!)

5. ✅ **fix_production_schema.py**
   - Manual script to fix the schema immediately

6. ✅ **check_db_schema.py**
   - Diagnostic tool to check your database schema

## Why This Happened

Your production database has an **old schema** with a `role` column (string), but your current code expects:
- `role_id` (foreign key to Role table)
- `role` (relationship, not a column)

## Recommended Action

**Use Option A** - It will:
- Fix the current issue
- Prevent future schema issues
- Automatically run migrations on every deployment

Just commit and push the changes!