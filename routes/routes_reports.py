
from flask import render_template, request, jsonify, send_file
from flask_login import login_required, current_user
from app import app, db
from core.models import Attendance, Employee, AuditLog, Department
from datetime import datetime, date, timedelta
import calendar
from sqlalchemy import func
import io
import csv

# -------------------------------------------------------------------------
# Monthly Attendance Register
# -------------------------------------------------------------------------

@app.route('/reports/attendance-register', methods=['GET'])
@login_required
def report_attendance_register():
    """Monthly Attendance Register (Grid View)"""
    # 1. Filters
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    department = request.args.get('department', '')
    
    # 2. Date Range
    _, last_day = calendar.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)
    
    # Generate list of days for header
    days_in_month = []
    current = start_date
    while current <= end_date:
        days_in_month.append(current)
        current += timedelta(days=1)
        
    # 3. Fetch Employees
    emp_query = Employee.query.filter_by(is_active=True)
    if department:
        emp_query = emp_query.filter(Employee.department == department)
        
    # Role based filtering
    if current_user.role.name == 'Manager':
        # Direct reports
        if current_user.employee_profile:
             emp_query = emp_query.filter(Employee.manager_id == current_user.employee_profile.id)
    elif current_user.role.name not in ['Super Admin', 'Admin', 'HR Manager', 'Tenant Admin']:
         # Regular employee should not see this or only see themselves? 
         # Usually reports are for mgmt. Let's restrict to own if employee.
         if current_user.employee_profile:
             emp_query = emp_query.filter(Employee.id == current_user.employee_profile.id)
             
    employees = emp_query.order_by(Employee.first_name).all()
    emp_ids = [e.id for e in employees]
    
    # 4. Fetch Attendance Map
    attendance_records = Attendance.query.filter(
        Attendance.date.between(start_date, end_date),
        Attendance.employee_id.in_(emp_ids)
    ).all()
    
    # key: (emp_id, day_int) -> status_code
    # Status Codes: P=Present, A=Absent, L=Leave, H=Holiday, WO=Weekly Off, HD=Half Day
    attendance_map = {}
    
    def get_status_code(status):
        if not status: return '-'
        if status == 'Present': return 'P'
        if status == 'Absent': return 'A'
        if status == 'Leave': return 'L'
        if status == 'Holiday': return 'H'
        if status == 'Weekly Off': return 'WO'
        if status == 'Half Day': return 'HD'
        if status == 'On Duty': return 'OD'
        if status == 'Incomplete': return 'INC'
        return '?'

    for record in attendance_records:
        attendance_map[(record.employee_id, record.date.day)] = {
            'code': get_status_code(record.status),
            'status': record.status, # Full status for tooltip
            'hours': record.total_hours
        }
        
    return render_template('reports/attendance_register.html',
                           employees=employees,
                           days=days_in_month,
                           month=month,
                           year=year,
                           attendance_map=attendance_map,
                           departments=[d.name for d in Department.query.all()],
                           current_department=department)


# -------------------------------------------------------------------------
# Absentee Report
# -------------------------------------------------------------------------

@app.route('/reports/absenteeism', methods=['GET'])
@login_required
def report_absenteeism():
    """List of absent employees per day"""
    target_date_str = request.args.get('date', date.today().strftime('%Y-%m-%d'))
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
    
    # Logic: Get all active employees. Check if they have attendance record for this day.
    # If no record -> likely absent (or holiday/weekend not generated yet if via script)
    # Actually, EOD process generates 'Absent' records. So we just query Attendance with status='Absent'
    
    absent_records = Attendance.query.join(Employee).filter(
        Attendance.date == target_date,
        Attendance.status == 'Absent'
    ).order_by(Employee.first_name).all()
    
    return render_template('reports/absentee_report.html', 
                           records=absent_records,
                           target_date=target_date)

# -------------------------------------------------------------------------
# Audit Logs
# -------------------------------------------------------------------------
@app.route('/reports/audit-logs', methods=['GET'])
@login_required
def report_audit_logs():
    """View System Audit Logs"""
    if current_user.role.name not in ['Super Admin', 'Admin']:
        return "Unauthorized", 403
        
    page = request.args.get('page', 1, type=int)
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(page=page, per_page=50)
    
    return render_template('reports/audit_logs.html', logs=logs)

