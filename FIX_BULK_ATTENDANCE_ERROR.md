# Fix: Missing hrm_user_company_access Table Error

## Problem
When clicking "Bulk Attendance" menu as an HR role user, you get the error:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) 
relation "hrm_user_company_access" does not exist
```

## Root Cause
The table `hrm_user_company_access` is defined in your data models but hasn't been created in the database. This is a database schema synchronization issue.

## Solution

### Option 1: Automatic Fix (Recommended)
Run this script to automatically create the table and populate it with data:

```bash
python fix_user_company_access.py
```

This script will:
1. ✓ Create the `hrm_user_company_access` table
2. ✓ Create necessary indexes
3. ✓ Populate initial user-company relationships
4. ✓ Mark the migration as applied
5. ✓ Verify the fix was successful

### Option 2: Using Flask-Migrate
If you prefer to use Flask migrations:

```bash
flask db upgrade
```

This will apply any pending migrations, including the `add_user_company_access` migration.

### Option 3: Direct SQL
If neither automatic option works, execute these SQL commands directly in your PostgreSQL database:

```sql
-- Create the junction table
CREATE TABLE IF NOT EXISTS hrm_user_company_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL,
    company_id UUID NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    modified_at TIMESTAMP,
    
    CONSTRAINT fk_user_company_access_user 
        FOREIGN KEY (user_id) REFERENCES hrm_users(id) ON DELETE CASCADE,
    CONSTRAINT fk_user_company_access_company 
        FOREIGN KEY (company_id) REFERENCES hrm_company(id) ON DELETE CASCADE,
    CONSTRAINT uq_user_company_access 
        UNIQUE (user_id, company_id)
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS ix_user_company_access_user_id 
ON hrm_user_company_access(user_id);

CREATE INDEX IF NOT EXISTS ix_user_company_access_company_id 
ON hrm_user_company_access(company_id);

-- Record the migration as applied (optional but recommended)
INSERT INTO alembic_version (version_num) VALUES ('add_user_company_access')
ON CONFLICT DO NOTHING;
```

## What This Table Does
- **Purpose**: Manages multi-company access for users
- **Junction Table**: Links users to companies they can access
- **Used By**: HR roles to determine which companies' data they can view/manage
- **Related Feature**: Bulk Attendance, which filters data by company

## After the Fix
Once the table is created:
1. ✓ The "Bulk Attendance" menu will work without errors
2. ✓ Users can be assigned to access multiple companies
3. ✓ HR Managers will only see data for companies they have access to

## Verification
To verify the fix was successful:

```bash
python -c "
from app import app, db
from sqlalchemy import text, inspect
ctx = app.app_context()
ctx.push()
inspector = inspect(db.engine)
if 'hrm_user_company_access' in inspector.get_table_names():
    count = db.session.execute(text('SELECT COUNT(*) FROM hrm_user_company_access')).scalar()
    print(f'✓ Table exists with {count} records')
else:
    print('✗ Table does not exist')
"
```

## Related Migrations
- Migration file: `migrations/versions/add_user_company_access.py`
- Model definition: `models.py` (class UserCompanyAccess)
- Routes that use this: `routes_hr_manager.py` and others

## Need More Help?
If this doesn't resolve the issue, check:
1. Database connection string is correct
2. PostgreSQL service is running
3. All required tables exist (`hrm_users`, `hrm_company`)
4. User has proper permissions to create tables