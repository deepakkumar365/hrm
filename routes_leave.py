"""Leave Management Routes"""
from flask import request, render_template, redirect, url_for, jsonify, flash
from flask_login import current_user
from app import app, db
from models import Leave, Employee, User
from auth import require_login
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import logging

logger = logging.getLogger(__name__)


# Leave Requests - Create/Form View
@app.route('/leave/request', methods=['GET', 'POST'])
@app.route('/leave', methods=['GET', 'POST'])
@require_login
def leave_request():
    """Request a new leave (GET shows form, POST submits)"""
    
    # Ensure user is an employee
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        flash("Only employees can request leave", "error")
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            leave_type = request.form.get('leave_type')
            start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            reason = request.form.get('reason', '')
            
            # Validate dates
            if start_date > end_date:
                flash("Start date must be before end date", "error")
                return redirect(url_for('leave_request'))
            
            if start_date < datetime.now().date():
                flash("Cannot create leave request for past dates", "error")
                return redirect(url_for('leave_request'))
            
            # Calculate days requested (excluding weekends)
            days_requested = 0
            current_date = start_date
            while current_date <= end_date:
                # 0=Monday, 6=Sunday
                if current_date.weekday() < 5:  # Monday to Friday
                    days_requested += 1
                current_date += timedelta(days=1)
            
            # Create leave request
            leave = Leave(
                employee_id=current_user.employee_profile.id,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                days_requested=days_requested,
                reason=reason,
                requested_by=current_user.id,
                status='Pending'
            )
            
            db.session.add(leave)
            db.session.commit()
            
            flash("Leave request submitted successfully", "success")
            return redirect(url_for('leave_list'))
            
        except ValueError as e:
            flash(f"Invalid input: {e}", "error")
            return redirect(url_for('leave_request'))
        except Exception as e:
            logger.error(f"Error creating leave request: {e}")
            db.session.rollback()
            flash("Error creating leave request", "error")
            return redirect(url_for('leave_request'))
    
    return render_template('leave/form.html')


# Leave Requests - List View
@app.route('/leave/list')
@require_login
def leave_list():
    """List all leave requests for the current user"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    
    try:
        query = Leave.query
        
        # Role-based filtering for leave requests
        user_role = current_user.role.name if hasattr(current_user, 'role') and current_user.role else None
        
        if user_role in ['Admin', 'Super Admin']:
            # Admins can see all leave requests
            pass # No additional filtering needed
        elif user_role == 'Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            # Managers see leave requests from their direct reports
            manager_id = current_user.employee_profile.id
            
            # Get IDs of employees who report to this manager
            team_employee_ids = [emp.id for emp in Employee.query.filter_by(manager_id=manager_id).all()]
            
            # Filter leaves for team members
            query = query.filter(Leave.employee_id.in_(team_employee_ids))
        elif hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            # Regular employees see only their own leave requests
            employee_id = current_user.employee_profile.id
            query = query.filter(Leave.employee_id == employee_id)
        else:
            # If user has no profile and is not an admin, show no leaves
            return render_template('leave/list.html', leave_requests=None, status_filter=status_filter)
        
        # Filter by status if provided
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Paginate results
        leave_requests = query.order_by(Leave.created_at.desc()).paginate(page=page, per_page=10)
        
        return render_template('leave/list.html', leave_requests=leave_requests, status_filter=status_filter)
    except Exception as e:
        logger.error(f"Error loading leave requests: {e}")
        flash("Error loading leave requests", "error")
        return redirect(url_for('dashboard'))


# Leave Request - Detail View
@app.route('/leave/<int:leave_id>')
@require_login
def leave_detail(leave_id):
    """View leave request details"""
    try:
        leave = Leave.query.get_or_404(leave_id)
        
        # Check authorization - can view own or if manager/admin
        if not (hasattr(current_user, 'employee_profile') and 
                current_user.employee_profile and
                current_user.employee_profile.id == leave.employee_id):
            # Check if user is a manager or admin
            if not (hasattr(current_user, 'role') and 
                    current_user.role in ['Manager', 'Admin', 'Super Admin']):
                flash("Unauthorized to view this leave request", "error")
                return redirect(url_for('leave_list'))
        
        return render_template('leave/detail.html', leave=leave)
    except Exception as e:
        logger.error(f"Error loading leave detail: {e}")
        flash("Leave request not found", "error")
        return redirect(url_for('leave_list'))


# Leave Request - Edit (Employee only, if pending)
@app.route('/leave/<int:leave_id>/edit', methods=['GET', 'POST'])
@require_login
def leave_edit(leave_id):
    """Edit a pending leave request"""
    try:
        leave = Leave.query.get_or_404(leave_id)

        # Authorization check: Only the employee who created it can edit, and only if it's pending.
        if not (hasattr(current_user, 'employee_profile') and
                current_user.employee_profile and
                current_user.employee_profile.id == leave.employee_id):
            flash("You are not authorized to edit this leave request.", "error")
            return redirect(url_for('leave_list'))

        if leave.status != 'Pending':
            flash("Only pending leave requests can be edited.", "error")
            return redirect(url_for('leave_detail', leave_id=leave_id))

        if request.method == 'POST':
            leave.leave_type = request.form.get('leave_type')
            leave.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
            leave.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
            leave.reason = request.form.get('reason', '')

            # Validate dates
            if leave.start_date > leave.end_date:
                flash("Start date must be before or on the end date.", "error")
                return render_template('leave/form.html', leave=leave)

            # Recalculate days requested
            days_requested = 0
            current_date = leave.start_date
            while current_date <= leave.end_date:
                if current_date.weekday() < 5:  # Monday to Friday
                    days_requested += 1
                current_date += timedelta(days=1)
            leave.days_requested = days_requested

            db.session.commit()
            flash("Leave request updated successfully.", "success")
            return redirect(url_for('leave_list'))

        # For GET request, show the form pre-filled with leave data
        return render_template('leave/form.html', leave=leave)
    except Exception as e:
        logger.error(f"Error editing leave request: {e}")
        flash("An error occurred while trying to edit the leave request.", "error")
        return redirect(url_for('leave_list'))

# Leave Request - Approve (Admin/Manager only)
@app.route('/leave/<int:leave_id>/approve', methods=['POST'])
@require_login
def leave_approve(leave_id):
    """Approve a leave request"""
    
    # Get user role and check authorization
    user_role = current_user.role.name if hasattr(current_user, 'role') and current_user.role else None
    if user_role not in ['Manager', 'Admin', 'Super Admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        leave = Leave.query.get_or_404(leave_id)
        
        # If user is a Manager, ensure they are the manager of the employee who requested leave
        if user_role == 'Manager':
            if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile):
                return jsonify({'error': 'Manager has no employee profile'}), 403
            
            employee_requesting_leave = leave.employee
            if not employee_requesting_leave or employee_requesting_leave.manager_id != current_user.employee_profile.id:
                flash("You can only approve requests for your direct reports.", "error")
                return redirect(url_for('leave_list'))

        if leave.status != 'Pending':
            return jsonify({'error': 'Can only approve pending requests'}), 400
        
        leave.status = 'Approved'
        leave.approved_by = current_user.id
        leave.approved_at = datetime.now()
        
        db.session.commit()
        
        flash("Leave request approved", "success")
        return redirect(url_for('leave_list'))
    except Exception as e:
        logger.error(f"Error approving leave: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error approving leave request'}), 500


# Leave Request - Reject (Admin/Manager only)
@app.route('/leave/<int:leave_id>/reject', methods=['POST'])
@require_login
def leave_reject(leave_id):
    """Reject a leave request"""
    
    # Get user role and check authorization
    user_role = current_user.role.name if hasattr(current_user, 'role') and current_user.role else None
    if user_role not in ['Manager', 'Admin', 'Super Admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        leave = Leave.query.get_or_404(leave_id)
        rejection_reason = request.form.get('rejection_reason', '')

        # If user is a Manager, ensure they are the manager of the employee who requested leave
        if user_role == 'Manager':
            if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile):
                return jsonify({'error': 'Manager has no employee profile'}), 403

            employee_requesting_leave = leave.employee
            if not employee_requesting_leave or employee_requesting_leave.manager_id != current_user.employee_profile.id:
                flash("You can only reject requests for your direct reports.", "error")
                return redirect(url_for('leave_list'))
        
        if leave.status != 'Pending':
            return jsonify({'error': 'Can only reject pending requests'}), 400
        
        leave.status = 'Rejected'
        leave.approved_by = current_user.id
        leave.approved_at = datetime.now()
        leave.rejection_reason = rejection_reason
        
        db.session.commit()
        
        flash("Leave request rejected", "success")
        return redirect(url_for('leave_list'))
    except Exception as e:
        logger.error(f"Error rejecting leave: {e}")
        db.session.rollback()
        return jsonify({'error': 'Error rejecting leave request'}), 500


# Leave Calendar
@app.route('/leave/calendar')
@require_login
def leave_calendar():
    """Display leave calendar"""
    try:
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Get all leaves for the month
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        leaves = Leave.query.filter(
            and_(
                Leave.start_date <= end_date,
                Leave.end_date >= start_date,
                Leave.status.in_(['Approved', 'Pending'])
            )
        ).all()
        
        return render_template('leave/calendar.html', leaves=leaves, month=month, year=year)
    except Exception as e:
        logger.error(f"Error loading leave calendar: {e}")
        flash("Error loading calendar", "error")
        return redirect(url_for('dashboard'))


# Leave Balance Report
@app.route('/leave/balance')
@require_login
def leave_balance():
    """View leave balance for employees"""
    try:
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            # Show only own leave balance
            employee = current_user.employee_profile
            leaves = Leave.query.filter_by(employee_id=employee.id).all()
            
            total_approved = sum(
                leave.days_requested for leave in leaves 
                if leave.status == 'Approved'
            )
            
            return render_template('leave/balance.html', 
                                 employee=employee, 
                                 total_approved=total_approved,
                                 leaves=leaves)
        else:
            # Show all employees' leave balance (Admin/Manager)
            if not (hasattr(current_user, 'role') and 
                    current_user.role in ['Manager', 'Admin', 'Super Admin']):
                flash("Unauthorized", "error")
                return redirect(url_for('dashboard'))
            
            employees = Employee.query.all()
            return render_template('leave/balance_report.html', employees=employees)
    except Exception as e:
        logger.error(f"Error loading leave balance: {e}")
        flash("Error loading leave balance", "error")
        return redirect(url_for('dashboard'))


# API Endpoint - Get leave data for calendar
@app.route('/api/leave/calendar-data')
@require_login
def api_leave_calendar_data():
    """Get leave data for calendar in JSON format"""
    try:
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        
        if not start_date or not end_date:
            return jsonify([])
        
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        leaves = Leave.query.filter(
            and_(
                Leave.start_date <= end,
                Leave.end_date >= start,
                Leave.status == 'Approved'
            )
        ).all()
        
        events = []
        for leave in leaves:
            events.append({
                'id': leave.id,
                'title': f"{leave.employee.first_name} - {leave.leave_type}",
                'start': leave.start_date.isoformat(),
                'end': (leave.end_date + timedelta(days=1)).isoformat(),
                'backgroundColor': '#28a745',
                'borderColor': '#20c997',
            })
        
        return jsonify(events)
    except Exception as e:
        logger.error(f"Error getting calendar data: {e}")
        return jsonify({'error': 'Error loading calendar data'}), 500