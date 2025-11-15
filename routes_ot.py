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
            
            # Create OT Request with pending_manager status
            ot_request = OTRequest(
                employee_id=employee.id,
                company_id=employee.company_id,
                ot_date=ot_attendance.ot_date,
                ot_type_id=ot_attendance.ot_type_id,
                requested_hours=ot_attendance.ot_hours or 0,
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
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error submitting OT: {str(e)}")
            flash(f'Error submitting OT: {str(e)}', 'danger')
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
                    # Manager Approves
                    ot_approval.status = 'manager_approved'
                    ot_approval.comments = comments
                    if modified_hours:
                        ot_approval.approved_hours = float(modified_hours)
                        ot_request.approved_hours = float(modified_hours)
                    ot_approval.created_at = datetime.now()  # Update timestamp
                    
                    # Update OTRequest status
                    ot_request.status = 'manager_approved'
                    
                    # Create Level 2 OTApproval for HR Manager
                    # Get HR Manager (user with HR Manager role)
                    hr_manager_role = Role.query.filter_by(name='HR Manager').first()
                    hr_managers = User.query.filter_by(role_id=hr_manager_role.id if hr_manager_role else None).all()
                    
                    if not hr_managers:
                        flash('Warning: No HR Manager found for level 2 approval', 'warning')
                    else:
                        # Create approval for first available HR Manager (or can assign logic)
                        hr_manager = hr_managers[0]
                        ot_approval_l2 = OTApproval(
                            ot_request_id=ot_request.id,
                            approver_id=hr_manager.id,
                            approval_level=2,
                            status='pending_hr',
                            comments=f'Approved by {current_user.full_name} ({manager_employee.first_name}), pending HR Manager approval'
                        )
                        db.session.add(ot_approval_l2)
                    
                    flash(f'✓ OT Approved. Sent to HR Manager for final approval.', 'success')
                
                elif action == 'reject':
                    # Manager Rejects
                    ot_approval.status = 'manager_rejected'
                    ot_approval.comments = comments
                    ot_approval.created_at = datetime.now()
                    
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
                
                db.session.commit()
                return redirect(url_for('ot_manager_approval'))
            
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error processing manager approval: {str(e)}")
                flash(f'Error: {str(e)}', 'danger')
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
                    ot_approval_l2.created_at = datetime.now()
                    
                    # Update OTRequest status - NOW READY FOR PAYROLL
                    ot_request.status = 'hr_approved'
                    ot_request.approver_id = current_user.id
                    ot_request.approved_at = datetime.now()
                    ot_request.approval_comments = comments
                    
                    flash(f'✓ OT Final Approved. Ready for Payroll calculation.', 'success')
                
                elif action == 'reject':
                    # HR Rejects - Send back to Manager
                    ot_approval_l2.status = 'hr_rejected'
                    ot_approval_l2.comments = comments
                    ot_approval_l2.created_at = datetime.now()
                    
                    # Update OTRequest status
                    ot_request.status = 'hr_rejected'
                    
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
                summary[ot_type_name] = {'hours': 0, 'amount': 0, 'count': 0}
            
            hours = float(ot.approved_hours or ot.requested_hours or 0)
            # Calculate rate multiplier for amount
            rate_multiplier = float(ot_type_obj.rate_multiplier or 1.0) if ot_type_obj else 1.0
            # Assume hourly_rate from employee or use ot_type rate
            employee = ot.employee
            hourly_rate = float(employee.hourly_rate) if employee and employee.hourly_rate else 0
            amount = hours * hourly_rate * rate_multiplier if hourly_rate else 0
            
            summary[ot_type_name]['hours'] += hours
            summary[ot_type_name]['amount'] += amount
            summary[ot_type_name]['count'] += 1
            
            # Track by employee
            emp_name = f"{employee.first_name} {employee.last_name}" if employee else "Unknown"
            if emp_name not in employee_summary:
                employee_summary[emp_name] = {'hours': 0, 'amount': 0}
            employee_summary[emp_name]['hours'] += hours
            employee_summary[emp_name]['amount'] += amount
            
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