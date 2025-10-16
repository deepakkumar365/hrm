# Role Table Migration Guide

## Overview
This guide explains how to migrate from the `role` table to the `hrm_roles` table in the HRMS system.

## What Changed?
- **Old table name**: `role`
- **New table name**: `hrm_roles`
- **Reason**: To follow the consistent naming convention with other HRM tables (hrm_users, hrm_employee, hrm_company, etc.)

## Files Modified

### 1. Model Changes (`models.py`)
- Changed `Role` model's `__tablename__` from `'role'` to `'hrm_roles'`
- Updated foreign key in `User` model from `'role.id'` to `'hrm_roles.id'`

### 2. Migration Scripts Created
Three migration options are provided:

#### Option A: Standalone Python Script (Recommended)
- **File**: `migrate_roles_table.py`
- **Usage**: Interactive script with safety checks
- **Best for**: Manual migration with verification

#### Option B: Alembic Migration
- **File**: `migrations/versions/005_migrate_role_to_hrm_roles.py`
- **Usage**: Standard Alembic migration
- **Best for**: Automated deployment pipelines

#### Option C: Raw SQL Script
- **File**: `migrations/versions/005_migrate_role_to_hrm_roles.sql`
- **Usage**: Direct SQL execution
- **Best for**: Database administrators

## Migration Steps

### Prerequisites
1. **Backup your database** (CRITICAL!)
   ```bash
   pg_dump -U your_username -d your_database > backup_before_role_migration.sql
   ```

2. **Stop the application** to prevent data inconsistencies

### Method 1: Using the Standalone Python Script (Recommended)

1. Navigate to the project directory:
   ```bash
   cd D:/Projects/HRMS/hrm
   ```

2. Run the migration script:
   ```bash
   python migrate_roles_table.py
   ```

3. Follow the interactive prompts:
   - Confirm you have a backup
   - Review the migration plan
   - Confirm to proceed

4. The script will:
   - Show current state of role table
   - Create hrm_roles table
   - Copy all data from role to hrm_roles
   - Update foreign key constraints
   - Drop the old role table
   - Verify the migration

### Method 2: Using Alembic

1. Update the `down_revision` in `005_migrate_role_to_hrm_roles.py` to match your latest migration

2. Run the migration:
   ```bash
   flask db upgrade
   ```

3. To rollback (if needed):
   ```bash
   flask db downgrade
   ```

### Method 3: Using Raw SQL

1. Connect to your PostgreSQL database:
   ```bash
   psql -U your_username -d your_database
   ```

2. Execute the SQL script:
   ```sql
   \i migrations/versions/005_migrate_role_to_hrm_roles.sql
   ```

## Verification

After migration, verify the changes:

1. **Check table exists**:
   ```sql
   SELECT table_name FROM information_schema.tables 
   WHERE table_name IN ('role', 'hrm_roles');
   ```
   Expected: Only `hrm_roles` should exist

2. **Check data migrated**:
   ```sql
   SELECT COUNT(*) FROM hrm_roles;
   SELECT * FROM hrm_roles ORDER BY id;
   ```

3. **Check foreign key constraint**:
   ```sql
   SELECT constraint_name, table_name, column_name 
   FROM information_schema.key_column_usage 
   WHERE table_name = 'hrm_users' AND column_name = 'role_id';
   ```

4. **Check users still have roles**:
   ```sql
   SELECT u.username, r.name as role_name 
   FROM hrm_users u 
   JOIN hrm_roles r ON u.role_id = r.id 
   LIMIT 10;
   ```

## What Happens During Migration

1. **Create hrm_roles table** with the same structure as role table
2. **Copy all data** from role to hrm_roles (preserves IDs, names, descriptions, etc.)
3. **Update sequence** to ensure new roles get correct IDs
4. **Drop old foreign key** constraint on hrm_users.role_id
5. **Create new foreign key** constraint pointing to hrm_roles
6. **Create indexes** for performance (name, is_active)
7. **Drop old role table**

## Rollback Plan

If something goes wrong:

### Using Alembic:
```bash
flask db downgrade
```

### Manual Rollback:
1. Restore from backup:
   ```bash
   psql -U your_username -d your_database < backup_before_role_migration.sql
   ```

2. Revert code changes in `models.py`:
   - Change `__tablename__ = 'hrm_roles'` back to `__tablename__ = 'role'`
   - Change foreign key from `'hrm_roles.id'` back to `'role.id'`

## Testing After Migration

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Test login** with existing users

3. **Check user roles** are displayed correctly

4. **Test role-based access control**:
   - Try accessing admin pages with admin user
   - Try accessing restricted pages with regular user

5. **Test role management**:
   - View roles list
   - Create new role
   - Edit existing role
   - Assign role to user

## Common Issues

### Issue 1: Foreign Key Constraint Error
**Error**: `foreign key constraint "hrm_users_role_id_fkey" already exists`

**Solution**: The constraint already points to hrm_roles. This is fine, skip the constraint creation step.

### Issue 2: Table Already Exists
**Error**: `relation "hrm_roles" already exists`

**Solution**: The migration was already run. Check if data is present in hrm_roles table.

### Issue 3: Data Mismatch
**Error**: Role counts don't match

**Solution**: 
1. Check for duplicate IDs
2. Verify ON CONFLICT clause worked correctly
3. Manually compare data between tables

## Support

If you encounter issues:
1. Check the error messages carefully
2. Verify your database backup is valid
3. Review the migration logs
4. Check PostgreSQL logs for detailed errors

## Post-Migration Cleanup

After successful migration and testing:
1. Keep the backup for at least 30 days
2. Monitor application logs for any role-related errors
3. Update any external documentation referencing the old table name
4. Update any custom SQL queries or reports that reference the role table

## Summary

✅ **Before Migration**:
- Database uses `role` table
- Foreign key: `hrm_users.role_id` → `role.id`

✅ **After Migration**:
- Database uses `hrm_roles` table
- Foreign key: `hrm_users.role_id` → `hrm_roles.id`
- All data preserved with same IDs
- Application code updated to use new table name

---

**Last Updated**: 2024-01-15
**Migration Version**: 005_migrate_role_to_hrm_roles