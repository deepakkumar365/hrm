"""
Master Data Management Routes
Handles CRUD operations for Roles, Departments, Working Hours, Work Schedules, and OT Types
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import or_
from datetime import datetime

from app import app, db
from core.auth import require_login, require_role
from core.models import Role, Department, WorkingHours, WorkSchedule, Employee, OTType, Company, User, Organization, Designation, LeaveType, EmployeeGroup, Tenant
from flask_login import current_user


# ============================================================================
# OPERATION MASTER DASHBOARD
# ============================================================================

@app.route('/masters/operation-master')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def operation_master_dashboard():
    """Consolidated dashboard for Operation Masters"""
    # Optimized: Only fetch dropdown data needed for modals
    # Panel data is loaded via AJAX in parallel
    
    all_working_hours = WorkingHours.query.order_by(WorkingHours.name).all()
    all_companies = Company.query.filter_by(is_active=True).all()
    
    return render_template('masters/operation_master.html',
                         all_working_hours=all_working_hours,
                         all_companies=all_companies)

@app.route('/masters/organization-master')
@require_role(['Super Admin', 'Tenant Admin'])
def organization_master_dashboard():
    """Consolidated dashboard for Organization Masters (Tenant, Company, Payment Config)"""
    
    tenants = []
    if current_user.role.name == 'Super Admin':
        tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.name).all()
    elif current_user.organization and current_user.organization.tenant:
         tenants = [current_user.organization.tenant]
    
    return render_template('masters/organization_master.html', tenants=tenants)


# ============================================================================
# API ENDPOINTS FOR DASHBOARD (PARALLEL LOADING)
# ============================================================================

@app.route('/api/masters/roles')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_roles_json():
    try:
        limit = 5
        roles = Role.query.order_by(Role.created_at.desc()).limit(limit).all()
        return jsonify({
            'success': True,
            'data': [{
                'name': r.name,
                'description': r.description
            } for r in roles],
            'count': len(roles) # Optionally return total count if needed
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/masters/departments')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_departments_json():
    try:
        from sqlalchemy.orm import joinedload
        limit = 5
        # Eager load manager to prevent N+1 queries
        departments = Department.query.options(joinedload(Department.manager))\
            .order_by(Department.created_at.desc()).limit(limit).all()
            
        data = []
        for d in departments:
            manager_name = "-"
            if d.manager:
                manager_name = f"{d.manager.first_name} {d.manager.last_name}"
            
            data.append({
                'name': d.name,
                'manager_name': manager_name
            })
            
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/masters/designations')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_designations_json():
    try:
        limit = 5
        designations = Designation.query.filter_by(is_active=True)\
            .order_by(Designation.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'name': d.name,
                'is_active': d.is_active
            } for d in designations]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/masters/working-hours')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_working_hours_json():
    try:
        limit = 5
        working_hours = WorkingHours.query.order_by(WorkingHours.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'name': w.name,
                'start_time': w.start_time.strftime('%H:%M'),
                'end_time': w.end_time.strftime('%H:%M')
            } for w in working_hours]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/masters/work-schedules')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_work_schedules_json():
    try:
        limit = 5
        schedules = WorkSchedule.query.order_by(WorkSchedule.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'name': s.name,
                'days': {
                    'monday': s.monday,
                    'tuesday': s.tuesday,
                    'wednesday': s.wednesday,
                    'thursday': s.thursday,
                    'friday': s.friday,
                    'saturday': s.saturday,
                    'sunday': s.sunday
                }
            } for s in schedules]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/masters/ot-types')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_ot_types_json():
    try:
        limit = 5
        ot_types = OTType.query.order_by(OTType.display_order).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'name': o.name,
                'code': o.code,
                'rate_multiplier': o.rate_multiplier
            } for o in ot_types]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/masters/leave-types')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_leave_types_json():
    try:
        limit = 5
        leave_types = LeaveType.query.filter_by(is_active=True)\
            .order_by(LeaveType.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'name': l.name,
                'code': l.code,
                'annual_allocation': l.annual_allocation
            } for l in leave_types]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/masters/leave-groups')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_leave_groups_json():
    try:
        limit = 5
        groups = EmployeeGroup.query.filter_by(is_active=True)\
            .order_by(EmployeeGroup.created_at.desc()).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'name': g.name,
                'description': g.description
            } for g in groups]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/masters/managers')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_managers_json():
    """Get active managers in JSON format for dropdowns"""
    try:
        managers = Employee.query.filter_by(is_active=True, is_manager=True)\
            .order_by(Employee.first_name, Employee.last_name).all()
        
        manager_list = [{
            'id': m.id,
            'name': f"{m.first_name} {m.last_name}"
        } for m in managers]
        
        return jsonify({'success': True, 'managers': manager_list})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


# ============================================================================
# ROLES MANAGEMENT
# ============================================================================

@app.route('/masters/roles')
@require_role(['Super Admin', 'Admin', 'Tenant Admin', 'HR Manager'])
def role_list():
    """List all roles with search and pagination"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Role.query
    
    if search:
        query = query.filter(
            or_(
                Role.name.ilike(f'%{search}%'),
                Role.description.ilike(f'%{search}%')
            )
        )
    
    roles = query.order_by(Role.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('masters/roles/list.html', 
                         roles=roles, 
                         search=search)


@app.route('/masters/roles/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'Tenant Admin', 'HR Manager'])
def role_add():
    """Add a new role"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not name:
            if is_ajax: return jsonify({'success': False, 'message': 'Role name is required'})
            flash('Role name is required', 'error')
            return redirect(url_for('role_add'))
        
        # Check if role already exists
        existing_role = Role.query.filter_by(name=name).first()
        if existing_role:
            if is_ajax: return jsonify({'success': False, 'message': f'Role "{name}" already exists'})
            flash(f'Role "{name}" already exists', 'error')
            return redirect(url_for('role_add'))
        
        try:
            role = Role(
                name=name,
                description=description if description else None
            )
            db.session.add(role)
            db.session.commit()
            if is_ajax: return jsonify({'success': True, 'message': f'Role "{name}" added successfully'})
            flash(f'Role "{name}" added successfully', 'success')
            return redirect(url_for('role_list'))
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'success': False, 'message': f'Error adding role: {str(e)}'})
            flash(f'Error adding role: {str(e)}', 'error')
            return redirect(url_for('role_add'))
    
    return render_template('masters/roles/form.html', role=None)


@app.route('/masters/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'Tenant Admin', 'HR Manager'])
def role_edit(role_id):
    """Edit an existing role"""
    role = Role.query.get_or_404(role_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Role name is required', 'error')
            return redirect(url_for('role_edit', role_id=role_id))
        
        # Check if another role with same name exists
        existing_role = Role.query.filter(
            Role.name == name,
            Role.id != role_id
        ).first()
        if existing_role:
            flash(f'Role "{name}" already exists', 'error')
            return redirect(url_for('role_edit', role_id=role_id))
        
        try:
            role.name = name
            role.description = description if description else None
            db.session.commit()
            flash(f'Role "{name}" updated successfully', 'success')
            return redirect(url_for('role_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating role: {str(e)}', 'error')
            return redirect(url_for('role_edit', role_id=role_id))
    
    return render_template('masters/roles/form.html', role=role)


@app.route('/masters/roles/<int:role_id>/delete', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Tenant Admin', 'HR Manager'])
def role_delete(role_id):
    """Delete a role"""
    role = Role.query.get_or_404(role_id)
    
    # Check if role is assigned to any employees
    employee_count = Employee.query.filter_by(role_id=role_id).count()
    if employee_count > 0:
        flash(f'Cannot delete role "{role.name}" as it is assigned to {employee_count} employee(s)', 'error')
        return redirect(url_for('role_list'))
    
    try:
        role_name = role.name
        db.session.delete(role)
        db.session.commit()
        flash(f'Role "{role_name}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting role: {str(e)}', 'error')
    
    return redirect(url_for('role_list'))


# ============================================================================
# DEPARTMENTS MANAGEMENT
# ============================================================================

@app.route('/masters/departments')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def department_list():
    """List all departments with search and pagination"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Department.query
    
    if search:
        query = query.filter(
            or_(
                Department.name.ilike(f'%{search}%'),
                Department.description.ilike(f'%{search}%')
            )
        )
    
    departments = query.order_by(Department.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('masters/departments/list.html', 
                         departments=departments, 
                         search=search)


@app.route('/masters/departments/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def department_add():
    """Add a new department"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        manager_id = request.form.get('manager_id')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not name:
            if is_ajax: return jsonify({'success': False, 'message': 'Department name is required'})
            flash('Department name is required', 'error')
            return redirect(url_for('department_add'))
        
        # Check if department already exists
        existing_dept = Department.query.filter_by(name=name).first()
        if existing_dept:
            if is_ajax: return jsonify({'success': False, 'message': f'Department "{name}" already exists'})
            flash(f'Department "{name}" already exists', 'error')
            return redirect(url_for('department_add'))
        
        try:
            department = Department(
                name=name,
                description=description if description else None,
                manager_id=int(manager_id) if manager_id else None
            )
            db.session.add(department)
            db.session.commit()
            if is_ajax: return jsonify({'success': True, 'message': f'Department "{name}" added successfully'})
            flash(f'Department "{name}" added successfully', 'success')
            return redirect(url_for('department_list'))
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'success': False, 'message': f'Error adding department: {str(e)}'})
            flash(f'Error adding department: {str(e)}', 'error')
            return redirect(url_for('department_add'))
    
    # Get all employees for manager selection
    managers = Employee.query.filter_by(is_active=True, is_manager=True).order_by(
        Employee.first_name, Employee.last_name
    ).all()
    
    return render_template('masters/departments/form.html', 
                         department=None, 
                         managers=managers)


@app.route('/masters/departments/<int:department_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def department_edit(department_id):
    """Edit an existing department"""
    department = Department.query.get_or_404(department_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        manager_id = request.form.get('manager_id')
        
        if not name:
            flash('Department name is required', 'error')
            return redirect(url_for('department_edit', department_id=department_id))
        
        # Check if another department with same name exists
        existing_dept = Department.query.filter(
            Department.name == name,
            Department.id != department_id
        ).first()
        if existing_dept:
            flash(f'Department "{name}" already exists', 'error')
            return redirect(url_for('department_edit', department_id=department_id))
        
        try:
            department.name = name
            department.description = description if description else None
            department.manager_id = int(manager_id) if manager_id else None
            db.session.commit()
            flash(f'Department "{name}" updated successfully', 'success')
            return redirect(url_for('department_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating department: {str(e)}', 'error')
            return redirect(url_for('department_edit', department_id=department_id))
    
    # Get all employees for manager selection
    managers = Employee.query.filter_by(is_active=True, is_manager=True).order_by(
        Employee.first_name, Employee.last_name
    ).all()
    
    return render_template('masters/departments/form.html', 
                         department=department, 
                         managers=managers)


@app.route('/masters/departments/<int:department_id>/delete', methods=['POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def department_delete(department_id):
    """Delete a department"""
    department = Department.query.get_or_404(department_id)
    
    # Check if department is assigned to any employees
    employee_count = Employee.query.filter_by(department_id=department_id).count()
    if employee_count > 0:
        flash(f'Cannot delete department "{department.name}" as it is assigned to {employee_count} employee(s)', 'error')
        return redirect(url_for('department_list'))
    
    try:
        dept_name = department.name
        db.session.delete(department)
        db.session.commit()
        flash(f'Department "{dept_name}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting department: {str(e)}', 'error')
    
    return redirect(url_for('department_list'))


# ============================================================================
# WORKING HOURS MANAGEMENT
# ============================================================================

@app.route('/masters/working-hours')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def working_hours_list():
    """List all working hours configurations with search and pagination"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = WorkingHours.query
    
    if search:
        query = query.filter(
            or_(
                WorkingHours.name.ilike(f'%{search}%'),
                WorkingHours.description.ilike(f'%{search}%')
            )
        )
    
    working_hours = query.order_by(WorkingHours.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('masters/working_hours/list.html', 
                         working_hours=working_hours, 
                         search=search)


@app.route('/masters/working-hours/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def working_hours_add():
    """Add a new working hours configuration"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        hours_per_day = request.form.get('hours_per_day', type=float)
        hours_per_week = request.form.get('hours_per_week', type=float)
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not name or not start_time or not end_time or not hours_per_day or not hours_per_week:
            if is_ajax: return jsonify({'success': False, 'message': 'All required fields must be filled'})
            flash('All required fields must be filled', 'error')
            return redirect(url_for('working_hours_add'))
        
        # Check if working hours config already exists
        existing_wh = WorkingHours.query.filter_by(name=name).first()
        if existing_wh:
            if is_ajax: return jsonify({'success': False, 'message': f'Working hours configuration "{name}" already exists'})
            flash(f'Working hours configuration "{name}" already exists', 'error')
            return redirect(url_for('working_hours_add'))
        
        try:
            # Parse time strings to time objects
            # Input format is HH:MM from HTML5 time input
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            working_hours = WorkingHours(
                name=name,
                description=description if description else None,
                start_time=start_time_obj,
                end_time=end_time_obj,
                hours_per_day=hours_per_day,
                hours_per_week=hours_per_week
            )
            db.session.add(working_hours)
            db.session.commit()
            if is_ajax: return jsonify({'success': True, 'message': f'Working hours configuration "{name}" added successfully'})
            flash(f'Working hours configuration "{name}" added successfully', 'success')
            return redirect(url_for('working_hours_list'))
        except ValueError:
            if is_ajax: return jsonify({'success': False, 'message': 'Invalid time format. Please use HH:MM format.'})
            flash('Invalid time format. Please use HH:MM format.', 'error')
            return redirect(url_for('working_hours_add'))
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'success': False, 'message': f'Error adding working hours: {str(e)}'})
            flash(f'Error adding working hours: {str(e)}', 'error')
            return redirect(url_for('working_hours_add'))
    
    return render_template('masters/working_hours/form.html', working_hours=None)


@app.route('/masters/working-hours/<int:working_hours_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def working_hours_edit(working_hours_id):
    """Edit an existing working hours configuration"""
    working_hours = WorkingHours.query.get_or_404(working_hours_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        hours_per_day = request.form.get('hours_per_day', type=float)
        hours_per_week = request.form.get('hours_per_week', type=float)
        
        if not name or not start_time or not end_time or not hours_per_day or not hours_per_week:
            flash('All required fields must be filled', 'error')
            return redirect(url_for('working_hours_edit', working_hours_id=working_hours_id))
        
        # Check if another working hours config with same name exists
        existing_wh = WorkingHours.query.filter(
            WorkingHours.name == name,
            WorkingHours.id != working_hours_id
        ).first()
        if existing_wh:
            flash(f'Working hours configuration "{name}" already exists', 'error')
            return redirect(url_for('working_hours_edit', working_hours_id=working_hours_id))
        
        try:
            # Parse time strings to time objects
            # Input format is HH:MM from HTML5 time input
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            working_hours.name = name
            working_hours.description = description if description else None
            working_hours.start_time = start_time_obj
            working_hours.end_time = end_time_obj
            working_hours.hours_per_day = hours_per_day
            working_hours.hours_per_week = hours_per_week
            db.session.commit()
            flash(f'Working hours configuration "{name}" updated successfully', 'success')
            return redirect(url_for('working_hours_list'))
        except ValueError:
            flash('Invalid time format. Please use HH:MM format.', 'error')
            return redirect(url_for('working_hours_edit', working_hours_id=working_hours_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating working hours: {str(e)}', 'error')
            return redirect(url_for('working_hours_edit', working_hours_id=working_hours_id))
    
    return render_template('masters/working_hours/form.html', working_hours=working_hours)


@app.route('/masters/working-hours/<int:working_hours_id>/delete', methods=['POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def working_hours_delete(working_hours_id):
    """Delete a working hours configuration"""
    working_hours = WorkingHours.query.get_or_404(working_hours_id)
    
    # Check if working hours is assigned to any work schedules
    schedule_count = WorkSchedule.query.filter_by(working_hours_id=working_hours_id).count()
    if schedule_count > 0:
        flash(f'Cannot delete working hours "{working_hours.name}" as it is assigned to {schedule_count} work schedule(s)', 'error')
        return redirect(url_for('working_hours_list'))
    
    try:
        wh_name = working_hours.name
        db.session.delete(working_hours)
        db.session.commit()
        flash(f'Working hours configuration "{wh_name}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting working hours: {str(e)}', 'error')
    
    return redirect(url_for('working_hours_list'))


# ============================================================================
# WORK SCHEDULES MANAGEMENT
# ============================================================================

@app.route('/masters/work-schedules')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def work_schedule_list():
    """List all work schedules with search and pagination"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = WorkSchedule.query
    
    if search:
        query = query.filter(
            or_(
                WorkSchedule.name.ilike(f'%{search}%'),
                WorkSchedule.description.ilike(f'%{search}%')
            )
        )
    
    work_schedules = query.order_by(WorkSchedule.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('masters/work_schedules/list.html', 
                         work_schedules=work_schedules, 
                         search=search)


@app.route('/masters/work-schedules/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def work_schedule_add():
    """Add a new work schedule"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        working_hours_id = request.form.get('working_hours_id')
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Get working days
        working_days = []
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if request.form.get(day):
                working_days.append(day)
        
        if not name or not working_hours_id or not working_days:
            if is_ajax: return jsonify({'success': False, 'message': 'Name, working hours, and at least one working day are required'})
            flash('Name, working hours, and at least one working day are required', 'error')
            return redirect(url_for('work_schedule_add'))
        
        # Check if work schedule already exists
        existing_ws = WorkSchedule.query.filter_by(name=name).first()
        if existing_ws:
            if is_ajax: return jsonify({'success': False, 'message': f'Work schedule "{name}" already exists'})
            flash(f'Work schedule "{name}" already exists', 'error')
            return redirect(url_for('work_schedule_add'))
        
        try:
            work_schedule = WorkSchedule(
                name=name,
                description=description if description else None,
                working_hours_id=int(working_hours_id),
                monday='monday' in working_days,
                tuesday='tuesday' in working_days,
                wednesday='wednesday' in working_days,
                thursday='thursday' in working_days,
                friday='friday' in working_days,
                saturday='saturday' in working_days,
                sunday='sunday' in working_days
            )
            db.session.add(work_schedule)
            db.session.commit()
            if is_ajax: return jsonify({'success': True, 'message': f'Work schedule "{name}" added successfully'})
            flash(f'Work schedule "{name}" added successfully', 'success')
            return redirect(url_for('work_schedule_list'))
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'success': False, 'message': f'Error adding work schedule: {str(e)}'})
            flash(f'Error adding work schedule: {str(e)}', 'error')
            return redirect(url_for('work_schedule_add'))
    
    # Get all working hours configurations
    working_hours_list = WorkingHours.query.order_by(WorkingHours.name).all()
    
    return render_template('masters/work_schedules/form.html', 
                         work_schedule=None, 
                         working_hours_list=working_hours_list)


@app.route('/masters/work-schedules/<int:work_schedule_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def work_schedule_edit(work_schedule_id):
    """Edit an existing work schedule"""
    work_schedule = WorkSchedule.query.get_or_404(work_schedule_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        working_hours_id = request.form.get('working_hours_id')
        
        # Get working days
        working_days = []
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            if request.form.get(day):
                working_days.append(day)
        
        if not name or not working_hours_id or not working_days:
            flash('Name, working hours, and at least one working day are required', 'error')
            return redirect(url_for('work_schedule_edit', work_schedule_id=work_schedule_id))
        
        # Check if another work schedule with same name exists
        existing_ws = WorkSchedule.query.filter(
            WorkSchedule.name == name,
            WorkSchedule.id != work_schedule_id
        ).first()
        if existing_ws:
            flash(f'Work schedule "{name}" already exists', 'error')
            return redirect(url_for('work_schedule_edit', work_schedule_id=work_schedule_id))
        
        try:
            work_schedule.name = name
            work_schedule.description = description if description else None
            work_schedule.working_hours_id = int(working_hours_id)
            work_schedule.monday = 'monday' in working_days
            work_schedule.tuesday = 'tuesday' in working_days
            work_schedule.wednesday = 'wednesday' in working_days
            work_schedule.thursday = 'thursday' in working_days
            work_schedule.friday = 'friday' in working_days
            work_schedule.saturday = 'saturday' in working_days
            work_schedule.sunday = 'sunday' in working_days
            db.session.commit()
            flash(f'Work schedule "{name}" updated successfully', 'success')
            return redirect(url_for('work_schedule_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating work schedule: {str(e)}', 'error')
            return redirect(url_for('work_schedule_edit', work_schedule_id=work_schedule_id))
    
    # Get all working hours configurations
    working_hours_list = WorkingHours.query.order_by(WorkingHours.name).all()
    
    return render_template('masters/work_schedules/form.html', 
                         work_schedule=work_schedule, 
                         working_hours_list=working_hours_list)


@app.route('/masters/work-schedules/<int:work_schedule_id>/delete', methods=['POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def work_schedule_delete(work_schedule_id):
    """Delete a work schedule"""
    work_schedule = WorkSchedule.query.get_or_404(work_schedule_id)
    
    # Check if work schedule is assigned to any employees
    employee_count = Employee.query.filter_by(work_schedule_id=work_schedule_id).count()
    if employee_count > 0:
        flash(f'Cannot delete work schedule "{work_schedule.name}" as it is assigned to {employee_count} employee(s)', 'error')
        return redirect(url_for('work_schedule_list'))
    
    try:
        ws_name = work_schedule.name
        db.session.delete(work_schedule)
        db.session.commit()
        flash(f'Work schedule "{ws_name}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting work schedule: {str(e)}', 'error')
    
    return redirect(url_for('work_schedule_list'))


# ============================================================================
# OT TYPES MANAGEMENT (Company-specific Overtime Types)
# ============================================================================

@app.route('/masters/ot-types')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def ot_type_list():
    """List all OT types for the tenant (applicable to all companies in tenant) with search and pagination"""
    from flask_login import current_user
    from sqlalchemy import and_
    
    # List all OT types globally (no tenant filtering)
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = OTType.query
    
    if search:
        query = query.filter(
            or_(
                OTType.name.ilike(f'%{search}%'),
                OTType.code.ilike(f'%{search}%'),
                OTType.description.ilike(f'%{search}%')
            )
        )
    
    ot_types = query.order_by(OTType.display_order, OTType.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('masters/ot_types/list.html', 
                         ot_types=ot_types, 
                         search=search)


@app.route('/masters/ot-types/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def ot_type_add():
    """Add a new OT type"""
    from flask_login import current_user
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        description = request.form.get('description', '').strip()
        rate_multiplier = request.form.get('rate_multiplier', '1.5')
        color_code = request.form.get('color_code', '#3498db')
        display_order = request.form.get('display_order', '0')
        is_active = request.form.get('is_active') == 'on'
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Get day flags
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_flags = {}
        for day in days:
            day_flags[day] = request.form.get(day) == 'on'
        
        if not name or not code:
            if is_ajax: return jsonify({'success': False, 'message': 'OT Type name and code are required'})
            flash('OT Type name and code are required', 'error')
            return redirect(url_for('ot_type_add'))
        
        # Check if OT type with same code already exists globally
        existing_ot = OTType.query.filter_by(code=code).first()
        if existing_ot:
            if is_ajax: return jsonify({'success': False, 'message': f'OT Type with code "{code}" already exists'})
            flash(f'OT Type with code "{code}" already exists', 'error')
            return redirect(url_for('ot_type_add'))
        
        try:
            ot_type = OTType(
                company_id=None, # Global
                name=name,
                code=code,
                description=description if description else None,
                rate_multiplier=float(rate_multiplier),
                color_code=color_code,
                # applicable_days=applicable_days if applicable_days else None, # Removed
                display_order=int(display_order),
                is_active=is_active,
                created_by=current_user.username,
                **day_flags # Unpack day flags
            )
            db.session.add(ot_type)
            db.session.commit()
            if is_ajax: return jsonify({'success': True, 'message': f'OT Type "{name}" added successfully'})
            flash(f'OT Type "{name}" added successfully', 'success')
            return redirect(url_for('ot_type_list'))
        except ValueError as e:
            if is_ajax: return jsonify({'success': False, 'message': f'Invalid input format: {str(e)}'})
            flash(f'Invalid input format: {str(e)}', 'error')
            return redirect(url_for('ot_type_add'))
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'success': False, 'message': f'Error adding OT Type: {str(e)}'})
            flash(f'Error adding OT Type: {str(e)}', 'error')
            return redirect(url_for('ot_type_add'))
    
    return render_template('masters/ot_types/form.html', ot_type=None)


@app.route('/masters/ot-types/<int:ot_type_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def ot_type_edit(ot_type_id):
    """Edit an existing OT type"""
    from flask_login import current_user
    
    ot_type = OTType.query.get_or_404(ot_type_id)
    
    # Global access - no tenant check
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        description = request.form.get('description', '').strip()
        rate_multiplier = request.form.get('rate_multiplier', '1.5')
        color_code = request.form.get('color_code', '#3498db')
        applicable_days = request.form.get('applicable_days', '')
        display_order = request.form.get('display_order', '0')
        is_active = request.form.get('is_active') == 'on'
        
        if not name or not code:
            flash('OT Type name and code are required', 'error')
            return redirect(url_for('ot_type_edit', ot_type_id=ot_type_id))
        
        # Check if another OT type with same code exists globally
        existing_ot = OTType.query.filter(
            OTType.code == code,
            OTType.id != ot_type_id
        ).first()
        if existing_ot:
            flash(f'Another OT Type with code "{code}" already exists', 'error')
            return redirect(url_for('ot_type_edit', ot_type_id=ot_type_id))
        
        try:
            ot_type.name = name
            ot_type.code = code
            ot_type.description = request.form.get('description')
            ot_type.rate_multiplier = float(rate_multiplier)
            ot_type.color_code = color_code
            ot_type.display_order = int(display_order)
            ot_type.is_active = request.form.get('is_active') == 'on'
            
            # Update day flags
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days:
                setattr(ot_type, day, request.form.get(day) == 'on')
            
            ot_type.modified_by = current_user.email
            ot_type.modified_at = datetime.now()
            
            db.session.commit()
            flash(f'OT Type "{name}" updated successfully', 'success')
            return redirect(url_for('ot_type_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating OT Type: {str(e)}', 'error')
            return redirect(url_for('ot_type_edit', ot_type_id=ot_type_id))
    
    return render_template('masters/ot_types/form.html', ot_type=ot_type)


@app.route('/masters/ot-types/<int:ot_type_id>/delete', methods=['POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def ot_type_delete(ot_type_id):
    """Delete an OT type"""
    from flask_login import current_user
    
    ot_type = OTType.query.get_or_404(ot_type_id)
    
    # Check access - only allow if user is from same tenant or is Super Admin
    user_tenant_id = None
    if hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.company_id:
        company = Company.query.get(current_user.employee_profile.company_id)
        if company:
            user_tenant_id = company.tenant_id
    
    # Get the OT Type's tenant (via its company)
    ot_company = Company.query.get(ot_type.company_id)
    ot_tenant_id = ot_company.tenant_id if ot_company else None
    
    if user_tenant_id and ot_tenant_id and ot_tenant_id != user_tenant_id:
        flash('Access Denied', 'error')
        return redirect(url_for('ot_type_list'))
    
    try:
        ot_name = ot_type.name
        db.session.delete(ot_type)
        db.session.commit()
        flash(f'OT Type "{ot_name}" deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting OT Type: {str(e)}', 'error')
    
    return redirect(url_for('ot_type_list'))


# ============================================================================
# USER STATUS TOGGLE MANAGEMENT
# ============================================================================

@app.route('/masters/user-status-toggle')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def user_status_toggle():
    """Manage user active/inactive status"""
    try:
        # Get users based on role
        if current_user.role and current_user.role.name == 'Super Admin':
            # Super Admin sees all users
            users = User.query.order_by(User.first_name, User.last_name).all()
        else:
            # Tenant Admin/HR Manager see only users from their tenant
            current_tenant_id = current_user.organization.tenant_id if current_user.organization else None
            if current_tenant_id:
                # Get all users in the same tenant
                users = db.session.query(User).join(
                    Organization, User.organization_id == Organization.id
                ).filter(
                    Organization.tenant_id == current_tenant_id
                ).order_by(User.first_name, User.last_name).all()
            else:
                users = []
        
        # Count active/inactive
        total_users = len(users)
        active_users = sum(1 for u in users if u.is_active)
        inactive_users = total_users - active_users
        
        return render_template(
            'masters/user_status_toggle.html',
            users=users,
            total_users=total_users,
            active_users=active_users,
            inactive_users=inactive_users
        )
    except Exception as e:
        flash(f'Error loading user status: {str(e)}', 'danger')
        return redirect(url_for('dashboard'))

# ============================================================================
# LEAVE MASTER ROUTES
# ============================================================================

@app.route('/masters/leave-types/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def leave_type_add():
    """Add a new Leave Type"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip().upper()
        annual_allocation = request.form.get('annual_allocation', 0, type=int)
        company_id = request.form.get('company_id')
        
        # Determine company context
        if not company_id:
            # If no company provided, try to use user's company (for HR Manager)
            if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
                company_id = current_user.employee_profile.company_id
            # If Tenant Admin/Super Admin, we might need a default or error if not provided
            # For simplicity, if not provided, try first active company (or handle error)
            
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not name or not code:
            msg = 'Name and Code are required'
            if is_ajax: return jsonify({'success': False, 'message': msg})
            flash(msg, 'error')
            return redirect(url_for('operation_master_dashboard'))

        try:
            # Need a company_id
            if not company_id:
                 company = Company.query.filter_by(is_active=True).first()
                 company_id = company.id if company else None
            
            # Check for duplication
            existing = LeaveType.query.filter_by(name=name, company_id=company_id).first()
            if existing:
                 msg = f'Leave Type "{name}" already exists'
                 if is_ajax: return jsonify({'success': False, 'message': msg})
                 flash(msg, 'error')
                 return redirect(url_for('operation_master_dashboard'))
            
            lt = LeaveType(
                name=name,
                code=code,
                annual_allocation=annual_allocation,
                company_id=company_id,
                created_by=getattr(current_user, 'username', 'system'),
                is_active=True
            )
            db.session.add(lt)
            db.session.commit()
            
            if is_ajax: return jsonify({'success': True, 'message': f'Leave Type "{name}" added successfully'})
            flash(f'Leave Type "{name}" added successfully', 'success')
            return redirect(url_for('operation_master_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'success': False, 'message': f'Error adding leave type: {str(e)}'})
            flash(f'Error adding leave type: {str(e)}', 'error')
            return redirect(url_for('operation_master_dashboard'))

    return redirect(url_for('operation_master_dashboard'))


@app.route('/masters/leave-groups/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def leave_group_add():
    """Add a new Leave Group"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        company_id = request.form.get('company_id')

        # Context logic similar to leave_type_add
        if not company_id and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
             company_id = current_user.employee_profile.company_id
        
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if not name:
             msg = 'Group Name is required'
             if is_ajax: return jsonify({'success': False, 'message': msg})
             flash(msg, 'error')
             return redirect(url_for('operation_master_dashboard'))
             
        try:
            if not company_id:
                 company = Company.query.filter_by(is_active=True).first()
                 company_id = company.id if company else None

            lg = EmployeeGroup(
                name=name, 
                description=description,
                company_id=company_id,
                category='Leave',
                created_by=getattr(current_user, 'username', 'system'),
                is_active=True
            )
            db.session.add(lg)
            db.session.commit()
            
            if is_ajax: return jsonify({'success': True, 'message': f'Leave Group "{name}" added successfully'})
            flash(f'Leave Group "{name}" added successfully', 'success')
            return redirect(url_for('operation_master_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            if is_ajax: return jsonify({'success': False, 'message': f'Error adding leave group: {str(e)}'})
            flash(f'Error adding leave group: {str(e)}', 'error')
            return redirect(url_for('operation_master_dashboard'))

    return redirect(url_for('operation_master_dashboard'))
