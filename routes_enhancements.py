"""
New routes for HRMS enhancements
- Employee Edit
- Password Reset
- Reports Module
- Bank Info Management
- Payroll Configuration Enhancements
"""

from flask import request, redirect, url_for, flash, jsonify, render_template, send_file
from flask_login import current_user
from datetime import datetime, date
from sqlalchemy import func, extract, and_
import io
import csv
from werkzeug.utils import secure_filename
import os
import time as pytime

from app import app, db
from auth import require_login, require_role
from models import (Employee, User, Role, Department, WorkingHours, WorkSchedule,
                    Company, PayrollConfiguration, EmployeeBankInfo, Payroll, Attendance, Leave)
from utils import (parse_date, validate_nric, format_currency, format_date, export_to_csv)
from constants import DEFAULT_USER_PASSWORD


# =====================================================
# EMPLOYEE EDIT ROUTE
# =====================================================
# NOTE: The employee_edit route is defined in routes.py
# This duplicate has been removed to avoid route conflicts.
# The routes.py version includes user role management functionality.


# Helper function for image validation
def _allowed_image(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in app.config.get('ALLOWED_IMAGE_EXTENSIONS', {'jpg', 'jpeg', 'png', 'gif'})


# =====================================================
# PASSWORD RESET ROUTE
# =====================================================

@app.route('/employees/<int:employee_id>/reset-password', methods=['POST'])
@require_role(['Super Admin', 'Tenant Admin'])
def employee_reset_password(employee_id):
    """Reset employee password"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        if not employee.user_id:
            return jsonify({'success': False, 'message': 'Employee has no user account'}), 400
        
        user = User.query.get(employee.user_id)
        if not user:
            return jsonify({'success': False, 'message': 'User account not found'}), 404
        
        # Reset to default password
        user.set_password(DEFAULT_USER_PASSWORD)
        user.must_reset_password = True
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Password reset successfully. New password: {DEFAULT_USER_PASSWORD}',
            'username': user.username,
            'temp_password': DEFAULT_USER_PASSWORD
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# REPORTS MODULE
# =====================================================

@app.route('/reports')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def reports_menu():
    """Reports landing page"""
    return render_template('reports/menu.html')


@app.route('/reports/employee-history')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def report_employee_history():
    """Employee History Report"""
    try:
        # Get current user's organization and company for tenant filtering
        user_org = current_user.organization
        if not user_org:
            flash('No organization assigned to your account. Please contact administrator.', 'warning')
            return render_template('reports/employee_history.html', employees=[])
        
        # Get company associated with this organization's tenant
        company = None
        if user_org.tenant_id:
            company = Company.query.filter_by(tenant_id=user_org.tenant_id).first()
        
        if not company:
            flash('No company found for your organization. Please contact administrator.', 'warning')
            return render_template('reports/employee_history.html', employees=[])
        
        # Filter employees by company
        employees = Employee.query.filter_by(
            company_id=company.id,
            is_active=True
        ).order_by(Employee.hire_date.desc()).all()
        
        # Export if requested
        if request.args.get('export') == 'csv':
            # Prepare data for CSV export
            report_data = []
            for emp in employees:
                report_data.append({
                    'employee_id': emp.employee_id,
                    'name': f"{emp.first_name} {emp.last_name}",
                    'email': emp.email,
                    'designation': emp.designation.name if emp.designation else '',
                    'department': emp.department,
                    'hire_date': emp.hire_date,
                    'exit_date': emp.termination_date,
                    'manager': f"{emp.manager.first_name} {emp.manager.last_name}" if emp.manager else 'N/A',
                    'status': 'Active' if emp.is_active else 'Inactive'
                })
            return export_employee_history_csv(report_data)
        
        # Pass actual Employee objects to template
        return render_template('reports/employee_history.html', employees=employees)
    
    except Exception as e:
        print(f"[ERROR] Employee History Report: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading employee history report: {str(e)}', 'error')
        return render_template('reports/employee_history.html', employees=[])


@app.route('/reports/payroll-configuration')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def report_payroll_configuration():
    """Payroll Configuration Report"""
    try:
        # Get current user's organization and company for tenant filtering
        user_org = current_user.organization
        if not user_org:
            flash('No organization assigned to your account. Please contact administrator.', 'warning')
            return render_template('reports/payroll_configuration.html', configs=[])
        
        # Get company associated with this organization's tenant
        company = None
        if user_org.tenant_id:
            company = Company.query.filter_by(tenant_id=user_org.tenant_id).first()
        
        if not company:
            flash('No company found for your organization. Please contact administrator.', 'warning')
            return render_template('reports/payroll_configuration.html', configs=[])
        
        # Filter by company
        configs = PayrollConfiguration.query.join(Employee).filter(
            Employee.company_id == company.id,
            Employee.is_active == True
        ).all()
        
        report_data = []
        for config in configs:
            emp = config.employee
            report_data.append({
                'employee_id': emp.employee_id,
                'name': f"{emp.first_name} {emp.last_name}",
                'basic_salary': emp.basic_salary,
                'allowance_1': f"{config.allowance_1_name}: {config.allowance_1_amount}",
                'allowance_2': f"{config.allowance_2_name}: {config.allowance_2_amount}",
                'allowance_3': f"{config.allowance_3_name}: {config.allowance_3_amount}",
                'allowance_4': f"{config.allowance_4_name}: {config.allowance_4_amount}",
                'employer_cpf': config.employer_cpf,
                'employee_cpf': config.employee_cpf,
                'net_salary': config.net_salary,
                'ot_rate': config.ot_rate_per_hour,
                'remarks': config.remarks
            })
        
        # Export if requested
        if request.args.get('export') == 'csv':
            return export_payroll_config_csv(report_data)
        
        return render_template('reports/payroll_configuration.html', configs=report_data)
    
    except Exception as e:
        print(f"[ERROR] Payroll Configuration Report: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading payroll configuration report: {str(e)}', 'error')
        return render_template('reports/payroll_configuration.html', configs=[])


@app.route('/reports/attendance')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def report_attendance():
    """Attendance Report"""
    try:
        # Get current user's organization and company for tenant filtering
        user_org = current_user.organization
        if not user_org:
            flash('No organization assigned to your account. Please contact administrator.', 'warning')
            return render_template('reports/attendance.html', attendance=[], 
                                 start_date=date.today(), end_date=date.today())
        
        # Get company associated with this organization's tenant
        company = None
        if user_org.tenant_id:
            company = Company.query.filter_by(tenant_id=user_org.tenant_id).first()
        
        if not company:
            flash('No company found for your organization. Please contact administrator.', 'warning')
            return render_template('reports/attendance.html', attendance=[], 
                                 start_date=date.today(), end_date=date.today())
        
        # Get date range from query params
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date or not end_date:
            # Default to current month
            today = date.today()
            start_date = date(today.year, today.month, 1)
            end_date = today
        else:
            start_date = parse_date(start_date)
            end_date = parse_date(end_date)
        
        # Filter by company
        attendance_records = Attendance.query.join(Employee).filter(
            Employee.company_id == company.id,
            Attendance.date.between(start_date, end_date),
            Employee.is_active == True
        ).order_by(Attendance.date.desc()).all()
        
        report_data = []
        for record in attendance_records:
            emp = record.employee
            report_data.append({
                'employee_id': emp.employee_id,
                'name': f"{emp.first_name} {emp.last_name}",
                'date': record.date,
                'clock_in': record.clock_in,
                'clock_out': record.clock_out,
                'regular_hours': record.regular_hours,
                'overtime_hours': record.overtime_hours,
                'total_hours': record.total_hours,
                'status': record.status
            })
        
        # Export if requested
        if request.args.get('export') == 'csv':
            return export_attendance_csv(report_data)
        
        return render_template('reports/attendance.html', 
                               attendance=report_data,
                               start_date=start_date,
                               end_date=end_date)
    
    except Exception as e:
        print(f"[ERROR] Attendance Report: {str(e)}")
        import traceback
        traceback.print_exc()
        flash(f'Error loading attendance report: {str(e)}', 'error')
        return render_template('reports/attendance.html', attendance=[], 
                             start_date=date.today(), end_date=date.today())


# Export helper functions
def export_employee_history_csv(data):
    """Export employee history to CSV"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'employee_history_{date.today()}.csv'
    )


def export_payroll_config_csv(data):
    """Export payroll configuration to CSV"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'payroll_configuration_{date.today()}.csv'
    )


def export_attendance_csv(data):
    """Export attendance to CSV"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'attendance_report_{date.today()}.csv'
    )


# =====================================================
# BANK INFO MANAGEMENT
# =====================================================

@app.route('/employees/<int:employee_id>/bank-info', methods=['GET'])
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def get_bank_info(employee_id):
    """Get employee bank information"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        bank_info = EmployeeBankInfo.query.filter_by(employee_id=employee_id).first()
        
        if bank_info:
            return jsonify({
                'success': True,
                'data': {
                    'bank_account_name': bank_info.bank_account_name,
                    'bank_account_number': bank_info.bank_account_number,
                    'bank_code': bank_info.bank_code,
                    'paynow_no': bank_info.paynow_no
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'bank_account_name': '',
                    'bank_account_number': '',
                    'bank_code': '',
                    'paynow_no': ''
                }
            })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/employees/<int:employee_id>/bank-info', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def save_bank_info(employee_id):
    """Save or update employee bank information"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        data = request.get_json()
        bank_info = EmployeeBankInfo.query.filter_by(employee_id=employee_id).first()
        
        if not bank_info:
            bank_info = EmployeeBankInfo(employee_id=employee_id)
            db.session.add(bank_info)
        
        bank_info.bank_account_name = data.get('bank_account_name')
        bank_info.bank_account_number = data.get('bank_account_number')
        bank_info.bank_code = data.get('bank_code')
        bank_info.paynow_no = data.get('paynow_no')
        bank_info.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Bank information saved successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# PAYROLL CONFIGURATION ENHANCEMENTS
# =====================================================

@app.route('/payroll/configuration/<int:config_id>/update', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def update_payroll_config(config_id):
    """Update payroll configuration with new CPF and net salary fields"""
    try:
        config = PayrollConfiguration.query.get_or_404(config_id)
        
        data = request.get_json()
        
        # Update CPF fields
        if 'employer_cpf' in data:
            config.employer_cpf = float(data['employer_cpf'])
        if 'employee_cpf' in data:
            config.employee_cpf = float(data['employee_cpf'])
        if 'net_salary' in data:
            config.net_salary = float(data['net_salary'])
        if 'remarks' in data:
            config.remarks = data['remarks']
        
        config.updated_at = datetime.now()
        config.updated_by = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payroll configuration updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# =====================================================
# EMPLOYEE ID GENERATION
# =====================================================

@app.route('/employees/generate-id', methods=['GET'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager', 'Admin'])
def generate_new_employee_id():
    """
    Generate a new unique employee ID in format: <CompanyCode><NextID>
    
    Query parameters:
        company_id: UUID of the company to generate ID for
    
    Returns:
        JSON with generated employee_id or error message
    """
    try:
        from utils import generate_employee_id
        from sqlalchemy import func
        
        company_id = request.args.get('company_id')
        
        if not company_id:
            return jsonify({
                'success': False,
                'message': 'Company ID is required'
            }), 400
        
        # Get the company
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'message': 'Company not found'
            }), 404
        
        # Get the next employee ID (max existing ID + 1)
        max_employee_id = db.session.query(func.max(Employee.id)).scalar() or 0
        next_employee_id = max_employee_id + 1
        
        # Generate formatted employee ID: CompanyCode + ID with zero-padding
        new_id = generate_employee_id(
            company_code=company.code,
            employee_db_id=next_employee_id
        )
        
        return jsonify({
            'success': True,
            'employee_id': new_id,
            'company_code': company.code,
            'next_id': next_employee_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500