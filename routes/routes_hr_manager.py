"""
HR Manager Dashboard Routes
Comprehensive dashboard for HR Managers and Tenant Admins
Features: Company-wise attendance, leave, OT management, payroll
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from sqlalchemy import func, and_, extract, case
from sqlalchemy.sql.functions import concat
from datetime import datetime, date, timedelta
import calendar
from uuid import UUID
import json

from app import app, db
from core.auth import require_login, require_role
from core.models import (
    Employee, Attendance, Leave, OTAttendance, OTApproval, OTRequest, Payroll,
    Company, User, LeaveType, Department, Designation
)
from core.utils import get_current_month_dates, check_permission


def get_user_companies():
    """Get companies accessible by current user"""
    return current_user.get_accessible_companies()


def get_company_id(company_id_param=None):
    """Get company_id as UUID, handling string conversion"""
    if company_id_param:
        try:
            if isinstance(company_id_param, str):
                return UUID(company_id_param)
            return company_id_param
        except (ValueError, TypeError):
            pass
    
    # Fallback to current user's company
    if current_user.company_id:
        if isinstance(current_user.company_id, str):
            return UUID(current_user.company_id)
        return current_user.company_id
    return None


def get_attendance_stats(company_id, date_from, date_to):
    """Get attendance statistics for date range"""
    # IMPORTANT: 'Present' count includes both 'Present' and 'Late' (they are present at work, just marked late)
    attendance = db.session.query(
        func.count(Attendance.id).label('total'),
        func.sum(case(
            (Attendance.status.in_(['Present', 'Late']), 1),
            else_=0
        )).label('present'),
        func.sum(case(
            (Attendance.status == 'Absent', 1),
            else_=0
        )).label('absent'),
        func.sum(case(
            (Attendance.status == 'Late', 1),
            else_=0
        )).label('late')
    ).join(Employee, Attendance.employee_id == Employee.id).filter(
        Employee.company_id == company_id,
        Attendance.date.between(date_from, date_to)
    ).first()
    
    return {
        'total': attendance.total or 0,
        'present': attendance.present or 0,
        'absent': attendance.absent or 0,
        'late': attendance.late or 0
    }


def get_leave_stats(company_id, month_start, month_end):
    """Get leave statistics for the month"""
    leaves = db.session.query(
        Leave.leave_type,
        func.count(Leave.id).label('count')
    ).join(Employee, Leave.employee_id == Employee.id).filter(
        Employee.company_id == company_id,
        Leave.start_date >= month_start,
        Leave.end_date <= month_end,
        Leave.status == 'Approved'
    ).group_by(Leave.leave_type).all()
    
    return leaves


def get_ot_stats(company_id, date_from, date_to):
    """Get OT attendance and approval statistics"""
    # Get OT attendance stats
    ot_attendance = db.session.query(
        func.count(OTAttendance.id).label('total_ot'),
        func.sum(OTAttendance.ot_hours).label('total_hours')
    ).join(Employee, OTAttendance.employee_id == Employee.id).filter(
        Employee.company_id == company_id,
        OTAttendance.ot_date.between(date_from, date_to)
    ).first()
    
    # Get pending approvals separately
    pending_approvals = db.session.query(
        func.count(OTApproval.id)
    ).join(OTRequest, OTApproval.ot_request_id == OTRequest.id).join(
        Employee, OTRequest.employee_id == Employee.id
    ).filter(
        Employee.company_id == company_id,
        OTApproval.status == 'Pending',
        OTRequest.ot_date.between(date_from, date_to)
    ).scalar() or 0
    
    return {
        'total_ot': ot_attendance.total_ot or 0,
        'total_hours': float(ot_attendance.total_hours) if ot_attendance.total_hours else 0,
        'pending_approvals': pending_approvals
    }


def get_attendance_details(company_id, status):
    """Get detailed user list for a specific attendance status"""
    today = date.today()
    
    if status == 'not_updated':
        # Get employees who haven't updated attendance
        employees_with_attendance = db.session.query(Employee.id).join(
            Attendance, Attendance.employee_id == Employee.id
        ).filter(
            Employee.company_id == company_id,
            Attendance.date == today
        ).distinct()
        
        all_employees = db.session.query(
            Employee.id,
            Employee.employee_id,
            concat(Employee.first_name, ' ', Employee.last_name).label('name'),
            Employee.department,
            Designation.name.label('designation')
        ).outerjoin(
            Designation, Employee.designation_id == Designation.id
        ).filter(
            Employee.company_id == company_id,
            Employee.is_active == True
        )
        
        not_updated = all_employees.filter(~Employee.id.in_(employees_with_attendance)).all()
        return [{
            'name': emp.name,
            'id': emp.employee_id,
            'department': emp.department or 'N/A',
            'designation': emp.designation or 'N/A',
            'time': 'Not Updated'
        } for emp in not_updated]
    
    else:
        # Get attendance records by status
        # IMPORTANT: When requesting 'Present', also include 'Late' employees 
        # (they are present at work, just marked as late)
        query = db.session.query(
            Employee.id,
            Employee.employee_id,
            concat(Employee.first_name, ' ', Employee.last_name).label('name'),
            Employee.department,
            Designation.name.label('designation'),
            Attendance.clock_in,
            Attendance.status
        ).join(Employee, Attendance.employee_id == Employee.id).outerjoin(
            Designation, Employee.designation_id == Designation.id
        ).filter(
            Employee.company_id == company_id,
            Attendance.date == today
        )
        
        # Apply status filter with special handling for 'Present' status
        if status == 'Present':
            # Include both 'Present' and 'Late' records for the Present section
            query = query.filter(Attendance.status.in_(['Present', 'Late']))
        else:
            # For other statuses (Late, Absent), filter by exact status
            query = query.filter(Attendance.status == status)
        
        records = query.all()
        
        return [{
            'name': rec.name,
            'id': rec.employee_id,
            'department': rec.department or 'N/A',
            'designation': rec.designation or 'N/A',
            'time': rec.clock_in.strftime('%H:%M') if rec.clock_in else 'N/A'
        } for rec in records]


def get_today_summary(company_id):
    """Get today's attendance and leave summary"""
    today = date.today()
    
    # Today's attendance
    # IMPORTANT: 'Present' count includes both 'Present' and 'Late' (they are present at work, just marked late)
    today_attendance = db.session.query(
        func.count(Attendance.id).label('total'),
        func.sum(case(
            (Attendance.status.in_(['Present', 'Late']), 1),
            else_=0
        )).label('present'),
        func.sum(case(
            (Attendance.status == 'Absent', 1),
            else_=0
        )).label('absent'),
        func.sum(case(
            (Attendance.status == 'Late', 1),
            else_=0
        )).label('late')
    ).join(Employee, Attendance.employee_id == Employee.id).filter(
        Employee.company_id == company_id,
        Attendance.date == today
    ).first()
    
    # Today's leaves
    today_leaves = db.session.query(
        func.count(Leave.id).label('count')
    ).join(Employee, Leave.employee_id == Employee.id).filter(
        Employee.company_id == company_id,
        Leave.start_date <= today,
        Leave.end_date >= today,
        Leave.status == 'Approved'
    ).first()
    
    # Get not updated count
    employees_with_attendance = db.session.query(Employee.id).join(
        Attendance, Attendance.employee_id == Employee.id
    ).filter(
        Employee.company_id == company_id,
        Attendance.date == today
    ).distinct()
    
    not_updated_count = db.session.query(func.count(Employee.id)).filter(
        Employee.company_id == company_id,
        Employee.is_active == True,
        ~Employee.id.in_(employees_with_attendance)
    ).scalar() or 0
    
    # Get present details for pre-loading
    present_details = get_attendance_details(company_id, 'Present')
    
    return {
        'date': today.strftime('%A, %B %d, %Y'),
        'attendance': {
            'total': today_attendance.total or 0,
            'present': today_attendance.present or 0,
            'absent': today_attendance.absent or 0,
            'late': today_attendance.late or 0
        },
        'leaves': today_leaves.count or 0,
        'not_updated': not_updated_count,
        'present_details': present_details,
        'present_details_json': json.dumps(present_details)
    }


def get_payroll_history(company_id, months=3):
    """Get recent payroll generation history - last 3 months"""
    today = date.today()
    start_date = today.replace(day=1) - timedelta(days=months*30)
    
    payrolls = db.session.query(
        extract('year', Payroll.pay_period_start).label('year'),
        extract('month', Payroll.pay_period_start).label('month'),
        func.count(Payroll.id).label('emp_count'),
        func.sum(Payroll.net_pay).label('total_salary')
    ).join(Employee, Payroll.employee_id == Employee.id).filter(
        Employee.company_id == company_id,
        Payroll.pay_period_start >= start_date,
        Payroll.pay_period_start <= today
    ).group_by(
        extract('year', Payroll.pay_period_start),
        extract('month', Payroll.pay_period_start)
    ).order_by(
        extract('year', Payroll.pay_period_start).asc(),
        extract('month', Payroll.pay_period_start).asc()
    ).limit(3).all()
    
    return payrolls


def get_ot_pending_approvals(company_id, limit=10):
    """Get pending OT approvals for the company (Level 2 - HR Manager approval)"""
    pending = db.session.query(
        OTApproval.id,
        OTRequest.ot_date,
        func.concat(Employee.first_name, ' ', Employee.last_name).label('emp_name'),
        OTRequest.requested_hours,
        OTApproval.created_at
    ).join(OTRequest, OTApproval.ot_request_id == OTRequest.id).join(
        Employee, OTRequest.employee_id == Employee.id
    ).filter(
        Employee.company_id == company_id,
        OTApproval.approval_level == 2,
        OTApproval.status == 'pending_hr'
    ).order_by(OTApproval.created_at.desc()).limit(limit).all()
    
    return pending


@app.route('/dashboard/hr-manager', methods=['GET', 'POST'])
@require_login
def hr_manager_dashboard():
    """HR Manager Dashboard"""
    # Check permission
    if current_user.role.name not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    
    companies = get_user_companies()

    if not companies:
        flash('No companies accessible. Please contact administrator.', 'warning')
        return redirect(url_for('index'))

    # Default to user's company or first company
    selected_company_id = get_company_id(request.args.get('company_id'))
    if not selected_company_id and companies:
        selected_company_id = companies[0].id

    if not selected_company_id:
        flash('No company assigned', 'warning')
        return redirect(url_for('index'))
    
    selected_company = Company.query.get(selected_company_id)
    
    if not selected_company:
        flash('Company not found', 'danger')
        return redirect(url_for('index'))
    
    # Get current month and year
    today = date.today()
    month_start, month_end = get_current_month_dates()
    
    # Get statistics
    today_summary = get_today_summary(selected_company_id)
    
    # MTD (Month-To-Date)
    mtd_attendance = get_attendance_stats(selected_company_id, month_start, month_end)
    mtd_leaves = get_leave_stats(selected_company_id, month_start, month_end)
    mtd_ot = get_ot_stats(selected_company_id, month_start, month_end)
    
    # YTD (Year-To-Date)
    year_start = date(today.year, 1, 1)
    ytd_attendance = get_attendance_stats(selected_company_id, year_start, today)
    ytd_ot = get_ot_stats(selected_company_id, year_start, today)
    
    # Payroll history and pending OT
    payroll_history = get_payroll_history(selected_company_id)
    pending_ot_approvals = get_ot_pending_approvals(selected_company_id)
    
    # Convert payroll_history to JSON for chart
    payroll_history_json = json.dumps([
        {
            'month': int(p.month) if p.month else 0,
            'year': int(p.year) if p.year else 0,
            'emp_count': p.emp_count or 0,
            'total_salary': float(p.total_salary or 0)
        }
        for p in payroll_history
    ]) if payroll_history else '[]'
    
    context = {
        'companies': companies,
        'selected_company': selected_company,
        'today_summary': today_summary,
        'mtd_attendance': mtd_attendance,
        'mtd_leaves': mtd_leaves,
        'mtd_ot': mtd_ot,
        'ytd_attendance': ytd_attendance,
        'ytd_ot': ytd_ot,
        'payroll_history': payroll_history,
        'payroll_history_json': payroll_history_json,
        'pending_ot_approvals': pending_ot_approvals,
        'month_name': today.strftime('%B %Y')
    }
    
    return render_template('hr_manager_dashboard.html', **context)


@app.route('/api/attendance-details', methods=['GET'])
@require_login
def api_attendance_details():
    """API endpoint to get detailed attendance information for a specific status"""
    status = request.args.get('status')  # 'Present', 'Absent', 'Late', 'not_updated'
    company_id = get_company_id(request.args.get('company_id'))
    
    if not status or not company_id:
        return jsonify({'error': 'Missing status or company_id'}), 400
    
    try:
        details = get_attendance_details(company_id, status)
        return jsonify({'data': details, 'count': len(details)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/leave-details', methods=['GET'])
@require_login
def api_leave_details():
    """API endpoint to get detailed leave information for today"""
    company_id = get_company_id(request.args.get('company_id'))
    
    if not company_id:
        return jsonify({'error': 'Missing company_id'}), 400
    
    try:
        today = date.today()
        
        # Get employees on approved leaves today
        records = db.session.query(
            Employee.id,
            Employee.employee_id,
            (Employee.first_name + ' ' + Employee.last_name).label('name'),
            Employee.department,
            Designation.name.label('designation'),
            Leave.leave_type
        ).join(Employee, Leave.employee_id == Employee.id).outerjoin(
            Designation, Employee.designation_id == Designation.id
        ).filter(
            Employee.company_id == company_id,
            Leave.start_date <= today,
            Leave.end_date >= today,
            Leave.status == 'Approved'
        ).all()
        
        details = [{
            'name': rec.name,
            'id': rec.employee_id,
            'department': rec.department or 'N/A',
            'designation': rec.designation or 'N/A',
            'time': rec.leave_type or 'N/A'
        } for rec in records]
        
        return jsonify({'data': details, 'count': len(details)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/dashboard/hr-manager/ot-approval', methods=['GET'])
@require_login
def hr_manager_ot_approval():
    """OT Approval Management"""
    if current_user.role.name not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    
    company_id = get_company_id(request.args.get('company_id'))
    if not company_id:
        flash('No company assigned', 'danger')
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    
    # Get pending OT approvals with pagination (OTApproval -> OTRequest -> Employee)
    approvals = OTApproval.query.filter_by(status='Pending').join(
        OTRequest, OTApproval.ot_request_id == OTRequest.id
    ).join(Employee, OTRequest.employee_id == Employee.id).filter(
        Employee.company_id == company_id
    ).paginate(page=page, per_page=20)
    
    return render_template('hr_manager/ot_approval.html', approvals=approvals)


@app.route('/dashboard/hr-manager/ot-attendance', methods=['GET'])
@require_login
def hr_manager_ot_attendance():
    """OT Attendance View"""
    if current_user.role.name not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    
    company_id = get_company_id(request.args.get('company_id'))
    if not company_id:
        flash('No company assigned', 'danger')
        return redirect(url_for('dashboard'))
    
    date_from = request.args.get('date_from', (date.today() - timedelta(days=30)).isoformat())
    date_to = request.args.get('date_to', date.today().isoformat())
    page = request.args.get('page', 1, type=int)
    
    # Get OT attendance records
    ot_records = OTAttendance.query.join(Employee, OTAttendance.employee_id == Employee.id).filter(
        Employee.company_id == company_id,
        OTAttendance.ot_date.between(date_from, date_to)
    ).order_by(OTAttendance.ot_date.desc()).paginate(page=page, per_page=20)
    
    return render_template('hr_manager/ot_attendance.html', 
                         ot_records=ot_records,
                         date_from=date_from,
                         date_to=date_to)


@app.route('/dashboard/hr-manager/generate-payroll', methods=['GET', 'POST'])
@require_login
def hr_manager_generate_payroll():
    """Redirect to Payroll Generate page"""
    if current_user.role.name not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    
    return redirect(url_for('payroll_generate'))


@app.route('/dashboard/hr-manager/payroll-reminder', methods=['GET'])
@require_login
def hr_manager_payroll_reminder():
    """Payroll Reminder"""
    if current_user.role.name not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
        flash('Access Denied', 'danger')
        return redirect(url_for('index'))
    
    company_id = get_company_id(request.args.get('company_id'))
    if not company_id:
        flash('No company assigned', 'danger')
        return redirect(url_for('dashboard'))
    
    today = date.today()
    month_start, month_end = get_current_month_dates()
    
    # Get pending payrolls for this month (filter by pay_period dates)
    pending_payrolls = Payroll.query.join(Employee, Payroll.employee_id == Employee.id).filter(
        Employee.company_id == company_id,
        Payroll.pay_period_start >= month_start,
        Payroll.pay_period_end <= month_end,
        Payroll.status == 'Draft'
    ).all()
    
    return render_template('hr_manager/payroll_reminder.html', 
                         pending_payrolls=pending_payrolls,
                         company_id=str(company_id))
