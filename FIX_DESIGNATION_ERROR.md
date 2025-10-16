# 🚨 QUICK FIX: designation_id Column Missing

**Error Message:**
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedColumn) 
column hrm_employee.designation_id does not exist
```

---

## ⚡ QUICK FIX (30 seconds)

Copy and paste this command:

```powershell
cd "D:/Projects/HRMS/hrm"; flask db upgrade
```

That's it! ✅

---

## 📖 What Happened?

- ✅ Your model (`models.py`) has a `designation_id` column
- ❌ Your database doesn't have this column yet
- ✅ A migration file exists to add it
- ❌ But it was never applied (run)

---

## 🔧 STEP-BY-STEP FIX

### Step 1: Make sure you're in the project directory
```powershell
cd "D:/Projects/HRMS/hrm"
```

### Step 2: Verify your .env file has database URL
```powershell
# Check if .env exists and has DATABASE_URL
Get-Content .env | Select-String "DATABASE_URL"
```

If it shows nothing, copy `.env.example` to `.env` and edit it:
```powershell
cp .env.example .env
# Edit .env with your database credentials
```

### Step 3: Run the migration
```powershell
flask db upgrade
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade...
✓ Added designation_id column to hrm_employee
```

### Step 4: Test the fix
```powershell
python verify_migration.py
```

**Expected output:**
```
✅ SCHEMA IS UP TO DATE!
   All 40 columns are present and correct

✅ QUERY SUCCESSFUL!
   Found X employees in database
```

### Step 5: Restart your application
```powershell
python main.py
```

---

## 🆘 IF THE ABOVE DOESN'T WORK

### Option A: Use automatic schema fixer
```powershell
python fix_database_schema.py
```

### Option B: Check if migrations are initialized
```powershell
# If migrations folder doesn't exist:
flask db init

# Create new migration:
flask db migrate -m "Add missing columns"

# Apply it:
flask db upgrade
```

### Option C: Check database connection
```powershell
# Test if database is accessible
python -c "from app import db, create_app; app = create_app(); print('✓ Database connected')"
```

---

## 📋 FILES INVOLVED

| File | Purpose |
|------|---------|
| `models.py` | Defines the Employee model with `designation_id` column (line 281) |
| `migrations/versions/add_designation_to_employee.py` | Migration file that adds the column |
| `flask db` command | Applies pending migrations |
| `.env` | Database connection configuration |

---

## ✅ HOW TO VERIFY IT'S FIXED

After running the fix, you should be able to:

```powershell
# 1. Load employees without error
python -c "from models import Employee; from app import create_app; app = create_app(); emp = Employee.query.first(); print(f'✓ Loaded {emp.first_name}')"

# 2. Access the new column
python -c "from models import Employee; from app import create_app; app = create_app(); emp = Employee.query.first(); print(f'✓ designation_id = {emp.designation_id}')"

# 3. Run your app
python main.py
# Should start without the ProgrammingError
```

---

## 🎯 COMMON ISSUES

### Issue: "flask: command not found"
**Solution:**
```powershell
# Install Flask CLI
pip install flask

# Or activate virtual environment
.\venv\Scripts\Activate.ps1
```

### Issue: "AttributeError: flask.current_app"
**Solution:** Make sure `.env` has valid `DEV_DATABASE_URL` set

### Issue: "Can't connect to database"
**Solution:** 
```powershell
# Check your database URL format is correct
# Should be like: postgresql://user:pass@localhost/dbname
# Or: mysql://user:pass@localhost/dbname
```

### Issue: "Migration target and head don't match"
**Solution:**
```powershell
# Check current migration state
flask db current
flask db heads

# Merge if needed
flask db merge -m "Merge heads"

# Apply
flask db upgrade
```

---

## 🎉 DONE!

Once `flask db upgrade` completes successfully, the error should disappear. Your application will now properly recognize the `designation_id` column and work as expected!

**Next:** Log in and try accessing employee records - they should load without the `ProgrammingError`.

---

**Timeline:** ⏱️ This should take ~1 minute to fix

**Risk:** ✅ Very low - migrations are designed to be reversible (can run `flask db downgrade` if needed)