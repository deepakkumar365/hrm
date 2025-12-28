"""
Routes for Employee Bulk Upload functionality
Requirement: EMP-BULK-001, EMP-BULK-002, EMP-BULK-003
"""
from flask import render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import current_user
from datetime import datetime
import io
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from werkzeug.utils import secure_filename
import os
import time as pytime

from app import app, db
from core.auth import require_login, require_role
from core.models import Employee, User, Role, Department, WorkingHours, WorkSchedule, Company
from core.utils import parse_date, validate_nric, generate_employee_id
from core.constants import DEFAULT_USER_PASSWORD


@app.route('/employees/bulk-upload')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def employee_bulk_upload():
    """Employee Bulk Upload page with download template and upload options"""
    return render_template('employees/bulk_upload.html')


@app.route('/employees/bulk-upload/download-template')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def download_employee_template():
    """Download Excel template for bulk employee upload"""
    
    # Create a new workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Employee Template"
    
    # Define headers with mandatory field indicators
    headers = [
        ('Employee ID*', 'Auto-generated if left blank'),
        ('First Name*', 'Required'),
        ('Last Name*', 'Required'),
        ('Email*', 'Required - must be unique'),
        ('Phone', 'Optional'),
        ('NRIC/Passport*', 'Required - must be unique (e.g., S1234567D)'),
        ('Date of Birth', 'Format: YYYY-MM-DD (e.g., 1990-01-15)'),
        ('Gender', 'Male/Female'),
        ('Nationality', 'e.g., Singaporean, Malaysian, Indian'),
        ('Address', 'Full address'),
        ('Postal Code', 'e.g., 123456'),
        ('Company Code*', 'Required - Company code from system'),
        ('User Role*', 'Required - Super Admin/Admin/HR Manager/Manager/User'),
        ('Department', 'Department name'),
        ('Manager Employee ID', 'Employee ID of reporting manager'),
        ('Hire Date*', 'Required - Format: YYYY-MM-DD'),
        ('Employment Type*', 'Required - Full-time/Part-time/Contract/Intern'),
        ('Work Permit Type*', 'Required - Citizen/PR/Work Permit/S Pass/Employment Pass'),
        ('Work Permit Expiry', 'Format: YYYY-MM-DD (leave blank for Citizen/PR)'),
        ('Basic Salary*', 'Required - Monthly salary in SGD'),
        ('Allowances', 'Monthly allowances in SGD (default: 0)'),
        ('Hourly Rate', 'Hourly rate for overtime calculation'),
        ('Employee CPF Rate', 'Percentage (default: 20.00)'),
        ('Employer CPF Rate', 'Percentage (default: 17.00)'),
        ('CPF Account', 'CPF account number'),
        ('Bank Name', 'e.g., DBS, OCBC, UOB'),
        ('Bank Account', 'Bank account number'),
        ('Account Holder Name', 'Name as per bank account'),
        ('Working Hours Name', 'Working hours configuration name'),
        ('Work Schedule Name', 'Work schedule name'),
    ]
    
    # Style definitions
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    mandatory_fill = PatternFill(start_color="FFE699", end_color="FFE699", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    # Write headers
    for col_num, (header, description) in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = border
        
        # Highlight mandatory fields
        if '*' in header:
            cell.fill = mandatory_fill
            cell.font = Font(bold=True, color="000000", size=11)
        else:
            cell.fill = header_fill
        
        # Write description in row 2
        desc_cell = ws.cell(row=2, column=col_num)
        desc_cell.value = description
        desc_cell.font = Font(italic=True, size=9, color="666666")
        desc_cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        desc_cell.border = border
        
        # Set column width
        ws.column_dimensions[get_column_letter(col_num)].width = 20
    
    # Set row heights
    ws.row_dimensions[1].height = 30
    ws.row_dimensions[2].height = 40
    
    # Add sample data row
    sample_data = [
        'EMP001',  # Employee ID
        'John',  # First Name
        'Doe',  # Last Name
        'john.doe@example.com',  # Email
        '+65 9123 4567',  # Phone
        'S1234567D',  # NRIC
        '1990-01-15',  # DOB
        'Male',  # Gender
        'Singaporean',  # Nationality
        '123 Main Street, Singapore',  # Address
        '123456',  # Postal Code
        'COMP001',  # Company Code
        'User',  # User Role
        'Engineering',  # Department
        'EMP000',  # Manager Employee ID
        '2024-01-01',  # Hire Date
        'Full-time',  # Employment Type
        'Citizen',  # Work Permit Type
        '',  # Work Permit Expiry
        '5000.00',  # Basic Salary
        '500.00',  # Allowances
        '30.00',  # Hourly Rate
        '20.00',  # Employee CPF Rate
        '17.00',  # Employer CPF Rate
        '',  # CPF Account
        'DBS',  # Bank Name
        '1234567890',  # Bank Account
        'John Doe',  # Account Holder Name
        'Standard Hours',  # Working Hours
        'Day Shift',  # Work Schedule
    ]
    
    for col_num, value in enumerate(sample_data, 1):
        cell = ws.cell(row=3, column=col_num)
        cell.value = value
        cell.font = Font(italic=True, color="999999")
        cell.border = border
    
    # Add instructions sheet
    ws_instructions = wb.create_sheet("Instructions")
    instructions = [
        ["Employee Bulk Upload Instructions", ""],
        ["", ""],
        ["Step 1:", "Download this template"],
        ["Step 2:", "Fill in employee data starting from row 3 (row 1 is headers, row 2 is descriptions)"],
        ["Step 3:", "Fields marked with * are mandatory"],
        ["Step 4:", "Mandatory fields are highlighted in YELLOW"],
        ["Step 5:", "Follow the date format: YYYY-MM-DD (e.g., 2024-01-15)"],
        ["Step 6:", "Employee ID will be auto-generated if left blank"],
        ["Step 7:", "Email and NRIC must be unique across all employees"],
        ["Step 8:", "Save the file and upload it using the 'Upload Excel' button"],
        ["", ""],
        ["Important Notes:", ""],
        ["", "• Company Code must exist in the system"],
        ["", "• User Role must be one of: Super Admin, Admin, HR Manager, Manager, User"],
        ["", "• Employment Type: Full-time, Part-time, Contract, or Intern"],
        ["", "• Work Permit Type: Citizen, PR, Work Permit, S Pass, or Employment Pass"],
        ["", "• All monetary values should be in SGD"],
        ["", "• CPF rates are in percentage (e.g., 20.00 for 20%)"],
        ["", "• Manager Employee ID should be an existing employee's ID"],
        ["", ""],
        ["For any issues, contact your system administrator.", ""],
    ]
    
    for row_num, (col1, col2) in enumerate(instructions, 1):
        ws_instructions.cell(row=row_num, column=1).value = col1
        ws_instructions.cell(row=row_num, column=2).value = col2
        if row_num == 1:
            ws_instructions.cell(row=row_num, column=1).font = Font(bold=True, size=14, color="4472C4")
        elif "Step" in col1 or "Important" in col1:
            ws_instructions.cell(row=row_num, column=1).font = Font(bold=True, size=11)
    
    ws_instructions.column_dimensions['A'].width = 30
    ws_instructions.column_dimensions['B'].width = 60
    
    # Save to BytesIO
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    
    # Generate filename with timestamp
    filename = f"Employee_Bulk_Upload_Template_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=filename
    )


@app.route('/employees/bulk-upload/upload', methods=['POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def upload_employee_excel():
    """Process uploaded Excel file and create employees"""
    
    if 'excel_file' not in request.files:
        flash('No file uploaded', 'error')
        return redirect(url_for('employee_bulk_upload'))
    
    file = request.files['excel_file']
    
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('employee_bulk_upload'))
    
    if not file.filename.endswith(('.xlsx', '.xls')):
        flash('Invalid file format. Please upload an Excel file (.xlsx or .xls)', 'error')
        return redirect(url_for('employee_bulk_upload'))
    
    try:
        # Read Excel file
        wb = openpyxl.load_workbook(file, data_only=True)
        ws = wb.active
        
        # Skip header rows (row 1 and 2)
        rows = list(ws.iter_rows(min_row=3, values_only=True))
        
        if not rows:
            flash('No data found in the Excel file', 'error')
            return redirect(url_for('employee_bulk_upload'))
        
        success_count = 0
        error_count = 0
        errors = []
        
        for row_num, row in enumerate(rows, start=3):
            # Skip empty rows
            if not any(row):
                continue
            
            try:
                # Extract data from row
                employee_id = row[0] if row[0] else generate_employee_id()
                first_name = row[1]
                last_name = row[2]
                email = row[3]
                phone = row[4] if len(row) > 4 else None
                nric = row[5] if len(row) > 5 else None
                date_of_birth = row[6] if len(row) > 6 else None
                gender = row[7] if len(row) > 7 else None
                nationality = row[8] if len(row) > 8 else None
                address = row[9] if len(row) > 9 else None
                postal_code = row[10] if len(row) > 10 else None
                company_code = row[11] if len(row) > 11 else None
                user_role_name = row[12] if len(row) > 12 else 'User'
                department = str(row[13]).strip() if len(row) > 13 and row[13] else None
                manager_employee_id = row[14] if len(row) > 14 else None
                hire_date = row[15] if len(row) > 15 else None
                employment_type = row[16] if len(row) > 16 else None
                work_permit_type = row[17] if len(row) > 17 else None
                work_permit_expiry = row[18] if len(row) > 18 else None
                basic_salary = row[19] if len(row) > 19 else None
                allowances = row[20] if len(row) > 20 else 0
                hourly_rate = row[21] if len(row) > 21 else None
                employee_cpf_rate = row[22] if len(row) > 22 else 20.00
                employer_cpf_rate = row[23] if len(row) > 23 else 17.00
                cpf_account = row[24] if len(row) > 24 else None
                bank_name = row[25] if len(row) > 25 else None
                bank_account = row[26] if len(row) > 26 else None
                account_holder_name = row[27] if len(row) > 27 else None
                working_hours_name = row[28] if len(row) > 28 else None
                work_schedule_name = row[29] if len(row) > 29 else None
                
                # Validate mandatory fields
                if not all([first_name, last_name, email, nric, company_code, hire_date, employment_type, work_permit_type, basic_salary]):
                    errors.append(f"Row {row_num}: Missing mandatory fields")
                    error_count += 1
                    continue
                
                # Check if employee already exists
                if Employee.query.filter_by(employee_id=employee_id).first():
                    errors.append(f"Row {row_num}: Employee ID {employee_id} already exists")
                    error_count += 1
                    continue
                
                if Employee.query.filter_by(email=email).first():
                    errors.append(f"Row {row_num}: Email {email} already exists")
                    error_count += 1
                    continue
                
                if Employee.query.filter_by(nric=nric).first():
                    errors.append(f"Row {row_num}: NRIC {nric} already exists")
                    error_count += 1
                    continue
                
                # Get company
                company = Company.query.filter_by(code=company_code).first()
                if not company:
                    errors.append(f"Row {row_num}: Company code {company_code} not found")
                    error_count += 1
                    continue
                
                # Get user role
                user_role = Role.query.filter_by(name=user_role_name).first()
                if not user_role:
                    errors.append(f"Row {row_num}: User role {user_role_name} not found")
                    error_count += 1
                    continue
                
                # Get manager if specified
                manager_id = None
                if manager_employee_id:
                    manager = Employee.query.filter_by(employee_id=manager_employee_id).first()
                    if manager:
                        manager_id = manager.id
                    else:
                        errors.append(f"Row {row_num}: Warning - Manager {manager_employee_id} not found, skipping manager assignment")
                
                # Get working hours if specified
                working_hours_id = None
                if working_hours_name:
                    working_hours = WorkingHours.query.filter_by(name=working_hours_name).first()
                    if working_hours:
                        working_hours_id = working_hours.id
                
                # Get work schedule if specified
                work_schedule_id = None
                if work_schedule_name:
                    work_schedule = WorkSchedule.query.filter_by(name=work_schedule_name).first()
                    if work_schedule:
                        work_schedule_id = work_schedule.id
                
                # Parse dates
                if isinstance(date_of_birth, str):
                    date_of_birth = parse_date(date_of_birth)
                if isinstance(hire_date, str):
                    hire_date = parse_date(hire_date)
                if isinstance(work_permit_expiry, str) and work_permit_expiry:
                    work_permit_expiry = parse_date(work_permit_expiry)
                
                # Create employee
                employee = Employee(
                    employee_id=employee_id,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    phone=phone,
                    nric=nric,
                    date_of_birth=date_of_birth,
                    gender=gender,
                    nationality=nationality,
                    address=address,
                    postal_code=postal_code,
                    company_id=company.id,
                    department=department,
                    manager_id=manager_id,
                    hire_date=hire_date,
                    employment_type=employment_type,
                    work_permit_type=work_permit_type,
                    work_permit_expiry=work_permit_expiry,
                    basic_salary=float(basic_salary),
                    allowances=float(allowances) if allowances else 0,
                    hourly_rate=float(hourly_rate) if hourly_rate else None,
                    employee_cpf_rate=float(employee_cpf_rate) if employee_cpf_rate else 20.00,
                    employer_cpf_rate=float(employer_cpf_rate) if employer_cpf_rate else 17.00,
                    cpf_account=cpf_account,
                    bank_name=bank_name,
                    bank_account=bank_account,
                    account_holder_name=account_holder_name,
                    working_hours_id=working_hours_id,
                    work_schedule_id=work_schedule_id,
                    organization_id=current_user.organization_id,
                    is_active=True,
                    created_by=current_user.username
                )
                
                db.session.add(employee)
                db.session.flush()  # Get employee ID
                
                # Create user account - use employee_id as username (case sensitive)
                username = employee.employee_id
                
                # Check if username already exists
                if User.query.filter_by(username=username).first():
                    raise ValueError(f"User account with username '{username}' already exists")
                
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    organization_id=current_user.organization_id,
                    role_id=user_role.id,
                    is_active=True
                )
                user.set_password(DEFAULT_USER_PASSWORD)
                user.must_reset_password = True
                
                db.session.add(user)
                db.session.flush()
                
                # Link employee to user
                employee.user_id = user.id
                
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                error_count += 1
                db.session.rollback()
                continue
        
        # Commit all successful records
        if success_count > 0:
            db.session.commit()
            flash(f'Successfully uploaded {success_count} employee(s)', 'success')
        
        if error_count > 0:
            flash(f'{error_count} row(s) failed to upload. See errors below.', 'warning')
            for error in errors[:10]:  # Show first 10 errors
                flash(error, 'error')
            if len(errors) > 10:
                flash(f'... and {len(errors) - 10} more errors', 'error')
        
        return redirect(url_for('employee_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing Excel file: {str(e)}', 'error')
        return redirect(url_for('employee_bulk_upload'))
