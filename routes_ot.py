"""
OT Management Routes - Two-Tier Approval System
Handles Overtime (OT) management with Manager and HR Manager approval levels

Workflow:
1. Employee marks OT → OTAttendance (Draft)
2. Manager submits for approval → OTRequest created + OTApproval Level 1 (pending_manager)
3. Manager approves → OTApproval Level 1 = "manager_approved" → OTApproval Level 2 created (pending_hr)
4. Manager rejects → OTApproval Level 1 = "manager_rejected" → Back to Employee
5. HR Manager approves → OTApproval Level 2 = "hr_approved" → OTRequest ready for payroll
6. HR Manager rejects → OTApproval Level 2 = "hr_rejected" → Back to Manager
"""
from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
import logging

from app import app, db
from models import OTAttendance, OTApproval, OTRequest, Employee, User, Role, Company, Department, OTType, OTDailySummary, PayrollConfiguration, Attendance
from auth import require_login, require_role

logger = logging.getLogger(__name__)


# ============ TEMPORARY: CREATE MISSING TABLE ============
@app.route('/admin/setup/create-ot-table', methods=['GET'])
@login_required
def setup_create_ot_table():
    """TEMPORARY: Create missing OTDailySummary table - Remove after first use"""
    try:
        # Security: Only allow access in development or from admin
        user_role = current_user.role.name if (hasattr(current_user, 'role') and current_user.role) else None
        if user_role not in ['Super Admin', 'Tenant Admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        from sqlalchemy import inspect
        
        # Check if table exists
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'hrm_ot_daily_summary' in existing_tables:
            return jsonify({
                'status': 'success',
                'message': 'Table hrm_ot_daily_summary already exists'
            }), 200
        
        # Create the table
        logger.info("Creating hrm_ot_daily_summary table...")
        OTDailySummary.__table__.create(db.engine, checkfirst=True)
        logger.info("✅ Table created successfully")
        
        # Verify it was created
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if 'hrm_ot_daily_summary' in existing_tables:
            return jsonify({
                'status': 'success',
                'message': 'Table hrm_ot_daily_summary created successfully!',
                'next_steps': 'Refresh the page and try OT Management > Payroll Summary (Grid)'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Table creation failed'
            }), 500
    
    except Exception as e:
        logger.error(f"Error creating table: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


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
        
        # Get today's attendance record for timeline
        today_attendance = Attendance.query.filter_by(
            employee_id=employee.id,
            date=today
        ).first()
        
        # Format attendance data for timeline
        attendance_data = []
        if today_attendance:
            if today_attendance.clock_in:
                attendance_data.append({
                    'time': today_attendance.clock_in.strftime('%I:%M %p'),
                    'activity': 'Clock In',
                    'activity_time': today_attendance.clock_in.strftime('%I:%M %p'),
                    'activity_type': 'Clock In'
                })
            if today_attendance.break_start:
                attendance_data.append({
                    'time': today_attendance.break_start.strftime('%I:%M %p'),
                    'activity': 'Start Break',
                    'activity_time': today_attendance.break_start.strftime('%I:%M %p'),
                    'activity_type': 'Start Break'
                })
            if today_attendance.break_end:
                attendance_data.append({
                    'time': today_attendance.break_end.strftime('%I:%M %p'),
                    'activity': 'End Break',
                    'activity_time': today_attendance.break_end.strftime('%I:%M %p'),
                    'activity_type': 'End Break'
                })
            if today_attendance.clock_out:
                attendance_data.append({
                    'time': today_attendance.clock_out.strftime('%I:%M %p'),
                    'activity': 'Clock Out',
                    'activity_time': today_attendance.clock_out.strftime('%I:%M %p'),
                    'activity_type': 'Clock Out'
                })
        
        # Get recent OT records for this employee
        recent_ots = OTAttendance.query.filter_by(
            employee_id=employee.id
        ).order_by(OTAttendance.ot_date.desc()).limit(10).all()
        
        return render_template('ot/mark_attendance.html',
                             employee=employee,
                             ot_types=ot_types,
                             today=today,
                             recent_ots=recent_ots,
                             has_ot_types=bool(ot_types),
                             attendance_data=attendance_data)
        
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
            user_company_id = None
            if hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
                user_company_id = current_user.employee_profile.company_id
            if user_company_id:
                query = query.filter_by(company_id=user_company_id)
        
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
        employees = []
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            employees = Employee.query.filter_by(company_id=current_user.employee_profile.company_id).all()
        
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


# ============ SUBMIT OT FOR MANAGER APPROVAL (Employee Self-Service) ============
@app.route('/ot/submit/<int:attendance_id>', methods=['POST'])
@login_required
def submit_ot_attendance(attendance_id):
    """
    Employee submits their own draft OT for manager approval
    Creates: OTRequest (pending_manager) + OTApproval Level 1 (pending_manager)
    """
    try:
        # Get OT Attendance record
        ot_attendance = OTAttendance.query.get_or_404(attendance_id)
        
        # Verify user owns this OT record
        if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
            flash('No employee profile found', 'danger')
            return redirect(url_for('mark_ot_attendance'))
        
        employee = current_user.employee_profile
        if ot_attendance.employee_id != employee.id:
            flash('Access Denied - You can only submit your own OT records', 'danger')
            return redirect(url_for('mark_ot_attendance'))
        
        # Check if OT is in Draft status
        if ot_attendance.status != 'Draft':
            flash('Only Draft OT records can be submitted', 'warning')
            return redirect(url_for('mark_ot_attendance'))
        
        # Check if OT has ot_type_id assigned
        if not ot_attendance.ot_type_id:
            flash('❌ Cannot submit: OT Type is not assigned. Please select an OT Type before submitting.', 'danger')
            return redirect(url_for('mark_ot_attendance'))
        
        # Check if OT has hours assigned
        if not ot_attendance.ot_hours or ot_attendance.ot_hours <= 0:
            flash('❌ Cannot submit: OT Hours must be greater than 0. Please enter valid hours.', 'danger')
            return redirect(url_for('mark_ot_attendance'))
        
        # Check if employee has a manager assigned
        if not employee.manager_id:
            flash('❌ Cannot submit: No reporting manager assigned to your profile. Contact HR.', 'danger')
            return redirect(url_for('mark_ot_attendance'))
        
        manager = Employee.query.get(employee.manager_id)
        if not manager or not manager.user_id:
            flash('❌ Your reporting manager does not have a user account. Contact HR.', 'danger')
            return redirect(url_for('mark_ot_attendance'))
        
        try:
            # Check if already submitted
            existing_request = OTRequest.query.filter_by(
                employee_id=employee.id,
                ot_date=ot_attendance.ot_date
            ).first()
            
            if existing_request:
                flash('⚠️  OT for this date already in approval workflow', 'warning')
                return redirect(url_for('mark_ot_attendance'))
            
            # Validate OT Type exists
            ot_type = OTType.query.get(ot_attendance.ot_type_id)
            if not ot_type:
                flash('❌ Error: OT Type is invalid or no longer exists. Please select a valid OT Type.', 'danger')
                return redirect(url_for('mark_ot_attendance'))
            
            # Create OT Request with pending_manager status
            ot_request = OTRequest(
                employee_id=employee.id,
                company_id=employee.company_id,
                ot_date=ot_attendance.ot_date,
                ot_type_id=ot_attendance.ot_type_id,
                requested_hours=float(ot_attendance.ot_hours) if ot_attendance.ot_hours else 0,
                reason=ot_attendance.notes or 'OT submitted for approval',
                status='pending_manager',
                created_by=current_user.username
            )
            db.session.add(ot_request)
            db.session.flush()  # Get the ID before commit
            
            # Create OT Approval Record - Level 1 (Manager)
            ot_approval_l1 = OTApproval(
                ot_request_id=ot_request.id,
                approver_id=manager.user_id,  # Send to manager
                approval_level=1,
                status='pending_manager',
                comments=f'Submitted for Manager approval by {current_user.full_name}'
            )
            db.session.add(ot_approval_l1)
            
            # Update OT Attendance status
            ot_attendance.status = 'Submitted'
            ot_attendance.modified_at = datetime.now()
            
            db.session.commit()
            
            manager_name = manager.user.full_name if manager.user else manager.first_name
            flash(f'✅ OT submitted to {manager_name} for approval. Hours: {ot_attendance.ot_hours}', 'success')
            return redirect(url_for('mark_ot_attendance'))
        
        except ValueError as ve:
            db.session.rollback()
            logger.error(f"Value error submitting OT: {str(ve)}")
            flash(f'❌ Invalid data format: {str(ve)}', 'danger')
            return redirect(url_for('mark_ot_attendance'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error submitting OT: {str(e)}", exc_info=True)
            flash(f'❌ Error submitting OT. Please contact support.', 'danger')
            return redirect(url_for('mark_ot_attendance'))
    
    except Exception as e:
        logger.error(f"Error in submit_ot_attendance: {str(e)}")
        flash('Error submitting OT', 'danger')
        return redirect(url_for('mark_ot_attendance'))


# ============ SUBMIT OT FOR MANAGER APPROVAL (HR Manager Action) ============
@app.route('/ot/submit-for-manager-approval/<int:attendance_id>', methods=['POST'])
@login_required
def submit_ot_for_manager_approval(attendance_id):
    """
    HR Manager submits OT Attendance to Employee's Reporting Manager
    Creates: OTRequest (pending_manager) + OTApproval Level 1 (pending_manager)
    """
    try:
        # Check access control - Only HR Manager and above
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied - HR Manager only', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get OT Attendance record
        ot_attendance = OTAttendance.query.get_or_404(attendance_id)
        
        # Verify company access
        user_company_id = None
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        if user_company_id and user_role != 'Super Admin' and ot_attendance.company_id != user_company_id:
            flash('Access Denied', 'danger')
            return redirect(url_for('ot_attendance'))
        
        # Check if already submitted
        existing_request = OTRequest.query.filter_by(
            employee_id=ot_attendance.employee_id,
            ot_date=ot_attendance.ot_date
        ).first()
        
        if existing_request:
            flash('OT for this date already in workflow', 'warning')
            return redirect(url_for('ot_attendance'))
        
        try:
            # Get employee and their reporting manager
            employee = ot_attendance.employee
            if not employee or not employee.manager_id:
                flash('Employee has no reporting manager assigned. Cannot submit for approval.', 'danger')
                return redirect(url_for('ot_attendance'))
            
            manager = Employee.query.get(employee.manager_id)
            if not manager or not manager.user_id:
                flash('Manager does not have a user account. Cannot submit.', 'danger')
                return redirect(url_for('ot_attendance'))
            
            # Create OT Request with pending_manager status
            ot_request = OTRequest(
                employee_id=ot_attendance.employee_id,
                company_id=ot_attendance.company_id,
                ot_date=ot_attendance.ot_date,
                ot_type_id=ot_attendance.ot_type_id,
                requested_hours=ot_attendance.ot_hours or 0,
                reason=ot_attendance.notes or 'OT submitted for approval',
                status='pending_manager',  # Status: Pending Manager Approval
                created_by=current_user.username
            )
            db.session.add(ot_request)
            db.session.flush()  # Get the ID before commit
            
            # Create OT Approval Record - Level 1 (Manager)
            ot_approval_l1 = OTApproval(
                ot_request_id=ot_request.id,
                approver_id=manager.user_id,  # Send to manager
                approval_level=1,
                status='pending_manager',
                comments=f'Submitted for Manager approval by {current_user.full_name}'
            )
            db.session.add(ot_approval_l1)
            
            # Update OT Attendance status
            ot_attendance.status = 'Submitted'
            ot_attendance.modified_at = datetime.now()
            
            db.session.commit()
            
            manager_name = manager.user.full_name if manager.user else manager.first_name
            flash(f'✓ OT submitted to {manager_name} for approval. Hours: {ot_attendance.ot_hours}', 'success')
            return redirect(url_for('ot_attendance'))
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error submitting OT for manager approval: {str(e)}")
            flash(f'Error submitting OT: {str(e)}', 'danger')
            return redirect(url_for('ot_attendance'))
    
    except Exception as e:
        logger.error(f"Error in submit_ot_for_manager_approval: {str(e)}")
        flash('Error submitting OT for approval', 'danger')
        return redirect(url_for('ot_attendance'))


# ============ OT REQUESTS - HR Manager View (Manager Approved) ============
@app.route('/ot/requests', methods=['GET'])
@login_required
def ot_requests():
    """
    Display OT Requests - HR Manager reviews Manager-Approved OT
    Shows: OT with status = 'manager_approved' (pending HR approval)
    Accessible to HR Manager, Tenant Admin, Super Admin
    """
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied. OT Requests is only for HR Manager and above.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get filter parameters
        status = request.args.get('status', 'manager_approved')
        employee_id = request.args.get('employee_id')
        
        # Build query - Look for OTRequest with manager_approved status
        query = OTRequest.query
        
        # Filter by company
        user_company_id = None
        if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        if user_company_id:
            query = query.filter(OTRequest.company_id == user_company_id)
        
        # Filter by status (only show manager_approved and hr_rejected for review)
        if status and status != 'all':
            query = query.filter(OTRequest.status.in_([status, 'hr_rejected']))
        else:
            query = query.filter(OTRequest.status.in_(['manager_approved', 'hr_rejected']))
        
        # Filter by employee
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        # Get paginated results
        page = request.args.get('page', 1, type=int)
        requests = query.order_by(OTRequest.created_at.asc()).paginate(page=page, per_page=20)
        
        # Get statistics
        if user_company_id:
            manager_approved_count = OTRequest.query.filter(
                OTRequest.company_id == user_company_id,
                OTRequest.status == 'manager_approved'
            ).count()
            hr_approved_count = OTRequest.query.filter(
                OTRequest.company_id == user_company_id,
                OTRequest.status == 'hr_approved'
            ).count()
            hr_rejected_count = OTRequest.query.filter(
                OTRequest.company_id == user_company_id,
                OTRequest.status == 'hr_rejected'
            ).count()
        else:
            manager_approved_count = OTRequest.query.filter_by(status='manager_approved').count()
            hr_approved_count = OTRequest.query.filter_by(status='hr_approved').count()
            hr_rejected_count = OTRequest.query.filter_by(status='hr_rejected').count()
        
        stats = {
            'manager_approved': manager_approved_count,
            'hr_approved': hr_approved_count,
            'hr_rejected': hr_rejected_count,
        }
        
        # Get employees for filter dropdown
        employees = []
        if user_company_id:
            employees = Employee.query.filter_by(company_id=user_company_id).all()
        
        return render_template('ot/requests.html',
                             requests=requests,
                             stats=stats,
                             status=status,
                             employees=employees,
                             selected_employee=employee_id,
                             approval_level='HR')
    
    except Exception as e:
        logger.error(f"Error in ot_requests: {str(e)}")
        flash('Error loading OT requests', 'danger')
        return redirect(url_for('dashboard'))


# ============ MANAGER APPROVAL DASHBOARD (Level 1) ============
@app.route('/ot/manager-approval', methods=['GET', 'POST'])
@login_required
def ot_manager_approval():
    """
    Manager Dashboard - Managers approve/reject Level 1 OT
    Shows: OT with status = 'pending_manager' assigned to this manager
    
    Actions:
    - Manager Approves → Status = 'manager_approved' → Creates Level 2 for HR
    - Manager Rejects → Status = 'manager_rejected' → Back to Employee
    """
    try:
        # Get current user's employee profile to find OT assigned to them as manager
        if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
            flash('No employee profile found', 'danger')
            return redirect(url_for('dashboard'))
        
        manager_employee = current_user.employee_profile
        
        # Check if this user is a manager
        if not manager_employee.is_manager:
            flash('You are not configured as a manager', 'danger')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            # Handle approval actions
            try:
                ot_request_id = request.form.get('ot_request_id')
                action = request.form.get('action')  # approve or reject
                comments = request.form.get('comments', '')
                modified_hours = request.form.get('modified_hours')
                
                logger.info(f"[OT_APPROVAL] POST received - Request ID: {ot_request_id}, Action: {action}")
                
                ot_request = OTRequest.query.get(ot_request_id)
                if not ot_request:
                    flash('OT request not found', 'danger')
                    return redirect(url_for('ot_manager_approval'))
                
                # Verify the OT is assigned to this manager
                ot_approval = OTApproval.query.filter_by(
                    ot_request_id=ot_request_id,
                    approval_level=1
                ).first()
                
                if not ot_approval or ot_approval.approver_id != current_user.id:
                    flash('This OT is not assigned to you for approval', 'danger')
                    return redirect(url_for('ot_manager_approval'))
                
                if action == 'approve':
                    logger.info(f"[OT_APPROVAL] Processing APPROVE action for approval ID: {ot_approval.id}")
                    
                    # Manager Approves
                    ot_approval.status = 'manager_approved'
                    ot_approval.comments = comments
                    if modified_hours:
                        ot_approval.approved_hours = float(modified_hours)
                        ot_request.approved_hours = float(modified_hours)
                    # Don't update created_at - it's immutable. Use created_at for record creation time
                    
                    # Update OTRequest status
                    ot_request.status = 'manager_approved'
                    logger.info(f"[OT_APPROVAL] Updated approval and request to manager_approved")
                    
                    # Create Level 2 OTApproval for HR Manager
                    # Get HR Manager (user with HR Manager role)
                    logger.info(f"[OT_APPROVAL] Looking for HR Manager role...")
                    hr_manager_role = Role.query.filter_by(name='HR Manager').first()
                    
                    if not hr_manager_role:
                        logger.error("HR Manager role not found in database")
                        flash('Error: HR Manager role not configured. Contact administrator.', 'danger')
                        return redirect(url_for('ot_manager_approval'))
                    
                    logger.info(f"[OT_APPROVAL] Found HR Manager role, querying users...")
                    hr_managers = User.query.filter_by(role_id=hr_manager_role.id).all()
                    logger.info(f"[OT_APPROVAL] Found {len(hr_managers)} HR Manager(s)")
                    
                    if not hr_managers:
                        logger.warning("[OT_APPROVAL] No HR Manager found for level 2 approval")
                        flash('Warning: No HR Manager found for level 2 approval', 'warning')
                    else:
                        # Create approval for first available HR Manager (or can assign logic)
                        hr_manager = hr_managers[0]
                        logger.info(f"[OT_APPROVAL] Creating Level 2 approval for HR Manager ID: {hr_manager.id}")
                        ot_approval_l2 = OTApproval(
                            ot_request_id=ot_request.id,
                            approver_id=hr_manager.id,
                            approval_level=2,
                            status='pending_hr',
                            comments=f'Approved by {current_user.full_name} ({manager_employee.first_name}), pending HR Manager approval'
                        )
                        db.session.add(ot_approval_l2)
                        logger.info(f"[OT_APPROVAL] Level 2 approval object added to session")
                    
                    # ✅ NEW: Auto-create OTDailySummary record for HR Manager to fill allowances
                    logger.info(f"[OT_APPROVAL] Creating OTDailySummary record for payroll grid...")
                    logger.info(f"[OT_APPROVAL] OT Request: emp_id={ot_request.employee_id}, date={ot_request.ot_date}, company={ot_request.company_id}")
                    try:
                        # Get employee and their OT rate
                        employee = Employee.query.get(ot_request.employee_id)
                        if employee:
                            logger.info(f"[OT_APPROVAL] Found employee: {employee.first_name} {employee.last_name}")
                            
                            # Get OT rate from PayrollConfiguration
                            ot_rate = 0
                            if employee.payroll_config and employee.payroll_config.ot_rate_per_hour:
                                ot_rate = float(employee.payroll_config.ot_rate_per_hour)
                                logger.info(f"[OT_APPROVAL] OT Rate from PayrollConfiguration: ₹{ot_rate}")
                            elif employee.hourly_rate:
                                ot_rate = float(employee.hourly_rate)
                                logger.info(f"[OT_APPROVAL] OT Rate from Employee hourly_rate: ₹{ot_rate}")
                            else:
                                logger.warning(f"[OT_APPROVAL] ⚠️ NO OT RATE FOUND! Please set in Masters > Payroll Configuration")
                            
                            # Calculate OT amount
                            approved_hours = ot_request.approved_hours or ot_request.requested_hours or 0
                            ot_amount = float(approved_hours) * ot_rate
                            logger.info(f"[OT_APPROVAL] OT Calculation: {approved_hours} hours × ₹{ot_rate} = ₹{ot_amount}")
                            
                            # Check if OTDailySummary already exists for this employee/date
                            existing_summary = OTDailySummary.query.filter_by(
                                employee_id=ot_request.employee_id,
                                ot_date=ot_request.ot_date
                            ).first()
                            
                            if not existing_summary:
                                # Create new OTDailySummary record
                                logger.info(f"[OT_APPROVAL] Creating NEW OTDailySummary record...")
                                ot_summary = OTDailySummary(
                                    employee_id=ot_request.employee_id,
                                    company_id=ot_request.company_id,
                                    ot_request_id=ot_request.id,
                                    ot_date=ot_request.ot_date,
                                    ot_hours=approved_hours,
                                    ot_rate_per_hour=ot_rate,
                                    ot_amount=ot_amount,
                                    status='Draft',
                                    created_by=current_user.username
                                )
                                db.session.add(ot_summary)
                                logger.info(f"[OT_APPROVAL] ✅ OTDailySummary created successfully for employee {employee.id} on {ot_request.ot_date}")
                                logger.info(f"[OT_APPROVAL] Grid will show this record when HR Manager filters by date: {ot_request.ot_date}")
                            else:
                                # Update existing record with OT hours and amount
                                logger.info(f"[OT_APPROVAL] UPDATING existing OTDailySummary record...")
                                existing_summary.ot_hours = approved_hours
                                existing_summary.ot_rate_per_hour = ot_rate
                                existing_summary.ot_amount = ot_amount
                                existing_summary.ot_request_id = ot_request.id
                                existing_summary.modified_by = current_user.username
                                existing_summary.modified_at = datetime.now()
                                logger.info(f"[OT_APPROVAL] ✅ OTDailySummary updated successfully for employee {employee.id} on {ot_request.ot_date}")
                        else:
                            logger.error(f"[OT_APPROVAL] ❌ Employee {ot_request.employee_id} NOT FOUND! Cannot create OTDailySummary")
                    except Exception as e:
                        logger.error(f"[OT_APPROVAL] ❌ Error creating OTDailySummary: {str(e)}", exc_info=True)
                        # Don't fail the approval if summary creation fails
                    
                    logger.info(f"[OT_APPROVAL] Ready to commit changes...")
                    flash(f'✓ OT Approved. Sent to HR Manager for final approval.', 'success')
                
                elif action == 'reject':
                    # Manager Rejects
                    ot_approval.status = 'manager_rejected'
                    ot_approval.comments = comments
                    # Don't update created_at - it's immutable. It tracks when the approval record was created
                    
                    # Update OTRequest status
                    ot_request.status = 'manager_rejected'
                    
                    # Reset OTAttendance back to Draft for employee to re-mark
                    ot_attendance = OTAttendance.query.filter_by(
                        employee_id=ot_request.employee_id,
                        ot_date=ot_request.ot_date
                    ).first()
                    
                    if ot_attendance:
                        ot_attendance.status = 'Draft'
                        ot_attendance.modified_at = datetime.now()
                    
                    flash(f'✗ OT Rejected. Returned to employee to re-mark.', 'danger')
                
                logger.info(f"[OT_APPROVAL] About to commit all changes...")
                db.session.commit()
                logger.info(f"[OT_APPROVAL] ✓ Commit successful! Redirecting to dashboard...")
                return redirect(url_for('ot_manager_approval'))
            
            except Exception as e:
                logger.error(f"[OT_APPROVAL] ✗ Exception occurred: {str(e)}", exc_info=True)
                db.session.rollback()
                flash(f'Error: {str(e)}', 'danger')
                logger.error(f"Error processing manager approval: {str(e)}")
                return redirect(url_for('ot_manager_approval'))
        
        # GET: Display OT pending manager approval
        query = OTApproval.query.filter(
            OTApproval.approver_id == current_user.id,
            OTApproval.approval_level == 1,
            OTApproval.status == 'pending_manager'
        )
        
        page = request.args.get('page', 1, type=int)
        pending_approvals = query.order_by(OTApproval.created_at.asc()).paginate(page=page, per_page=20)
        
        # Get statistics for this manager
        pending_count = OTApproval.query.filter(
            OTApproval.approver_id == current_user.id,
            OTApproval.approval_level == 1,
            OTApproval.status == 'pending_manager'
        ).count()
        
        approved_count = OTApproval.query.filter(
            OTApproval.approver_id == current_user.id,
            OTApproval.approval_level == 1,
            OTApproval.status == 'manager_approved'
        ).count()
        
        rejected_count = OTApproval.query.filter(
            OTApproval.approver_id == current_user.id,
            OTApproval.approval_level == 1,
            OTApproval.status == 'manager_rejected'
        ).count()
        
        stats = {
            'pending': pending_count,
            'approved': approved_count,
            'rejected': rejected_count,
        }
        
        return render_template('ot/manager_approval_dashboard.html',
                             pending_approvals=pending_approvals,
                             stats=stats,
                             manager_name=manager_employee.first_name)
    
    except Exception as e:
        logger.error(f"Error in ot_manager_approval: {str(e)}")
        flash('Error loading manager approval dashboard', 'danger')
        return redirect(url_for('dashboard'))


# ============ OT APPROVAL DASHBOARD - HR Manager (Level 2) ============
@app.route('/ot/approval', methods=['GET', 'POST'])
@login_required
def ot_approval():
    """
    HR Manager Approval Dashboard - Final approval level
    Shows: OT with status = 'pending_hr' or 'hr_rejected' (waiting HR approval)
    
    Actions:
    - HR Approves → Status = 'hr_approved' → Ready for Payroll
    - HR Rejects → Status = 'hr_rejected' → Back to Manager (creates Level 1 again)
    """
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied. OT Approval is only for HR Manager and above.', 'danger')
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            try:
                ot_request_id = request.form.get('ot_request_id')
                action = request.form.get('action')  # approve or reject
                comments = request.form.get('comments', '')
                modified_hours = request.form.get('modified_hours')

                # Get allowance fields
                allowances = {
                    'kd_and_claim': request.form.get('kd_and_claim', type=float) or 0,
                    'trips': request.form.get('trips', type=float) or 0,
                    'sinpost': request.form.get('sinpost', type=float) or 0,
                    'sandstone': request.form.get('sandstone', type=float) or 0,
                    'spx': request.form.get('spx', type=float) or 0,
                    'psle': request.form.get('psle', type=float) or 0,
                    'manpower': request.form.get('manpower', type=float) or 0,
                    'stacking': request.form.get('stacking', type=float) or 0,
                    'dispose': request.form.get('dispose', type=float) or 0,
                    'night': request.form.get('night', type=float) or 0,
                    'ph': request.form.get('ph', type=float) or 0,
                    'sun': request.form.get('sun', type=float) or 0,
                }

                ot_request = OTRequest.query.get(ot_request_id)
                if not ot_request:
                    flash('OT request not found', 'danger')
                    return redirect(url_for('ot_approval'))
                
                # Check company access
                user_company_id = None
                if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
                    user_company_id = current_user.employee_profile.company_id
                
                if user_company_id and ot_request.company_id != user_company_id:
                    flash('Access Denied', 'danger')
                    return redirect(url_for('ot_approval'))
                
                # Get Level 2 approval record
                ot_approval_l2 = OTApproval.query.filter_by(
                    ot_request_id=ot_request_id,
                    approval_level=2
                ).first()
                
                if not ot_approval_l2:
                    flash('HR approval record not found', 'danger')
                    return redirect(url_for('ot_approval'))
                
                if action == 'approve':
                    # HR Approves - FINAL APPROVAL
                    ot_approval_l2.status = 'hr_approved'
                    ot_approval_l2.comments = comments
                    if modified_hours:
                        ot_approval_l2.approved_hours = float(modified_hours)
                        ot_request.approved_hours = float(modified_hours)

                    # ✅ Update OTDailySummary with hours and allowances
                    ot_summary = OTDailySummary.query.filter_by(ot_request_id=ot_request_id).first()
                    if ot_summary:
                        if modified_hours:
                            ot_amount = float(modified_hours) * float(ot_summary.ot_rate_per_hour or 0)
                            ot_summary.ot_hours = float(modified_hours)
                            ot_summary.ot_amount = ot_amount

                        # Update allowances from form data
                        for allowance_field, value in allowances.items():
                            setattr(ot_summary, allowance_field, value)

                        # Calculate totals (total_allowances and total_amount)
                        ot_summary.calculate_totals()

                        ot_summary.status = 'Approved'
                        ot_summary.modified_by = current_user.username
                        ot_summary.modified_at = datetime.now()
                        logger.info(f"[OT_APPROVAL] Updated OTDailySummary with allowances and totals")
                    # Don't update created_at - it's immutable. It tracks when the approval record was created

                    # Update OTRequest status - NOW READY FOR PAYROLL
                    ot_request.status = 'hr_approved'
                    ot_request.approver_id = current_user.id
                    ot_request.approved_at = datetime.now()
                    ot_request.approval_comments = comments

                    flash(f'✓ OT Final Approved with allowances. Ready for Payroll calculation.', 'success')
                
                elif action == 'reject':
                    # HR Rejects - Send back to Manager
                    ot_approval_l2.status = 'hr_rejected'
                    ot_approval_l2.comments = comments
                    # Don't update created_at - it's immutable. It tracks when the approval record was created
                    
                    # Update OTRequest status
                    ot_request.status = 'hr_rejected'
                    
                    # ✅ Mark OTDailySummary as rejected (don't delete, keep audit trail)
                    ot_summary = OTDailySummary.query.filter_by(ot_request_id=ot_request_id).first()
                    if ot_summary:
                        ot_summary.status = 'Rejected'
                        ot_summary.notes = f'Rejected by HR Manager: {comments}'
                        ot_summary.modified_by = current_user.username
                        ot_summary.modified_at = datetime.now()
                        logger.info(f"[OT_APPROVAL] Marked OTDailySummary as Rejected")
                    
                    # Get Level 1 approval and reset it to pending_manager
                    ot_approval_l1 = OTApproval.query.filter_by(
                        ot_request_id=ot_request_id,
                        approval_level=1
                    ).first()
                    
                    if ot_approval_l1:
                        ot_approval_l1.status = 'pending_manager'  # Back to pending for manager review
                        ot_approval_l1.comments = f'{ot_approval_l1.comments}\n\n[HR Rejected - {comments}]'
                    
                    flash(f'✗ OT Rejected. Returned to Manager for review.', 'danger')
                
                db.session.commit()
                return redirect(url_for('ot_approval'))
            
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error processing HR approval: {str(e)}")
                flash(f'Error: {str(e)}', 'danger')
                return redirect(url_for('ot_approval'))
        
        # GET: Display OT pending HR approval
        user_company_id = None
        if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        # Query OTApproval Level 2 with pending_hr status
        query = OTApproval.query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status.in_(['pending_hr', 'hr_rejected'])
        )
        
        if user_company_id:
            query = query.join(OTRequest).filter(OTRequest.company_id == user_company_id)
        
        page = request.args.get('page', 1, type=int)
        pending_approvals = query.order_by(OTApproval.created_at.asc()).paginate(page=page, per_page=20)
        
        # Get statistics
        if user_company_id:
            pending_hr_count = OTApproval.query.join(OTRequest).filter(
                OTApproval.approval_level == 2,
                OTApproval.status == 'pending_hr',
                OTRequest.company_id == user_company_id
            ).count()
            hr_approved_count = OTApproval.query.join(OTRequest).filter(
                OTApproval.approval_level == 2,
                OTApproval.status == 'hr_approved',
                OTRequest.company_id == user_company_id
            ).count()
            hr_rejected_count = OTApproval.query.join(OTRequest).filter(
                OTApproval.approval_level == 2,
                OTApproval.status == 'hr_rejected',
                OTRequest.company_id == user_company_id
            ).count()
        else:
            pending_hr_count = OTApproval.query.filter(
                OTApproval.approval_level == 2,
                OTApproval.status == 'pending_hr'
            ).count()
            hr_approved_count = OTApproval.query.filter(
                OTApproval.approval_level == 2,
                OTApproval.status == 'hr_approved'
            ).count()
            hr_rejected_count = OTApproval.query.filter(
                OTApproval.approval_level == 2,
                OTApproval.status == 'hr_rejected'
            ).count()
        
        stats = {
            'pending_hr': pending_hr_count,
            'hr_approved': hr_approved_count,
            'hr_rejected': hr_rejected_count,
        }
        
        return render_template('ot/approval_dashboard.html',
                             pending_approvals=pending_approvals,
                             stats=stats,
                             approval_level='HR')
    
    except Exception as e:
        logger.error(f"Error in ot_approval: {str(e)}")
        flash('Error loading OT approval dashboard', 'danger')
        return redirect(url_for('dashboard'))


# ============ PAYROLL OT SUMMARY (Only HR-Approved) ============
@app.route('/ot/payroll-summary', methods=['GET'])
@login_required
def ot_payroll_summary():
    """
    Display OT Payroll Summary - Only shows HR-APPROVED OT ready for payroll
    Accessible to HR Manager, Tenant Admin, Super Admin
    
    Only includes: OT with status = 'hr_approved' (final approval complete)
    """
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied. OT Payroll Summary is only for HR Manager and above.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get filter parameters
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        # Build summary query - Only HR-APPROVED OT (status = 'hr_approved')
        query = OTRequest.query.filter_by(status='hr_approved')
        
        user_company_id = None
        if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        if user_company_id:
            query = query.filter_by(company_id=user_company_id)
        
        # Filter by month/year (based on OT date, not approval date)
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date()
        else:
            end_date = datetime(year, month + 1, 1).date()
        
        approved_ots = query.filter(
            OTRequest.ot_date >= start_date,
            OTRequest.ot_date < end_date
        ).all()
        
        # Calculate summary by OT type
        summary = {}
        total_hours = 0
        total_amount = 0
        employee_summary = {}  # Track by employee too
        
        for ot in approved_ots:
            ot_type_obj = ot.ot_type
            ot_type_name = ot_type_obj.name if ot_type_obj else 'General'
            
            if ot_type_name not in summary:
                summary[ot_type_name] = {'hours': 0, 'amount': 0, 'count': 0, 'rate_per_hour': 0}
            
            hours = float(ot.approved_hours or ot.requested_hours or 0)
            
            # Get Employee's Rate/Hour from master (primary source)
            employee = ot.employee
            hourly_rate = float(employee.hourly_rate) if employee and employee.hourly_rate else 0
            
            # Apply OT Type rate multiplier if present
            rate_multiplier = float(ot_type_obj.rate_multiplier or 1.0) if ot_type_obj else 1.0
            
            # Calculate OT amount using Employee's Rate/Hour × Multiplier
            amount = hours * hourly_rate * rate_multiplier if hourly_rate else 0
            
            # Track rate per hour for display
            summary[ot_type_name]['rate_per_hour'] = hourly_rate * rate_multiplier
            
            summary[ot_type_name]['hours'] += hours
            summary[ot_type_name]['amount'] += amount
            summary[ot_type_name]['count'] += 1
            
            # Track by employee
            emp_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"
            if emp_name not in employee_summary:
                employee_summary[emp_name] = {'hours': 0, 'amount': 0, 'hourly_rate': 0}
            employee_summary[emp_name]['hours'] += hours
            employee_summary[emp_name]['amount'] += amount
            employee_summary[emp_name]['hourly_rate'] = hourly_rate
            
            total_hours += hours
            total_amount += amount
        
        return render_template('ot/payroll_summary.html',
                             summary=summary,
                             employee_summary=employee_summary,
                             total_hours=total_hours,
                             total_amount=total_amount,
                             month=month,
                             year=year,
                             status_label='HR Approved')
    
    except Exception as e:
        logger.error(f"Error in ot_payroll_summary: {str(e)}")
        flash('Error loading OT payroll summary', 'danger')
        return redirect(url_for('dashboard'))


# ============ OT DAILY SUMMARY GRID (HR Manager Payroll Summary) ============
@app.route('/ot/daily-summary', methods=['GET', 'POST'])
@login_required
def ot_daily_summary():
    """
    OT Daily Summary Grid - HR Manager Dashboard for Payroll Summary
    Shows daily OT records with editable allowance columns
    Accessible to HR Manager, Tenant Admin, Super Admin
    """
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            flash('Access Denied. OT Daily Summary is only for HR Manager and above.', 'danger')
            return redirect(url_for('dashboard'))
        
        # Get filter parameters
        filter_date_str = request.args.get('date') or request.form.get('date')
        if not filter_date_str:
            filter_date = datetime.now().date()
        else:
            filter_date = datetime.strptime(filter_date_str, '%Y-%m-%d').date()
        
        # Get user's company
        user_company_id = None
        if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        # Query OT Daily Summary for the selected date (exclude rejected records)
        query = OTDailySummary.query.filter_by(ot_date=filter_date)
        
        # ✅ Only show Draft and Submitted records (exclude Rejected, Finalized, etc.)
        query = query.filter(OTDailySummary.status.in_(['Draft', 'Submitted']))
        
        if user_company_id:
            query = query.filter_by(company_id=user_company_id)
        
        ot_records = query.order_by(OTDailySummary.employee_id.asc()).all()
        
        # Get statistics for the day
        stats = {
            'total_records': len(ot_records),
            'total_ot_hours': sum(float(r.ot_hours or 0) for r in ot_records),
            'total_ot_amount': sum(float(r.ot_amount or 0) for r in ot_records),
            'total_allowances': sum(float(r.total_allowances or 0) for r in ot_records),
            'total_amount': sum(float(r.total_amount or 0) for r in ot_records),
        }
        
        return render_template('ot/daily_summary_grid.html',
                             ot_records=ot_records,
                             filter_date=filter_date,
                             stats=stats)
    
    except Exception as e:
        logger.error(f"Error in ot_daily_summary: {str(e)}")
        flash(f'Error loading OT daily summary: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))


@app.route('/ot/daily-summary/add', methods=['POST'])
@login_required
def ot_daily_summary_add():
    """Add new employee to OT Daily Summary for manual OT entry"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            return jsonify({'error': 'Access Denied'}), 403
        
        employee_id = request.form.get('employee_id', type=int)
        ot_date_str = request.form.get('ot_date')
        
        if not employee_id or not ot_date_str:
            return jsonify({'error': 'Missing employee_id or ot_date'}), 400
        
        ot_date = datetime.strptime(ot_date_str, '%Y-%m-%d').date()
        
        # Check if employee exists and get their payroll config
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Check access to this employee's company
        user_company_id = None
        if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        if user_company_id and employee.company_id != user_company_id:
            return jsonify({'error': 'Access Denied'}), 403
        
        # Check if record already exists
        existing = OTDailySummary.query.filter_by(employee_id=employee_id, ot_date=ot_date).first()
        if existing:
            return jsonify({'error': 'Record already exists for this employee and date'}), 400
        
        # Get OT rate from payroll config
        payroll_config = PayrollConfiguration.query.filter_by(employee_id=employee_id).first()
        ot_rate = float(payroll_config.ot_rate_per_hour or 0) if payroll_config else 0
        
        # Create new OT Daily Summary record
        ot_summary = OTDailySummary(
            employee_id=employee_id,
            company_id=employee.company_id,
            ot_date=ot_date,
            ot_rate_per_hour=ot_rate,
            created_by=current_user.username,
            status='Draft'
        )
        
        db.session.add(ot_summary)
        db.session.commit()
        
        logger.info(f"OT Daily Summary created: Employee {employee_id}, Date {ot_date}")
        
        return jsonify({
            'success': True,
            'id': ot_summary.id,
            'message': f'OT record created for {employee.first_name} {employee.last_name}'
        })
    
    except Exception as e:
        logger.error(f"Error in ot_daily_summary_add: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/ot/daily-summary/update/<int:summary_id>', methods=['POST'])
@login_required
def ot_daily_summary_update(summary_id):
    """Update OT Daily Summary record with hours and allowances"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            return jsonify({'error': 'Access Denied'}), 403
        
        ot_summary = OTDailySummary.query.get(summary_id)
        if not ot_summary:
            return jsonify({'error': 'Record not found'}), 404
        
        # Check access to this employee's company
        user_company_id = None
        if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        if user_company_id and ot_summary.company_id != user_company_id:
            return jsonify({'error': 'Access Denied'}), 403
        
        # Update fields
        ot_hours = request.form.get('ot_hours', type=float)
        if ot_hours is not None:
            ot_summary.ot_hours = ot_hours
            # Calculate OT amount
            ot_rate = float(ot_summary.ot_rate_per_hour or 0)
            ot_summary.ot_amount = ot_hours * ot_rate if ot_rate else 0
        
        # Update allowances
        allowance_fields = ['kd_and_claim', 'trips', 'sinpost', 'sandstone', 'spx', 'psle', 
                           'manpower', 'stacking', 'dispose', 'night', 'ph', 'sun']
        
        for field in allowance_fields:
            value = request.form.get(field, type=float)
            if value is not None:
                setattr(ot_summary, field, value)
        
        # Calculate totals
        ot_summary.calculate_totals()
        
        # Update metadata
        ot_summary.modified_by = current_user.username
        ot_summary.modified_at = datetime.now()
        ot_summary.notes = request.form.get('notes', '')
        
        db.session.commit()
        
        logger.info(f"OT Daily Summary updated: ID {summary_id}")
        
        return jsonify({
            'success': True,
            'message': 'OT record updated successfully',
            'total_amount': float(ot_summary.total_amount or 0)
        })
    
    except Exception as e:
        logger.error(f"Error in ot_daily_summary_update: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/ot/daily-summary/calendar/<int:employee_id>', methods=['GET'])
@login_required
def ot_daily_summary_calendar(employee_id):
    """Get date-wise OT amounts for calendar view"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            return jsonify({'error': 'Access Denied'}), 403
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Employee not found'}), 404
        
        # Check access to this employee's company
        user_company_id = None
        if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        if user_company_id and employee.company_id != user_company_id:
            return jsonify({'error': 'Access Denied'}), 403
        
        # Get current month OT records
        current_date = datetime.now().date()
        month_start = current_date.replace(day=1)
        if current_date.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)
        
        records = OTDailySummary.query.filter(
            OTDailySummary.employee_id == employee_id,
            OTDailySummary.ot_date >= month_start,
            OTDailySummary.ot_date < month_end
        ).all()
        
        # Build calendar data
        calendar_data = {}
        for record in records:
            date_key = record.ot_date.isoformat()
            calendar_data[date_key] = {
                'hours': float(record.ot_hours or 0),
                'amount': float(record.ot_amount or 0),
                'allowances': float(record.total_allowances or 0),
                'total': float(record.total_amount or 0)
            }
        
        return jsonify({
            'employee_id': employee_id,
            'employee_name': f"{employee.first_name} {employee.last_name}",
            'month': current_date.month,
            'year': current_date.year,
            'calendar_data': calendar_data
        })
    
    except Exception as e:
        logger.error(f"Error in ot_daily_summary_calendar: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/employees', methods=['GET'])
@login_required
def api_get_employees():
    """API endpoint to get list of employees for the user's company"""
    try:
        # Check access control
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            return jsonify({'error': 'Access Denied'}), 403
        
        # Get user's company
        user_company_id = None
        if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
            user_company_id = current_user.employee_profile.company_id
        
        # Query employees
        query = Employee.query.filter_by(is_active=True)
        
        if user_company_id:
            query = query.filter_by(company_id=user_company_id)
        
        employees = query.order_by(Employee.first_name.asc()).all()
        
        emp_list = []
        for emp in employees:
            emp_list.append({
                'id': emp.id,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'employee_id': emp.employee_id or '',
                'department_id': emp.department_id,
                'department_name': emp.department.name if emp.department else ''
            })
        
        return jsonify(emp_list)
    
    except Exception as e:
        logger.error(f"Error in api_get_employees: {str(e)}")
        return jsonify({'error': str(e)}), 500


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
            user_company_id = None
            if hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
                user_company_id = current_user.employee_profile.company_id
            if user_company_id and record.company_id != user_company_id:
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