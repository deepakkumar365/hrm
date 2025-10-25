# HRMS Enhancements Implementation Guide

## Overview
This document outlines all the enhancements implemented for the HRMS application across three main areas: **Attendance**, **Payroll**, and **Tenant Configuration**.

---

## 1. ATTENDANCE MODULE - BULK ATTENDANCE PAGE

### Feature: LOP (Loss of Pay) Column
**Status**: ✅ COMPLETE

#### What Was Implemented:
- **LOP Checkbox**: Added in attendance bulk management template (`bulk_manage.html`)
- **Conditional Display**: LOP checkbox is only enabled when employee status is "Absent"
- **Database Support**: `lop` boolean column already exists in `hrm_attendance` table

#### Location:
- Template: `templates/attendance/bulk_manage.html` (Lines 126, 163-171, 214-224)
- Model: `models.py` - `Attendance` class, line 487

#### Functionality:
```
- Visible in bulk attendance table for all roles with access
- Can only be checked when attendance status = "Absent"
- Affects payroll deductions when LOP days are calculated
- Displays LOP days count in payroll generation
```

---

## 2. PAYROLL MODULE - GENERATE PAYROLL PAGE

### Feature: Other Deductions Column
**Status**: ✅ COMPLETE

#### What Was Implemented:
1. **Database Schema**: 
   - `other_deductions` column exists in `hrm_payroll` table
   - Numeric(10,2) field for manual deduction entry

2. **Backend Updates**:
   - Updated `/api/payroll/preview` endpoint to include `other_deductions` in response
   - Added logic to include other_deductions in total_deductions calculation
   - Modified net salary calculation: `net_salary = gross_salary - (cpf_deduction + lop_deduction + other_deductions)`

3. **Frontend Updates**:
   - Added "Other Ded." column header in payroll table (template line 114)
   - Made column editable with numeric input field
   - Real-time calculation of total deductions and net salary when value changes
   - Added `updateEmployeeDeductions()` JavaScript function

#### Locations:
- API: `routes.py` lines 1970-2003
- Template: `templates/payroll/generate.html` lines 114-115, 279-286
- JavaScript: `templates/payroll/generate.html` lines 298-321

#### Features:
```
- Editable numeric input field in payroll preview table
- Minimum value: 0
- Step: 0.01 (to nearest cent)
- Real-time recalculation of:
  * Total Deductions = CPF + LOP + Other Deductions
  * Net Salary = Gross - Total Deductions
  * Summary total updates dynamically
- Works on selected employees only
```

---

## 3. TENANT ADMIN - CONFIGURATION PAGE

### Features Implemented

#### 3.1 Payslip Logo Configuration
**Status**: ✅ COMPLETE

**What It Does**:
- Allows tenant admins to upload a company logo for payslip headers
- Logo is saved per-tenant and displayed in generated payslips
- Supports JPG, PNG, SVG formats (max 2MB)

**Implementation**:
- Route: `POST /tenant/configuration/logo-upload` (routes_tenant_config.py)
- Template: `tenant_configuration.html` (Logo Tab)
- Database: `TenantConfiguration.payslip_logo_path`, `payslip_logo_filename`, etc.
- Features:
  * File type validation (jpg, jpeg, png, svg)
  * File size validation (2MB max)
  * Logo preview display
  * Upload history (who uploaded, when)
  * Automatic old logo deletion on new upload

#### 3.2 Employee ID Configuration
**Status**: ✅ COMPLETE

**What It Does**:
- Allows admins to define custom employee ID format and generation logic
- Supports multiple format components: prefix, company code, running number, suffix
- Auto-increments with configurable padding

**Configuration Options**:
```
- Prefix: Starting code (e.g., "EMP")
- Company Code: Company identifier (e.g., "ACME")
- Separator: Character(s) between components (e.g., "-")
- Number Padding: Zeros to pad running number (e.g., 4 → "0001")
- Suffix: Ending code (optional, e.g., "SG")
```

**Example Formats**:
- Basic: `EMP-0001`
- With Company: `EMP-ACME-0001`
- With Suffix: `EMP-ACME-0001-SG`

**Implementation**:
- Route: `POST /tenant/configuration/generate-employee-id` (generates preview)
- Database Fields: Multiple fields in `TenantConfiguration` model
- Template: `tenant_configuration.html` (Employee ID Tab)
- Real-time preview updates as user modifies format

#### 3.3 Overtime Function Toggle
**Status**: ✅ COMPLETE

**What It Does**:
- Enable/disable overtime calculations globally per tenant
- When disabled:
  * Overtime-related menus are hidden
  * Overtime calculations skip in payroll
  * Reduces system complexity for organizations without overtime

**Implementation**:
- Field: `TenantConfiguration.overtime_enabled` (boolean)
- Template: Toggle switch in Overtime Settings tab
- Behavior: Disables all related fields when turned off

#### 3.4 Overtime Charges Configuration
**Status**: ✅ COMPLETE

**What It Does**:
- Configure how overtime is calculated and charged
- Supports different rates for different circumstances
- Flexible calculation methods

**Configuration Options**:
```
1. Calculation Method:
   - By User: Individual OT rates per employee
   - By Designation: Same rate for all employees with same designation
   - By Group: Group-based rates (Group 1, 2, 3)

2. Overtime Rates (multipliers):
   - General Overtime Rate: Regular OT multiplier (default: 1.5x)
   - Holiday Overtime Rate: OT on holidays (default: 2.0x)
   - Weekend Overtime Rate: OT on weekends (default: 1.5x)
```

**Example Calculation**:
```
Hourly Rate: $10
General OT Rate: 1.5x
OT Hour Rate: $10 × 1.5 = $15/hour

Holiday OT Rate: 2.0x
Holiday OT Hour Rate: $10 × 2.0 = $20/hour
```

**Implementation**:
- Fields in `TenantConfiguration` model:
  * `overtime_calculation_method`
  * `overtime_group_type`
  * `general_overtime_rate`
  * `holiday_overtime_rate`
  * `weekend_overtime_rate`
- Template: `tenant_configuration.html` (Overtime Settings Tab)
- Routes: Update via `POST /tenant/configuration/update`

---

## Database Schema Changes

### New Model: TenantConfiguration

**Table**: `hrm_tenant_configuration`

**Fields**:
```
id (Integer, Primary Key)
tenant_id (UUID, Foreign Key → hrm_tenant.id, UNIQUE)

-- Payslip Logo
payslip_logo_path (String(255), nullable)
payslip_logo_filename (String(255), nullable)
payslip_logo_uploaded_by (String(100), nullable)
payslip_logo_uploaded_at (DateTime, nullable)

-- Employee ID Configuration
employee_id_prefix (String(50), default='EMP')
employee_id_company_code (String(20), nullable)
employee_id_format (String(100), default='prefix-company-number')
employee_id_separator (String(5), default='-')
employee_id_next_number (Integer, default=1)
employee_id_pad_length (Integer, default=4)
employee_id_suffix (String(50), nullable)

-- Overtime Configuration
overtime_enabled (Boolean, default=True)
overtime_calculation_method (String(20), default='By User')
overtime_group_type (String(50), nullable)

-- Overtime Charges
general_overtime_rate (Numeric(5,2), default=1.5)
holiday_overtime_rate (Numeric(5,2), default=2.0)
weekend_overtime_rate (Numeric(5,2), default=1.5)

-- Metadata
created_at (DateTime, default=now())
updated_at (DateTime, default=now())
updated_by (String(100), nullable)
```

### Relationships:
- Added to `Tenant` model: `configuration` (one-to-one relationship)

---

## Routes Added

### Tenant Configuration Routes

#### 1. GET /tenant/configuration
- Display tenant configuration page
- Auto-creates configuration if doesn't exist
- Requires: Tenant Admin role

#### 2. POST /tenant/configuration/update
- Update all configuration settings
- Accepts form data
- Returns: JSON response
- Requires: Tenant Admin role

#### 3. POST /tenant/configuration/logo-upload
- Upload payslip logo file
- File validation (type, size)
- Auto-deletes old logo
- Returns: JSON with logo path
- Requires: Tenant Admin role

#### 4. POST /tenant/configuration/generate-employee-id
- Generate preview of employee ID format
- Used for real-time preview updates
- Returns: JSON with sample employee ID
- Requires: Tenant Admin role

---

## Files Modified/Created

### Created Files:
1. **routes_tenant_config.py** - All tenant configuration routes
2. **templates/tenant_configuration.html** - Configuration UI with tabs
3. **migrations/versions/add_tenant_configuration.py** - Database migration

### Modified Files:
1. **models.py** - Added TenantConfiguration model and Tenant relationship
2. **routes.py** - Updated payroll preview API to include other_deductions
3. **templates/payroll/generate.html** - Added Other Deductions column and JS
4. **main.py** - Added import for routes_tenant_config
5. **app.py** - No changes needed (uses existing app factory)

---

## Migration Instructions

### Step 1: Install Dependencies (if needed)
```bash
pip install flask flask-sqlalchemy flask-migrate
```

### Step 2: Run Database Migration
```bash
# Generate new migration (should be automatic)
python -m flask db migrate

# Apply migration
python -m flask db upgrade
```

### Step 3: Restart Application
```bash
python main.py
# or
python app.py
```

### Step 4: Access Tenant Configuration
- Login as Tenant Admin
- Navigate to: `/tenant/configuration`
- Or from dashboard, look for Configuration menu option

---

## Usage Examples

### For HR Managers (Payroll):

**Setting Other Deductions**:
1. Go to Payroll → Generate Payroll
2. Select month, year, and company
3. Click "Load Employee Data"
4. In the "Other Ded." column, enter deduction amount
5. Press Enter or click elsewhere to recalculate
6. Total Deductions and Net Salary update automatically

### For Tenant Admins (Configuration):

**1. Upload Payslip Logo**:
1. Go to Tenant Configuration
2. Click on "Payslip Logo" tab
3. Click "Choose File" and select JPG/PNG/SVG (max 2MB)
4. Click "Upload"
5. Logo appears in preview immediately

**2. Configure Employee ID Format**:
1. Go to Employee ID Format tab
2. Enter:
   - Prefix: "EMP"
   - Company Code: "ACME"
   - Separator: "-"
   - Pad Length: "4"
   - Suffix: "SG" (optional)
3. See preview: "EMP-ACME-0001-SG"
4. Click "Save Configuration"

**3. Configure Overtime Settings**:
1. Go to Overtime Settings tab
2. Enable/disable overtime calculation
3. Choose calculation method (By User/Designation/Group)
4. If "By Group", select group type
5. Set rates:
   - General: 1.5x
   - Holiday: 2.0x
   - Weekend: 1.5x
6. Click "Save Configuration"

---

## Testing Checklist

- [ ] LOP checkbox appears only for Absent attendance status
- [ ] LOP checkbox can be checked/unchecked
- [ ] LOP days reflected in payroll generation
- [ ] Other Deductions column visible and editable
- [ ] Deduction values update total and net salary
- [ ] Tenant Configuration page loads without errors
- [ ] Logo upload accepts valid formats
- [ ] Logo upload rejects files > 2MB
- [ ] Employee ID preview updates in real-time
- [ ] Overtime toggle disables related fields
- [ ] Configuration saves successfully
- [ ] Overtime rates display with examples

---

## Troubleshooting

### Issue: Tenant Configuration page shows 404
**Solution**: Ensure `routes_tenant_config.py` is imported in `main.py`

### Issue: Logo upload fails
**Solution**: 
- Check file format (JPG, PNG, SVG only)
- Verify file size < 2MB
- Ensure `static/uploads/tenant_logos/` directory exists

### Issue: Employee ID preview not updating
**Solution**: Check browser console for JavaScript errors

### Issue: Other Deductions not saving
**Solution**: 
- Ensure payroll creation endpoint includes other_deductions
- Check database migration applied successfully

---

## Future Enhancements

1. **Employee ID Auto-Generation**: 
   - Auto-generate IDs when creating employees
   - Bulk generate IDs for existing employees

2. **Payslip Template Customization**:
   - Custom payslip layout per tenant
   - Additional logo placement options
   - Custom footer/header text

3. **OT Groups Management UI**:
   - Create/edit OT groups
   - Assign employees to groups
   - Group-wise rate management

4. **Attendance Bulk Management**:
   - LOP day type (Full Day vs Half Day)
   - LOP reason/category
   - LOP approval workflow

5. **Employee Profile Enhancement**:
   - OT group assignment field
   - Individual OT rate override option
   - Overtime eligibility flag

---

## Support & Documentation

For issues or questions:
1. Check the template comments in each HTML file
2. Review JavaScript console for errors
3. Check Flask logs for backend errors
4. Refer to models.py for schema details

---

**Last Updated**: 2024-01-20
**Version**: 1.0
**Status**: Ready for Testing