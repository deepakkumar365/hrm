"""
Master Data Management Routes
Handles CRUD operations for Roles, Departments, Working Hours, and Work Schedules
"""

from flask import render_template, request, redirect, url_for, flash
from sqlalchemy import or_
from datetime import datetime

from app import app, db
from auth import require_login, require_role
from models import Role, Department, WorkingHours, WorkSchedule, Employee  # , Designation  # UNCOMMENT AFTER MIGRATION


# ============================================================================
# ROLES MANAGEMENT
# ============================================================================

@app.route('/masters/roles')
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
def role_add():
    """Add a new role"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        
        if not name:
            flash('Role name is required', 'error')
            return redirect(url_for('role_add'))
        
        # Check if role already exists
        existing_role = Role.query.filter_by(name=name).first()
        if existing_role:
            flash(f'Role "{name}" already exists', 'error')
            return redirect(url_for('role_add'))
        
        try:
            role = Role(
                name=name,
                description=description if description else None
            )
            db.session.add(role)
            db.session.commit()
            flash(f'Role "{name}" added successfully', 'success')
            return redirect(url_for('role_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding role: {str(e)}', 'error')
            return redirect(url_for('role_add'))
    
    return render_template('masters/roles/form.html', role=None)


@app.route('/masters/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
def department_add():
    """Add a new department"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        manager_id = request.form.get('manager_id')
        
        if not name:
            flash('Department name is required', 'error')
            return redirect(url_for('department_add'))
        
        # Check if department already exists
        existing_dept = Department.query.filter_by(name=name).first()
        if existing_dept:
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
            flash(f'Department "{name}" added successfully', 'success')
            return redirect(url_for('department_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding department: {str(e)}', 'error')
            return redirect(url_for('department_add'))
    
    # Get all employees for manager selection
    managers = Employee.query.filter_by(is_active=True).order_by(
        Employee.first_name, Employee.last_name
    ).all()
    
    return render_template('masters/departments/form.html', 
                         department=None, 
                         managers=managers)


@app.route('/masters/departments/<int:department_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin'])
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
    managers = Employee.query.filter_by(is_active=True).order_by(
        Employee.first_name, Employee.last_name
    ).all()
    
    return render_template('masters/departments/form.html', 
                         department=department, 
                         managers=managers)


@app.route('/masters/departments/<int:department_id>/delete', methods=['POST'])
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
def working_hours_add():
    """Add a new working hours configuration"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        hours_per_day = request.form.get('hours_per_day', type=float)
        
        if not name or not start_time or not end_time or not hours_per_day:
            flash('All required fields must be filled', 'error')
            return redirect(url_for('working_hours_add'))
        
        # Check if working hours config already exists
        existing_wh = WorkingHours.query.filter_by(name=name).first()
        if existing_wh:
            flash(f'Working hours configuration "{name}" already exists', 'error')
            return redirect(url_for('working_hours_add'))
        
        try:
            # Parse time strings to time objects
            from datetime import datetime
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            working_hours = WorkingHours(
                name=name,
                description=description if description else None,
                start_time=start_time_obj,
                end_time=end_time_obj,
                hours_per_day=hours_per_day
            )
            db.session.add(working_hours)
            db.session.commit()
            flash(f'Working hours configuration "{name}" added successfully', 'success')
            return redirect(url_for('working_hours_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding working hours: {str(e)}', 'error')
            return redirect(url_for('working_hours_add'))
    
    return render_template('masters/working_hours/form.html', working_hours=None)


@app.route('/masters/working-hours/<int:working_hours_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin'])
def working_hours_edit(working_hours_id):
    """Edit an existing working hours configuration"""
    working_hours = WorkingHours.query.get_or_404(working_hours_id)
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')
        hours_per_day = request.form.get('hours_per_day', type=float)
        
        if not name or not start_time or not end_time or not hours_per_day:
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
            from datetime import datetime
            start_time_obj = datetime.strptime(start_time, '%H:%M').time()
            end_time_obj = datetime.strptime(end_time, '%H:%M').time()
            
            working_hours.name = name
            working_hours.description = description if description else None
            working_hours.start_time = start_time_obj
            working_hours.end_time = end_time_obj
            working_hours.hours_per_day = hours_per_day
            db.session.commit()
            flash(f'Working hours configuration "{name}" updated successfully', 'success')
            return redirect(url_for('working_hours_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating working hours: {str(e)}', 'error')
            return redirect(url_for('working_hours_edit', working_hours_id=working_hours_id))
    
    return render_template('masters/working_hours/form.html', working_hours=working_hours)


@app.route('/masters/working-hours/<int:working_hours_id>/delete', methods=['POST'])
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
def work_schedule_add():
    """Add a new work schedule"""
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
            return redirect(url_for('work_schedule_add'))
        
        # Check if work schedule already exists
        existing_ws = WorkSchedule.query.filter_by(name=name).first()
        if existing_ws:
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
            flash(f'Work schedule "{name}" added successfully', 'success')
            return redirect(url_for('work_schedule_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding work schedule: {str(e)}', 'error')
            return redirect(url_for('work_schedule_add'))
    
    # Get all working hours configurations
    working_hours_list = WorkingHours.query.order_by(WorkingHours.name).all()
    
    return render_template('masters/work_schedules/form.html', 
                         work_schedule=None, 
                         working_hours_list=working_hours_list)


@app.route('/masters/work-schedules/<int:work_schedule_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin'])
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
@require_role(['Super Admin', 'Admin'])
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
# DESIGNATIONS MANAGEMENT - UNCOMMENT AFTER MIGRATION
# ============================================================================

# @app.route('/masters/designations')
# @require_role(['Super Admin', 'Admin', 'HR Manager'])
# def designation_list():
#     """List all designations with search and pagination"""
#     page = request.args.get('page', 1, type=int)
#     search = request.args.get('search', '')
#     
#     query = Designation.query
#     
#     if search:
#         query = query.filter(
#             or_(
#                 Designation.name.ilike(f'%{search}%'),
#                 Designation.description.ilike(f'%{search}%')
#             )
#         )
#     
#     designations = query.order_by(Designation.created_at.desc()).paginate(
#         page=page, per_page=20, error_out=False
#     )
#     
#     return render_template('masters/designations/list.html', 
#                          designations=designations, 
#                          search=search)
# 
# 
# @app.route('/masters/designations/add', methods=['GET', 'POST'])
# @require_role(['Super Admin', 'Admin', 'HR Manager'])
# def designation_add():
#     """Add a new designation"""
#     if request.method == 'POST':
#         name = request.form.get('name', '').strip()
#         description = request.form.get('description', '').strip()
#         
#         if not name:
#             flash('Designation name is required', 'error')
#             return redirect(url_for('designation_add'))
#         
#         # Check if designation already exists
#         existing_designation = Designation.query.filter_by(name=name).first()
#         if existing_designation:
#             flash(f'Designation "{name}" already exists', 'error')
#             return redirect(url_for('designation_add'))
#         
#         try:
#             designation = Designation(
#                 name=name,
#                 description=description if description else None
#             )
#             db.session.add(designation)
#             db.session.commit()
#             flash(f'Designation "{name}" added successfully', 'success')
#             return redirect(url_for('designation_list'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error adding designation: {str(e)}', 'error')
#             return redirect(url_for('designation_add'))
#     
#     return render_template('masters/designations/form.html', designation=None)
# 
# 
# @app.route('/masters/designations/<int:designation_id>/edit', methods=['GET', 'POST'])
# @require_role(['Super Admin', 'Admin', 'HR Manager'])
# def designation_edit(designation_id):
#     """Edit an existing designation"""
#     designation = Designation.query.get_or_404(designation_id)
#     
#     if request.method == 'POST':
#         name = request.form.get('name', '').strip()
#         description = request.form.get('description', '').strip()
#         
#         if not name:
#             flash('Designation name is required', 'error')
#             return redirect(url_for('designation_edit', designation_id=designation_id))
#         
#         # Check if another designation with same name exists
#         existing_designation = Designation.query.filter(
#             Designation.name == name,
#             Designation.id != designation_id
#         ).first()
#         if existing_designation:
#             flash(f'Designation "{name}" already exists', 'error')
#             return redirect(url_for('designation_edit', designation_id=designation_id))
#         
#         try:
#             designation.name = name
#             designation.description = description if description else None
#             designation.updated_at = datetime.utcnow()
#             db.session.commit()
#             flash(f'Designation "{name}" updated successfully', 'success')
#             return redirect(url_for('designation_list'))
#         except Exception as e:
#             db.session.rollback()
#             flash(f'Error updating designation: {str(e)}', 'error')
#             return redirect(url_for('designation_edit', designation_id=designation_id))
#     
#     return render_template('masters/designations/form.html', designation=designation)
# 
# 
# @app.route('/masters/designations/<int:designation_id>/delete', methods=['POST'])
# @require_role(['Super Admin', 'Admin', 'HR Manager'])
# def designation_delete(designation_id):
#     """Delete a designation"""
#     designation = Designation.query.get_or_404(designation_id)
#     
#     # Check if designation is assigned to any employees
#     employee_count = Employee.query.filter_by(designation_id=designation_id).count()
#     if employee_count > 0:
#         flash(f'Cannot delete designation "{designation.name}" as it is assigned to {employee_count} employee(s)', 'error')
#         return redirect(url_for('designation_list'))
#     
#     try:
#         designation_name = designation.name
#         db.session.delete(designation)
#         db.session.commit()
#         flash(f'Designation "{designation_name}" deleted successfully', 'success')
#     except Exception as e:
#         db.session.rollback()
#         flash(f'Error deleting designation: {str(e)}', 'error')
#     
#     return redirect(url_for('designation_list'))