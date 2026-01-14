from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from core.models import Employee, Company, User, Role
from sqlalchemy.orm import aliased
import json

org_structure_bp = Blueprint('org_structure', __name__)

def build_hierarchy(employees, manager_id=None):
    """
    Recursive function to build hierarchy tree.
    """
    hierarchy = []
    
    # Filter employees for current level
    # If manager_id is None, we look for top-level employees (no manager or manager not in list)
    current_level_employees = []
    
    if manager_id is None:
        # Find roots: Employees whose manager is None OR manager is not in the provided employee list
        # Map of all employee IDs in this company
        all_emp_ids = set(e.id for e in employees)
        for emp in employees:
            if emp.manager_id is None or emp.manager_id not in all_emp_ids:
                current_level_employees.append(emp)
    else:
        current_level_employees = [e for e in employees if e.manager_id == manager_id]

    for emp in current_level_employees:
        node = {
            'id': emp.id,
            'name': f"{emp.first_name} {emp.last_name}",
            'title': emp.designation.name if emp.designation else "No Designation",
            'image': emp.photo_url,
            'children': build_hierarchy(employees, emp.id)
        }
        hierarchy.append(node)
    
    return hierarchy

@org_structure_bp.route('/org-structure')
@login_required
def index():
    # Role check
    if current_user.role.name not in ['Super Admin', 'Tenant Admin', 'HR Manager', 'Manager']:
         flash("You do not have permission to view the Organization Structure.", "error")
         return redirect(url_for('dashboard'))

    # Get accessible companies similar to approvals logic
    companies = current_user.get_accessible_companies()
    
    # Default to first company if available
    selected_company_id = request.args.get('company_id')
    if not selected_company_id and companies:
        selected_company_id = str(companies[0].id)
        
    return render_template('org_structure/index.html', companies=companies, selected_company_id=selected_company_id)

@org_structure_bp.route('/org-structure/api/tree/<company_id>')
@login_required
def get_tree_data(company_id):
    # Verify access to this company
    accessible_companies = current_user.get_accessible_companies()
    if not any(str(c.id) == company_id for c in accessible_companies):
        return jsonify({'error': 'Access denied to this company'}), 403

    # Fetch all active employees for this company
    employees = Employee.query.filter_by(company_id=company_id, is_active=True).all()
    
    # Build Tree
    tree_data = build_hierarchy(employees)
    
    return jsonify(tree_data)

@org_structure_bp.route('/org-structure/api/update', methods=['POST'])
@login_required
def update_structure():
    if current_user.role.name not in ['Super Admin', 'Tenant Admin', 'HR Manager']:
        return jsonify({'error': 'Permission denied'}), 403

    data = request.get_json()
    employee_id = data.get('employee_id')
    new_manager_id = data.get('new_manager_id')

    if not employee_id:
        return jsonify({'error': 'Invalid data'}), 400

    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'Employee not found'}), 404

    # Validate Company Access
    accessible_companies = current_user.get_accessible_companies()
    if not any(c.id == employee.company_id for c in accessible_companies):
        return jsonify({'error': 'Access denied for this employee'}), 403

    # If new_manager_id is provided, validate it
    if new_manager_id:
        new_manager = Employee.query.get(new_manager_id)
        if not new_manager:
            return jsonify({'error': 'Manager not found'}), 404
        
        if new_manager.company_id != employee.company_id:
             return jsonify({'error': 'Manager must belong to the same company'}), 400

        # CYCLE DETECTION
        # Check if employee is an ancestor of new_manager
        # Traverse up from new_manager; if we hit employee, it's a cycle.
        checker = new_manager
        while checker.manager_id:
            if checker.manager_id == employee.id:
                return jsonify({'error': 'Cannot move a manager under their own subordinate (Cycle detected)'}), 400
            checker_parent = Employee.query.get(checker.manager_id)
            if not checker_parent: 
                break # Should not happen if constraint correct, but safety break
            checker = checker_parent

        employee.manager_id = new_manager_id
    else:
        # Making top level (no manager)
        employee.manager_id = None

    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Reporting line updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
