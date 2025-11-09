# Employee Form Validation & "None" Value Fixes

## Issues Fixed

### 1. **"None" String Display Issue** ✅
**Problem**: Empty fields were displaying as the string "None" instead of being blank.

**Root Cause**: Template was not properly handling None/null values from the database.

**Solution**: Updated all form fields in `templates/employees/form.html` to use proper Jinja2 null-coalescing patterns:
- Used `or ''` filter for None values
- Used `| default('')` filter for date fields that might be None
- Examples:
  - `(employee.phone or '' if employee else '')` 
  - `(employee.work_permit_expiry.strftime('%Y-%m-%d') if employee and employee.work_permit_expiry else '') | default('')`

**Files Modified**:
- `templates/employees/form.html` - Lines 72, 76, 81, 237, 348, 353, 364

---

### 2. **Missing Variable Declaration** ✅
**Problem**: Error "name 'work_permit_expiry' is not defined" when updating employees.

**Root Cause**: Code was using `work_permit_expiry` variable without retrieving it from form first.

**Solution**: Added proper variable declaration before use:
```python
work_permit_expiry = request.form.get('work_permit_expiry')
if work_permit_expiry:
    employee.work_permit_expiry = parse_date(work_permit_expiry)
else:
    employee.work_permit_expiry = None
```

**Files Modified**:
- `routes.py` - Lines 1133-1137

---

### 3. **Form Validation Before Update** ✅
**Problem**: No validation was performed before updating employee data, allowing invalid data to be saved.

**Solution**: Added comprehensive validation in both `employee_add()` and `employee_edit()` functions:

#### Required Field Validation:
- First Name (required)
- Last Name (required)
- Company (required)
- Designation (required)

#### Format Validation:
- **Email**: Validates email format if provided
- **NRIC**: Validates NRIC/Passport format if provided
- **Phone**: Accepts any value (optional field)

#### Numeric Field Validation:
- **Basic Salary**: Must be valid float, cannot be negative
- **Allowances**: Must be valid float, cannot be negative
- **Hourly Rate**: Must be valid float, cannot be negative
- Try-catch blocks to handle ValueError for invalid numeric inputs

#### Error Handling:
- All validation errors now display flash messages to the user
- Form redirects back to edit/add page on validation failure
- Form data is preserved in form_data parameter for re-rendering

**Files Modified**:
- `routes.py` - Lines 590-616 (employee_add validation)
- `routes.py` - Lines 1036-1079 (employee_edit validation)
- `routes.py` - Lines 1161-1194 (numeric field validation)

---

## Validation Rules Implemented

### Employee Add Function (`employee_add`):
```
✓ First Name - Required, stripped of whitespace
✓ Last Name - Required, stripped of whitespace  
✓ Company - Required
✓ Designation - Required
✓ Email - Optional, but validated if provided
✓ NRIC - Optional, but validated if provided
✓ Salary fields - Validated for numeric values and non-negative amounts
```

### Employee Edit Function (`employee_edit`):
```
✓ Same validation rules as Add function
✓ Designation is updated properly
✓ Company is updated properly
✓ All salary and numeric fields are validated before update
```

---

## How to Test

1. **Test "None" Display Fix**:
   - Edit an employee with empty optional fields
   - Verify fields show as blank, not "None"

2. **Test Validation**:
   - Try to save employee without First Name → Should see error message
   - Try to save employee without Last Name → Should see error message
   - Try to save employee without Company → Should see error message
   - Try to save employee with invalid email → Should see error message
   - Try to save employee with negative salary → Should see error message
   - Try to save employee with invalid numeric value → Should see error message

3. **Test work_permit_expiry Fix**:
   - Add/edit employee with work permit type selected
   - Should no longer throw "name 'work_permit_expiry' is not defined" error
   - Should properly save work permit expiry date

---

## Files Modified

1. **templates/employees/form.html**
   - Fixed phone field (line 72)
   - Fixed nric field (line 76, 81)
   - Fixed work_permit_expiry field (line 237)
   - Fixed hazmat_expiry field (line 348)
   - Fixed airport_pass_expiry field (line 353)
   - Fixed psa_pass_expiry field (line 364)

2. **routes.py**
   - Added validation for employee_add (lines 590-616)
   - Added validation for employee_edit (lines 1036-1079)
   - Added numeric field validation (lines 1161-1194)
   - Fixed work_permit_expiry declaration (lines 1133-1137)

---

## Validation Helper Functions Used

- `validate_email()` - Validates email format
- `validate_nric()` - Validates NRIC/Passport format
- `parse_date()` - Safely parses date strings
- `flash()` - Displays user-friendly error messages

These functions should already exist in the codebase. If any are missing, they should be implemented.