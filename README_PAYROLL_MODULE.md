# Payroll Management Module

## Overview
The Payroll Management module provides comprehensive payroll processing capabilities including salary configuration, payroll generation, and payslip management.

## Features Implemented

### 1. Payroll Configuration (`/payroll/config`)
**Purpose:** Configure employee-specific salary allowances and overtime rates

**Features:**
- Grid-based employee list with inline editing
- Configure up to 4 different allowances per employee:
  - Transport Allowance
  - Housing Allowance
  - Meal Allowance
  - Other Allowance
- Set custom overtime rate per hour for each employee
- Search and filter employees
- Pagination support
- AJAX-based updates (no page reload)
- Real-time validation

**Access:** Super Admin, Admin, HR Manager

**Technical Details:**
- **Model:** `PayrollConfiguration`
- **Route:** `payroll_config()` (GET), `payroll_config_update()` (POST/AJAX)
- **Template:** `templates/payroll/config.html`
- **API Endpoint:** `/payroll/config/update` (POST JSON)

**Database Schema:**
```sql
CREATE TABLE hrm_payroll_configuration (
    id INTEGER PRIMARY KEY,
    employee_id INTEGER UNIQUE NOT NULL,
    allowance_1_name VARCHAR(100) DEFAULT 'Transport Allowance',
    allowance_1_amount NUMERIC(10,2) DEFAULT 0,
    allowance_2_name VARCHAR(100) DEFAULT 'Housing Allowance',
    allowance_2_amount NUMERIC(10,2) DEFAULT 0,
    allowance_3_name VARCHAR(100) DEFAULT 'Meal Allowance',
    allowance_3_amount NUMERIC(10,2) DEFAULT 0,
    allowance_4_name VARCHAR(100) DEFAULT 'Other Allowance',
    allowance_4_amount NUMERIC(10,2) DEFAULT 0,
    ot_rate_per_hour NUMERIC(8,2),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    updated_by INTEGER,
    FOREIGN KEY (employee_id) REFERENCES hrm_employee(id),
    FOREIGN KEY (updated_by) REFERENCES hrm_users(id)
);
```

---

### 2. Generate Payroll (`/payroll/generate`)
**Purpose:** Generate monthly payroll and payslips for employees

**Features:**
- Month and year selection
- Dynamic employee data loading with preview
- Real-time calculation of:
  - Base salary
  - Individual allowances (Transport, Housing, Meal, Other)
  - Overtime hours and amount
  - Attendance days
  - CPF deductions
  - Net salary
- Multi-employee selection with checkboxes
- Total payroll summary
- Bulk payroll generation
- Duplicate detection (skips existing payroll)

**Access:** Super Admin, Admin, HR Manager

**Technical Details:**
- **Route:** `payroll_generate()` (GET/POST)
- **Template:** `templates/payroll/generate.html`
- **API Endpoint:** `/api/payroll/preview` (GET JSON)

**Calculation Logic:**
```python
# Allowances
total_allowances = allowance_1 + allowance_2 + allowance_3 + allowance_4

# Overtime
ot_rate = config.ot_rate_per_hour or employee.hourly_rate
ot_amount = ot_hours * ot_rate

# Gross Pay
gross_pay = basic_salary + total_allowances + ot_amount

# CPF Deduction
employee_cpf = gross_pay * (employee.employee_cpf_rate / 100)
employer_cpf = gross_pay * (employer.employer_cpf_rate / 100)

# Net Pay
net_pay = gross_pay - employee_cpf
```

**Workflow:**
1. Admin selects month and year
2. Clicks "Load Employee Data"
3. System fetches all active employees
4. For each employee:
   - Retrieves payroll configuration
   - Calculates allowances from config
   - Fetches attendance records for the month
   - Calculates OT hours and amount
   - Calculates CPF deductions
   - Computes net salary
5. Admin reviews preview table
6. Selects employees to generate payroll
7. Clicks "Generate Payslips"
8. System creates Payroll records with status "Draft"

---

### 3. Payslip Viewer (`/payroll`)
**Purpose:** View and manage generated payslips

**Features:**
- List all payroll records
- Filter by month, year, and employee
- View payslip details
- Approve payroll (Admin only)
- Download payslip (future enhancement)
- Status tracking (Draft, Approved, Paid)
- Mobile-responsive design

**Access:** 
- Super Admin, Admin, HR Manager: View all payslips
- Manager: View own and team payslips
- User: View own payslips only

**Technical Details:**
- **Route:** `payroll_list()` (GET), `payroll_payslip()` (GET)
- **Template:** `templates/payroll/list.html`, `templates/payroll/payslip.html`

---

## Database Models

### PayrollConfiguration
```python
class PayrollConfiguration(db.Model):
    __tablename__ = 'hrm_payroll_configuration'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, unique=True, nullable=False)
    
    # Allowances
    allowance_1_name = db.Column(db.String(100), default='Transport Allowance')
    allowance_1_amount = db.Column(db.Numeric(10, 2), default=0)
    allowance_2_name = db.Column(db.String(100), default='Housing Allowance')
    allowance_2_amount = db.Column(db.Numeric(10, 2), default=0)
    allowance_3_name = db.Column(db.String(100), default='Meal Allowance')
    allowance_3_amount = db.Column(db.Numeric(10, 2), default=0)
    allowance_4_name = db.Column(db.String(100), default='Other Allowance')
    allowance_4_amount = db.Column(db.Numeric(10, 2), default=0)
    
    # Overtime
    ot_rate_per_hour = db.Column(db.Numeric(8, 2), nullable=True)
    
    # Audit
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = db.Column(db.Integer, db.ForeignKey('hrm_users.id'))
    
    # Relationships
    employee = db.relationship('Employee', backref='payroll_config')
    updated_by_user = db.relationship('User')
    
    def get_total_allowances(self):
        return sum([self.allowance_1_amount or 0, 
                   self.allowance_2_amount or 0,
                   self.allowance_3_amount or 0, 
                   self.allowance_4_amount or 0])
```

### Payroll (Existing - Enhanced)
```python
class Payroll(db.Model):
    __tablename__ = 'hrm_payroll'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    
    # Earnings
    basic_pay = db.Column(db.Numeric(10, 2), nullable=False)
    overtime_pay = db.Column(db.Numeric(10, 2), default=0)
    allowances = db.Column(db.Numeric(10, 2), default=0)  # Total from config
    bonuses = db.Column(db.Numeric(10, 2), default=0)
    gross_pay = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Deductions
    employee_cpf = db.Column(db.Numeric(10, 2), default=0)
    employer_cpf = db.Column(db.Numeric(10, 2), default=0)
    income_tax = db.Column(db.Numeric(10, 2), default=0)
    other_deductions = db.Column(db.Numeric(10, 2), default=0)
    
    # Net pay
    net_pay = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Work details
    days_worked = db.Column(db.Integer, default=0)
    overtime_hours = db.Column(db.Numeric(5, 2), default=0)
    leave_days = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(20), default='Draft')
    generated_by = db.Column(db.Integer)
    generated_at = db.Column(db.DateTime, default=datetime.now)
```

---

## API Endpoints

### 1. Update Payroll Configuration
**Endpoint:** `POST /payroll/config/update`

**Request Body:**
```json
{
  "employee_id": 123,
  "basic_salary": 5000.00,
  "allowance_1_amount": 200.00,
  "allowance_2_amount": 500.00,
  "allowance_3_amount": 150.00,
  "allowance_4_amount": 100.00,
  "ot_rate_per_hour": 25.00
}
```

**Response:**
```json
{
  "success": true,
  "message": "Payroll configuration updated successfully",
  "total_allowances": 950.00
}
```

### 2. Payroll Preview
**Endpoint:** `GET /api/payroll/preview?month=1&year=2025`

**Response:**
```json
{
  "success": true,
  "month": 1,
  "year": 2025,
  "employees": [
    {
      "id": 123,
      "employee_id": "EMP001",
      "name": "John Doe",
      "basic_salary": 5000.00,
      "allowance_1": 200.00,
      "allowance_2": 500.00,
      "allowance_3": 150.00,
      "allowance_4": 100.00,
      "total_allowances": 950.00,
      "ot_hours": 10.5,
      "ot_rate": 25.00,
      "ot_amount": 262.50,
      "attendance_days": 22,
      "gross_salary": 6212.50,
      "cpf_deduction": 1242.50,
      "total_deductions": 1242.50,
      "net_salary": 4970.00
    }
  ]
}
```

---

## Installation & Setup

### 1. Run Database Migration
```bash
# Create migration
flask db migrate -m "Add payroll configuration table"

# Apply migration
flask db upgrade
```

Or manually run the migration file:
```bash
python -c "from app import app, db; from models import PayrollConfiguration; app.app_context().push(); db.create_all()"
```

### 2. Initialize Payroll Configurations
The system automatically creates PayrollConfiguration records for employees when they visit the config page. Alternatively, run:

```python
from app import app, db
from models import Employee, PayrollConfiguration

with app.app_context():
    employees = Employee.query.filter_by(is_active=True).all()
    for emp in employees:
        if not emp.payroll_config:
            config = PayrollConfiguration(employee_id=emp.id)
            db.session.add(config)
    db.session.commit()
```

---

## Usage Guide

### For Administrators

#### Step 1: Configure Employee Allowances
1. Navigate to **Payroll > Payroll Configuration**
2. Search for an employee (optional)
3. Click the **Edit** button (pencil icon) for an employee
4. Update the following fields:
   - Base Salary
   - Transport Allowance
   - Housing Allowance
   - Meal Allowance
   - Other Allowance
   - OT Rate per Hour
5. Click the **Save** button (checkmark icon)
6. Repeat for other employees

#### Step 2: Generate Monthly Payroll
1. Navigate to **Payroll > Generate Payroll**
2. Select the **Month** and **Year**
3. Click **Load Employee Data**
4. Review the payroll preview table showing:
   - Base salary
   - All allowances
   - OT hours and amount
   - Attendance days
   - Deductions
   - Net salary
5. Select employees using checkboxes (or Select All)
6. Review the total payroll amount
7. Click **Generate Payslips**
8. System creates payroll records with "Draft" status

#### Step 3: Review and Approve Payroll
1. Navigate to **Payroll > Payroll List**
2. Filter by month/year if needed
3. Review payroll records
4. Click **Approve** button for each payroll (Admin only)
5. Status changes from "Draft" to "Approved"

#### Step 4: View Payslips
1. Navigate to **Payroll > Payroll List**
2. Click the **Payslip** icon for any employee
3. View detailed payslip with:
   - Employee details
   - Company details
   - Earnings breakdown
   - Deductions breakdown
   - Net pay

---

## Testing Checklist

### Payroll Configuration
- [ ] Can view list of all active employees
- [ ] Can search employees by name or ID
- [ ] Can enable edit mode for an employee
- [ ] Can update base salary
- [ ] Can update all 4 allowances
- [ ] Can update OT rate
- [ ] Can save changes via AJAX
- [ ] Can cancel edit without saving
- [ ] Changes persist after page reload
- [ ] Pagination works correctly

### Payroll Generation
- [ ] Can select month and year
- [ ] Can load employee data
- [ ] Preview shows correct calculations
- [ ] Allowances display correctly
- [ ] OT hours calculated from attendance
- [ ] OT amount calculated correctly
- [ ] CPF deductions calculated correctly
- [ ] Net salary calculated correctly
- [ ] Can select/deselect employees
- [ ] Select All works
- [ ] Total payroll updates correctly
- [ ] Can generate payroll for selected employees
- [ ] Duplicate payroll detection works
- [ ] Success message shows correct count

### Payslip Viewer
- [ ] Can view list of all payrolls
- [ ] Can filter by month
- [ ] Can filter by year
- [ ] Can filter by employee (Admin)
- [ ] Can view individual payslip
- [ ] Payslip shows correct data
- [ ] Can approve payroll (Admin)
- [ ] Status updates correctly
- [ ] Role-based access control works
- [ ] Pagination works

### Access Control
- [ ] Super Admin can access all features
- [ ] Admin can access all features
- [ ] HR Manager can access all features
- [ ] Manager can view own and team payroll
- [ ] User can view only own payslip
- [ ] Unauthorized access returns 403

---

## Future Enhancements

1. **PDF Generation**
   - Generate payslip PDFs
   - Bulk PDF download
   - Email payslips to employees

2. **Advanced Deductions**
   - Loan deductions
   - Advance salary deductions
   - Custom deduction types

3. **Bonus Management**
   - Performance bonuses
   - Festival bonuses
   - One-time payments

4. **Payroll Reports**
   - Monthly payroll summary
   - Department-wise payroll
   - Year-to-date reports
   - Tax reports

5. **Bank Integration**
   - Generate bank transfer files
   - GIRO file generation
   - Payment tracking

6. **Employee Self-Service**
   - View own payslips
   - Download payslip history
   - View YTD earnings

7. **Audit Trail**
   - Track all payroll changes
   - View modification history
   - Compliance reporting

---

## Troubleshooting

### Issue: Payroll configuration not saving
**Solution:** Check browser console for JavaScript errors. Ensure AJAX endpoint is accessible.

### Issue: OT hours not calculating
**Solution:** Verify attendance records exist for the selected month. Check that overtime_hours field is populated in attendance records.

### Issue: CPF deduction incorrect
**Solution:** Verify employee CPF rates are set correctly in employee profile. Check employee.employee_cpf_rate and employee.employer_cpf_rate fields.

### Issue: Allowances not showing in payslip
**Solution:** Ensure PayrollConfiguration record exists for the employee. Check that allowance amounts are greater than 0.

### Issue: Cannot generate payroll
**Solution:** Check that employees are selected. Verify month and year are valid. Check for existing payroll records for the same period.

---

## Support

For issues or questions, contact the development team or refer to the main HRMS documentation.

---

**Last Updated:** January 22, 2025
**Version:** 1.0.0
**Module:** Payroll Management