# Payslip Template Deployment Checklist

## 📋 Pre-Deployment Checklist

Use this checklist to ensure everything is properly set up before deploying to production.

---

## ✅ Phase 1: Database Setup

### **1.1 Apply Migration**
- [ ] Navigate to project directory: `E:/Gobi/Pro/HRMS/hrm`
- [ ] Run migration: `python -m flask db upgrade`
- [ ] Verify migration applied: `python -m flask db current`
- [ ] Expected output: `add_organization_logo (head)`

### **1.2 Verify Database Schema**
- [ ] Check organization table has `logo_path` column
- [ ] Run verification query:
  ```sql
  SELECT id, name, logo_path FROM organization;
  ```
- [ ] Confirm column exists (value can be NULL initially)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 2: File System Setup

### **2.1 Create Directories**
- [ ] Create logos directory: `New-Item -ItemType Directory -Path "static/logos" -Force`
- [ ] Verify directory exists: `Test-Path "static/logos"`
- [ ] Expected output: `True`

### **2.2 Prepare Company Logo**
- [ ] Logo file prepared (PNG, JPG, or SVG)
- [ ] Logo dimensions appropriate (recommended: 120px × 80px)
- [ ] Logo file size reasonable (< 500KB recommended)
- [ ] Logo filename decided (e.g., `company_logo.png`)

### **2.3 Upload Logo**
- [ ] Copy logo to `static/logos/` directory
- [ ] Verify file exists: `Test-Path "static/logos/company_logo.png"`
- [ ] Expected output: `True`

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 3: Database Configuration

### **3.1 Update Organization Record**
- [ ] Identify organization ID to update
- [ ] Update logo_path field
- [ ] Method used:
  - [ ] Python shell
  - [ ] SQL query
  - [ ] Admin interface

### **3.2 Verification**
- [ ] Run verification query:
  ```python
  from app import app, db
  from models import Organization
  with app.app_context():
      org = Organization.query.first()
      print(f"Name: {org.name}")
      print(f"Logo: {org.logo_path}")
  ```
- [ ] Confirm logo_path is set correctly
- [ ] Path format: `logos/company_logo.png` (relative to static/)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 4: Template Verification

### **4.1 File Integrity**
- [ ] Verify `templates/payroll/payslip.html` exists
- [ ] File size approximately 30-35 KB
- [ ] File contains 708 lines
- [ ] Check for syntax errors: `python -m py_compile templates/payroll/payslip.html`

### **4.2 Template Content**
- [ ] Company logo section present
- [ ] Dynamic company name: `{{ payroll.employee.organization.name }}`
- [ ] Dynamic logo path: `{{ payroll.employee.organization.logo_path }}`
- [ ] Allowances calculated from `employee.allowances`
- [ ] Currency filter applied: `| currency`

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 5: Data Verification

### **5.1 Check Sample Employee Data**
- [ ] At least one active employee exists
- [ ] Employee has all required fields:
  - [ ] employee_id
  - [ ] first_name, last_name
  - [ ] position
  - [ ] department
  - [ ] basic_salary
  - [ ] allowances (> 0 for testing)
  - [ ] bank_account
  - [ ] nric

### **5.2 Check Sample Payroll Data**
- [ ] At least one payroll record exists
- [ ] Payroll has all required fields:
  - [ ] employee_id (valid)
  - [ ] pay_period_start, pay_period_end
  - [ ] basic_pay
  - [ ] gross_pay
  - [ ] net_pay
  - [ ] status (Approved or Paid)

### **5.3 Run Verification Queries**
- [ ] Run queries from `sample_data_setup.sql`
- [ ] Check allowances breakdown preview
- [ ] Check deductions breakdown preview
- [ ] Verify calculations are correct

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 6: Functional Testing

### **6.1 Start Application**
- [ ] Start Flask application: `python app.py`
- [ ] Application starts without errors
- [ ] No template syntax errors in console
- [ ] Application accessible at `http://localhost:5000`

### **6.2 Login and Navigation**
- [ ] Login successful
- [ ] Navigate to Payroll → Payroll List
- [ ] Payroll list displays correctly
- [ ] "View Payslip" button visible

### **6.3 View Payslip**
- [ ] Click "View Payslip" on a record
- [ ] Payslip page loads without errors
- [ ] No JavaScript errors in console (F12)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 7: Visual Verification

### **7.1 Company Header**
- [ ] Company logo displays correctly
- [ ] Logo size is appropriate (not too large/small)
- [ ] Company name displays correctly (not "NOLTRION" unless that's your company)
- [ ] "Human Resource Management System" tagline present
- [ ] "SALARY SLIP" title present

### **7.2 Employee Details Section**
- [ ] Two-column layout displays correctly
- [ ] Left column: Employee Information
  - [ ] Employee Name
  - [ ] Employee Code
  - [ ] Department
  - [ ] Designation
- [ ] Right column: Payment Information
  - [ ] Pay Period (format: "Month Year")
  - [ ] Pay Date
  - [ ] Bank Account
  - [ ] PAN / Tax ID

### **7.3 Allowances Table**
- [ ] Green header displays
- [ ] Basic Salary shows
- [ ] Allowances breakdown shows (if employee.allowances > 0):
  - [ ] HRA (40%)
  - [ ] DA (30%)
  - [ ] Travel Allowance (20%)
  - [ ] Special Allowance (10%)
- [ ] Overtime Pay shows (if applicable)
- [ ] Performance Bonus shows (if applicable)
- [ ] Gross Salary total row displays (bold, gray background)

### **7.4 Deductions Table**
- [ ] Red header displays
- [ ] Provident Fund shows (if applicable)
- [ ] Income Tax shows (if applicable)
- [ ] Other deductions breakdown shows (if applicable):
  - [ ] Professional Tax (40%)
  - [ ] ESI Contribution (30%)
  - [ ] Insurance Premium (20%)
  - [ ] Other Deductions (10%)
- [ ] Total Deductions row displays (bold, gray background)

### **7.5 Summary Section**
- [ ] Compact table layout (not grid)
- [ ] Three rows:
  - [ ] Gross Salary
  - [ ] Total Deductions
  - [ ] NET SALARY (dark background, white text, bold)
- [ ] All amounts right-aligned
- [ ] Currency format: S$ X,XXX.XX

### **7.6 Footer**
- [ ] "Computer-generated payslip" message
- [ ] Generated date and time
- [ ] Generated by user name
- [ ] HR contact message
- [ ] Bank payment message (if bank_name exists)

### **7.7 Currency Formatting**
- [ ] All amounts show as: S$ X,XXX.XX
- [ ] Two decimal places
- [ ] Comma-separated thousands
- [ ] Right-aligned in tables
- [ ] Monospace font (Roboto Mono)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 8: Print Testing

### **8.1 Print Preview**
- [ ] Click "Print / Save PDF" button (or Ctrl+P)
- [ ] Print preview opens
- [ ] Action buttons hidden in preview
- [ ] Layout fits on single page
- [ ] No content cut off

### **8.2 Color Verification**
- [ ] Company logo displays in color
- [ ] Green header for Allowances
- [ ] Red header for Deductions
- [ ] Dark background for Net Salary row
- [ ] Alternating row colors visible

### **8.3 PDF Generation**
- [ ] Choose "Save as PDF" in print dialog
- [ ] PDF generates successfully
- [ ] Open PDF and verify:
  - [ ] All content visible
  - [ ] Colors preserved
  - [ ] Logo displays
  - [ ] Text is readable
  - [ ] Layout is professional
  - [ ] Fits on single A4 page

### **8.4 Black & White Test**
- [ ] Print preview in B/W mode
- [ ] Content still readable
- [ ] Borders and lines visible
- [ ] Text contrast sufficient

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 9: Responsive Testing

### **9.1 Desktop View (> 768px)**
- [ ] Two-column employee details
- [ ] Side-by-side allowances/deductions tables
- [ ] Full padding and spacing
- [ ] Company name: 28px

### **9.2 Mobile View (≤ 768px)**
- [ ] Resize browser to mobile width
- [ ] Single-column employee details
- [ ] Stacked tables (allowances above deductions)
- [ ] Reduced padding
- [ ] Company name: 22px
- [ ] All content still readable

### **9.3 Tablet View (768px - 1024px)**
- [ ] Layout adapts appropriately
- [ ] No horizontal scrolling
- [ ] Content readable

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 10: Edge Cases Testing

### **10.1 Employee with No Allowances**
- [ ] View payslip for employee with allowances = 0
- [ ] Only Basic Salary shows in Allowances table
- [ ] No HRA, DA, Travel, Special rows
- [ ] Gross Salary = Basic Salary (+ overtime + bonuses if any)

### **10.2 Employee with No Deductions**
- [ ] View payslip with all deductions = 0
- [ ] "No Deductions" row shows
- [ ] Total Deductions = S$ 0.00
- [ ] Net Salary = Gross Salary

### **10.3 Employee with Overtime**
- [ ] View payslip with overtime_pay > 0
- [ ] Overtime Pay row shows
- [ ] Overtime hours displayed
- [ ] Included in Gross Salary

### **10.4 Employee with Bonus**
- [ ] View payslip with bonuses > 0
- [ ] Performance Bonus row shows
- [ ] Included in Gross Salary

### **10.5 Missing Optional Fields**
- [ ] Employee with no bank_account
- [ ] Shows "N/A" instead of error
- [ ] Employee with no department
- [ ] Shows "N/A" instead of error

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 11: Calculation Verification

### **11.1 Allowances Breakdown**
- [ ] Calculate manually: employee.allowances × 0.40 (HRA)
- [ ] Compare with displayed value
- [ ] Verify all percentages add up to 100%
- [ ] Check rounding (2 decimal places)

### **11.2 Deductions Breakdown**
- [ ] Calculate manually: other_deductions × 0.40 (Prof Tax)
- [ ] Compare with displayed value
- [ ] Verify all percentages add up to 100%
- [ ] Check rounding (2 decimal places)

### **11.3 Gross Salary**
- [ ] Calculate: basic + overtime + allowances + bonuses
- [ ] Compare with displayed Gross Salary
- [ ] Verify matches payroll.gross_pay

### **11.4 Total Deductions**
- [ ] Calculate: employee_cpf + income_tax + other_deductions
- [ ] Compare with displayed Total Deductions
- [ ] Verify calculation is correct

### **11.5 Net Salary**
- [ ] Calculate: gross_pay - total_deductions
- [ ] Compare with displayed Net Salary
- [ ] Verify matches payroll.net_pay

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 12: Performance Testing

### **12.1 Page Load Time**
- [ ] Measure page load time (should be < 500ms)
- [ ] Check for slow database queries
- [ ] Verify logo loads quickly

### **12.2 Multiple Payslips**
- [ ] View 5-10 different payslips
- [ ] All load correctly
- [ ] No performance degradation

### **12.3 Browser Compatibility**
- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Edge
- [ ] Test in Safari (if available)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 13: Security Testing

### **13.1 Access Control**
- [ ] Login as Employee
- [ ] Can view own payslip
- [ ] Cannot view other employees' payslips (403 error)

- [ ] Login as Manager
- [ ] Can view direct reports' payslips
- [ ] Cannot view other employees' payslips (403 error)

- [ ] Login as Admin
- [ ] Can view all payslips

### **13.2 Data Privacy**
- [ ] Sensitive data (bank account, tax ID) only visible to authorized users
- [ ] No data leakage in URLs
- [ ] No sensitive data in browser console

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 14: Documentation Review

### **14.1 Documentation Files**
- [ ] QUICK_START_GUIDE.md reviewed
- [ ] PAYSLIP_IMPLEMENTATION_GUIDE.md reviewed
- [ ] MIGRATION_INSTRUCTIONS.md reviewed
- [ ] PAYSLIP_CHANGES_SUMMARY.md reviewed
- [ ] PAYSLIP_LAYOUT_DIAGRAM.txt reviewed
- [ ] README_PAYSLIP.md reviewed
- [ ] sample_data_setup.sql reviewed

### **14.2 Code Comments**
- [ ] Template has clear comments
- [ ] CSS sections are labeled
- [ ] Jinja2 logic is documented

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 15: User Acceptance Testing

### **15.1 HR Team Review**
- [ ] HR team views sample payslips
- [ ] Layout approved
- [ ] All required information present
- [ ] Professional appearance confirmed

### **15.2 Employee Feedback**
- [ ] Sample employees view their payslips
- [ ] Information is clear and understandable
- [ ] No confusion about breakdown

### **15.3 Management Approval**
- [ ] Management reviews payslip design
- [ ] Approves for production use

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 16: Production Deployment

### **16.1 Backup**
- [ ] Backup current database
- [ ] Backup current template files
- [ ] Backup location documented

### **16.2 Deployment**
- [ ] Apply migration on production database
- [ ] Upload new template file
- [ ] Upload logo file
- [ ] Update organization record

### **16.3 Post-Deployment Verification**
- [ ] Test payslip generation on production
- [ ] Verify logo displays
- [ ] Verify all data correct
- [ ] Test print functionality

### **16.4 Rollback Plan**
- [ ] Rollback procedure documented
- [ ] Backup files accessible
- [ ] Rollback tested (if possible)

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 17: Training & Communication

### **17.1 User Training**
- [ ] HR team trained on new payslip
- [ ] Managers informed of changes
- [ ] Employees notified of new format

### **17.2 Documentation Distribution**
- [ ] Quick Start Guide shared with HR
- [ ] Troubleshooting guide available
- [ ] Support contact information provided

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## ✅ Phase 18: Monitoring

### **18.1 First Week Monitoring**
- [ ] Monitor for errors in logs
- [ ] Check for user complaints
- [ ] Verify payslips generating correctly

### **18.2 Feedback Collection**
- [ ] Collect feedback from HR team
- [ ] Collect feedback from employees
- [ ] Document any issues

### **18.3 Issue Resolution**
- [ ] Address any reported issues
- [ ] Apply fixes if needed
- [ ] Update documentation if needed

**Status:** ⬜ Not Started | ⏳ In Progress | ✅ Complete

---

## 📊 Final Sign-Off

### **Deployment Summary**
- **Deployment Date:** _______________
- **Deployed By:** _______________
- **Version:** 2.0
- **Status:** ⬜ Success | ⬜ Issues Found | ⬜ Rolled Back

### **Sign-Off**
- [ ] Technical Lead Approval: _______________
- [ ] HR Manager Approval: _______________
- [ ] IT Manager Approval: _______________

### **Notes**
```
_________________________________________________________________

_________________________________________________________________

_________________________________________________________________
```

---

## 🎉 Deployment Complete!

Congratulations! Your professional payslip template is now live in production.

**Next Steps:**
1. Monitor for the first week
2. Collect user feedback
3. Make adjustments if needed
4. Document lessons learned

---

**Checklist Version:** 1.0  
**Last Updated:** January 2025  
**Total Phases:** 18  
**Total Checkpoints:** 200+

---

**Status Legend:**
- ⬜ Not Started
- ⏳ In Progress
- ✅ Complete
- ❌ Failed
- ⚠️ Issues Found