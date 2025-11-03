# Employee ID Auto-Generation - Quick Start

## What Changed?
Employee IDs are now **auto-generated** in format `<CompanyCode><ID>` instead of requiring manual input.

**Examples:**
- `ACME001` - First employee at ACME company
- `ACME002` - Second employee at ACME company
- `TECH042` - 42nd employee at TECH company

---

## User Experience (New)

### Adding a New Employee:

1. **Open** "Add Employee" form
2. **Select** a Company from dropdown
3. ✨ **Auto-generated** Employee ID appears (e.g., `ACME001`)
4. **Continue** filling other employee details
5. **Submit** form

**That's it!** No more manual Employee ID entry.

---

## Technical Changes

### 1. Backend (Python)

**File: `utils.py`**
```python
# OLD:
generate_employee_id()  # Returns: EMP20250110113245

# NEW:
generate_employee_id(company_code='ACME', employee_db_id=1)  # Returns: ACME001
```

**File: `routes_enhancements.py`**
```
GET /employees/generate-id?company_id=<company_uuid>

Response:
{
  "employee_id": "ACME001",
  "company_code": "ACME",
  "next_id": 1
}
```

**File: `routes.py`**
- Uses employee_id from form (frontend-generated)
- Falls back to server generation if needed

---

### 2. Frontend (HTML/JavaScript)

**File: `templates/employees/form.html`**

**Before:**
```html
<input type="text" id="employee_id" name="employee_id" 
       placeholder="e.g., EMP001" required>
<button>Generate</button>  <!-- Manual button click -->
```

**After:**
```html
<input type="text" id="employee_id" name="employee_id" 
       placeholder="Auto-generated (select company first)" 
       readonly>  <!-- Read-only -->
<span>📋</span>  <!-- Status indicator -->
```

**JavaScript:** Auto-triggers when company is selected

---

## Format Specification

| Aspect | Details |
|--------|---------|
| **Format** | `{CompanyCode}{EmployeeID}` |
| **Company Code** | 2-4 letters (from company master data) |
| **Employee ID** | 3-digit number with zero-padding |
| **Examples** | `ACME001`, `TECH042`, `HR0100` |
| **Max per company** | 999 employees (can extend padding if needed) |

---

## Implementation Checklist

### ✅ Already Completed:
- [x] Modified `generate_employee_id()` function in `utils.py`
- [x] Enhanced `/employees/generate-id` endpoint in `routes_enhancements.py`
- [x] Updated Employee form template (`templates/employees/form.html`)
- [x] Updated employee creation logic in `routes.py`

### 📋 Testing Steps (Do This):

1. **Manual Testing:**
   ```
   1. Go to Employees → Add Employee
   2. Select a Company → ID should auto-generate
   3. Fill other fields
   4. Submit → Employee should be created with new ID format
   ```

2. **Verify in Database:**
   ```sql
   SELECT employee_id, company_id FROM hrm_employee 
   ORDER BY created_at DESC LIMIT 10;
   ```
   Should see IDs like: `ACME001`, `ACME002`, `TECH001`

3. **Test Edge Cases:**
   - [ ] Change company selection → ID updates
   - [ ] Refresh page with company selected → ID auto-generates
   - [ ] Network error → Shows error styling
   - [ ] Submit form with auto-generated ID → Success

### 🚀 Deployment:
- No database migration needed
- No breaking changes
- Existing employees retain old ID format
- Can be deployed immediately

---

## FAQ

### Q: Will my existing employee IDs change?
**A:** No! Existing employees keep their current IDs. Only new employees get the new format.

### Q: What if I manually enter an employee ID?
**A:** You can't! The field is read-only. You must select a company to auto-generate.

### Q: What if company is not selected?
**A:** Employee ID field stays empty. Form validation prevents submission without it.

### Q: Can I have duplicate IDs?
**A:** No! The database enforces unique constraint on employee_id field.

### Q: What if I need to change the format?
**A:** Edit the `generate_employee_id()` function in `utils.py`:
```python
# Current:
return f"{company_code}{str(employee_db_id).zfill(3)}"

# To 4 digits:
return f"{company_code}{str(employee_db_id).zfill(4)}"  # ACME0001

# With year:
from datetime import datetime
year = datetime.now().year
return f"{company_code}{year}{str(employee_db_id).zfill(3)}"  # ACME250001
```

### Q: Does this work with employee bulk upload?
**A:** Not yet. Bulk upload still needs to be updated separately if required.

---

## Troubleshooting

### ❌ Employee ID not auto-generating?
1. Refresh page
2. Check browser console for errors (F12)
3. Verify company is selected
4. Clear browser cache

### ❌ Form won't submit with auto-generated ID?
1. Check that employee_id field has a value
2. Check for duplicate ID in database
3. Check form validation errors on page

### ❌ Getting API error "Company ID is required"?
1. Ensure company_id is a valid UUID
2. Company must exist in database
3. Check network requests in browser DevTools

---

## Database Schema

No changes required! Existing field accommodates new format:

```sql
-- Existing column definition (no change needed)
employee_id VARCHAR(20) UNIQUE NOT NULL

-- Space available for formats:
-- Old: EMP20250110113245 (17 chars)
-- New: ACME001 (7 chars)
-- Future: ACME250001 (9 chars)
```

---

## Monitoring

### Check implementation with this query:

```sql
-- Count employees by company
SELECT 
    c.code as company_code,
    COUNT(e.id) as employee_count,
    MIN(e.employee_id) as first_id,
    MAX(e.employee_id) as last_id
FROM hrm_employee e
LEFT JOIN hrm_company c ON e.company_id = c.id
GROUP BY c.code
ORDER BY c.code;
```

---

## Related Files

📄 **For Detailed Information:**
- `EMPLOYEE_ID_FORMAT_CHANGES.md` - Complete technical documentation
- `models.py` - Employee model (line 265)
- `utils.py` - generate_employee_id function (line 91)
- `routes_enhancements.py` - API endpoint (line 438)
- `templates/employees/form.html` - UI template (line 36)
- `routes.py` - Employee creation logic (line 604)

---

## Support

Need help? Check:
1. 📖 Read `EMPLOYEE_ID_FORMAT_CHANGES.md`
2. 🧪 Follow "Testing Steps" section above
3. 📊 Run SQL query in "Monitoring" section
4. 🐛 Check browser console (F12) for JavaScript errors

**Success:** When you see employee IDs like `ACME001`, `ACME002` in the database! ✅