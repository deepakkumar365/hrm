"""
Employee Group Management Routes
Handles CRUD operations for Employee Groups used in Leave Configuration
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app import app, db
from auth import require_login, require_role
from models import EmployeeGroup, Company
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# EMPLOYEE GROUP MANAGEMENT
# ============================================================================

@app.route('/masters/employee-groups')
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def employee_group_list():
    """List all employee groups"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        company_id = request.args.get('company_id', type=str)
        
        # Determine user's company context
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            default_company_id = current_user.employee_profile.company_id
        else:
            companies = Company.query.filter_by(is_active=True).first()
            default_company_id = companies.id if companies else None
        
        if not company_id and default_company_id:
            company_id = default_company_id
        
        query = EmployeeGroup.query.filter_by(is_active=True)
        
        if company_id:
            query = query.filter_by(company_id=company_id)
        
        if search:
            query = query.filter(
                db.or_(
                    EmployeeGroup.name.ilike(f'%{search}%'),
                    EmployeeGroup.category.ilike(f'%{search}%'),
                    EmployeeGroup.description.ilike(f'%{search}%')
                )
            )
        
        groups = query.order_by(EmployeeGroup.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        all_companies = Company.query.filter_by(is_active=True).all()
        selected_company = Company.query.filter_by(id=company_id).first() if company_id else None
        
        return render_template('employee_groups/list.html', 
                             groups=groups, 
                             search=search,
                             all_companies=all_companies,
                             selected_company=selected_company)
    except Exception as e:
        logger.error(f"Error loading employee groups: {e}")
        flash("Error loading employee groups", "error")
        return redirect(url_for('dashboard'))


@app.route('/masters/employee-groups/add', methods=['GET', 'POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def employee_group_add():
    """Add a new employee group"""
    try:
        company_id = request.args.get('company_id', type=str)
        
        # Determine default company
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
            default_company_id = current_user.employee_profile.company_id
        else:
            companies = Company.query.filter_by(is_active=True).first()
            default_company_id = companies.id if companies else None
        
        if not company_id:
            company_id = default_company_id
        
        company = Company.query.filter_by(id=company_id, is_active=True).first_or_404()
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Employee Group name is required', 'error')
                return render_template('employee_groups/form.html', 
                                     company=company, action='Add')
            
            if not category:
                flash('Category is required', 'error')
                return render_template('employee_groups/form.html', 
                                     company=company, action='Add')
            
            # Check if group already exists
            existing_group = EmployeeGroup.query.filter(
                EmployeeGroup.name.ilike(name),
                EmployeeGroup.company_id == company_id
            ).first()
            
            if existing_group:
                flash(f'Employee Group "{name}" already exists for this company', 'error')
                return render_template('employee_groups/form.html', 
                                     company=company, action='Add')
            
            try:
                group = EmployeeGroup(
                    company_id=company_id,
                    name=name,
                    category=category,
                    description=description if description else None,
                    created_by=current_user.username if hasattr(current_user, 'username') else 'system'
                )
                db.session.add(group)
                db.session.commit()
                flash(f'Employee Group "{name}" added successfully', 'success')
                return redirect(url_for('employee_group_list', company_id=company_id))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error adding employee group: {e}")
                flash(f'Error adding employee group: {str(e)}', 'error')
                return render_template('employee_groups/form.html', 
                                     company=company, action='Add')
        
        return render_template('employee_groups/form.html', 
                             company=company, action='Add')
    except Exception as e:
        logger.error(f"Error in employee group add: {e}")
        flash("Error loading form", "error")
        return redirect(url_for('employee_group_list'))


@app.route('/masters/employee-groups/<int:group_id>/edit', methods=['GET', 'POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def employee_group_edit(group_id):
    """Edit an employee group"""
    try:
        group = EmployeeGroup.query.get_or_404(group_id)
        company = group.company
        
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            description = request.form.get('description', '').strip()
            
            if not name:
                flash('Employee Group name is required', 'error')
                return render_template('employee_groups/form.html', 
                                     group=group, company=company, action='Edit')
            
            if not category:
                flash('Category is required', 'error')
                return render_template('employee_groups/form.html', 
                                     group=group, company=company, action='Edit')
            
            # Check for duplicate name
            existing_group = EmployeeGroup.query.filter(
                EmployeeGroup.name.ilike(name),
                EmployeeGroup.company_id == group.company_id,
                EmployeeGroup.id != group_id
            ).first()
            
            if existing_group:
                flash(f'Employee Group "{name}" already exists for this company', 'error')
                return render_template('employee_groups/form.html', 
                                     group=group, company=company, action='Edit')
            
            try:
                group.name = name
                group.category = category
                group.description = description if description else None
                group.modified_by = current_user.username if hasattr(current_user, 'username') else 'system'
                
                db.session.commit()
                flash(f'Employee Group "{name}" updated successfully', 'success')
                return redirect(url_for('employee_group_list', company_id=group.company_id))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating employee group: {e}")
                flash(f'Error updating employee group: {str(e)}', 'error')
                return render_template('employee_groups/form.html', 
                                     group=group, company=company, action='Edit')
        
        return render_template('employee_groups/form.html', 
                             group=group, company=company, action='Edit')
    except Exception as e:
        logger.error(f"Error in employee group edit: {e}")
        flash("Error loading form", "error")
        return redirect(url_for('employee_group_list'))


@app.route('/masters/employee-groups/<int:group_id>/delete', methods=['POST'])
@require_login
@require_role(['Tenant Admin', 'HR Manager', 'Super Admin'])
def employee_group_delete(group_id):
    """Delete an employee group (soft delete)"""
    try:
        group = EmployeeGroup.query.get_or_404(group_id)
        company_id = group.company_id
        group_name = group.name
        
        # Check if any employees are using this group
        employee_count = db.session.query(db.func.count(db.text('*'))).select_from(
            db.text('hrm_employee')
        ).filter(
            db.text(f'employee_group_id = {group_id}')
        ).scalar()
        
        if employee_count > 0:
            # Soft delete
            group.is_active = False
            group.modified_by = current_user.username if hasattr(current_user, 'username') else 'system'
            db.session.commit()
            flash(f'Employee Group "{group_name}" deactivated (used by {employee_count} employee(s))', 'info')
        else:
            # Hard delete if not used
            db.session.delete(group)
            db.session.commit()
            flash(f'Employee Group "{group_name}" deleted successfully', 'success')
        
        return redirect(url_for('employee_group_list', company_id=company_id))
    except Exception as e:
        logger.error(f"Error deleting employee group: {e}")
        db.session.rollback()
        flash("Error deleting employee group", "error")
        return redirect(url_for('employee_group_list'))


# API Endpoint - Get employee groups by company
@app.route('/api/employee-groups/<company_id>')
@require_login
def api_get_employee_groups(company_id):
    """Get all active employee groups for a company"""
    try:
        groups = EmployeeGroup.query.filter_by(
            company_id=company_id,
            is_active=True
        ).order_by(EmployeeGroup.category, EmployeeGroup.name).all()
        
        return jsonify([{
            'id': g.id,
            'name': g.name,
            'category': g.category,
            'description': g.description
        } for g in groups])
    except Exception as e:
        logger.error(f"Error fetching employee groups: {e}")
        return jsonify({'error': str(e)}), 500