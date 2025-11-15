"""
OT Management Routes
Handles Overtime (OT) management for HR Manager and Tenant Admin
"""
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import logging

from app import app, db
from models import OTAttendance, OTApproval, OTRequest, Employee, User, Role, Company, Department, OTType
from auth import require_login, require_role

logger = logging.getLogger(__name__)


# ============ MARK OT ATTENDANCE (Employee Self-Service) ============
@app.route('/ot/mark', methods=['GET', 'POST'])
@login_required
def mark_ot_attendance():
    """Mark OT Attendance - Self-service for all employees (except Super Admin)"""
    try:
        # Check access control - Allow all roles except Super Admin to mark their own OT
        user_role = current_user.role.name if current_user.role else None
        if user_role == 'Super Admin':
            flash('Super Admin cannot mark OT attendance. Use OT Management section.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get employee profile
        if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
            flash('Employee profile required for OT marking', 'danger')
            return redirect(url_for('dashboard'))
        
        employee = current_user.employee_profile
        company_id = employee.company_id
        
        if request.method == 'POST':
            try:
                ot_date_str = request.form.get('ot_date')
                ot_in_time_str = request.form.get('ot_in_time')
                ot_out_time_str = request.form.get('ot_out_time')
                ot_hours = request.form.get('ot_hours')
                ot_type_id = request.form.get('ot_type_id')
                notes = request.form.get('notes', '')
                
                # Validate inputs
                if not ot_date_str:
                    flash('Please select an OT date', 'danger')
                    return redirect(url_for('mark_ot_attendance'))
                
                if not ot_type_id:
                    flash('Please select an OT type', 'danger')
                    return redirect(url_for('mark_ot_attendance'))
                
                # Parse date
                ot_date = datetime.strptime(ot_date_str, '%Y-%m-%d').date()
                
                # Check if OT record for this date already exists
                existing_ot = OTAttendance.query.filter_by(
                    employee_id=employee.id,
                    ot_date=ot_date
                ).first()
                
                if existing_ot:
                    existing_ot.notes = notes
                    existing_ot.ot_type_id = ot_type_id
                    existing_ot.status = 'Draft'
                    
                    # Handle time or hours entry
                    if ot_in_time_str and ot_out_time_str:
                        ot_in_time = datetime.strptime(ot_in_time_str, '%H:%M').time()
                        ot_out_time = datetime.strptime(ot_out_time_str, '%H:%M').time()
                        
                        ot_in_dt = datetime.combine(ot_date, ot_in_time)
                        ot_out_dt = datetime.combine(ot_date, ot_out_time)
                        
                        existing_ot.ot_in_time = ot_in_dt
                        existing_ot.ot_out_time = ot_out_dt
                        existing_ot.calculate_ot_hours()
                    elif ot_hours:
                        existing_ot.ot_hours = float(ot_hours)
                    else:
                        flash('Please provide either OT hours or OT in/out times', 'danger')
                        return redirect(url_for('mark_ot_attendance'))
                    
                    existing_ot.modified_at = datetime.now()
                else:
                    # Create new OT attendance record
                    ot_record = OTAttendance(
                        employee_id=employee.id,
                        company_id=company_id,
                        ot_date=ot_date,
                        ot_type_id=ot_type_id,
                        status='Draft',
                        notes=notes,
                        created_by=current_user.username
                    )
                    
                    # Handle time or hours entry
                    if ot_in_time_str and ot_out_time_str:
                        ot_in_time = datetime.strptime(ot_in_time_str, '%H:%M').time()
                        ot_out_time = datetime.strptime(ot_out_time_str, '%H:%M').time()
                        
                        ot_in_dt = datetime.combine(ot_date, ot_in_time)
                        ot_out_dt = datetime.combine(ot_date, ot_out_time)
                        
                        ot_record.ot_in_time = ot_in_dt
                        ot_record.ot_out_time = ot_out_dt
                        ot_record.calculate_ot_hours()
                    elif ot_hours:
                        ot_record.ot_hours = float(ot_hours)
                    else:
                        flash('Please provide either OT hours or OT in/out times', 'danger')
                        return redirect(url_for('mark_ot_attendance'))
                    
                    db.session.add(ot_record)
                
                db.session.commit()
                flash('OT Attendance recorded successfully!', 'success')
                return redirect(url_for('mark_ot_attendance'))
                
            except ValueError as e:
                flash(f'Invalid input: {str(e)}', 'danger')
                return redirect(url_for('mark_ot_attendance'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error marking OT attendance: {str(e)}")
                flash('Error recording OT attendance', 'danger')
                return redirect(url_for('mark_ot_attendance'))
        
        # GET request - Show form
        # Get active OT types for this company
        ot_types = OTType.query.filter_by(company_id=company_id, is_active=True).order_by(OTType.display_order).all()
        
        # Check if OT types are configured
        if not ot_types:
            flash('⚠️  No OT types are configured for your company. Please contact your HR Manager or Tenant Admin to set up OT types first in Masters > OT Types.', 'warning')
        
        # Get today's date for default
        today = datetime.now().date()
        
        # Get recent OT records for this employee
        recent_ots = OTAttendance.query.filter_by(
            employee_id=employee.id
        ).order_by(OTAttendance.ot_date.desc()).limit(10).all()
        
        return render_template('ot/mark_attendance.html',
                             employee=employee,
                             ot_types=ot_types,
                             today=today,
                             recent_ots=recent_ots,
                             has_ot_types=bool(ot_types))
        
    except Exception as e:
        logger.error(f"Error in mark_ot_attendance: {str(e)}")
        flash('Error accessing OT marking form', 'danger')
        return redirect(url_for('dashboard'))


# ============ OT ATTENDANCE ============
@app.route('/ot/attendance', methods=['GET'])
@login_required
def ot_attendance():
    """Display OT Attendance records - Accessible to HR Manager, Tenant Admin, Super Admin"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied. OT Attendance is only for HR Manager and above.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get filter parameters
        employee_id = request.args.get('employee_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = OTAttendance.query
        
        # Filter by company if not Super Admin
        if user_role != 'Super Admin':
            if hasattr(current_user, 'company_id') and current_user.company_id:
                query = query.filter_by(company_id=current_user.company_id)
        
        # Apply filters
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d')
                query = query.filter(OTAttendance.ot_date >= start)
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d')
                query = query.filter(OTAttendance.ot_date <= end)
            except ValueError:
                pass
        
        # Get paginated results
        page = request.args.get('page', 1, type=int)
        ot_records = query.order_by(OTAttendance.ot_date.desc()).paginate(page=page, per_page=20)
        
        # Get employees for filter dropdown
        if hasattr(current_user, 'company_id'):
            employees = Employee.query.filter_by(company_id=current_user.company_id).all()
        else:
            employees = []
        
        return render_template('ot/attendance.html', 
                             ot_records=ot_records,
                             employees=employees,
                             selected_employee=employee_id,
                             start_date=start_date,
                             end_date=end_date)
    
    except Exception as e:
        logger.error(f"Error in ot_attendance: {str(e)}")
        flash('Error loading OT attendance records', 'danger')
        return redirect(url_for('dashboard'))


# ============ OT REQUESTS ============
@app.route('/ot/requests', methods=['GET'])
@login_required
def ot_requests():
    """Display OT Requests - Accessible to HR Manager, Tenant Admin, Super Admin"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied. OT Requests is only for HR Manager and above.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get filter parameters
        status = request.args.get('status', 'pending')
        employee_id = request.args.get('employee_id')
        
        # Build query
        query = OTApproval.query
        
        # Filter by company
        if user_role != 'Super Admin':
            if hasattr(current_user, 'company_id') and current_user.company_id:
                query = query.filter_by(company_id=current_user.company_id)
        
        # Filter by status
        if status and status != 'all':
            query = query.filter_by(status=status)
        
        # Filter by employee
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        # Get paginated results
        page = request.args.get('page', 1, type=int)
        requests = query.order_by(OTApproval.created_at.desc()).paginate(page=page, per_page=20)
        
        # Get statistics
        company_filter = {}
        if user_role != 'Super Admin' and hasattr(current_user, 'company_id'):
            company_filter = {'company_id': current_user.company_id}
        
        stats = {
            'pending': OTApproval.query.filter_by(status='pending', **company_filter).count(),
            'approved': OTApproval.query.filter_by(status='approved', **company_filter).count(),
            'rejected': OTApproval.query.filter_by(status='rejected', **company_filter).count(),
        }
        
        if hasattr(current_user, 'company_id'):
            employees = Employee.query.filter_by(company_id=current_user.company_id).all()
        else:
            employees = []
        
        return render_template('ot/requests.html',
                             requests=requests,
                             stats=stats,
                             status=status,
                             employees=employees,
                             selected_employee=employee_id)
    
    except Exception as e:
        logger.error(f"Error in ot_requests: {str(e)}")
        flash('Error loading OT requests', 'danger')
        return redirect(url_for('dashboard'))


# ============ OT APPROVAL DASHBOARD ============
@app.route('/ot/approval', methods=['GET', 'POST'])
@login_required
def ot_approval():
    """OT Approval Dashboard - Accessible to HR Manager, Tenant Admin, Super Admin"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied. OT Approval is only for HR Manager and above.', 'danger')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            approval_id = request.form.get('approval_id')
            action = request.form.get('action')  # approve, reject, modify
            comments = request.form.get('comments', '')
            modified_hours = request.form.get('modified_hours')
            
            approval = OTApproval.query.get(approval_id)
            if not approval:
                flash('OT request not found', 'danger')
                return redirect(url_for('ot_approval'))
            
            # Check company access
            if user_role != 'Super Admin' and hasattr(current_user, 'company_id'):
                if approval.company_id != current_user.company_id:
                    flash('Access Denied', 'danger')
                    return redirect(url_for('ot_approval'))
            
            try:
                if action == 'approve':
                    approval.status = 'approved'
                    approval.approved_by = current_user.id
                    approval.approved_at = datetime.utcnow()
                    approval.comments = comments
                    if modified_hours:
                        approval.hours = float(modified_hours)
                    flash('OT request approved', 'success')
                
                elif action == 'reject':
                    approval.status = 'rejected'
                    approval.rejected_by = current_user.id
                    approval.rejected_at = datetime.utcnow()
                    approval.comments = comments
                    flash('OT request rejected', 'success')
                
                elif action == 'modify':
                    if modified_hours:
                        approval.hours = float(modified_hours)
                        approval.comments = comments
                        flash('OT hours modified', 'success')
                
                db.session.commit()
                return redirect(url_for('ot_approval'))
            
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error processing OT approval: {str(e)}")
                flash('Error processing approval', 'danger')
        
        # GET: Display pending approvals
        query = OTApproval.query.filter_by(status='pending')
        
        if user_role != 'Super Admin':
            if hasattr(current_user, 'company_id') and current_user.company_id:
                query = query.filter_by(company_id=current_user.company_id)
        
        page = request.args.get('page', 1, type=int)
        pending_approvals = query.order_by(OTApproval.created_at.asc()).paginate(page=page, per_page=20)
        
        return render_template('ot/approval_dashboard.html', 
                             pending_approvals=pending_approvals)
    
    except Exception as e:
        logger.error(f"Error in ot_approval: {str(e)}")
        flash('Error loading OT approval dashboard', 'danger')
        return redirect(url_for('dashboard'))


# ============ PAYROLL OT SUMMARY ============
@app.route('/ot/payroll-summary', methods=['GET'])
@login_required
def ot_payroll_summary():
    """Display OT Payroll Summary (View Only for HR Manager) - Accessible to HR Manager, Tenant Admin, Super Admin"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied. OT Payroll Summary is only for HR Manager and above.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get filter parameters
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Build summary query - use OTRequest which has approved_at
        query = OTRequest.query.filter_by(status='Approved')
        
        if user_role != 'Super Admin':
            if hasattr(current_user, 'company_id') and current_user.company_id:
                query = query.filter_by(company_id=current_user.company_id)
        
        # Filter by month/year
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        approved_ots = query.filter(
            OTRequest.approved_at >= start_date,
            OTRequest.approved_at < end_date
        ).all()
        
        # Calculate summary by OT type
        summary = {}
        total_hours = 0
        total_amount = 0
        
        for ot in approved_ots:
            ot_type_obj = ot.ot_type
            ot_type_name = ot_type_obj.name if ot_type_obj else 'General'
            if ot_type_name not in summary:
                summary[ot_type_name] = {'hours': 0, 'amount': 0, 'count': 0}
            
            hours = float(ot.approved_hours or 0)
            amount = float(hours * float(ot_type_obj.rate_multiplier or 1.0)) if ot_type_obj else 0
            
            summary[ot_type_name]['hours'] += hours
            summary[ot_type_name]['amount'] += amount
            summary[ot_type_name]['count'] += 1
            
            total_hours += hours
            total_amount += amount
        
        return render_template('ot/payroll_summary.html',
                             summary=summary,
                             total_hours=total_hours,
                             total_amount=total_amount,
                             month=month,
                             year=year)
    
    except Exception as e:
        logger.error(f"Error in ot_payroll_summary: {str(e)}")
        flash('Error loading OT payroll summary', 'danger')
        return redirect(url_for('dashboard'))


# ============ API ENDPOINTS ============
@app.route('/api/ot/attendance/<int:attendance_id>', methods=['GET'])
@login_required
def get_attendance_detail(attendance_id):
    """API endpoint to get OT attendance details"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            return jsonify({'error': 'Access Denied'}), 403
        
        record = OTAttendance.query.get(attendance_id)
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        # Check company access
        if user_role != 'Super Admin':
            if hasattr(current_user, 'company_id') and record.company_id != current_user.company_id:
                return jsonify({'error': 'Access Denied'}), 403
        
        return jsonify({
            'id': record.id,
            'employee_id': record.employee_id,
            'date': record.ot_date.isoformat() if hasattr(record.ot_date, 'isoformat') else str(record.ot_date),
            'check_in': record.check_in_time.isoformat() if hasattr(record, 'check_in_time') and record.check_in_time else None,
            'check_out': record.check_out_time.isoformat() if hasattr(record, 'check_out_time') and record.check_out_time else None,
            'hours': float(record.ot_hours) if hasattr(record, 'ot_hours') else 0,
            'reason': record.reason if hasattr(record, 'reason') else '',
            'status': record.status if hasattr(record, 'status') else 'pending'
        })
    
    except Exception as e:
        logger.error(f"Error in get_attendance_detail: {str(e)}")
        return jsonify({'error': 'Server error'}), 500


@app.route('/api/ot/requests/<int:request_id>', methods=['GET'])
@login_required
def get_request_detail(request_id):
    """API endpoint to get OT request details"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            return jsonify({'error': 'Access Denied'}), 403
        
        ot_request = OTApproval.query.get(request_id)
        if not ot_request:
            return jsonify({'error': 'Request not found'}), 404
        
        # Check company access
        if user_role != 'Super Admin':
            if hasattr(current_user, 'company_id') and ot_request.company_id != current_user.company_id:
                return jsonify({'error': 'Access Denied'}), 403
        
        return jsonify({
            'id': ot_request.id,
            'employee_id': ot_request.employee_id,
            'hours': float(ot_request.hours),
            'ot_type': ot_request.ot_type or 'General',
            'reason': ot_request.reason if hasattr(ot_request, 'reason') else '',
            'status': ot_request.status,
            'created_at': ot_request.created_at.isoformat() if hasattr(ot_request.created_at, 'isoformat') else str(ot_request.created_at),
            'approved_at': ot_request.approved_at.isoformat() if ot_request.approved_at and hasattr(ot_request.approved_at, 'isoformat') else None,
            'approved_by': ot_request.approved_by,
            'comments': ot_request.comments if hasattr(ot_request, 'comments') else ''
        })
    
    except Exception as e:
        logger.error(f"Error in get_request_detail: {str(e)}")
        return jsonify({'error': 'Server error'}), 500