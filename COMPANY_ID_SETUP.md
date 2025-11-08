# Quick Setup Guide: Company-Specific Employee IDs

## ⚡ Quick Start (1 Step - AUTOMATED!) 🚀

### Single Command: Migration Handles Everything!
```bash
# This single command automatically:
# ✅ Creates the hrm_company_employee_id_config table
# ✅ Initializes configs for ALL existing companies
# ✅ Preserves existing employee ID sequences
# ✅ Ready to use immediately
flask db upgrade
```

**That's it!** No manual scripts needed. The migration is fully automated.

### Optional: Verify Installation
```bash
# Run test suite to confirm everything works
python test_company_employee_id.py
```

---

## 📊 Example: How It Works

**Before:**
- Company ACME: EMP001, EMP002, EMP003 (uses global sequence)
- Company NEXAR: EMP004, EMP005, EMP006

**After:**
- Company ACME: ACME001, ACME002, ACME003 (starts from 1)
- Company NEXAR: NEXAR001, NEXAR002, NEXAR003 (independent sequence, also starts from 1)

---

## 🔧 Configuration Table

**Table:** `hrm_company_employee_id_config`

```
company_id           | last_sequence_number | id_prefix | created_by | created_at
─────────────────────┼──────────────────────┼───────────┼────────────┼──────────
5f8c9e3b-2a1d-41e8  | 5                    | ACME      | system     | 2025-01-15
6g9d0f4c-3b2e-42f9  | 12                   | NEXAR     | system     | 2025-01-15
```

---

## 🎯 What Changed

### Files Modified:
1. ✅ **models.py** - Added `CompanyEmployeeIdConfig` model
2. ✅ **routes.py** - Updated `employee_add()` function
3. ✅ **utils.py** - Added `get_company_employee_id()` function

### Files Created:
1. 📄 **init_company_employee_id_config.py** - Setup script
2. 📄 **docs/COMPANY_EMPLOYEE_ID_CONFIG.md** - Full documentation

---

## 📋 Verification

After running `flask db upgrade`, verify with:

```bash
# 1. Check table exists and has data
python -c "from models import CompanyEmployeeIdConfig; configs = CompanyEmployeeIdConfig.query.all(); print(f'✅ Found {len(configs)} company configs')"

# 2. Or use the test suite (comprehensive)
python test_company_employee_id.py

# 3. Manual test: Add an employee
# - Go to Employees → Add Employee 
# - Select a Company from dropdown
# - The Employee ID will auto-generate (e.g., ACME001)
# - Verify it follows the CompanyCode### format
```

---

## 🐛 Troubleshooting

### "Table hrm_company_employee_id_config doesn't exist"
**Solution:** Run migrations again: `flask db upgrade`
- The migration automatically creates the table and initializes data

### Employee IDs not generated correctly
**Solution:** Verify migration completed successfully
```bash
# Check Alembic history
flask db history
# Should show: "add_company_employee_id_config" as the latest version
```

### "CompanyEmployeeIdConfig is not defined"
**Solution:** Ensure `routes.py` has the updated imports:
```python
from models import CompanyEmployeeIdConfig
```

### Config data not initialized after migration
**Solution:** This shouldn't happen - the migration auto-initializes
- But if needed, you can run the init script manually:
```bash
python init_company_employee_id_config.py
```

---

## 📈 Next Steps

1. Run the 3-step setup above
2. Test by adding an employee from each company
3. Verify IDs follow the format: `CompanyCode###` (e.g., ACME001)
4. Monitor the sequence with: `CompanyEmployeeIdConfig` table

---

## 💡 Key Benefits

✅ **Per-company sequences** - Each company starts from 001  
✅ **Cleaner IDs** - ACME001 instead of ACME101  
✅ **Scalable** - Works with unlimited companies  
✅ **Audit trail** - Tracks who created/modified config  
✅ **Backward compatible** - Old IDs remain unchanged  

---

## 📞 Need Help?

See `docs/COMPANY_EMPLOYEE_ID_CONFIG.md` for detailed documentation.

**Full Documentation:**
```
D:/Projects/HRMS/hrm/docs/COMPANY_EMPLOYEE_ID_CONFIG.md
```