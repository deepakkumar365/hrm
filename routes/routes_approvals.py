"""
Approval Dashboard Routes
Centralized dashboard for managers and HR to view pending approvals (Leave, OT, Regularization)
"""
from flask import render_template, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, func

from app import app, db
from core.models import (
    Employee, Leave, OTAttendance, OTRequest, OTApproval, AttendanceRegularization,
    Company
)
from core.auth import require_login

def get_approval_counts_for_user(user):
    """
    Helper to calculate approval counts based on user role
    """
    counts = {
        'leaves': 0,
        'ot': 0,
        'regularization': 0
    }
    

    user_role = user.role.name if user.role else None
    
    # Check for reporting manager status
    is_reporting_manager = False
    if hasattr(user, 'employee_profile') and user.employee_profile:
        is_reporting_manager = user.employee_profile.is_manager
    
    try:
        # Get accessible companies for the user
        accessible_companies = user.get_accessible_companies()
        accessible_company_ids = [c.id for c in accessible_companies]
        
        # --- 1. LEAVES ---
        leave_query = Leave.query.filter_by(status='Pending')
        
        if user_role == 'Manager' or (user_role == 'Employee' and is_reporting_manager):
             # Only direct reports
             if user.employee_profile:
                 leave_query = leave_query.join(Employee).filter(Employee.manager_id == user.employee_profile.id)
             else:
                 leave_query = leave_query.filter(False)
        elif user_role in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            # Filter by accessible companies
            # Optimization: If Super Admin and wants to see all, get_accessible_companies returns all.
            # But checking if list is not empty is safer.
            if accessible_company_ids:
                 leave_query = leave_query.join(Employee).filter(Employee.company_id.in_(accessible_company_ids))
            else:
                 # No accessible companies means no data
                 leave_query = leave_query.filter(False)
                 
        counts['leaves'] = leave_query.count()

        # --- 2. OT REQUESTS ---
        if user_role == 'Manager' or (user_role == 'Employee' and is_reporting_manager):
            ot_query = OTApproval.query.filter_by(status='pending_manager', approval_level=1)
            ot_query = ot_query.filter(OTApproval.approver_id == user.id)
            counts['ot'] = ot_query.count()
            
        elif user_role in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            ot_req_query = OTRequest.query.filter_by(status='manager_approved')
            
            if accessible_company_ids:
                 ot_req_query = ot_req_query.filter(OTRequest.company_id.in_(accessible_company_ids))
            else:
                 ot_req_query = ot_req_query.filter(False)
            
            counts['ot'] = ot_req_query.count()

        # --- 3. REGULARIZATION ---
        reg_query = AttendanceRegularization.query.filter_by(status='Pending')
        
        if user_role == 'Manager' or (user_role == 'Employee' and is_reporting_manager):
             if user.employee_profile:
                 reg_query = reg_query.join(Employee).filter(Employee.manager_id == user.employee_profile.id)
             else:
                 reg_query = reg_query.filter(False)
        elif user_role in ['HR Manager', 'Tenant Admin', 'Super Admin']:
             if accessible_company_ids:
                reg_query = reg_query.join(Employee).filter(Employee.company_id.in_(accessible_company_ids))
             else:
                reg_query = reg_query.filter(False)
                 
        counts['regularization'] = reg_query.count()
        
    except Exception as e:
        print(f"Error calculating counts: {e}")
        
    return counts

@app.route('/dashboard/approvals')
@require_login
def approval_dashboard():
    """
    Unified Approval Dashboard
    """
    allowed_roles = ['Manager', 'HR Manager', 'Tenant Admin', 'Super Admin']
    user_role = current_user.role.name if current_user.role else None
    
    # Check for reporting manager status
    is_reporting_manager = False
    if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        is_reporting_manager = current_user.employee_profile.is_manager
    
    if user_role not in allowed_roles and not is_reporting_manager:
        flash('Access Denied', 'danger')
        return redirect(url_for('dashboard'))
        
    counts = get_approval_counts_for_user(current_user)
    
    links = {
        'leaves': url_for('leave_list', status='Pending'),
        'ot': '#', # Dynamic based on role
        'regularization': url_for('attendance_regularization_manage')
    }
    
    return render_template('approval_dashboard.html', counts=counts, links=links)

@app.route('/dashboard/approvals/api/counts')
@require_login
def api_get_approval_counts():
    """
    API to get current approval counts for live updates
    """
    counts = get_approval_counts_for_user(current_user)
    return jsonify(counts)


@app.route('/dashboard/approvals/load/<type>')
@require_login
def load_approval_data(type):
    """
    Dynamic loader for approval dashboard content
    """
    allowed_roles = ['Manager', 'HR Manager', 'Tenant Admin', 'Super Admin']
    user_role = current_user.role.name if current_user.role else None
    
    # Check for reporting manager status
    is_reporting_manager = False
    if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        is_reporting_manager = current_user.employee_profile.is_manager

    if user_role not in allowed_roles and not is_reporting_manager:
        return "Unauthorized", 403

    user_role = current_user.role.name
    
    # Get accessible companies
    accessible_companies = current_user.get_accessible_companies()
    accessible_company_ids = [c.id for c in accessible_companies]

    if type == 'leaves':
        query = Leave.query.filter_by(status='Pending')
        
        if user_role == 'Manager' or (user_role == 'Employee' and is_reporting_manager):
            if current_user.employee_profile:
                query = query.join(Employee).filter(Employee.manager_id == current_user.employee_profile.id)
            else:
                 query = query.filter(False)
        elif user_role in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            if accessible_company_ids:
                query = query.join(Employee).filter(Employee.company_id.in_(accessible_company_ids))
            else:
                query = query.filter(False)
        
        leaves = query.order_by(Leave.created_at.desc()).all()
        return render_template('approvals/partials/leave_table.html', leaves=leaves, user_role=user_role)

    elif type == 'ot':
        if user_role == 'Manager' or (user_role == 'Employee' and is_reporting_manager):
            # Level 1 Pending
            query = OTApproval.query.filter_by(status='pending_manager', approval_level=1)
            query = query.filter(OTApproval.approver_id == current_user.id)
            # Better approach: Join to make sure we have data eager loaded
            query = query.join(OTRequest).join(Employee)
            ot_requests = query.all()

        elif user_role in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            # Level 2 Pending (manager_approved requests)
            query = OTRequest.query.filter_by(status='manager_approved')
            if accessible_company_ids:
                 query = query.filter(OTRequest.company_id.in_(accessible_company_ids))
            else:
                 query = query.filter(False)
            ot_requests = query.all()
        
        else:
            ot_requests = []

        link_target = "#"
        if user_role == 'Manager' or (user_role == 'Employee' and is_reporting_manager):
             link_target = url_for('ot_manager_approval') if 'ot_manager_approval' in app.view_functions else '#'
        elif user_role in ['HR Manager', 'Tenant Admin', 'Super Admin']:
             link_target = url_for('hr_manager_ot_approval')

        return render_template('approvals/partials/ot_table.html', ot_requests=ot_requests, link_target=link_target, user_role=user_role)

    elif type == 'regularization':
        query = AttendanceRegularization.query.filter_by(status='Pending')
        
        if user_role == 'Manager' or (user_role == 'Employee' and is_reporting_manager):
            if current_user.employee_profile:
                query = query.join(Employee).filter(Employee.manager_id == current_user.employee_profile.id)
            else:
                query = query.filter(False)
        elif user_role in ['HR Manager', 'Tenant Admin', 'Super Admin']:
            if accessible_company_ids:
                query = query.join(Employee).filter(Employee.company_id.in_(accessible_company_ids))
            else:
                query = query.filter(False)
        
        requests = query.all()
        return render_template('approvals/partials/regularization_table.html', requests=requests, user_role=user_role)

    return "Invalid Type", 400
