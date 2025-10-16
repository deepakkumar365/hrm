# Role Table Migration Summary

## Overview
Successfully prepared migration from `role` table to `hrm_roles` table to maintain consistent naming convention across the HRMS system.

## Changes Made

### 1. Code Changes

#### `models.py`
- ✅ Changed `Role` model's `__tablename__` from `'role'` to `'hrm_roles'`
- ✅ Updated `User` model's foreign key from `'role.id'` to `'hrm_roles.id'`

### 2. Migration Scripts Created

| File | Purpose | Usage |
|------|---------|-------|
| `migrate_roles_table.py` | **Standalone migration script** | `python migrate_roles_table.py` |
| `migrations/versions/005_migrate_role_to_hrm_roles.py` | **Alembic migration** | `flask db upgrade` |
| `migrations/versions/005_migrate_role_to_hrm_roles.sql` | **Raw SQL script** | Direct SQL execution |
| `verify_role_migration.py` | **Verification script** | `python verify_role_migration.py` |
| `ROLE_MIGRATION_README.md` | **Detailed documentation** | Reference guide |

## Quick Start Guide

### Step 1: Backup Database (CRITICAL!)
```bash
pg_dump -U your_username -d your_database > backup_before_migration.sql
```

### Step 2: Stop Application
Stop your Flask application to prevent data inconsistencies.

### Step 3: Run Migration (Choose ONE method)

#### Method A: Standalone Script (Recommended)
```bash
python migrate_roles_table.py
```
- Interactive prompts
- Built-in verification
- Safety checks
- Detailed progress output

#### Method B: Alembic
```bash
flask db upgrade
```
- Automated migration
- Version control
- Easy rollback

#### Method C: Direct SQL
```bash
psql -U username -d database < migrations/versions/005_migrate_role_to_hrm_roles.sql
```
- Direct database access
- For DBAs

### Step 4: Verify Migration
```bash
python verify_role_migration.py
```

### Step 5: Start Application
```bash
python app.py
```

## What the Migration Does

1. **Creates** `hrm_roles` table with same structure as `role`
2. **Copies** all data from `role` to `hrm_roles` (preserves IDs)
3. **Updates** foreign key constraint in `hrm_users` table
4. **Creates** indexes for performance
5. **Drops** old `role` table
6. **Verifies** data integrity

## Migration Safety Features

✅ **Data Preservation**: All role IDs are preserved  
✅ **Foreign Key Integrity**: User-role relationships maintained  
✅ **Rollback Support**: Can revert if needed  
✅ **Verification**: Built-in checks for data consistency  
✅ **Interactive Prompts**: Confirms before destructive operations  

## Expected Results

### Before Migration
```
Tables: role, hrm_users, hrm_employee, ...
Foreign Key: hrm_users.role_id → role.id
```

### After Migration
```
Tables: hrm_roles, hrm_users, hrm_employee, ...
Foreign Key: hrm_users.role_id → hrm_roles.id
```

## Verification Checklist

After migration, verify:

- [ ] `hrm_roles` table exists
- [ ] Old `role` table is dropped
- [ ] All roles are present in `hrm_roles`
- [ ] Role IDs match original IDs
- [ ] Users still have correct role assignments
- [ ] Foreign key points to `hrm_roles`
- [ ] Application starts without errors
- [ ] Login works correctly
- [ ] Role-based access control works
- [ ] Can view/edit roles in admin panel

## Rollback Instructions

If something goes wrong:

### Using Alembic:
```bash
flask db downgrade
```

### Manual Rollback:
```bash
# Restore database
psql -U username -d database < backup_before_migration.sql

# Revert code changes in models.py
# Change __tablename__ = 'hrm_roles' back to 'role'
# Change ForeignKey('hrm_roles.id') back to ForeignKey('role.id')
```

## Testing After Migration

1. **Login Test**: Verify users can log in
2. **Role Display**: Check user roles display correctly
3. **Access Control**: Test role-based permissions
4. **Role Management**: Create/edit/delete roles
5. **User Assignment**: Assign roles to users

## Common Issues & Solutions

### Issue: "Table already exists"
**Solution**: Migration already run. Verify with `verify_role_migration.py`

### Issue: "Foreign key constraint error"
**Solution**: Constraint may already exist. Check with verification script.

### Issue: "Data count mismatch"
**Solution**: Check for conflicts. Review migration logs.

## Files Reference

### Migration Files
- `migrate_roles_table.py` - Main migration script
- `migrations/versions/005_migrate_role_to_hrm_roles.py` - Alembic version
- `migrations/versions/005_migrate_role_to_hrm_roles.sql` - SQL version

### Documentation
- `ROLE_MIGRATION_README.md` - Detailed guide
- `MIGRATION_SUMMARY.md` - This file

### Verification
- `verify_role_migration.py` - Status checker
- `check_roles.py` - Simple role checker

## Support

If you encounter issues:
1. Check error messages in migration output
2. Run verification script: `python verify_role_migration.py`
3. Review PostgreSQL logs
4. Check database backup is valid
5. Refer to `ROLE_MIGRATION_README.md` for detailed troubleshooting

## Timeline

- **Preparation**: 5 minutes (backup, stop app)
- **Migration**: 1-2 minutes (actual migration)
- **Verification**: 2-3 minutes (testing)
- **Total**: ~10 minutes

## Success Criteria

✅ Migration is successful when:
1. `hrm_roles` table exists with all data
2. Old `role` table is dropped
3. Foreign keys are correctly configured
4. All users have their roles intact
5. Application runs without errors
6. Role-based features work correctly

---

**Status**: Ready to migrate  
**Risk Level**: Low (with backup)  
**Reversible**: Yes (with backup or Alembic downgrade)  
**Estimated Downtime**: 5-10 minutes  

**Next Steps**:
1. Create database backup
2. Stop application
3. Run `python migrate_roles_table.py`
4. Verify with `python verify_role_migration.py`
5. Start application and test

---

**Created**: 2024-01-15  
**Version**: 1.0  
**Migration ID**: 005_migrate_role_to_hrm_roles