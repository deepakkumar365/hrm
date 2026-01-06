
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import app, db
from core.models import Attendance, AttendanceRegularization, Employee, User, AuditLog
from datetime import datetime
from services.attendance_service import AttendanceService

# -------------------------------------------------------------------------
# Regularization Request (Employee Side)
# -------------------------------------------------------------------------

@app.route('/attendance/regularize', methods=['POST'])
@login_required
def attendance_regularize_request():
    """Submit a regularization request for a specific attendance record"""
    try:
        attendance_id = request.form.get('attendance_id')
        reason = request.form.get('reason')
        corrected_in = request.form.get('corrected_clock_in')
        corrected_out = request.form.get('corrected_clock_out')
        
        if not attendance_id or not corrected_in:
            flash('Missing required fields', 'error')
            return redirect(url_for('attendance_list_view'))
            
        attendance = Attendance.query.get_or_404(attendance_id)
        
        # Security check: Ensure user owns this record or is HR/Admin
        if attendance.employee.user_id != current_user.id and current_user.role.name not in ['HR Manager', 'Super Admin', 'Tenant Admin']:
            flash('Unauthorized access', 'error')
            return redirect(url_for('attendance_list_view'))

        # Check if pending request exists
        existing = AttendanceRegularization.query.filter_by(
            employee_id=attendance.employee_id,
            date=attendance.date,
            status='Pending'
        ).first()
        
        if existing:
            flash('A pending regularization request already exists for this date.', 'warning')
            return redirect(url_for('attendance_list_view'))

        # Create Request
        # Parse times. Input format is usually "HH:MM" or "YYYY-MM-DDTHH:MM" depending on input type
        # For simplicity, let's assume input is datetime-local "YYYY-MM-DDTHH:MM" or similar
        # If UI sends just time, we combine with attendance date. 
        # Let's assume the UI sends full datetime string or we handle it.
        
        # Helper to parse form datetime-local input "2023-10-25T09:00"
        def parse_dt(dt_str):
            if not dt_str: return None
            return datetime.strptime(dt_str, '%Y-%m-%dT%H:%M')

        new_in = parse_dt(corrected_in)
        new_out = parse_dt(corrected_out) if corrected_out else None
        
        req = AttendanceRegularization(
            employee_id=attendance.employee_id,
            date=attendance.date,
            original_clock_in=attendance.clock_in_time,
            original_clock_out=attendance.clock_out_time,
            corrected_clock_in=new_in,
            corrected_clock_out=new_out,
            reason=reason,
            status='Pending',
            requested_by=current_user.id
        )
        
        db.session.add(req)
        
        # Update Attendance sub-status
        attendance.sub_status = 'Regularization Pending'
        
        db.session.commit()
        
        flash('Regularization request submitted successfully.', 'success')
        return redirect(url_for('attendance_list_view'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting request: {str(e)}', 'error')
        return redirect(url_for('attendance_list_view'))

@app.route('/attendance/regularize/list', methods=['GET'])
@login_required
def attendance_regularization_list():
    """View my regularization requests"""
    requests = AttendanceRegularization.query.join(Employee).filter(
        Employee.user_id == current_user.id
    ).order_by(AttendanceRegularization.created_at.desc()).all()
    
    return render_template('attendance/regularization_list.html', requests=requests)


# -------------------------------------------------------------------------
# Management & Approval (Manager/HR Side)
# -------------------------------------------------------------------------

@app.route('/attendance/regularize/manage', methods=['GET'])
@login_required
def attendance_regularization_manage():
    """List pending regularization requests for approval"""
    if current_user.role.name not in ['HR Manager', 'Super Admin', 'Tenant Admin', 'Manager']:
        flash('Unauthorized', 'error')
        return redirect(url_for('dashboard'))
        
    # Filter logic:
    # Super Admin/Tenant Admin: All
    # HR Manager: Their Company
    # Manager: Their Direct Reports
    
    query = AttendanceRegularization.query.filter_by(status='Pending').join(Employee)
    
    if current_user.role.name == 'Manager':
        # Get employees reporting to this user
        # user.employee_profile.id is the manager_employee_id
        if not current_user.employee_profile:
             requests = []
        else:
            # Subordinates
            subordinates = Employee.query.filter_by(manager_id=current_user.employee_profile.id).with_entities(Employee.id).all()
            sub_ids = [s[0] for s in subordinates]
            query = query.filter(AttendanceRegularization.employee_id.in_(sub_ids))
            requests = query.all()
            
    elif current_user.role.name == 'HR Manager':
        # Filter by company
        company_id = current_user.company_id
        if company_id:
             query = query.filter(Employee.company_id == company_id)
        requests = query.all()
        
    else:
        # Admin sees all (or filtered by tenant if implemented)
        requests = query.all()
        
    return render_template('attendance/regularization_manage.html', requests=requests)

@app.route('/attendance/regularize/<int:id>/approve', methods=['POST'])
@login_required
def attendance_regularization_approve(id):
    """Approve a regularization request and update attendance"""
    # Authorization checks...
    req = AttendanceRegularization.query.get_or_404(id)
    
    # Check permissions (simplified here, assume access if they reached here via manage)
    
    try:
        req.status = 'Approved'
        req.approved_by = current_user.id
        req.approved_at = datetime.utcnow()
        
        # Update Actual Attendance Record
        attendance = Attendance.query.filter_by(employee_id=req.employee_id, date=req.date).first()
        if attendance:
            attendance.clock_in_time = req.corrected_clock_in
            attendance.clock_out_time = req.corrected_clock_out
            attendance.regularization_id = req.id
            attendance.sub_status = 'Regularized'
            
            # Recalculate Logic
            # Use AttendanceService to recalculate hours and status
            # We assume AttendanceService has a method providing this logic, creates it if not.
            # For now, inline basic recalc or call service function if available.
            
            # Re-evaluating status
            # If we have In and Out -> Present
            # If duration < half_day -> Half Day
            
            # Simple Recalc:
            if attendance.clock_out_time and attendance.clock_in_time:
                 duration = (attendance.clock_out_time - attendance.clock_in_time).total_seconds() / 3600
                 attendance.total_hours = round(duration, 2)
                 attendance.regular_hours = attendance.total_hours # Simplified
                 
                 # Check thresholds from WorkingHours
                 wh = attendance.employee.working_hours
                 half_day_thresh = (wh.half_day_threshold / 60) if wh and wh.half_day_threshold else 4.0
                 
                 if attendance.total_hours >= half_day_thresh:
                     attendance.status = 'Present'
                 else:
                     attendance.status = 'Half Day'
            else:
                 attendance.status = 'Incomplete'
            
            # Clear LOP if present
            attendance.lop = False
            
        # Audit Log
        audit = AuditLog(
            user_id=current_user.id,
            action='Regularization Approved',
            resource_type='AttendanceRegularization',
            resource_id=str(req.id),
            changes=f"Approved request for {req.employee.first_name}. Status changed to {attendance.status}.",
            status='Success'
        )
        db.session.add(audit)

        db.session.commit()
        flash('Request approved and attendance updated.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error approving request: {str(e)}', 'error')
        
    return redirect(url_for('attendance_regularization_manage'))

@app.route('/attendance/regularize/<int:id>/reject', methods=['POST'])
@login_required
def attendance_regularization_reject(id):
    """Reject a regularization request"""
    req = AttendanceRegularization.query.get_or_404(id)
    reason = request.form.get('rejection_reason', 'No reason provided')
    
    try:
        req.status = 'Rejected'
        req.approved_by = current_user.id
        req.approved_at = datetime.utcnow()
        req.rejection_reason = reason
        
        # Update Attendance sub-status
        attendance = Attendance.query.filter_by(employee_id=req.employee_id, date=req.date).first()
        if attendance:
             attendance.sub_status = 'Regularization Rejected'
        
        # Audit Log
        audit = AuditLog(
            user_id=current_user.id,
            action='Regularization Rejected',
            resource_type='AttendanceRegularization',
            resource_id=str(req.id),
            changes=f"Rejected request for {req.employee.first_name}. Reason: {reason}",
            status='Success'
        )
        db.session.add(audit)

        db.session.commit()
        flash('Request rejected.', 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error rejecting request: {str(e)}', 'error')
        
    return redirect(url_for('attendance_regularization_manage'))
