"""Leave Management Routes"""
from flask import request, render_template, redirect, url_for, jsonify, flash
from flask_login import current_user
from app import app, db
from core.models import Leave, Employee, User, LeaveType, Company, Tenant, EmployeeGroup, EmployeeGroupLeaveAllocation
from core.auth import require_login, require_role
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
        
        # Filter by current user's leaves if they're an employee
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            query = query.filter_by(employee_id=current_user.employee_profile.id)
        
        # Filter by status if provided
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # Paginate results
        leaves = query.order_by(Leave.created_at.desc()).paginate(page=page, per_page=10)
        
        return render_template('leave/list.html', leaves=leaves, status_filter=status_filter)
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


# Leave Request - Approve (Admin/Manager only)
@app.route('/leave/<int:leave_id>/approve', methods=['POST'])
@require_login
def leave_approve(leave_id):
    """Approve a leave request"""
    
    # Check authorization
    if not (hasattr(current_user, 'role') and 
            current_user.role in ['Manager', 'Admin', 'Super Admin']):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        leave = Leave.query.get_or_404(leave_id)
        
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
    
    # Check authorization
    if not (hasattr(current_user, 'role') and 
            current_user.role in ['Manager', 'Admin', 'Super Admin']):
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        leave = Leave.query.get_or_404(leave_id)
        rejection_reason = request.form.get('rejection_reason', '')
        
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


# ==================== LEAVE CONFIGURATION ROUTES ====================

# Leave Type Configuration - List View
@app.route('/leave-configuration', methods=['GET'])
@app.route('/leave-config', methods=['GET'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_configuration():
    """List leave types - configure leaves for the current user's company/tenant"""
    try:
        # Check if LeaveType table exists
        inspector = db.inspect(db.engine)
        if 'hrm_leave_type' not in inspector.get_table_names():
            logger.warning("LeaveType table does not exist. Please run database migrations.")
            flash("Database not initialized. Please run: flask db upgrade", "warning")
            return redirect(url_for('dashboard'))
        
        # Determine if user is Tenant Admin or HR Manager
        company = None
        tenant = None
        
        # Get tenant admin context
        if hasattr(current_user, 'role') and current_user.role:
            role_name = current_user.role.name if hasattr(current_user.role, 'name') else str(current_user.role)
            
            if role_name == 'Tenant Admin' or role_name == 'Super Admin':
                # Get first tenant of the super admin or tenant's tenant
                if role_name == 'Super Admin':
                    # Super Admin can configure for all companies
                    companies = Company.query.filter_by(is_active=True).all()
                else:
                    # Tenant Admin configuration
                    tenants = Tenant.query.filter_by(is_active=True).all()
                    company = None  # Will show all companies of first tenant
            else:
                # HR Manager - get their company
                if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
                    company = current_user.employee_profile.company
        
        # Get company_id from query parameter if provided
        company_id = request.args.get('company_id', type=str)
        
        if company_id:
            company = Company.query.filter_by(id=company_id, is_active=True).first_or_404()
        
        # Get leave types
        if company:
            leave_types = LeaveType.query.filter_by(company_id=company.id).order_by(LeaveType.created_at.desc()).all()
            leave_groups = EmployeeGroup.query.filter_by(company_id=company.id).order_by(EmployeeGroup.created_at.desc()).all()
            companies = [company]
        else:
            leave_types = LeaveType.query.order_by(LeaveType.created_at.desc()).all()
            leave_groups = EmployeeGroup.query.order_by(EmployeeGroup.created_at.desc()).all()
            companies = Company.query.filter_by(is_active=True).all()
        
        # Get all active companies for the dropdown
        all_companies = Company.query.filter_by(is_active=True).all()
        
        return render_template('leave/configuration.html', 
                             leave_types=leave_types,
                             leave_groups=leave_groups, 
                             companies=companies,
                             all_companies=all_companies,
                             selected_company=company)
    except Exception as e:
        logger.error(f"Error loading leave configuration: {e}")
        flash(f"Error loading leave configuration: {str(e)}", "error")
        return redirect(url_for('dashboard'))


# Leave Type Configuration - Create/Edit
@app.route('/leave-configuration/form', methods=['GET', 'POST'])
@app.route('/leave-config/form', methods=['GET', 'POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_configuration_form():
    """Create or edit a leave type"""
    leave_type = None
    
    try:
        leave_type_id = request.args.get('id', type=int)
        company_id = request.args.get('company_id', type=str)
        
        # Validate company_id
        if not company_id:
            flash("Company is required", "error")
            return redirect(url_for('leave_configuration'))
        
        company = Company.query.filter_by(id=company_id, is_active=True).first_or_404()
        
        # If editing, fetch the leave type
        if leave_type_id:
            leave_type = LeaveType.query.filter_by(id=leave_type_id, company_id=company_id).first_or_404()
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            code = request.form.get('code', '').strip().upper()
            description = request.form.get('description', '').strip()
            annual_allocation = request.form.get('annual_allocation', 0, type=int)
            color = request.form.get('color', '#3498db').strip()
            is_active = request.form.get('is_active') == 'on'
            
            # Validation
            if not name:
                flash("Leave type name is required", "error")
                return render_template('leave/configuration_form.html', 
                                     leave_type=leave_type, 
                                     company=company)
            
            if not code:
                flash("Leave type code is required", "error")
                return render_template('leave/configuration_form.html', 
                                     leave_type=leave_type, 
                                     company=company)
            
            if annual_allocation < 0:
                flash("Annual allocation cannot be negative", "error")
                return render_template('leave/configuration_form.html', 
                                     leave_type=leave_type, 
                                     company=company)
            
            try:
                if leave_type:
                    # Update existing leave type
                    leave_type.name = name
                    leave_type.code = code
                    leave_type.description = description
                    leave_type.annual_allocation = annual_allocation
                    leave_type.color = color
                    leave_type.is_active = is_active
                    leave_type.modified_by = current_user.username if hasattr(current_user, 'username') else 'system'
                    leave_type.modified_at = datetime.now()
                    
                    db.session.commit()
                    flash("Leave type updated successfully", "success")
                else:
                    # Check for duplicate
                    existing = LeaveType.query.filter_by(
                        company_id=company_id,
                        name=name
                    ).first()
                    
                    if existing:
                        flash("A leave type with this name already exists for this company", "error")
                        return render_template('leave/configuration_form.html', 
                                             leave_type=leave_type, 
                                             company=company)
                    
                    # Create new leave type
                    leave_type = LeaveType(
                        company_id=company_id,
                        name=name,
                        code=code,
                        description=description,
                        annual_allocation=annual_allocation,
                        color=color,
                        is_active=is_active,
                        created_by=current_user.username if hasattr(current_user, 'username') else 'system'
                    )
                    
                    db.session.add(leave_type)
                    db.session.commit()
                    flash("Leave type created successfully", "success")
                
                return redirect(url_for('leave_configuration', company_id=company_id))
            
            except Exception as e:
                logger.error(f"Error saving leave type: {e}")
                db.session.rollback()
                flash("Error saving leave type", "error")
                return render_template('leave/configuration_form.html', 
                                     leave_type=leave_type, 
                                     company=company)
        
        # GET request - show form
        return render_template('leave/configuration_form.html', 
                             leave_type=leave_type, 
                             company=company)
    
    except Exception as e:
        logger.error(f"Error in leave configuration form: {e}")
        flash("Error loading form", "error")
        return redirect(url_for('leave_configuration'))


# Leave Type Configuration - Delete
@app.route('/leave-configuration/<int:leave_type_id>/delete', methods=['POST'])
@app.route('/leave-config/<int:leave_type_id>/delete', methods=['POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_configuration_delete(leave_type_id):
    """Delete a leave type"""
    try:
        company_id = request.args.get('company_id', type=str)
        
        if not company_id:
            flash("Company is required", "error")
            return redirect(url_for('leave_configuration'))
        
        leave_type = LeaveType.query.filter_by(id=leave_type_id, company_id=company_id).first_or_404()
        
        # Check if leave type is being used in leave requests
        leave_count = Leave.query.filter_by(leave_type=leave_type.name).count()
        
        if leave_count > 0:
            # Don't delete, just deactivate
            leave_type.is_active = False
            leave_type.modified_by = current_user.username if hasattr(current_user, 'username') else 'system'
            leave_type.modified_at = datetime.now()
            db.session.commit()
            flash(f"Leave type deactivated (cannot delete as it's used in {leave_count} leave request(s))", "info")
        else:
            # Safe to delete
            db.session.delete(leave_type)
            db.session.commit()
            flash("Leave type deleted successfully", "success")
        
        return redirect(url_for('leave_configuration', company_id=company_id))
    
    except Exception as e:
        logger.error(f"Error deleting leave type: {e}")
        db.session.rollback()
        flash("Error deleting leave type", "error")
        return redirect(url_for('leave_configuration', company_id=company_id))


# Leave Group Routes
@app.route('/leave-group/form', methods=['GET', 'POST'])
@app.route('/leave-group/<int:group_id>/edit', methods=['GET', 'POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_group_form(group_id=None):
    """Create or edit a leave group"""
    try:
        group = None
        if group_id:
            group = EmployeeGroup.query.get(group_id)
            if not group:
                flash("Leave group not found", "error")
                return redirect(url_for('leave_configuration'))
        
        company_id = request.args.get('company_id')
        company = None
        if company_id:
            company = Company.query.get(company_id)
        
        # Get all active companies for dropdown
        all_companies = Company.query.filter_by(is_active=True).all()
        
        if request.method == 'POST':
            # Get company ID from form
            form_company_id = request.form.get('company_id') or (group.company_id if group else None)
            if not form_company_id:
                flash("Company is required", "error")
                return render_template('leave/leave_group_form.html', 
                                     group=group, company=company, all_companies=all_companies)
            
            company = Company.query.get(form_company_id)
            if not company:
                flash("Invalid company", "error")
                return render_template('leave/leave_group_form.html', 
                                     group=group, company=company, all_companies=all_companies)
            
            name = request.form.get('name', '').strip()
            if not name:
                flash("Group name is required", "error")
                return render_template('leave/leave_group_form.html', 
                                     group=group, company=company, all_companies=all_companies)
            
            description = request.form.get('description', '').strip()
            is_active = bool(request.form.get('is_active'))
            
            if group:
                # Update existing group
                group.name = name
                group.description = description
                group.is_active = is_active
                group.modified_by = current_user.username
                group.modified_at = datetime.now()
                db.session.commit()
                flash("Leave group updated successfully", "success")
            else:
                # Create new group
                group = EmployeeGroup(
                    company_id=company.id,
                    name=name,
                    category='Leave',
                    description=description,
                    is_active=is_active,
                    created_by=current_user.username
                )
                db.session.add(group)
                db.session.commit()
                flash("Leave group created successfully", "success")
            
            return redirect(url_for('leave_configuration', company_id=company.id))
        
        return render_template('leave/leave_group_form.html', 
                             group=group, company=company, all_companies=all_companies)
    
    except Exception as e:
        logger.error(f"Error in leave_group_form: {e}")
        db.session.rollback()
        flash("Error processing leave group", "error")
        return redirect(url_for('leave_configuration'))


@app.route('/leave-group/<int:group_id>/delete', methods=['POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_group_delete(group_id):
    """Delete a leave group"""
    try:
        group = EmployeeGroup.query.get(group_id)
        if not group:
            flash("Leave group not found", "error")
            return redirect(url_for('leave_configuration'))
        
        company_id = group.company_id
        
        # Check if group has assigned employees
        has_employees = Employee.query.filter_by(employee_group_id=group.id).count() > 0
        
        if has_employees:
            # Deactivate instead of delete
            group.is_active = False
            group.modified_by = current_user.username
            group.modified_at = datetime.now()
            db.session.commit()
            flash("Leave group has assigned employees. Group has been deactivated instead.", "warning")
        else:
            # Delete the group and its allocations
            EmployeeGroupLeaveAllocation.query.filter_by(employee_group_id=group.id).delete()
            db.session.delete(group)
            db.session.commit()
            flash("Leave group deleted successfully", "success")
        
        return redirect(url_for('leave_configuration', company_id=company_id))
    
    except Exception as e:
        logger.error(f"Error deleting leave group: {e}")
        db.session.rollback()
        flash("Error deleting leave group", "error")
        return redirect(url_for('leave_configuration'))


@app.route('/leave-group/<int:group_id>/allocation', methods=['GET', 'POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_group_allocation(group_id):
    """Manage leave allocations for a group"""
    try:
        group = EmployeeGroup.query.get(group_id)
        if not group:
            flash("Leave group not found", "error")
            return redirect(url_for('leave_configuration'))
        
        # Get current allocations
        allocations = EmployeeGroupLeaveAllocation.query.filter_by(employee_group_id=group.id).all()
        
        # Get available leave types (not already assigned to this group)
        assigned_leave_types = [a.leave_type_id for a in allocations]
        available_leave_types = LeaveType.query.filter_by(
            company_id=group.company_id,
            is_active=True
        ).filter(~LeaveType.id.in_(assigned_leave_types)).all()
        
        return render_template('leave/leave_group_allocation.html',
                             group=group,
                             allocations=allocations,
                             available_leave_types=available_leave_types)
    
    except Exception as e:
        logger.error(f"Error in leave_group_allocation: {e}")
        flash("Error loading leave allocations", "error")
        return redirect(url_for('leave_configuration'))


@app.route('/leave-group/<int:group_id>/allocation/form', methods=['POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_group_allocation_form(group_id):
    """Add a leave type to a group"""
    try:
        group = EmployeeGroup.query.get(group_id)
        if not group:
            flash("Leave group not found", "error")
            return redirect(url_for('leave_configuration'))
        
        leave_type_id = request.form.get('leave_type_id')
        annual_allocation = request.form.get('annual_allocation')
        
        if not leave_type_id or not annual_allocation:
            flash("Leave type and allocation are required", "error")
            return redirect(url_for('leave_group_allocation', group_id=group.id))
        
        try:
            annual_allocation = int(annual_allocation)
        except ValueError:
            flash("Invalid allocation value", "error")
            return redirect(url_for('leave_group_allocation', group_id=group.id))
        
        # Check if already assigned
        existing = EmployeeGroupLeaveAllocation.query.filter_by(
            employee_group_id=group.id,
            leave_type_id=leave_type_id
        ).first()
        
        if existing:
            flash("This leave type is already assigned to the group", "warning")
            return redirect(url_for('leave_group_allocation', group_id=group.id))
        
        # Create allocation
        allocation = EmployeeGroupLeaveAllocation(
            employee_group_id=group.id,
            leave_type_id=leave_type_id,
            annual_allocation=annual_allocation
        )
        db.session.add(allocation)
        db.session.commit()
        flash("Leave type assigned to group successfully", "success")
        
        return redirect(url_for('leave_group_allocation', group_id=group.id))
    
    except Exception as e:
        logger.error(f"Error adding leave type to group: {e}")
        db.session.rollback()
        flash("Error assigning leave type", "error")
        return redirect(url_for('leave_group_allocation', group_id=group_id))


@app.route('/leave-group/<int:group_id>/allocation/<int:allocation_id>/delete', methods=['POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_group_allocation_delete(group_id, allocation_id):
    """Remove a leave type from a group"""
    try:
        allocation = EmployeeGroupLeaveAllocation.query.get(allocation_id)
        if not allocation or allocation.employee_group_id != group_id:
            flash("Allocation not found", "error")
            return redirect(url_for('leave_group_allocation', group_id=group_id))
        
        db.session.delete(allocation)
        db.session.commit()
        flash("Leave type removed from group successfully", "success")
        
        return redirect(url_for('leave_group_allocation', group_id=group_id))
    
    except Exception as e:
        logger.error(f"Error deleting leave allocation: {e}")
        db.session.rollback()
        flash("Error removing leave type", "error")
        return redirect(url_for('leave_group_allocation', group_id=group_id))


# API Endpoint - Get leave types by company
@app.route('/api/leave-types', methods=['GET'])
@require_login
def api_get_leave_types():
    """Get leave types for a company - for populating dropdowns in leave requests"""
    try:
        company_id = request.args.get('company_id', type=str)
        
        if not company_id:
            return jsonify({'error': 'Company ID is required'}), 400
        
        leave_types = LeaveType.query.filter_by(
            company_id=company_id,
            is_active=True
        ).all()
        
        return jsonify([{
            'id': lt.id,
            'name': lt.name,
            'code': lt.code,
            'annual_allocation': lt.annual_allocation,
            'color': lt.color
        } for lt in leave_types])
    
    except Exception as e:
        logger.error(f"Error getting leave types: {e}")
        return jsonify({'error': 'Error loading leave types'}), 500
