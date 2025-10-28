# 🗄️ DATABASE SCHEMA FIX GUIDE

## Problem
```
sqlalchemy.exc.ProgrammingError: column hrm_employee.designation_id does not exist
```

**Root Cause:** The SQLAlchemy model expects a `designation_id` column, but your database doesn't have it yet. The migration file exists but hasn't been applied to your database.

---

## ✅ SOLUTION - Choose ONE method

### **Method 1: Standard Migration (RECOMMENDED)** ⭐

This is the proper way to fix it using Flask-Migrate:

```powershell
# 1. Navigate to project directory
cd "D:/Projects/HRMS/hrm"

# 2. Run all pending migrations
flask db upgrade

# 3. Verify the fix worked (optional)
python verify_migration.py
```

**What this does:**
- Applies all pending migrations from `migrations/versions/`
- Creates the missing `designation_id` column
- Sets up all foreign key constraints
- Safe and reversible (can rollback with `flask db downgrade`)

**Expected output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade...
✓ Added designation_id column to hrm_employee
```

---

### **Method 2: Automated Schema Fix Script**

If Method 1 fails or you need an immediate fix:

```powershell
# 1. Navigate to project directory
cd "D:/Projects/HRMS/hrm"

# 2. Run the automatic schema fixer
python fix_database_schema.py
```

**What this does:**
- Checks for all missing columns in `hrm_employee`
- Adds any columns that exist in the model but not in the database
- Creates foreign key constraints automatically
- Safe: skips already-existing columns

**Expected output:**
```
============================================================
🔧 DATABASE SCHEMA FIX FOR hrm_employee
============================================================

📊 Current database columns: 38
📊 Expected model columns: 40

⚠️  Missing columns (2):
   - designation_id
   - work_schedule_id

⏳ Adding 2 missing columns...
   ✅ Added column: designation_id (INTEGER)
      ↳ Foreign key added: fk_hrm_employee_designation_id
   ✅ Added column: work_schedule_id (UUID)
      ↳ Foreign key added: fk_hrm_employee_work_schedule_id

============================================================
✅ DATABASE SCHEMA FIX COMPLETE
============================================================
```

---

### **Method 3: Direct SQL Fix (Emergency Only)**

Only use if the above methods fail. This adds just the missing column:

```powershell
cd "D:/Projects/HRMS/hrm"
python fix_missing_designation_column.py
```

---

## 📋 VERIFICATION

After running one of the above methods, verify the fix:

```powershell
# Test if the column exists
python -c "
from app import db, create_app
from models import Employee

app = create_app()
with app.app_context():
    cursor = db.engine.raw_connection().cursor()
    cursor.execute('''
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'hrm_employee' AND column_name = 'designation_id'
    ''')
    result = cursor.fetchone()
    if result:
        print('✅ Column designation_id exists!')
    else:
        print('❌ Column designation_id NOT found')
"
```

Or simply try to load an employee profile:

```powershell
python -c "
from app import db, create_app
from models import Employee

app = create_app()
with app.app_context():
    emp = Employee.query.first()
    if emp:
        print(f'✅ Successfully loaded employee: {emp.first_name}')
    else:
        print('⚠️  No employees in database')
"
```

---

## 🔍 WHY THIS HAPPENED

The HRMS project uses **Flask-Migrate (Alembic)** for database version control:

```
Models (models.py) 
    ↓ (defines schema)
    ↓
Migrations (migrations/versions/)
    ↓ (version control for database)
    ↓
Database (PostgreSQL/MySQL)
```

**Timeline:**
1. ✅ The `designation_id` column was added to the `Employee` model
2. ✅ A migration file was created: `add_designation_to_employee.py`
3. ❌ But the migration was **never applied** to the database
4. ❌ So the database doesn't have the column

**Solution:** Apply the migration using `flask db upgrade`

---

## 🚀 COMPLETE SETUP WORKFLOW

If you're starting fresh, here's the proper sequence:

```powershell
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 4. Create database (if new)
# Ensure DATABASE_URL in .env points to a created but empty database

# 5. Initialize database schema with migrations
flask db upgrade

# 6. Seed test data (optional)
python seed.py

# 7. Run application
python main.py
```

---

## ❓ TROUBLESHOOTING

### Problem: "Migration conflict" or "Can't find Alembic init"

**Solution:**
```powershell
# Initialize migrations if missing
flask db init

# Create new migration for schema
flask db migrate -m "Auto schema update"

# Apply it
flask db upgrade
```

### Problem: "Migration target and head don't match"

**Solution:**
```powershell
# Check migration status
flask db current
flask db heads

# Merge heads if there are conflicts
flask db merge -m "Merge heads"

# Apply migrations
flask db upgrade
```

### Problem: "Column already exists" error

**Solution:** The column is already there - you can safely ignore this. Just restart your application.

### Problem: Foreign key constraint error

**Solution:** The `hrm_designation` table might not exist. Check:
```powershell
python -c "
from app import db, create_app
app = create_app()
with app.app_context():
    cursor = db.engine.raw_connection().cursor()
    cursor.execute('''
        SELECT EXISTS(SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'hrm_designation')
    ''')
    print('hrm_designation exists' if cursor.fetchone()[0] else 'hrm_designation NOT found')
"
```

---

## 📚 RELATED FILES

- **Migration file:** `migrations/versions/add_designation_to_employee.py`
- **Model definition:** `models.py` (line 260-330, Employee class)
- **Database config:** `app.py` (line 36-48)
- **Environment setup:** `.env` file

---

## ✅ SUMMARY

| Step | Action | Command |
|------|--------|---------|
| 1️⃣ | Check current state | `flask db current` |
| 2️⃣ | Apply migrations | `flask db upgrade` |
| 3️⃣ | Test if fixed | `python verify_migration.py` |
| 4️⃣ | Restart app | `python main.py` |

---

**Status:** Once you run `flask db upgrade`, the error should disappear! 🎉