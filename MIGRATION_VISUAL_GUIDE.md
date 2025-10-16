# Role Table Migration - Visual Guide

## 🎯 Migration Goal

```
FROM: role table
TO:   hrm_roles table
WHY:  Consistent naming convention (hrm_* prefix)
```

## 📊 Current vs Target State

### BEFORE Migration
```
┌─────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │     role     │                                       │
│  ├──────────────┤                                       │
│  │ id (PK)      │◄──────────┐                          │
│  │ name         │            │                          │
│  │ description  │            │                          │
│  │ is_active    │            │                          │
│  │ created_at   │            │                          │
│  │ updated_at   │            │                          │
│  └──────────────┘            │                          │
│                               │                          │
│                               │ FK: role_id              │
│                               │                          │
│  ┌──────────────┐            │                          │
│  │  hrm_users   │            │                          │
│  ├──────────────┤            │                          │
│  │ id (PK)      │            │                          │
│  │ username     │            │                          │
│  │ email        │            │                          │
│  │ role_id      │────────────┘                          │
│  │ ...          │                                       │
│  └──────────────┘                                       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### AFTER Migration
```
┌─────────────────────────────────────────────────────────┐
│                    DATABASE SCHEMA                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐                                       │
│  │  hrm_roles   │  ✅ NEW TABLE                        │
│  ├──────────────┤                                       │
│  │ id (PK)      │◄──────────┐                          │
│  │ name         │            │                          │
│  │ description  │            │                          │
│  │ is_active    │            │                          │
│  │ created_at   │            │                          │
│  │ updated_at   │            │                          │
│  └──────────────┘            │                          │
│                               │                          │
│                               │ FK: role_id              │
│                               │ ✅ UPDATED               │
│  ┌──────────────┐            │                          │
│  │  hrm_users   │            │                          │
│  ├──────────────┤            │                          │
│  │ id (PK)      │            │                          │
│  │ username     │            │                          │
│  │ email        │            │                          │
│  │ role_id      │────────────┘                          │
│  │ ...          │                                       │
│  └──────────────┘                                       │
│                                                          │
│  ❌ role table DROPPED                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🔄 Migration Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    MIGRATION PROCESS                         │
└─────────────────────────────────────────────────────────────┘

1️⃣  BACKUP DATABASE
    ├─ Create full backup
    ├─ Verify backup file
    └─ Store safely
    
2️⃣  STOP APPLICATION
    ├─ Stop Flask app
    └─ Ensure no active connections
    
3️⃣  CREATE NEW TABLE
    ├─ CREATE TABLE hrm_roles
    ├─ Same structure as role
    └─ Add indexes
    
4️⃣  MIGRATE DATA
    ├─ INSERT INTO hrm_roles
    ├─ SELECT FROM role
    ├─ Preserve all IDs
    └─ Update sequence
    
5️⃣  UPDATE FOREIGN KEYS
    ├─ DROP old FK constraint
    ├─ CREATE new FK constraint
    └─ Point to hrm_roles
    
6️⃣  DROP OLD TABLE
    ├─ DROP TABLE role
    └─ CASCADE constraints
    
7️⃣  VERIFY MIGRATION
    ├─ Check table exists
    ├─ Verify data count
    ├─ Test FK constraints
    └─ Validate user roles
    
8️⃣  START APPLICATION
    ├─ Start Flask app
    ├─ Test login
    └─ Verify functionality
    
✅  MIGRATION COMPLETE
```

## 📁 Files Created

```
D:/Projects/HRMS/hrm/
│
├── 📝 models.py (MODIFIED)
│   ├─ Role.__tablename__ = 'hrm_roles'
│   └─ User.role_id FK → 'hrm_roles.id'
│
├── 🔧 Migration Scripts
│   ├── migrate_roles_table.py ⭐ RECOMMENDED
│   │   └─ Interactive, safe, verified
│   │
│   ├── migrations/versions/
│   │   ├── 005_migrate_role_to_hrm_roles.py
│   │   │   └─ Alembic migration
│   │   └── 005_migrate_role_to_hrm_roles.sql
│   │       └─ Raw SQL script
│   │
│   └── verify_role_migration.py
│       └─ Verification & status check
│
├── 📚 Documentation
│   ├── ROLE_MIGRATION_README.md
│   │   └─ Detailed guide
│   │
│   ├── MIGRATION_SUMMARY.md
│   │   └─ Quick overview
│   │
│   ├── MIGRATION_CHECKLIST.md
│   │   └─ Step-by-step checklist
│   │
│   └── MIGRATION_VISUAL_GUIDE.md (this file)
│       └─ Visual reference
│
└── 🛠️ Helper Scripts
    ├── install_migration_deps.py
    │   └─ Install dependencies
    └── check_roles.py
        └─ Quick role check
```

## 🚀 Quick Start (3 Steps)

```
┌────────────────────────────────────────────────────────┐
│  STEP 1: BACKUP                                        │
├────────────────────────────────────────────────────────┤
│  $ pg_dump -U user -d db > backup.sql                 │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│  STEP 2: MIGRATE                                       │
├────────────────────────────────────────────────────────┤
│  $ python migrate_roles_table.py                      │
│                                                        │
│  Follow prompts:                                       │
│  ✓ Confirm backup                                     │
│  ✓ Review plan                                        │
│  ✓ Confirm proceed                                    │
└────────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────────┐
│  STEP 3: VERIFY                                        │
├────────────────────────────────────────────────────────┤
│  $ python verify_role_migration.py                    │
│                                                        │
│  Check:                                                │
│  ✓ hrm_roles exists                                   │
│  ✓ role dropped                                       │
│  ✓ Data migrated                                      │
│  ✓ FK updated                                         │
└────────────────────────────────────────────────────────┘
```

## 📊 Data Flow

```
┌─────────────┐
│    role     │  Original table with data
│  (10 rows)  │
└──────┬──────┘
       │
       │ COPY ALL DATA
       │ (preserve IDs)
       ↓
┌─────────────┐
│ hrm_roles   │  New table with same data
│  (10 rows)  │
└──────┬──────┘
       │
       │ UPDATE FK
       │ (hrm_users.role_id)
       ↓
┌─────────────┐
│  hrm_users  │  Users now reference hrm_roles
│ role_id FK  │  (no data change in users)
└─────────────┘
```

## ⚠️ Important Notes

### Data Preservation
```
✅ All role IDs are preserved
✅ All role names are preserved
✅ All descriptions are preserved
✅ All timestamps are preserved
✅ All active/inactive status preserved
✅ All user-role relationships preserved
```

### What Changes
```
❌ Table name: role → hrm_roles
❌ Foreign key reference updated
❌ Old table dropped
```

### What Doesn't Change
```
✅ Role IDs (same numbers)
✅ User role assignments
✅ Application functionality
✅ User experience
```

## 🔍 Verification Points

```
┌─────────────────────────────────────────────────────┐
│  VERIFICATION CHECKLIST                             │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ✓ Table Structure                                 │
│    └─ hrm_roles exists                             │
│    └─ role does not exist                          │
│                                                     │
│  ✓ Data Integrity                                  │
│    └─ Row count matches                            │
│    └─ All IDs present                              │
│    └─ No data loss                                 │
│                                                     │
│  ✓ Relationships                                   │
│    └─ FK points to hrm_roles                       │
│    └─ Users have roles                             │
│    └─ No orphaned records                          │
│                                                     │
│  ✓ Functionality                                   │
│    └─ Login works                                  │
│    └─ Roles display                                │
│    └─ Access control works                         │
│    └─ Role management works                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 🎯 Success Indicators

```
✅ Migration Successful When:

┌─────────────────────────────────────────┐
│  DATABASE                               │
├─────────────────────────────────────────┤
│  ✓ hrm_roles table exists              │
│  ✓ role table dropped                  │
│  ✓ Data count matches                  │
│  ✓ FK constraint correct               │
│  ✓ Indexes created                     │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  APPLICATION                            │
├─────────────────────────────────────────┤
│  ✓ Starts without errors               │
│  ✓ No warnings in logs                 │
│  ✓ Login works                         │
│  ✓ Roles display correctly             │
│  ✓ Access control works                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  USERS                                  │
├─────────────────────────────────────────┤
│  ✓ Can log in                          │
│  ✓ See correct roles                   │
│  ✓ Access appropriate pages            │
│  ✓ No functionality loss               │
└─────────────────────────────────────────┘
```

## 🔄 Rollback Plan

```
IF SOMETHING GOES WRONG:

Option 1: Restore Backup
┌────────────────────────────────────────┐
│ $ psql -U user -d db < backup.sql     │
└────────────────────────────────────────┘

Option 2: Alembic Downgrade
┌────────────────────────────────────────┐
│ $ flask db downgrade                  │
└────────────────────────────────────────┘

Then: Revert code changes in models.py
```

## 📞 Support

```
Need Help?

1. Check error messages
2. Run: python verify_role_migration.py
3. Review: ROLE_MIGRATION_README.md
4. Check PostgreSQL logs
5. Verify backup is valid
```

## ⏱️ Timeline

```
┌─────────────────────────────────────────┐
│  ESTIMATED TIME                         │
├─────────────────────────────────────────┤
│  Backup:        2-3 minutes            │
│  Migration:     1-2 minutes            │
│  Verification:  2-3 minutes            │
│  Testing:       3-5 minutes            │
│  ─────────────────────────────          │
│  TOTAL:         8-13 minutes           │
└─────────────────────────────────────────┘
```

---

## 🎉 Ready to Migrate?

```
1. Read this guide ✓
2. Have backup plan ✓
3. Understand changes ✓
4. Know rollback steps ✓

👉 Run: python migrate_roles_table.py
```

---

**Version**: 1.0  
**Created**: 2024-01-15  
**Migration ID**: 005_migrate_role_to_hrm_roles