"""
Leave Allocation Configuration Routes
Handles configuration of leave allocations for designations, employee groups, and individual employees
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app import app, db
from core.auth import require_login, require_role
from core.models import (
    Designation, EmployeeGroup, LeaveType, Company,
    DesignationLeaveAllocation, EmployeeGroupLeaveAllocation, EmployeeLeaveAllocation,
    Employee
)
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DESIGNATION-BASED LEAVE ALLOCATION
# ============================================================================

@app.route('/leave-management/allocation/designation')
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_allocation_designation_list():
    """List leave allocations for designations"""
    try:
        company_id = request.args.get('company_id', type=str)
        designation_id = request.args.get('designation_id', type=int)
        leave_type_id = request.args.get('leave_type_id', type=int)
        
        # Determine user's company context
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            default_company_id = current_user.employee_profile.company_id
        else:
            companies = Company.query.filter_by(is_active=True).first()
            default_company_id = companies.id if companies else None
        
        if not company_id and default_company_id:
            company_id = default_company_id
        
        company = Company.query.filter_by(id=company_id, is_active=True).first_or_404() if company_id else None
        
        query = DesignationLeaveAllocation.query
        if company_id:
            query = query.filter_by(company_id=company_id)
        if designation_id:
            query = query.filter_by(designation_id=designation_id)
        if leave_type_id:
            query = query.filter_by(leave_type_id=leave_type_id)
        
        allocations = query.order_by(
            DesignationLeaveAllocation.company_id,
            DesignationLeaveAllocation.designation_id
        ).all()
        
        designations = Designation.query.filter_by(is_active=True).all()
        leave_types = LeaveType.query.filter_by(company_id=company_id, is_active=True).all() if company_id else []
        all_companies = Company.query.filter_by(is_active=True).all()
        
        return render_template('leave/allocation_designation_list.html',
                             allocations=allocations,
                             company=company,
                             companies=all_companies,
                             designations=designations,
                             leave_types=leave_types,
                             selected_designation_id=designation_id,
                             selected_leave_type_id=leave_type_id)
    except Exception as e:
        logger.error(f"Error loading designation leave allocations: {e}")
        flash("Error loading leave allocations", "error")
        return redirect(url_for('dashboard'))


@app.route('/leave-management/allocation/designation/form', methods=['GET', 'POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_allocation_designation_form():
    """Create or edit designation leave allocation"""
    try:
        company_id = request.args.get('company_id', type=str)
        allocation_id = request.args.get('allocation_id', type=int)
        
        if not company_id:
            flash("Company is required", "error")
            return redirect(url_for('leave_allocation_designation_list'))
        
        company = Company.query.filter_by(id=company_id, is_active=True).first_or_404()
        allocation = None
        
        if allocation_id:
            allocation = DesignationLeaveAllocation.query.filter_by(
                id=allocation_id,
                company_id=company_id
            ).first_or_404()
        
        if request.method == 'POST':
            designation_id = request.form.get('designation_id', type=int)
            leave_type_id = request.form.get('leave_type_id', type=int)
            total_days = request.form.get('total_days', type=int)
            
            if not designation_id or not leave_type_id or total_days is None:
                flash("All fields are required", "error")
                return render_template('leave/allocation_designation_form.html',
                                     company=company,
                                     designations=Designation.query.filter_by(is_active=True).all(),
                                     leave_types=LeaveType.query.filter_by(company_id=company_id, is_active=True).all(),
                                     allocation=allocation)
            
            if total_days < 0:
                flash("Total days cannot be negative", "error")
                return render_template('leave/allocation_designation_form.html',
                                     company=company,
                                     designations=Designation.query.filter_by(is_active=True).all(),
                                     leave_types=LeaveType.query.filter_by(company_id=company_id, is_active=True).all(),
                                     allocation=allocation)
            
            try:
                if allocation:
                    allocation.total_days = total_days
                    allocation.modified_by = current_user.username if hasattr(current_user, 'username') else 'system'
                    db.session.commit()
                    flash("Leave allocation updated successfully", "success")
                else:
                    # Check for duplicate
                    existing = DesignationLeaveAllocation.query.filter_by(
                        company_id=company_id,
                        designation_id=designation_id,
                        leave_type_id=leave_type_id
                    ).first()
                    
                    if existing:
                        flash("This allocation already exists", "error")
                        return render_template('leave/allocation_designation_form.html',
                                             company=company,
                                             designations=Designation.query.filter_by(is_active=True).all(),
                                             leave_types=LeaveType.query.filter_by(company_id=company_id, is_active=True).all(),
                                             allocation=allocation)
                    
                    allocation = DesignationLeaveAllocation(
                        company_id=company_id,
                        designation_id=designation_id,
                        leave_type_id=leave_type_id,
                        total_days=total_days,
                        created_by=current_user.username if hasattr(current_user, 'username') else 'system'
                    )
                    db.session.add(allocation)
                    db.session.commit()
                    flash("Leave allocation created successfully", "success")
                
                return redirect(url_for('leave_allocation_designation_list', company_id=company_id))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error saving leave allocation: {e}")
                flash("Error saving leave allocation", "error")
                return render_template('leave/allocation_designation_form.html',
                                     company=company,
                                     designations=Designation.query.filter_by(is_active=True).all(),
                                     leave_types=LeaveType.query.filter_by(company_id=company_id, is_active=True).all(),
                                     allocation=allocation)
        
        designations = Designation.query.filter_by(is_active=True).all()
        leave_types = LeaveType.query.filter_by(company_id=company_id, is_active=True).all()
        
        return render_template('leave/allocation_designation_form.html',
                             company=company,
                             designations=designations,
                             leave_types=leave_types,
                             allocation=allocation)
    except Exception as e:
        logger.error(f"Error in leave allocation form: {e}")
        flash("Error loading form", "error")
        return redirect(url_for('leave_allocation_designation_list'))


@app.route('/leave-management/allocation/designation/<int:allocation_id>/delete', methods=['POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_allocation_designation_delete(allocation_id):
    """Delete a designation leave allocation"""
    try:
        allocation = DesignationLeaveAllocation.query.get_or_404(allocation_id)
        company_id = allocation.company_id
        
        db.session.delete(allocation)
        db.session.commit()
        flash("Leave allocation deleted successfully", "success")
        
        return redirect(url_for('leave_allocation_designation_list', company_id=company_id))
    except Exception as e:
        logger.error(f"Error deleting leave allocation: {e}")
        db.session.rollback()
        flash("Error deleting leave allocation", "error")
        return redirect(url_for('leave_allocation_designation_list'))


# ============================================================================
# EMPLOYEE GROUP-BASED LEAVE ALLOCATION
# ============================================================================

@app.route('/leave-management/allocation/employee-group')
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_allocation_employee_group_list():
    """List leave allocations for employee groups"""
    try:
        company_id = request.args.get('company_id', type=str)
        employee_group_id = request.args.get('employee_group_id', type=int)
        leave_type_id = request.args.get('leave_type_id', type=int)
        
        # Determine user's company context
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            default_company_id = current_user.employee_profile.company_id
        else:
            companies = Company.query.filter_by(is_active=True).first()
            default_company_id = companies.id if companies else None
        
        if not company_id and default_company_id:
            company_id = default_company_id
        
        company = Company.query.filter_by(id=company_id, is_active=True).first_or_404() if company_id else None
        
        query = EmployeeGroupLeaveAllocation.query
        if company_id:
            query = query.filter_by(company_id=company_id)
        if employee_group_id:
            query = query.filter_by(employee_group_id=employee_group_id)
        if leave_type_id:
            query = query.filter_by(leave_type_id=leave_type_id)
        
        allocations = query.order_by(
            EmployeeGroupLeaveAllocation.company_id,
            EmployeeGroupLeaveAllocation.employee_group_id
        ).all()
        
        employee_groups = EmployeeGroup.query.filter_by(is_active=True).all()
        leave_types = LeaveType.query.filter_by(company_id=company_id, is_active=True).all() if company_id else []
        all_companies = Company.query.filter_by(is_active=True).all()
        
        return render_template('leave/allocation_employee_group_list.html',
                             allocations=allocations,
                             company=company,
                             companies=all_companies,
                             employee_groups=employee_groups,
                             leave_types=leave_types,
                             selected_employee_group_id=employee_group_id,
                             selected_leave_type_id=leave_type_id)
    except Exception as e:
        logger.error(f"Error loading employee group leave allocations: {e}")
        flash("Error loading leave allocations", "error")
        return redirect(url_for('dashboard'))


@app.route('/leave-management/allocation/employee-group/form', methods=['GET', 'POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_allocation_employee_group_form():
    """Create or edit employee group leave allocation"""
    try:
        company_id = request.args.get('company_id', type=str)
        allocation_id = request.args.get('allocation_id', type=int)
        
        if not company_id:
            flash("Company is required", "error")
            return redirect(url_for('leave_allocation_employee_group_list'))
        
        company = Company.query.filter_by(id=company_id, is_active=True).first_or_404()
        allocation = None
        
        if allocation_id:
            allocation = EmployeeGroupLeaveAllocation.query.filter_by(
                id=allocation_id,
                company_id=company_id
            ).first_or_404()
        
        if request.method == 'POST':
            employee_group_id = request.form.get('employee_group_id', type=int)
            leave_type_id = request.form.get('leave_type_id', type=int)
            total_days = request.form.get('total_days', type=int)
            
            if not employee_group_id or not leave_type_id or total_days is None:
                flash("All fields are required", "error")
                return render_template('leave/allocation_employee_group_form.html',
                                     company=company,
                                     employee_groups=EmployeeGroup.query.filter_by(is_active=True).all(),
                                     leave_types=LeaveType.query.filter_by(company_id=company_id, is_active=True).all(),
                                     allocation=allocation)
            
            if total_days < 0:
                flash("Total days cannot be negative", "error")
                return render_template('leave/allocation_employee_group_form.html',
                                     company=company,
                                     employee_groups=EmployeeGroup.query.filter_by(is_active=True).all(),
                                     leave_types=LeaveType.query.filter_by(company_id=company_id, is_active=True).all(),
                                     allocation=allocation)
            
            try:
                if allocation:
                    allocation.total_days = total_days
                    allocation.modified_by = current_user.username if hasattr(current_user, 'username') else 'system'
                    db.session.commit()
                    flash("Leave allocation updated successfully", "success")
                else:
                    # Check for duplicate
                    existing = EmployeeGroupLeaveAllocation.query.filter_by(
                        company_id=company_id,
                        employee_group_id=employee_group_id,
                        leave_type_id=leave_type_id
                    ).first()
                    
                    if existing:
                        flash("This allocation already exists", "error")
                        return render_template('leave/allocation_employee_group_form.html',
                                             company=company,
                                             employee_groups=EmployeeGroup.query.filter_by(is_active=True).all(),
                                             leave_types=LeaveType.query.filter_by(company_id=company_id, is_active=True).all(),
                                             allocation=allocation)
                    
                    allocation = EmployeeGroupLeaveAllocation(
                        company_id=company_id,
                        employee_group_id=employee_group_id,
                        leave_type_id=leave_type_id,
                        total_days=total_days,
                        created_by=current_user.username if hasattr(current_user, 'username') else 'system'
                    )
                    db.session.add(allocation)
                    db.session.commit()
                    flash("Leave allocation created successfully", "success")
                
                return redirect(url_for('leave_allocation_employee_group_list', company_id=company_id))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error saving leave allocation: {e}")
                flash("Error saving leave allocation", "error")
                return render_template('leave/allocation_employee_group_form.html',
                                     company=company,
                                     employee_groups=EmployeeGroup.query.filter_by(is_active=True).all(),
                                     leave_types=LeaveType.query.filter_by(company_id=company_id, is_active=True).all(),
                                     allocation=allocation)
        
        employee_groups = EmployeeGroup.query.filter_by(is_active=True).all()
        leave_types = LeaveType.query.filter_by(company_id=company_id, is_active=True).all()
        
        return render_template('leave/allocation_employee_group_form.html',
                             company=company,
                             employee_groups=employee_groups,
                             leave_types=leave_types,
                             allocation=allocation)
    except Exception as e:
        logger.error(f"Error in leave allocation form: {e}")
        flash("Error loading form", "error")
        return redirect(url_for('leave_allocation_employee_group_list'))


@app.route('/leave-management/allocation/employee-group/<int:allocation_id>/delete', methods=['POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_allocation_employee_group_delete(allocation_id):
    """Delete an employee group leave allocation"""
    try:
        allocation = EmployeeGroupLeaveAllocation.query.get_or_404(allocation_id)
        company_id = allocation.company_id
        
        db.session.delete(allocation)
        db.session.commit()
        flash("Leave allocation deleted successfully", "success")
        
        return redirect(url_for('leave_allocation_employee_group_list', company_id=company_id))
    except Exception as e:
        logger.error(f"Error deleting leave allocation: {e}")
        db.session.rollback()
        flash("Error deleting leave allocation", "error")
        return redirect(url_for('leave_allocation_employee_group_list'))


# ============================================================================
# INDIVIDUAL EMPLOYEE LEAVE ALLOCATION (OVERRIDES)
# ============================================================================

@app.route('/leave-management/allocation/employee')
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_allocation_employee_list():
    """List individual employee leave allocations"""
    try:
        company_id = request.args.get('company_id', type=str)
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        # Determine user's company context
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            default_company_id = current_user.employee_profile.company_id
        else:
            companies = Company.query.filter_by(is_active=True).first()
            default_company_id = companies.id if companies else None
        
        if not company_id and default_company_id:
            company_id = default_company_id
        
        company = Company.query.filter_by(id=company_id, is_active=True).first_or_404() if company_id else None
        
        query = EmployeeLeaveAllocation.query
        
        if search:
            query = query.join(Employee).filter(
                db.or_(
                    Employee.first_name.ilike(f'%{search}%'),
                    Employee.last_name.ilike(f'%{search}%'),
                    Employee.employee_id.ilike(f'%{search}%')
                )
            )
        
        allocations = query.order_by(EmployeeLeaveAllocation.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        all_companies = Company.query.filter_by(is_active=True).all()
        
        return render_template('leave/allocation_employee_list.html',
                             allocations=allocations,
                             company=company,
                             companies=all_companies,
                             search=search)
    except Exception as e:
        logger.error(f"Error loading employee leave allocations: {e}")
        flash("Error loading leave allocations", "error")
        return redirect(url_for('dashboard'))


@app.route('/leave-management/allocation/employee/<int:allocation_id>/delete', methods=['POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def leave_allocation_employee_delete(allocation_id):
    """Delete an individual employee leave allocation"""
    try:
        allocation = EmployeeLeaveAllocation.query.get_or_404(allocation_id)
        
        db.session.delete(allocation)
        db.session.commit()
        flash("Employee leave allocation deleted successfully", "success")
        
        return redirect(url_for('leave_allocation_employee_list'))
    except Exception as e:
        logger.error(f"Error deleting employee leave allocation: {e}")
        db.session.rollback()
        flash("Error deleting leave allocation", "error")
        return redirect(url_for('leave_allocation_employee_list'))
