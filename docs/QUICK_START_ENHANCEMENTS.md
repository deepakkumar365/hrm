# Quick Start Guide - HRMS Enhancements

## What's New? 🎉

Three major feature sets added to your HRMS:

1. **LOP (Loss of Pay)** - Mark absent employees as LOP for salary deductions
2. **Other Deductions** - Manually add deductions in payroll generation
3. **Tenant Configuration** - Advanced settings for logos, employee IDs, and overtime

---

## Prerequisites

✅ Existing HRMS installation  
✅ Database access (PostgreSQL recommended)  
✅ Python 3.8+  
✅ Flask and SQLAlchemy

---

## Step-by-Step Setup

### 1. **Database Migration**

Run the migration to add the new `TenantConfiguration` table:

```bash
# In your HRMS root directory
python -m flask db upgrade
```

Or manually run the migration:

```bash
# Check migrations were created
ls migrations/versions/ | grep tenant_configuration

# If migration exists, Flask will auto-apply on startup
```

### 2. **Restart Application**

```bash
# Stop the running app (Ctrl+C)

# Restart with new routes
python main.py
```

### 3. **Verify Installation**

Check these work in your browser:

- ✅ Attendance → Bulk Attendance → See LOP column
- ✅ Payroll → Generate Payroll → See "Other Ded." column
- ✅ Tenant Admin → Configuration (new page)

---

## Quick Feature Usage

### Feature 1: LOP (Loss of Pay) ⏱️

**Where**: Attendance → Bulk Attendance

```
1. Select a date
2. Look for "LOP" column
3. Mark employees as Absent → LOP checkbox enables
4. Check LOP box → Salary deduction applies in payroll
```

**Result**: LOP days appear in payroll and reduce net salary

---

### Feature 2: Other Deductions 💰

**Where**: Payroll → Generate Payroll

```
1. Select company, month, year
2. Click "Load Employee Data"
3. Look for "Other Ded." column
4. Enter deduction amount (e.g., 50.00)
5. Press Enter → Totals recalculate automatically
6. Net Salary updates in real-time
```

**How it affects payroll**:
```
Net Salary = Gross Salary - (CPF + LOP + Other Deductions)
```

---

### Feature 3: Tenant Configuration ⚙️

**Where**: `/tenant/configuration` or Dashboard → Configuration

#### 3.1 Payslip Logo 📸

```
1. Go to Tenant Configuration
2. Click "Payslip Logo" tab
3. Upload JPG/PNG/SVG file (max 2MB)
4. Preview shows immediately
5. Logo now appears in all generated payslips
```

#### 3.2 Employee ID Format 🆔

```
1. Click "Employee ID Format" tab
2. Configure:
   - Prefix: "EMP" (starting code)
   - Company Code: "ACME" (company identifier)
   - Separator: "-" (joining character)
   - Pad Length: "4" (number of zeros: 0001)
   - Suffix: "SG" (optional ending)
3. See preview: "EMP-ACME-0001-SG"
4. Click "Save Configuration"
```

#### 3.3 Overtime Settings ⏰

```
1. Click "Overtime Settings" tab
2. Toggle "Enable Overtime Calculation"
3. Choose method:
   - By User: Individual rates
   - By Designation: Same rate for designation
   - By Group: Grouped rates
4. Set multipliers:
   - General OT: 1.5x (default)
   - Holiday OT: 2.0x (default)
   - Weekend OT: 1.5x (default)
5. Click "Save Configuration"
```

---

## File Structure

New/Modified files:

```
routes_tenant_config.py          ← New file (all config routes)
templates/
  ├── tenant_configuration.html   ← New template (config UI)
  └── payroll/generate.html       ← Modified (added Other Ded. column)
models.py                         ← Modified (added TenantConfiguration)
migrations/versions/
  └── add_tenant_configuration.py ← New migration
main.py                           ← Modified (added import)
```

---

## Common Issues & Fixes

### ❌ "Tenant Configuration not found (404)"
**Fix**: Ensure `main.py` imports `routes_tenant_config`
```python
import routes_tenant_config  # Add if missing
```

### ❌ "Logo upload fails"
**Fix**: 
- File must be: JPG, PNG, or SVG
- File size must be: < 2MB
- Directory `static/uploads/tenant_logos/` must exist

```bash
# Create directory if missing
mkdir -p static/uploads/tenant_logos
chmod 755 static/uploads/tenant_logos
```

### ❌ "Other Deductions column not showing"
**Fix**: Clear browser cache and refresh
```
Ctrl+Shift+Delete → Clear all → Refresh page
```

### ❌ Database error on startup
**Fix**: Run migration manually
```bash
python -m flask db upgrade
```

---

## Testing the Features

### Test 1: LOP Functionality
```
1. Go to Attendance → Bulk Attendance
2. Select today's date
3. Mark an employee as "Absent"
4. LOP checkbox should be enabled
5. Check the LOP box
6. Save attendance
7. Go to Payroll → Generate Payroll
8. Verify LOP days count increased
9. Verify salary deduction applied
```

### Test 2: Other Deductions
```
1. Go to Payroll → Generate Payroll
2. Select company, month, year
3. Click "Load Employee Data"
4. Find "Other Ded." column
5. Enter: 100.00
6. Press Tab/Enter
7. Verify:
   - Total Deductions updated
   - Net Salary recalculated
   - Summary total changed
```

### Test 3: Tenant Configuration
```
1. Login as Tenant Admin
2. Navigate to /tenant/configuration
3. Upload a logo
4. Set Employee ID format: EMP-ACME-0001
5. Enable overtime with rates 1.5x, 2.0x, 1.5x
6. Click "Save Configuration"
7. Refresh page
8. Verify all settings saved
```

---

## Database Verification

Check if tables created correctly:

```sql
-- List all tenant configuration records
SELECT id, tenant_id, employee_id_prefix, overtime_enabled 
FROM hrm_tenant_configuration;

-- Check payroll other_deductions column exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='hrm_payroll' AND column_name='other_deductions';

-- Verify LOP column in attendance
SELECT column_name 
FROM information_schema.columns 
WHERE table_name='hrm_attendance' AND column_name='lop';
```

---

## Deployment Checklist

- [ ] Code deployed to server
- [ ] Database migration executed (`flask db upgrade`)
- [ ] Application restarted
- [ ] Tenant Configuration page loads (no 404)
- [ ] Can upload payslip logo
- [ ] Employee ID preview works
- [ ] Overtime settings save
- [ ] Other Deductions column visible in payroll
- [ ] LOP checkbox works in attendance
- [ ] All calculations correct

---

## Support Resources

📖 **Documentation**: See `ENHANCEMENT_IMPLEMENTATION.md`  
🔧 **Troubleshooting**: See issues section above  
📧 **Need Help?**: Check Flask logs and browser console  

---

## What's Next?

Consider these additions:

1. ✨ Auto-generate employee IDs on creation
2. ✨ Custom payslip layouts
3. ✨ Employee ID bulk generation tool
4. ✨ OT group management UI
5. ✨ LOP approval workflow

---

**Version**: 1.0  
**Status**: ✅ Ready to Use  
**Last Updated**: 2024-01-20