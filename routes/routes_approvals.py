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

    # Roles classification based on user request rules
    # 1. Managers/HR Manager -> See requests from reporting employees
    # 2. Tenant Admin (and Super Admin) -> See ALL requests
    is_tenant_level = user_role in ['Tenant Admin', 'Super Admin']
    is_managerial = (user_role in ['Manager', 'HR Manager']) or is_reporting_manager
    
    # Self-exclusion ID
    self_emp_id = user.employee_profile.id if user.employee_profile else -1

    try:
        # Get accessible companies for the user
        accessible_companies = user.get_accessible_companies()
        accessible_company_ids = [c.id for c in accessible_companies]
        
        # --- 1. LEAVES ---
        leave_query = Leave.query.filter_by(status='Pending')
        leave_query = leave_query.join(Employee)
        
        # Rule 3: Cannot approve own request
        leave_query = leave_query.filter(Employee.id != self_emp_id)

        if is_tenant_level:
             # Rule 2: Tenant Admin sees all in their companies
             if accessible_company_ids:
                  leave_query = leave_query.filter(Employee.company_id.in_(accessible_company_ids))
             else:
                  leave_query = leave_query.filter(False)
        elif is_managerial:
             # Rule 1: Managers/HR Manager see direct reports
             if user.employee_profile:
                 leave_query = leave_query.filter(Employee.manager_id == user.employee_profile.id)
             else:
                 leave_query = leave_query.filter(False)
        else:
             leave_query = leave_query.filter(False)
                 
        counts['leaves'] = leave_query.count()

        # --- 2. OT REQUESTS ---
        ot_count = 0
        
        # A. Level 1 Pending (Approvals table)
        q1 = OTApproval.query.filter_by(status='pending_manager', approval_level=1)
        q1 = q1.join(OTRequest).join(Employee)
        q1 = q1.filter(Employee.id != self_emp_id)

        if is_tenant_level:
            if accessible_company_ids:
                q1 = q1.filter(Employee.company_id.in_(accessible_company_ids))
                ot_count += q1.count()
            
            # Plus Level 2 (Manager Approved, waiting for HR/Admin)
            q2 = OTRequest.query.filter_by(status='manager_approved')
            q2 = q2.join(Employee)
            q2 = q2.filter(Employee.id != self_emp_id)
            if accessible_company_ids:
                q2 = q2.filter(Employee.company_id.in_(accessible_company_ids))
                ot_count += q2.count()

        elif is_managerial:
            # Managers only see Level 1 for their reports
            if user.employee_profile:
                q1 = q1.filter(Employee.manager_id == user.employee_profile.id)
                ot_count += q1.count()
            
        counts['ot'] = ot_count

        # --- 3. REGULARIZATION ---
        reg_query = AttendanceRegularization.query.filter_by(status='Pending')
        reg_query = reg_query.join(Employee)
        reg_query = reg_query.filter(Employee.id != self_emp_id)

        if is_tenant_level:
             if accessible_company_ids:
                reg_query = reg_query.filter(Employee.company_id.in_(accessible_company_ids))
             else:
                reg_query = reg_query.filter(False)
        elif is_managerial:
             if user.employee_profile:
                reg_query = reg_query.filter(Employee.manager_id == user.employee_profile.id)
             else:
                reg_query = reg_query.filter(False)
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
    
    # Roles classification based on user request rules
    is_tenant_level = user_role in ['Tenant Admin', 'Super Admin']
    is_managerial = (user_role in ['Manager', 'HR Manager']) or is_reporting_manager
    
    # Self-exclusion ID
    self_emp_id = current_user.employee_profile.id if current_user.employee_profile else -1
    
    # Get accessible companies
    accessible_companies = current_user.get_accessible_companies()
    accessible_company_ids = [c.id for c in accessible_companies]

    if type == 'leaves':
        query = Leave.query.filter_by(status='Pending')
        query = query.join(Employee)
        query = query.filter(Employee.id != self_emp_id)
        
        if is_tenant_level:
            if accessible_company_ids:
                query = query.filter(Employee.company_id.in_(accessible_company_ids))
            else:
                 query = query.filter(False)
                 
        elif is_managerial:
            if current_user.employee_profile:
                query = query.filter(Employee.manager_id == current_user.employee_profile.id)
            else:
                 query = query.filter(False)
        else:
             query = query.filter(False)
        
        leaves = query.order_by(Leave.created_at.desc()).all()
        return render_template('approvals/partials/leave_table.html', leaves=leaves, user_role=user_role)

    elif type == 'ot':
        ot_requests = []
        
        # 1. Level 1 Pending
        q1 = OTApproval.query.filter_by(status='pending_manager', approval_level=1)
        q1 = q1.join(OTRequest).join(Employee)
        q1 = q1.filter(Employee.id != self_emp_id)

        if is_tenant_level:
             # Admin sees all Level 1
             if accessible_company_ids:
                 q1 = q1.filter(Employee.company_id.in_(accessible_company_ids))
                 
             # Get results
             approvals = q1.all()
             for app_obj in approvals:
                 req = app_obj.ot_request
                 req._approval_context = 'manager' 
                 req._approval_id = app_obj.id
                 if req not in ot_requests:
                    ot_requests.append(req)

             # Admin ALSO sees Level 2 (Manager Approved)
             q2 = OTRequest.query.filter_by(status='manager_approved')
             q2 = q2.join(Employee).filter(Employee.id != self_emp_id)
             
             if accessible_company_ids:
                  q2 = q2.filter(Employee.company_id.in_(accessible_company_ids))
                  requests_l2 = q2.all()
                  for req in requests_l2:
                      req._approval_context = 'admin'
                      if req not in ot_requests:
                          ot_requests.append(req)

        elif is_managerial:
             # Manager sees Level 1 for direct reports
             if current_user.employee_profile:
                 q1 = q1.filter(Employee.manager_id == current_user.employee_profile.id)
                 approvals = q1.all()
                 for app_obj in approvals:
                     req = app_obj.ot_request
                     req._approval_context = 'manager'
                     req._approval_id = app_obj.id
                     ot_requests.append(req)
        
        link_target = "#"
        if is_tenant_level:
             link_target = url_for('hr_manager_ot_approval')
        elif is_managerial:
             link_target = url_for('ot_manager_approval') if 'ot_manager_approval' in app.view_functions else '#'

        return render_template('approvals/partials/ot_table.html', ot_requests=ot_requests, link_target=link_target, user_role=user_role)

    elif type == 'regularization':
        query = AttendanceRegularization.query.filter_by(status='Pending')
        query = query.join(Employee)
        query = query.filter(Employee.id != self_emp_id)
        
        if is_tenant_level:
            if accessible_company_ids:
                query = query.filter(Employee.company_id.in_(accessible_company_ids))
            else:
                query = query.filter(False)
        elif is_managerial:
            if current_user.employee_profile:
                query = query.filter(Employee.manager_id == current_user.employee_profile.id)
            else:
                query = query.filter(False)
        else:
            query = query.filter(False)
        
        requests = query.all()
        return render_template('approvals/partials/regularization_table.html', requests=requests, user_role=user_role)

    return "Invalid Type", 400
