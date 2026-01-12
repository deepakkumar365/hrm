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
from app import app, db
from core.models import OTAttendance, OTApproval, OTRequest, Employee, User, Role, Company, Department, OTType, OTDailySummary, PayrollConfiguration, Attendance, AuditLog
from core.auth import require_login, require_role

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


# ============ TEMPORARY: FIX OT CONSTRAINT ============
@app.route('/admin/setup/fix-ot-constraint', methods=['GET'])
@login_required
def setup_fix_ot_constraint():
    """TEMPORARY: Drop the unique constraint uq_ot_attendance_emp_date to allow multiple OT entries"""
    try:
        # Security: Only allow access in development or from admin
        user_role = current_user.role.name if (hasattr(current_user, 'role') and current_user.role) else None
        if user_role not in ['Super Admin', 'Tenant Admin']:
            return jsonify({'error': 'Unauthorized'}), 403
        
        from sqlalchemy import text
        
        # SQL to drop the constraint
        sql = text("ALTER TABLE hrm_ot_attendance DROP CONSTRAINT IF EXISTS uq_ot_attendance_emp_date")
        
        logger.info("Dropping constraint uq_ot_attendance_emp_date...")
        db.session.execute(sql)
        db.session.commit()
        logger.info("✅ Constraint dropped successfully")
        
        return jsonify({
            'status': 'success',
            'message': 'Constraint uq_ot_attendance_emp_date dropped successfully!',
            'next_steps': 'You can now log multiple OT entries per day. Try marking OT again.'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error dropping constraint: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/ot/mark', methods=['GET'])
@login_required
def mark_ot_attendance():
    """Mark OT Attendance - Self-service for all employees (except Super Admin)"""
    try:
        # Check access control - Allow all roles except Super Admin to mark their own OT
        # Check access control - Allow all roles except Super Admin to mark their own OT
        # user_role = current_user.role.name if current_user.role else None
        # if user_role == 'Super Admin':
        #     flash('Super Admin cannot mark OT attendance. Use OT Management section.', 'danger')
        #     return redirect(url_for('dashboard'))
        
        # Get employee profile
        if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
            flash('Employee profile required for OT marking', 'danger')
            return redirect(url_for('dashboard'))
        
        employee = current_user.employee_profile
        company_id = employee.company_id
        
        # GET request - Show form
        # Get active OT types for this tenant
        company = Company.query.get(company_id)
        tenant_id = company.tenant_id if company else None
        
        if tenant_id:
            # Fix SAWarning: Pass query directly to in_(), not subquery()
            company_ids = db.session.query(Company.id).filter_by(tenant_id=tenant_id)
            ot_types = OTType.query.filter(
                OTType.company_id.in_(company_ids),
                OTType.is_active == True
            ).order_by(OTType.display_order).all()
        else:
            ot_types = []
        
        if not ot_types:
            flash('⚠️  No OT types are configured for your tenant.', 'warning')
        
        # Get today's date in user's localized timezone
        from core.utils import get_current_user_timezone
        from pytz import timezone, utc
        user_tz_str = get_current_user_timezone()
        user_tz = timezone(user_tz_str)
        now_utc = datetime.now(utc)
        today = now_utc.astimezone(user_tz).date()
        
        # Get today's logs (Drafts and Submitted)
        today_logs = OTAttendance.query.filter_by(
            employee_id=employee.id,
            ot_date=today
        ).order_by(OTAttendance.created_at.desc()).all()
        
        # Get Recent History (Past 5 days excluding today)
        recent_history = OTAttendance.query.filter(
            OTAttendance.employee_id == employee.id,
            OTAttendance.ot_date < today
        ).order_by(OTAttendance.ot_date.desc()).limit(10).all()
        
        # Determine Employee Hourly Rate
        # Priority: PayrollConfig > Employee Profile > Calculated from Basic
        hourly_rate = 0
        if employee.payroll_config and employee.payroll_config.ot_rate_per_hour:
             hourly_rate = float(employee.payroll_config.ot_rate_per_hour)
        elif employee.hourly_rate:
             hourly_rate = float(employee.hourly_rate)
        else:
             # Fallback calculation: Basic / 173.33 (Standard approx hours/month)
             # This is a Rough Estimate if not configured
             if employee.basic_salary:
                 hourly_rate = float(employee.basic_salary) / 173.33
        
        hourly_rate = round(hourly_rate, 2)

        company_timezone = company.timezone if company and company.timezone else 'Asia/Singapore'
        
        # Check if employee has a manager assigned
        has_manager = True if employee.manager_id else False

        return render_template('ot/mark_attendance.html',
                             employee=employee,
                             ot_types=ot_types,
                             today=today,
                             today_logs=today_logs,
                             recent_history=recent_history,
                             hourly_rate=hourly_rate,
                             company_timezone=company_timezone,
                             has_manager=has_manager)
        
    except Exception as e:
        logger.error(f"Error in mark_ot_attendance: {str(e)}")
        flash('Error accessing OT marking form', 'danger')
        return redirect(url_for('dashboard'))


# ============ LOG OT ENTRY (New Log & Go) ============
@app.route('/api/ot/log-entry', methods=['POST'])
@login_required
def log_ot_entry():
    """
    Log a new OT entry (Log & Go).
    Calculates rate and amount, saves as Draft.
    """
    try:
        if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
            return jsonify({'success': False, 'message': 'Employee profile required'}), 403
        
        employee = current_user.employee_profile
        company_id = employee.company_id
        
        data = request.get_json()
        ot_date_str = data.get('ot_date')
        ot_type_id = data.get('ot_type_id')
        quantity = data.get('quantity')
        notes = data.get('notes', '')
        
        if not ot_date_str or not ot_type_id or not quantity:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
        try:
            ot_date = datetime.strptime(ot_date_str, '%Y-%m-%d').date()
            quantity = float(quantity)
            ot_type_id = int(ot_type_id)
        except ValueError:
             return jsonify({'success': False, 'message': 'Invalid data format'}), 400
             
        # Calculate Rate and Amount
        ot_type = OTType.query.get(ot_type_id)
        if not ot_type:
            return jsonify({'success': False, 'message': 'Invalid OT Type'}), 400
            
        # Effective Rate = Multiplier (User simplified logic: Multiplier IS the Rate)
        # We ignore base salary/hourly rate entirely.
        
        multiplier = float(ot_type.rate_multiplier) if ot_type.rate_multiplier else 0.0
        effective_rate = round(multiplier, 2)
        
        # Total Amount
        total_amount = round(effective_rate * quantity, 2)
        
        # Create Record
        new_ot = OTAttendance(
            employee_id=employee.id,
            company_id=company_id,
            ot_date=ot_date,
            ot_type_id=ot_type_id,
            quantity=quantity,
            rate=effective_rate,
            amount=total_amount,
            status='Draft',
            notes=notes,
            created_by=current_user.username,
            # Maintain legacy fields for compatibility if needed
            ot_hours=quantity # Assuming quantity is usually hours for now
        )
        
        db.session.add(new_ot)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'OT Logged Successfully',
            'entry': {
                'id': new_ot.id,
                'ot_type_name': ot_type.name,
                'quantity': quantity,
                'amount': total_amount,
                'status': 'Draft'
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving OT draft: {str(e)}")
        return jsonify({'success': False, 'message': f'Error saving draft: {str(e)}'}), 500


# ============ GET OT DRAFT ============
@app.route('/api/ot/get-draft', methods=['GET'])
@login_required
def get_ot_draft():
    """
    Get existing OT draft for a specific date to populate the form on page load.
    """
    try:
        # Get employee profile
        if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
            return jsonify({'success': False, 'message': 'Employee profile required'}), 403
        
        employee = current_user.employee_profile
        ot_date_str = request.args.get('ot_date')
        
        if not ot_date_str:
            return jsonify({'success': False, 'message': 'OT date is required'}), 400
        
        try:
            ot_date = datetime.strptime(ot_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid date format'}), 400
        
        # Find existing draft for this date (status must be 'Draft')
        ot_record = OTAttendance.query.filter_by(
            employee_id=employee.id,
            ot_date=ot_date,
            status='Draft'
        ).first()
        
        if not ot_record:
            return jsonify({'success': False, 'message': 'No draft found'}), 404
        
        # Build response
        response = {
            'success': True,
            'ot_date': ot_date_str,
            'ot_id': ot_record.id,
            'status': ot_record.status,
            'ot_type_id': ot_record.ot_type_id,
            'notes': ot_record.notes or ''
        }
        
        # Include times only if they exist
        if ot_record.ot_in_time:
            response['ot_in_time'] = ot_record.ot_in_time.strftime('%H:%M')
        
        if ot_record.ot_out_time:
            response['ot_out_time'] = ot_record.ot_out_time.strftime('%H:%M')
        
        if ot_record.ot_hours:
            response['ot_hours'] = ot_record.ot_hours
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting OT draft: {str(e)}")
        return jsonify({'success': False, 'message': f'Error retrieving draft: {str(e)}'}), 500


# ============ HELPER FUNCTION: Get Approval Statuses (Cached) ============
def get_approval_statuses_batch(ot_attendance_records):
    """
    ⚡ OPTIMIZED: Get manager and HR manager approval statuses for multiple OT records in one query.
    This eliminates N+1 query problem by loading all approvals at once.
    """
    # Build map of (employee_id, ot_date) -> record for quick lookup
    record_map = {(r.employee_id, r.ot_date): r for r in ot_attendance_records}
    
    # Get all OT requests for these records
    emp_dates = list(record_map.keys())
    if not emp_dates:
        return
    
    try:
        from sqlalchemy import and_, or_
        
        # Build OR conditions for all employee_id, ot_date pairs
        conditions = [and_(OTRequest.employee_id == emp_id, OTRequest.ot_date == ot_date) 
                     for emp_id, ot_date in emp_dates]
        
        ot_requests = OTRequest.query.filter(or_(*conditions)).all()
        
        # Get all approvals for these requests in one query
        request_ids = [r.id for r in ot_requests]
        if request_ids:
            approvals = OTApproval.query.filter(
                OTApproval.ot_request_id.in_(request_ids)
            ).all()
            
            # Build lookup dicts
            request_map = {(r.employee_id, r.ot_date): r for r in ot_requests}
            approval_map = {}
            for approval in approvals:
                key = (approval.ot_request_id, approval.approval_level)
                approval_map[key] = approval.status
            
            # Attach statuses to records
            for record in ot_attendance_records:
                key = (record.employee_id, record.ot_date)
                ot_request = request_map.get(key)
                
                if ot_request:
                    manager_approval_status = approval_map.get((ot_request.id, 1))
                    hr_approval_status = approval_map.get((ot_request.id, 2))
                else:
                    manager_approval_status = None
                    hr_approval_status = None
                
                record.manager_approval_status = manager_approval_status
                record.hr_approval_status = hr_approval_status
    
    except Exception as e:
        logger.error(f"Error getting approval statuses: {str(e)}")
        # Fallback: set all to None
        for record in ot_attendance_records:
            record.manager_approval_status = None
            record.hr_approval_status = None


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
        # Filter by accessible companies (Tenant Admin vs HR Manager scope)
        if user_role != 'Super Admin':
            accessible_companies = current_user.get_accessible_companies()
            company_ids = [c.id for c in accessible_companies]
            if company_ids:
                query = query.filter(OTAttendance.company_id.in_(company_ids))
            else:
                query = query.filter(OTAttendance.id == None) # Return nothing
        
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
        
        # ⚡ OPTIMIZED: Enrich ALL records with approval statuses in single batch query
        get_approval_statuses_batch(ot_records.items)
        
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
        
        # Validation for Hours/Quantity
        # Logic: Must have explicit quantity OR calculated ot_hours > 0
        has_quantity = ot_attendance.quantity and ot_attendance.quantity > 0
        has_hours = ot_attendance.ot_hours and ot_attendance.ot_hours > 0
        
        if not (has_quantity or has_hours):
             flash('❌ Cannot submit: Invalid Quantity/Hours.', 'danger')
             return redirect(url_for('mark_ot_attendance'))

        # Check if employee has a manager assigned
        if not employee.manager_id:
            flash('❌ Cannot submit: No reporting manager assigned to your profile. Contact HR.', 'danger')
            return redirect(url_for('mark_ot_attendance'))
        
        try:
            # ⚡ OPTIMIZED: Fetch manager with eager-loaded user relationship
            from sqlalchemy.orm import joinedload
            manager = Employee.query.options(
                joinedload(Employee.user)
            ).filter_by(id=employee.manager_id).first()
            
            if not manager or not manager.user_id:
                flash('❌ Your reporting manager does not have a user account. Contact HR.', 'danger')
                return redirect(url_for('mark_ot_attendance'))
            
            # ⚡ OPTIMIZED: Store manager name BEFORE commit
            manager_name = manager.user.full_name if manager.user else manager.first_name
            # Use Quantity as primary if available, else OT hours
            requested_hours = float(ot_attendance.quantity) if ot_attendance.quantity else (float(ot_attendance.ot_hours) if ot_attendance.ot_hours else 0)
            
            # Recalculate amount if 0 (Self-Correction for old records or missing rates)
            current_amount = float(ot_attendance.amount) if ot_attendance.amount else 0
            if current_amount == 0 and requested_hours > 0:
                # Simplified Logic: Rate = Multiplier
                multiplier = float(ot_attendance.ot_type.rate_multiplier) if ot_attendance.ot_type and ot_attendance.ot_type.rate_multiplier else 0.0
                effective_rate = round(multiplier, 2)
                
                calculated_amount = round(effective_rate * requested_hours, 2)
                
                if calculated_amount > 0:
                    ot_attendance.amount = calculated_amount
                    ot_attendance.rate = effective_rate
                    current_amount = calculated_amount
                    logger.info(f"Auto-calculated OT Amount for ID {attendance_id}: {calculated_amount} (Rate: {effective_rate})")

            # Create OT Request with pending_manager status
            # Note: We allow multiple requests per day now
            ot_request = OTRequest(
                employee_id=employee.id,
                company_id=employee.company_id,
                ot_date=ot_attendance.ot_date,
                ot_type_id=ot_attendance.ot_type_id,
                requested_hours=requested_hours,
                amount=current_amount,
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
            ot_attendance.modified_at = datetime.utcnow()
            
            db.session.commit()
            
            flash(f'✅ OT submitted to {manager_name} for approval.', 'success')
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

# ============ DELETE OT ENTRY (Draft Only) ============
@app.route('/api/ot/delete-entry/<int:attendance_id>', methods=['POST'])
@login_required
def delete_ot_entry(attendance_id):
    """
    Delete a Draft OT entry.
    """
    try:
        ot_attendance = OTAttendance.query.get_or_404(attendance_id)
        
        # Verify ownership
        employee = current_user.employee_profile
        if not employee or ot_attendance.employee_id != employee.id:
             return jsonify({'success': False, 'message': 'Unauthorized'}), 403
             
        if ot_attendance.status != 'Draft':
             return jsonify({'success': False, 'message': 'Only drafts can be deleted'}), 400
             
        db.session.delete(ot_attendance)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Entry deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting OT: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500


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
            # ⚡ OPTIMIZED: Get employee with eager-loaded manager.user relationship
            from sqlalchemy.orm import joinedload
            employee = ot_attendance.employee
            if not employee or not employee.manager_id:
                flash('Employee has no reporting manager assigned. Cannot submit for approval.', 'danger')
                return redirect(url_for('ot_attendance'))
            
            manager = Employee.query.options(
                joinedload(Employee.user)
            ).filter_by(id=employee.manager_id).first()
            
            if not manager or not manager.user_id:
                flash('Manager does not have a user account. Cannot submit.', 'danger')
                return redirect(url_for('ot_attendance'))
            
            # ⚡ OPTIMIZED: Store manager name BEFORE commit
            manager_name = manager.user.full_name if manager.user else manager.first_name
            requested_hours = ot_attendance.ot_hours or 0
            
            # Create OT Request with pending_manager status
            ot_request = OTRequest(
                employee_id=ot_attendance.employee_id,
                company_id=ot_attendance.company_id,
                ot_date=ot_attendance.ot_date,
                ot_type_id=ot_attendance.ot_type_id,
                requested_hours=requested_hours,
                amount=ot_attendance.amount or 0,
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
            ot_attendance.modified_at = datetime.utcnow()
            
            db.session.commit()
            
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
        # Filter by accessible companies
        user_company_id = None # Keep variable for stats logic below if needed, but primary filter is list
        
        if user_role != 'Super Admin':
            accessible_companies = current_user.get_accessible_companies()
            company_ids = [c.id for c in accessible_companies]
            
            if company_ids:
                query = query.filter(OTRequest.company_id.in_(company_ids))
                # optimize stats queries below by using list if multiple, or single if only one
            else:
                query = query.filter(OTRequest.id == None)
        
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
        # Get current user's employee profile
        if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
            flash('No employee profile found', 'danger')
            return redirect(url_for('dashboard'))
        
        manager_employee = current_user.employee_profile
        
        # Check if this user is a manager
        if not manager_employee.is_manager:
            flash('You are not configured as a manager', 'danger')
            return redirect(url_for('dashboard'))
            
        # Handle Single Action POST (Legacy support, though we'll move to new Bulk route mostly)
        if request.method == 'POST':
            # Redirect to the new bulk action handler if it's a form submit from the new UI
            # But for now, let's keep the legacy logic inline or just use the separate route.
            # We will implement the logic here to support single actions via the same route if needed,
            # but ideally, the UI will point to the bulk route even for single items.
            pass

        # GET Request - Show Dashboard
        status_filter = request.args.get('status', 'pending') # Default to pending, but UI will have 'all' option
        
        page = request.args.get('page', 1, type=int)
        
        # Base Query: Approvals assigned to this manager (Level 1)
        query = OTApproval.query.filter_by(
            approver_id=current_user.id,
            approval_level=1
        )
        
        # Apply Status Filter
        if status_filter == 'all':
            pass # No filter
        elif status_filter == 'pending':
            query = query.filter_by(status='pending_manager')
        elif status_filter == 'approved':
            query = query.filter_by(status='manager_approved')
        elif status_filter == 'rejected':
            query = query.filter_by(status='manager_rejected')
        
        # Sort by Date (Join with OTRequest)
        # We need to join OTRequest to sort by ot_date usually, or just by created_at
        query = query.join(OTRequest).order_by(OTRequest.ot_date.desc(), OTApproval.created_at.desc())
            
        # Pagination
        approvals = query.paginate(page=page, per_page=20)
            
        # Pagination
        approvals = query.paginate(page=page, per_page=20)
        
        # Stats for the Header
        pending_count = OTApproval.query.filter_by(approver_id=current_user.id, approval_level=1, status='pending_manager').count()
        approved_count = OTApproval.query.filter_by(approver_id=current_user.id, approval_level=1, status='manager_approved').count()
        rejected_count = OTApproval.query.filter_by(approver_id=current_user.id, approval_level=1, status='manager_rejected').count()
        
        stats = {
            'pending': pending_count,
            'approved': approved_count,
            'rejected': rejected_count, 
            'total_history': approved_count + rejected_count
        }

        # Get active OT Types for the modification dropdown
        ot_types = []
        if manager_employee.company_id:
             ot_types = OTType.query.filter_by(company_id=manager_employee.company_id, is_active=True).all()
        # Fallback or additional global types? For now company specific or all if no company set (safer to show none if no company)
        if not ot_types and not manager_employee.company_id:
             # Maybe tenant based? Assuming manager has company.
             pass

        return render_template('ot/manager_approval_dashboard.html',
                             approvals=approvals,
                             stats=stats,
                             ot_types=ot_types,
                             current_filter=status_filter)

    except Exception as e:
        import traceback
        logger.error(f"Error in ot_manager_approval: {str(e)}")
        logger.error(traceback.format_exc())
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/ot/manager/export')
@login_required
def export_ot_manager_report():
    try:
        status_filter = request.args.get('status', 'all')
        
        query = OTApproval.query.filter_by(
            approver_id=current_user.id,
            approval_level=1
        )
        
        if status_filter != 'all':
            if status_filter == 'pending':
                query = query.filter_by(status='pending_manager')
            elif status_filter == 'approved':
                query = query.filter_by(status='manager_approved')
            elif status_filter == 'rejected':
                query = query.filter_by(status='manager_rejected')
        
        # Join with OTRequest to get date
        query = query.join(OTRequest).order_by(OTRequest.ot_date.desc())
        
        approvals = query.all()
        
        # Generate CSV
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow(['Date', 'Employee', 'Type', 'Status', 'Requested Qty', 'Amount', 'Reason', 'Approver Comments', 'Approved/Rejected At'])
        
        for app in approvals:
            req = app.ot_request
            emp = req.employee.first_name + ' ' + req.employee.last_name if req.employee else 'Unknown'
            type_name = req.ot_type.name if req.ot_type else 'Unknown'
            
            writer.writerow([
                req.ot_date,
                emp,
                type_name,
                app.status,
                req.requested_hours,
                req.amount,
                req.reason,
                app.comments,
                app.updated_at or app.created_at
            ])
            
        output.seek(0)
        
        return Response(
            output,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=ot_report.csv"}
        )
        
    except Exception as e:
        logger.error(f"Export Error: {str(e)}")
        flash('Failed to export report', 'danger')
        return redirect(url_for('ot_manager_approval'))


# ============ BULK ACTIONS (Manager) ============
@app.route('/ot/manager-bulk-action', methods=['POST'])
@login_required
def ot_manager_bulk_action():
    """
    Handle Bulk Approve/Reject for Manager
    """
    try:
        action = request.form.get('action') # 'approve' or 'reject'
        approval_ids_str = request.form.get('approval_ids') # Comma separated list
        comments = request.form.get('comments', '')
        
        if not action or not approval_ids_str:
            flash('Invalid action parameters', 'warning')
            return redirect(url_for('ot_manager_approval'))
            
        approval_ids = [int(id) for id in approval_ids_str.split(',') if id.strip()]
        
        if not approval_ids:
            flash('No items selected', 'warning')
            return redirect(url_for('ot_manager_approval'))
            
        success_count = 0
        error_count = 0
        
        for approval_id in approval_ids:
            try:
                # Get Approval Record
                approval = OTApproval.query.get(approval_id)
                
                # Security Check
                if not approval or approval.approver_id != current_user.id or approval.status != 'pending_manager':
                    error_count += 1
                    continue
                
                ot_request = approval.ot_request
                
                if action == 'approve':
                    # Check for modifications
                    modified_date = request.form.get('modified_date')
                    modified_ot_type_id = request.form.get('modified_ot_type')
                    modified_quantity = request.form.get('modified_quantity')
                    modified_amount = request.form.get('modified_amount')
                    modified_reason = request.form.get('modified_reason')

                    # Update Request if modifications exist (only for the specific item if single, or all if bulk? 
                    # The modal usually is for single item modification. If bulk, we skip modification or apply to all?
                    # The current UI modal is per-item. Bulk modify is complex.
                    # Assumption: The modification fields are passed when actioning likely a SINGLE item via the specific form or modal.
                    # However, the form submits to this route. If `approval_ids` contains one ID, we can apply mods. 
                    # If multiple, applying same date/qty is risky.
                    # LIMITATION: Modification only works for single item approval via the modal.
                    
                    # Update Approval Record
                    approval.status = 'manager_approved'
                    approval.comments = comments if comments else 'Approved by Manager'
                    approval.updated_at = datetime.now()
                    
                    # Create Audit Log for Modifications
                    old_amount = ot_request.amount
                    
                    if len(approval_ids) == 1:
                        if modified_date:
                            ot_request.ot_date = datetime.strptime(modified_date, '%Y-%m-%d').date()
                        if modified_ot_type_id:
                            ot_request.ot_type_id = int(modified_ot_type_id)
                        if modified_quantity:
                            ot_request.requested_hours = float(modified_quantity)
                        
                        if modified_amount:
                            new_amount = float(modified_amount)
                            if new_amount != float(old_amount or 0):
                                ot_request.amount = new_amount
                                # Log amendment
                                audit = AuditLog(
                                    user_id=current_user.id,
                                    action='OT_AMOUNT_AMEND_MANAGER',
                                    resource_type='OTRequest',
                                    resource_id=str(ot_request.id),
                                    changes=f'Amount changed from {old_amount} to {new_amount}',
                                    status='Success'
                                )
                                db.session.add(audit)

                        if modified_reason:
                            ot_request.reason = modified_reason
                    
                    # Update Request Status
                    ot_request.status = 'manager_approved'
                    
                    # Create Level 2 Approval (HR)
                    # Find HR Manager to assign
                    hr_approver_id = None
                    hr_role = Role.query.filter_by(name='HR Manager').first()
                    if hr_role:
                        # Find first active HR Manager
                        hr_user = User.query.filter_by(role_id=hr_role.id, is_active=True).first()
                        if hr_user:
                            hr_approver_id = hr_user.id
                    
                    # Fallback: Tenant Admin
                    if not hr_approver_id:
                        admin_role = Role.query.filter_by(name='Tenant Admin').first()
                        if admin_role:
                            admin_user = User.query.filter_by(role_id=admin_role.id, is_active=True).first()
                            if admin_user:
                                hr_approver_id = admin_user.id
                    
                    # Fallback: Super Admin
                    if not hr_approver_id:
                        sa_role = Role.query.filter_by(name='Super Admin').first()
                        if sa_role:
                            sa_user = User.query.filter_by(role_id=sa_role.id, is_active=True).first()
                            if sa_user:
                                hr_approver_id = sa_user.id
                                
                    if not hr_approver_id:
                        raise Exception("Cannot proceed: No valid HR Manager or Admin found to assign next approval level.")

                    hr_approval = OTApproval(
                        ot_request_id=ot_request.id,
                        approver_id=hr_approver_id,
                        approval_level=2,
                        status='pending_hr',
                        comments='Pending HR Approval'
                    )
                    hr_approval = OTApproval(
                        ot_request_id=ot_request.id,
                        approver_id=hr_approver_id,
                        approval_level=2,
                        status='pending_hr',
                        comments='Pending HR Approval'
                    )
                    db.session.add(hr_approval)
                    
                    # Update Original OT Attendance Status
                    ot_attendance = OTAttendance.query.filter_by(
                        employee_id=ot_request.employee_id, 
                        ot_date=ot_request.ot_date
                    ).first()
                    if ot_attendance:
                        ot_attendance.status = 'manager_approved'
                    
                elif action == 'reject':
                    # Update Approval Record
                    approval.status = 'manager_rejected'
                    approval.comments = comments if comments else 'Rejected by Manager'
                    approval.updated_at = datetime.now()
                    
                    # Update Request Status
                    ot_request.status = 'manager_rejected'
                    
                    # Also update the original OT Attendance record to 'Draft' or 'Rejected'?
                    # Workflow says: Back to Employee. 
                    # Usually we update the OTAttendance to 'Rejected' so they can see it and maybe delete/re-submit.
                    ot_attendance = OTAttendance.query.filter_by(
                        employee_id=ot_request.employee_id, 
                        ot_date=ot_request.ot_date
                    ).first()
                    
                    if ot_attendance:
                        ot_attendance.status = 'manager_rejected' # Or 'Draft' if you want them to edit immediately
                        # Let's set to Rejected so history is preserved, they can clone or delete.
                
                success_count += 1
                
            except Exception as e:
                logger.error(f"Error processing approval {approval_id}: {str(e)}")
                error_count += 1
                

        db.session.commit()
        
        if success_count > 0:
            flash(f'Successfully {action}ed {success_count} requests.', 'success')
        if error_count > 0:
            flash(f'Failed to process {error_count} requests.', 'warning')
            
        return redirect(url_for('ot_manager_approval', status='pending'))

    except Exception as e:
        logger.error(f"Error in ot_manager_bulk_action: {str(e)}")
        flash('Error processing bulk action', 'danger')
        return redirect(url_for('ot_manager_approval'))


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
                modified_amount = request.form.get('modified_amount')

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
                    return redirect('/ot/approval')
                
                # Check company access
                user_company_id = None
                if user_role != 'Super Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
                    user_company_id = current_user.employee_profile.company_id
                
                if user_company_id and ot_request.company_id != user_company_id:
                    flash('Access Denied', 'danger')
                    return redirect('/ot/approval')
                
                # Get Level 2 approval record
                ot_approval_l2 = OTApproval.query.filter_by(
                    ot_request_id=ot_request_id,
                    approval_level=2
                ).first()
                
                if not ot_approval_l2:
                    flash('HR approval record not found', 'danger')
                    return redirect('/ot/approval')
                    
                if action == 'approve':
                    # ✅ 1:1 Mapping: Find Summary for THIS Request (or create)
                    ot_summary = OTDailySummary.query.filter_by(
                        ot_request_id=ot_request.id
                    ).first()
                    
                    if not ot_summary:
                        # Create new summary for this request
                        # Simplified Logic: Rate = Multiplier
                        multiplier = float(ot_request.ot_type.rate_multiplier) if ot_request.ot_type and ot_request.ot_type.rate_multiplier else 0.0
                        ot_rate_per_hour = round(multiplier, 2)

                        ot_summary = OTDailySummary(
                            employee_id=ot_request.employee_id,
                            company_id=ot_request.company_id,
                            ot_request_id=ot_request.id, 
                            ot_date=ot_request.ot_date,
                            ot_hours=0, 
                            ot_rate_per_hour=ot_rate_per_hour,
                            ot_amount=0,
                            created_by=current_user.username
                        )
                        db.session.add(ot_summary)
                        logger.info(f"[OT_APPROVAL] Creating 1:1 OTDailySummary for Request {ot_request.id}")
                    
                    # Update Request Status
                    ot_request.status = 'hr_approved'
                    ot_request.approver_id = current_user.id
                    ot_request.approved_at = datetime.now()
                    ot_request.approval_comments = comments
                    ot_request.approved_hours = float(modified_hours) if modified_hours else ot_request.requested_hours
                    
                    # Handle HR Amount Amendment
                    if modified_amount:
                        old_amount = ot_request.amount
                        new_amount = float(modified_amount)
                        if new_amount != float(old_amount or 0):
                            ot_request.amount = new_amount
                            # Log amendment
                            audit = AuditLog(
                                user_id=current_user.id,
                                action='OT_AMOUNT_AMEND_HR',
                                resource_type='OTRequest',
                                resource_id=str(ot_request.id),
                                changes=f'Amount changed from {old_amount} to {new_amount}',
                                status='Success'
                            )
                            db.session.add(audit)

                    db.session.flush()

                    # Calculate Amount for THIS Request
                    h = float(ot_request.approved_hours)
                    
                    # Re-verify rate (in case emp config changed, but sticking to created summary rate is usually safer unless 0)
                    if not ot_summary.ot_rate_per_hour:
                         # recalculate if missing
                         # Simplified Logic: Rate = Multiplier
                         multiplier = float(ot_request.ot_type.rate_multiplier) if ot_request.ot_type and ot_request.ot_type.rate_multiplier else 0.0
                         ot_summary.ot_rate_per_hour = round(multiplier, 2)

                    ot_summary.ot_hours = h
                    ot_summary.ot_amount = round(h * float(ot_summary.ot_rate_per_hour), 2)
                    
                    # Update allowances from form data
                    for allowance_field, value in allowances.items():
                        setattr(ot_summary, allowance_field, value)

                    # Calculate totals
                    ot_summary.calculate_totals()

                    ot_summary.status = 'Approved'
                    ot_summary.modified_by = current_user.username
                    ot_summary.modified_at = datetime.now()
                    
                    flash(f'✓ OT Final Approved. {h}h recorded.', 'success')
                
                elif action == 'reject':
                    # HR Rejects - Send back to Manager
                    ot_approval_l2.status = 'hr_rejected'
                    ot_approval_l2.comments = comments
                    
                    # Update OTRequest status
                    ot_request.status = 'hr_rejected'
                    
                    # Find and update summary if exists (e.g. was previously approved)
                    ot_summary = OTDailySummary.query.filter_by(
                         ot_request_id=ot_request.id
                    ).first()

                    if ot_summary:
                        # Mark as rejected or Zero out
                        ot_summary.ot_hours = 0
                        ot_summary.ot_amount = 0
                        ot_summary.status = 'Rejected'
                        ot_summary.calculate_totals()
                        ot_summary.modified_by = current_user.username
                        ot_summary.modified_at = datetime.now()

                    # Get Level 1 approval and reset it to pending_manager
                    ot_approval_l1 = OTApproval.query.filter_by(
                        ot_request_id=ot_request.id,
                        approval_level=1
                    ).first()
                    
                    if ot_approval_l1:
                        ot_approval_l1.status = 'pending_manager'
                        ot_approval_l1.comments = f'{ot_approval_l1.comments}\n\n[HR Rejected - {comments}]'
                    
                    flash(f'✗ OT Rejected. Returned to Manager for review.', 'danger')
                
                db.session.commit()
                return redirect('/ot/approval')
            
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error processing HR approval: {str(e)}")
                flash(f'Error: {str(e)}', 'danger')
                return redirect('/ot/approval')
        
        # GET: Display OT pending HR approval
        
        if user_role == 'Super Admin':
            company_ids = None # All
            logger.info(f"[OT_APPROVAL_DEBUG] Super Admin - No company filter")
        else:
            accessible_companies = current_user.get_accessible_companies()
            company_ids = [c.id for c in accessible_companies]
            logger.info(f"[OT_APPROVAL_DEBUG] User {current_user.username} - Accessible Companies: {len(company_ids)}")
            if len(company_ids) == 0:
                 logger.warning(f"[OT_APPROVAL_DEBUG] User has NO accessible companies!")
                 flash(f"Debug: You have access to 0 companies. Check your Employee Profile or Access settings.", "warning")
        
        # Query OTApproval Level 2 with pending_hr status
        query = OTApproval.query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status.in_(['pending_hr', 'hr_rejected'])
        )
        
        if company_ids is not None:
            if company_ids:
                 query = query.join(OTRequest).filter(OTRequest.company_id.in_(company_ids))
                 logger.info(f"[OT_APPROVAL_DEBUG] Filtered by {len(company_ids)} companies")
            else:
                 query = query.filter(OTApproval.id == None) # No access
                 logger.warning(f"[OT_APPROVAL_DEBUG] Blocked query due to no company access")

        total_pending = query.count()
        logger.info(f"[OT_APPROVAL_DEBUG] Total Pending found: {total_pending}")
        
        # Consolidate flash
        if company_ids is not None:
            if len(company_ids) > 0:
                 flash(f"Debug: Access to {len(company_ids)} companies. Found {total_pending} pending requests.", "info")
        elif user_role == 'Super Admin':
             flash(f"Debug: Super Admin Access (All Companies). Found {total_pending} pending requests.", "info")
        
        page = request.args.get('page', 1, type=int)
        pending_approvals = query.order_by(OTApproval.created_at.asc()).paginate(page=page, per_page=20)
        
        # Get statistics
        # Reuse filtered base queries or create new ones? Creating new for clarity
        stats_query = OTApproval.query.join(OTRequest)
        if company_ids is not None:
             if company_ids:
                 stats_query = stats_query.filter(OTRequest.company_id.in_(company_ids))
             else:
                 stats_query = stats_query.filter(OTRequest.id == None)

        pending_hr_count = stats_query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status == 'pending_hr'
        ).count()
        
        hr_approved_count = stats_query.filter(
            OTApproval.approval_level == 2,
            OTApproval.status == 'hr_approved'
        ).count()
        
        hr_rejected_count = stats_query.filter(
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
    Filters: Company, User Name, Month, Year
    
    Multi-Company Support:
    - Super Admin: Can see all companies
    - HR Manager: Can see all companies they have access to (via UserCompanyAccess)
    - Tenant Admin: Can see all companies
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
        selected_company_id = request.args.get('company_id', '')
        selected_user_id = request.args.get('user_id', '')
        
        # Build summary query - Only HR-APPROVED OT (status = 'hr_approved')
        query = OTRequest.query.filter_by(status='hr_approved')
        
        # Get list of available companies for dropdown
        # Super Admin sees all companies
        if user_role == 'Super Admin':
            available_companies = Company.query.all()
        # HR Manager and Tenant Admin see all companies they have access to
        else:
            available_companies = current_user.get_accessible_companies()
        
        # Determine which company to filter by
        if selected_company_id:
            query = query.filter_by(company_id=selected_company_id)
            filter_company_id = selected_company_id
        elif available_companies:
            # Default to first available company if user doesn't have access to selected one
            first_company_id = available_companies[0].id if available_companies else None
            if first_company_id:
                query = query.filter_by(company_id=first_company_id)
                filter_company_id = first_company_id
            else:
                filter_company_id = None
        else:
            filter_company_id = None
        
        # Get list of available users/employees for dropdown (based on filtered company)
        if filter_company_id:
            available_employees = Employee.query.filter_by(company_id=filter_company_id).all()
        else:
            available_employees = []
        
        # Apply employee/user filter
        if selected_user_id:
            query = query.filter_by(employee_id=selected_user_id)
        
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
                             available_companies=available_companies,
                             available_employees=available_employees,
                             selected_company_id=selected_company_id,
                             selected_user_id=selected_user_id,
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
        
        # Get current month OT records in user's localized timezone
        from core.utils import get_current_user_timezone
        from pytz import timezone, utc
        user_tz_str = get_current_user_timezone()
        user_tz = timezone(user_tz_str)
        current_date = datetime.now(utc).astimezone(user_tz).date()
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
            'check_in': record.ot_in_time.isoformat() if hasattr(record, 'ot_in_time') and record.ot_in_time else None,
            'check_out': record.ot_out_time.isoformat() if hasattr(record, 'ot_out_time') and record.ot_out_time else None,
            'hours': float(record.ot_hours) if hasattr(record, 'ot_hours') else 0,
            'reason': record.notes if hasattr(record, 'notes') else '',
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


# ============ DELETE DRAFT OT ATTENDANCE ============
@app.route('/api/ot/delete-draft/<int:attendance_id>', methods=['POST'])
@login_required
def delete_draft_ot(attendance_id):
    """Delete a draft OT attendance record - Only allows deletion of records in 'Draft' status"""
    try:
        # Get the OT attendance record
        ot_record = OTAttendance.query.get(attendance_id)
        
        if not ot_record:
            return jsonify({
                'success': False,
                'message': 'OT record not found'
            }), 404
        
        # Security check: Only the record owner or admin can delete
        user_role = current_user.role.name if current_user.role else None
        
        # Get current user's employee ID (not User ID)
        current_user_employee_id = None
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            current_user_employee_id = current_user.employee_profile.id
        
        is_owner = ot_record.employee_id == current_user_employee_id if current_user_employee_id else False
        is_admin = user_role in ['Tenant Admin', 'Super Admin']
        
        if not (is_owner or is_admin):
            logger.warning(f"[OT DELETE] Access denied for user {current_user.id}: not owner (employee_id {current_user_employee_id} vs {ot_record.employee_id}) and not admin (role: {user_role})")
            return jsonify({
                'success': False,
                'message': 'You do not have permission to delete this record'
            }), 403
        
        # Only allow deletion of Draft records
        if ot_record.status != 'Draft':
            return jsonify({
                'success': False,
                'message': f'Cannot delete {ot_record.status} records. Only Draft records can be deleted.'
            }), 400
        
        # Delete the record
        try:
            record_date = ot_record.ot_date.strftime('%d %b %Y') if ot_record.ot_date else 'Unknown date'
            db.session.delete(ot_record)
            db.session.commit()
            
            logger.info(f"[OT DELETE] User {current_user.id} deleted draft OT record {attendance_id} for date {record_date}")
            
            return jsonify({
                'success': True,
                'message': f'Draft OT record for {record_date} has been deleted successfully'
            }), 200
        
        except Exception as db_error:
            db.session.rollback()
            logger.error(f"Database error deleting OT record: {str(db_error)}")
            return jsonify({
                'success': False,
                'message': 'Database error: Could not delete record'
            }), 500
    
    except Exception as e:
        logger.error(f"Error deleting draft OT attendance: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Server error: {str(e)}'
        }), 500
