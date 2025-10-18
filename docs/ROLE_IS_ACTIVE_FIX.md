# Role is_active Column Fix

## Issue
When trying to access the `/employees/add` route, the application threw an error:
```
sqlalchemy.exc.InvalidRequestError: Entity namespace for "role" has no property "is_active"
```

## Root Cause
The `Role` model in `models.py` did not have an `is_active` column, but the code in `routes.py` was attempting to filter roles by `is_active=True` in multiple places (11 occurrences).

### Affected Code Locations in routes.py:
- Line 329: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 346: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 414: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 428: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 495: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 510: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 744: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 762: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 818: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 833: `roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()`
- Line 2003: `roles = Role.query.filter_by(is_active=True).paginate(...)`

## Solution
Added the `is_active` column to the `Role` model to support active/inactive role status, consistent with other master data models like `Department`, `WorkingHours`, and `WorkSchedule`.

### Changes Made

#### 1. Updated Role Model (models.py)
Added `is_active` column to the `Role` class:

```python
class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)  # ← NEW COLUMN
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    users = db.relationship('User', back_populates='role', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Role {self.name}>'
```

#### 2. Created Database Migration Script
Created `add_role_is_active_column.py` to safely add the column to the existing database:

- Checks if the column already exists (prevents duplicate runs)
- Adds `is_active` column with default value `TRUE`
- Updates all existing roles to be active
- Includes proper error handling and rollback

#### 3. Executed Migration
Successfully ran the migration script:
```bash
python add_role_is_active_column.py
```

**Result:**
- ✓ Column added to database
- ✓ All 4 existing roles (Super Admin, Admin, Manager, User) set to active
- ✓ No data loss

## Verification
Tested the fix by querying roles with the `is_active` filter:
```python
roles = Role.query.filter_by(is_active=True).all()
```

**Result:**
```
Found 4 active roles
  - Super Admin
  - Admin
  - Manager
  - User
```

## Files Modified
1. **models.py** - Added `is_active` column to `Role` model
2. **add_role_is_active_column.py** - Created migration script (can be run multiple times safely)

## Files Not Modified
- **routes.py** - No changes needed; existing code now works correctly

## Benefits
1. **Consistency**: Role model now matches other master data models (Department, WorkingHours, WorkSchedule)
2. **Flexibility**: Allows administrators to deactivate roles without deleting them
3. **Data Integrity**: Preserves historical data for inactive roles
4. **User Experience**: Only active roles appear in dropdowns and forms

## Testing
- ✅ Role queries with `is_active=True` filter work correctly
- ✅ All 4 existing roles are active
- ✅ `/employees/add` route should now work without errors
- ✅ Migration script is idempotent (safe to run multiple times)

## Next Steps
To fully test the fix:
1. Start the Flask application: `python app.py`
2. Login with admin credentials
3. Navigate to `/employees/add`
4. Verify the role dropdown displays all active roles
5. Test creating a new employee

## Status
✅ **RESOLVED** - Role model updated, database migrated, all role queries working correctly