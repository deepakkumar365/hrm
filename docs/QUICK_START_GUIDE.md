# Quick Start Guide - Professional Payslip Template

## 🚀 Get Started in 5 Minutes

Follow these steps to deploy the new professional payslip template.

---

## Step 1: Apply Database Migration (1 minute)

Open PowerShell and run:

```powershell
# Navigate to project directory
Set-Location "E:/Gobi/Pro/HRMS/hrm"

# Apply migration
python -m flask db upgrade
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade 28f425a665b2 -> add_organization_logo
```

✅ **Verification:**
```powershell
python -m flask db current
```
Should show: `add_organization_logo (head)`

---

## Step 2: Create Logos Directory (30 seconds)

```powershell
# Create directory for company logos
New-Item -ItemType Directory -Path "E:/Gobi/Pro/HRMS/hrm/static/logos" -Force
```

✅ **Verification:**
```powershell
Test-Path "E:/Gobi/Pro/HRMS/hrm/static/logos"
```
Should return: `True`

---

## Step 3: Upload Company Logo (1 minute)

1. **Prepare your logo:**
   - Format: PNG, JPG, or SVG
   - Recommended size: 120px × 80px
   - Name it: `company_logo.png` (or any name you prefer)

2. **Copy to logos directory:**
   ```powershell
   # Example: Copy from Downloads
   Copy-Item "C:/Users/YourName/Downloads/company_logo.png" -Destination "E:/Gobi/Pro/HRMS/hrm/static/logos/"
   ```

✅ **Verification:**
```powershell
Get-ChildItem "E:/Gobi/Pro/HRMS/hrm/static/logos"
```
Should list your logo file.

---

## Step 4: Update Organization Record (1 minute)

**Option A: Using Python Shell**

```powershell
# Start Python shell
python

# Then run:
>>> from app import app, db
>>> from models import Organization
>>> with app.app_context():
...     org = Organization.query.first()
...     org.logo_path = 'logos/company_logo.png'
...     db.session.commit()
...     print(f"✅ Logo updated for {org.name}")
>>> exit()
```

**Option B: Using SQL**

```powershell
# If using SQLite (default)
sqlite3 instance/hrm.db

# Then run:
UPDATE organization SET logo_path = 'logos/company_logo.png' WHERE id = 1;
.exit
```

✅ **Verification:**
```python
python
>>> from app import app, db
>>> from models import Organization
>>> with app.app_context():
...     org = Organization.query.first()
...     print(f"Name: {org.name}")
...     print(f"Logo: {org.logo_path}")
>>> exit()
```

---

## Step 5: Test the Payslip (2 minutes)

1. **Start the application:**
   ```powershell
   python app.py
   ```

2. **Open browser and navigate to:**
   ```
   http://localhost:5000
   ```

3. **Login and view a payslip:**
   - Go to Payroll → Payroll List
   - Click "View Payslip" on any record
   - Verify the new design appears

4. **Test print functionality:**
   - Click "Print / Save PDF" button
   - Or press `Ctrl+P`
   - Choose "Save as PDF"
   - Verify the PDF looks professional

✅ **What to Check:**
- [ ] Company logo appears at the top
- [ ] Company name is correct (not hardcoded)
- [ ] Employee details display correctly
- [ ] Allowances breakdown shows (HRA, DA, Travel, Special)
- [ ] Deductions breakdown shows (if applicable)
- [ ] Summary section is compact
- [ ] All amounts show as S$ format
- [ ] Print preview looks good
- [ ] PDF generation works

---

## 🎯 Quick Troubleshooting

### Issue: Logo doesn't appear
**Fix:**
1. Check file exists: `Test-Path "E:/Gobi/Pro/HRMS/hrm/static/logos/company_logo.png"`
2. Check organization record: `SELECT logo_path FROM organization;`
3. Verify path is relative to `static/` (e.g., `logos/company_logo.png`, not `static/logos/company_logo.png`)

### Issue: Company name still shows "NOLTRION"
**Fix:**
1. Clear browser cache (Ctrl+Shift+R)
2. Verify template was updated: `Get-Content "E:/Gobi/Pro/HRMS/hrm/templates/payroll/payslip.html" | Select-String "organization.name"`

### Issue: Allowances not showing
**Fix:**
1. Check employee has allowances: `SELECT allowances FROM hrm_employee WHERE id = X;`
2. Verify allowances > 0

### Issue: Migration fails
**Fix:**
1. Check current version: `python -m flask db current`
2. If already applied, skip migration
3. If error persists, check database connection

---

## 📊 Sample Data (Optional)

If you need to create test data, run the SQL queries in `sample_data_setup.sql`:

```powershell
# For SQLite
sqlite3 instance/hrm.db < sample_data_setup.sql
```

---

## 📚 Documentation Files

After setup, refer to these documents for more details:

1. **PAYSLIP_IMPLEMENTATION_GUIDE.md** - Complete technical documentation
2. **MIGRATION_INSTRUCTIONS.md** - Detailed migration steps
3. **PAYSLIP_CHANGES_SUMMARY.md** - What changed and why
4. **sample_data_setup.sql** - SQL queries for testing

---

## ✅ Success Checklist

After completing all steps, verify:

- [x] Database migration applied successfully
- [x] Logos directory created
- [x] Company logo uploaded
- [x] Organization record updated with logo path
- [x] Payslip displays correctly in browser
- [x] Company logo appears on payslip
- [x] Company name is dynamic (from database)
- [x] Employee details are correct
- [x] Allowances breakdown displays
- [x] Deductions breakdown displays
- [x] Summary section is compact
- [x] Currency shows as S$
- [x] Print preview looks professional
- [x] PDF generation works
- [x] Layout fits on single A4 page

---

## 🎉 You're Done!

Your professional payslip template is now live and ready for production use!

### Next Steps:

1. **Generate payslips for all employees**
2. **Test with different scenarios:**
   - Employees with no allowances
   - Employees with no deductions
   - Employees with overtime
   - Employees with bonuses

3. **Customize if needed:**
   - Adjust allowance percentages
   - Adjust deduction percentages
   - Change colors
   - Add custom fields

4. **Train users:**
   - Show HR team how to generate payslips
   - Demonstrate print/PDF functionality
   - Explain the new layout

---

## 📞 Need Help?

If you encounter any issues:

1. Check the troubleshooting section above
2. Review the detailed documentation files
3. Check browser console for errors (F12)
4. Verify database relationships are intact
5. Test with sample data

---

## 🔄 Rollback (If Needed)

If you need to revert to the old version:

```powershell
# Rollback database migration
python -m flask db downgrade

# Restore old template (if you have a backup)
Copy-Item "templates/payroll/payslip.html.backup" -Destination "templates/payroll/payslip.html"
```

---

**Total Setup Time:** ~5 minutes  
**Difficulty:** Easy  
**Status:** Production Ready ✅

---

**Last Updated:** January 2025  
**Version:** 2.0