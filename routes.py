from flask import session, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from sqlalchemy import func, extract, and_
from datetime import datetime, date, time, timedelta
import calendar

from app import app, db
from auth import require_login, require_role, create_default_users
from models import Employee, Payroll, Attendance, Leave, Claim, Appraisal, ComplianceReport, User
from forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user
from singapore_payroll import SingaporePayrollCalculator
from utils import (export_to_csv, format_currency, format_date, parse_date,
                   validate_nric, generate_employee_id, check_permission,
                   mobile_optimized_pagination, get_current_month_dates)

# Initialize payroll calculator
payroll_calc = SingaporePayrollCalculator()

# Create default users on first run
with app.app_context():
    if create_default_users():
        print("Default users created successfully!")


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/')
def index():
    """Landing page and dashboard"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            flash(f'Welcome back, {user.first_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(
                url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('auth/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin'])
def register():
    """Register new user (Admin only)"""
    form = RegisterForm()
    if form.validate_on_submit():
        user = User()
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role = form.role.data if current_user.role in [
            'Super Admin', 'Admin'
        ] else 'User'
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'User {user.username} created successfully!', 'success')
        return redirect(url_for('user_management'))

    return render_template('auth/register.html', form=form)


@app.route('/logout')
@require_login
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@require_login
def dashboard():
    """Main dashboard with HR metrics"""

    # Get basic statistics
    stats = {
        'total_employees': Employee.query.filter_by(is_active=True).count(),
        'pending_leaves': Leave.query.filter_by(status='Pending').count(),
        'pending_claims': Claim.query.filter_by(status='Pending').count(),
        'this_month_attendance': 0
    }

    # Get current month attendance rate
    start_date, end_date = get_current_month_dates()
    total_attendance_records = Attendance.query.filter(
        Attendance.date.between(start_date, end_date)).count()

    working_days = sum(1 for d in range((end_date - start_date).days + 1)
                       if (start_date + timedelta(d)).weekday() < 5)

    if working_days > 0:
        expected_records = stats['total_employees'] * working_days
        if expected_records > 0:
            stats['attendance_rate'] = round(
                (total_attendance_records / expected_records) * 100.0)
        else:
            stats['attendance_rate'] = 0
    else:
        stats['attendance_rate'] = 0

    # Recent activities based on role
    recent_activities = []

    if current_user.role in ['Super Admin', 'Admin']:
        # Recent leaves for approval
        recent_leaves = Leave.query.filter_by(status='Pending').order_by(
            Leave.created_at.desc()).limit(5).all()
        for leave in recent_leaves:
            recent_activities.append({
                'type': 'leave_request',
                'employee':
                f"{leave.employee.first_name} {leave.employee.last_name}",
                'details':
                f"{leave.leave_type} leave from {format_date(leave.start_date)}",
                'date': leave.created_at
            })

    elif current_user.role == 'Manager':
        # Team member activities
        team_leaves = Leave.query.join(Employee).filter(
            Employee.manager_id == current_user.employee_profile.id,
            Leave.status == 'Pending').order_by(
                Leave.created_at.desc()).limit(5).all()

        for leave in team_leaves:
            recent_activities.append({
                'type': 'team_leave',
                'employee':
                f"{leave.employee.first_name} {leave.employee.last_name}",
                'details': f"{leave.leave_type} leave request",
                'date': leave.created_at
            })

    else:  # Employee
        # Own recent activities
        if hasattr(current_user,
                   'employee_profile') and current_user.employee_profile:
            emp_id = current_user.employee_profile.id
            my_leaves = Leave.query.filter_by(employee_id=emp_id).order_by(
                Leave.created_at.desc()).limit(3).all()

            for leave in my_leaves:
                recent_activities.append({
                    'type': 'my_leave',
                    'details': f"{leave.leave_type} leave - {leave.status}",
                    'date': leave.created_at
                })

    return render_template('dashboard.html',
                           stats=stats,
                           recent_activities=recent_activities,
                           moment=datetime.now)


# Employee Management Routes
@app.route('/employees')
@require_login
def employee_list():
    """List all employees with search and pagination"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    department = request.args.get('department', '', type=str)

    query = Employee.query.filter_by(is_active=True)

    if search:
        query = query.filter(
            db.or_(Employee.first_name.ilike(f'%{search}%'),
                   Employee.last_name.ilike(f'%{search}%'),
                   Employee.employee_id.ilike(f'%{search}%'),
                   Employee.email.ilike(f'%{search}%')))

    if department:
        query = query.filter(Employee.department == department)

    # Role-based filtering
    if current_user.role == 'Manager' and hasattr(current_user,
                                                  'employee_profile'):
        query = query.filter(
            Employee.manager_id == current_user.employee_profile.id)

    employees = query.order_by(Employee.first_name).paginate(page=page,
                                                             per_page=20,
                                                             error_out=False)

    # Get departments for filter
    departments = db.session.query(Employee.department).distinct().filter(
        Employee.department.isnot(None), Employee.is_active == True).all()
    departments = [d[0] for d in departments]

    return render_template('employees/list.html',
                           employees=employees,
                           search=search,
                           department=department,
                           departments=departments)


@app.route('/employees/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin'])
def employee_add():
    """Add new employee"""
    if request.method == 'POST':
        try:
            # Validate NRIC
            nric = request.form.get('nric', '').upper()
            if not validate_nric(nric):
                flash('Invalid NRIC format', 'error')
                return render_template('employees/form.html')

            # Check for duplicate NRIC
            if Employee.query.filter_by(nric=nric).first():
                flash('Employee with this NRIC already exists', 'error')
                return render_template('employees/form.html')

            # Create new employee
            employee = Employee()
            employee.employee_id = generate_employee_id()
            employee.first_name = request.form.get('first_name')
            employee.last_name = request.form.get('last_name')
            employee.email = request.form.get('email')
            employee.phone = request.form.get('phone')
            employee.nric = nric
            employee.date_of_birth = parse_date(
                request.form.get('date_of_birth'))
            employee.gender = request.form.get('gender')
            employee.nationality = request.form.get('nationality')
            employee.address = request.form.get('address')
            employee.postal_code = request.form.get('postal_code')
            employee.position = request.form.get('position')
            employee.department = request.form.get('department')
            employee.hire_date = parse_date(request.form.get('hire_date'))
            employee.employment_type = request.form.get('employment_type')
            employee.work_permit_type = request.form.get('work_permit_type')

            work_permit_expiry = request.form.get('work_permit_expiry')
            if work_permit_expiry:
                employee.work_permit_expiry = parse_date(work_permit_expiry)

            employee.basic_salary = float(request.form.get('basic_salary', 0))
            employee.allowances = float(request.form.get('allowances', 0))

            hourly_rate = request.form.get('hourly_rate')
            if hourly_rate:
                employee.hourly_rate = float(hourly_rate)

            employee.cpf_account = request.form.get('cpf_account')
            employee.bank_name = request.form.get('bank_name')
            employee.bank_account = request.form.get('bank_account')

            manager_id = request.form.get('manager_id')
            if manager_id:
                employee.manager_id = int(manager_id)

            db.session.add(employee)
            db.session.commit()

            flash('Employee added successfully', 'success')
            return redirect(url_for('employee_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')

    # Get managers for dropdown
    managers = Employee.query.filter_by(is_active=True).filter(
        Employee.position.ilike('%manager%')).all()

    return render_template('employees/form.html', managers=managers)


@app.route('/employees/<int:employee_id>')
@require_login
def employee_view(employee_id):
    """View employee details"""
    employee = Employee.query.get_or_404(employee_id)

    # Check permission
    if current_user.role == 'Employee':
        if not (hasattr(current_user, 'employee_profile')
                and current_user.employee_profile.id == employee_id):
            return render_template('403.html'), 403
    elif current_user.role == 'Manager':
        if not (hasattr(current_user, 'employee_profile') and
                (current_user.employee_profile.id == employee_id
                 or employee.manager_id == current_user.employee_profile.id)):
            return render_template('403.html'), 403

    # Get recent payslips
    recent_payslips = Payroll.query.filter_by(
        employee_id=employee_id).order_by(
            Payroll.pay_period_end.desc()).limit(3).all()

    # Get recent attendance
    recent_attendance = Attendance.query.filter_by(
        employee_id=employee_id).order_by(
            Attendance.date.desc()).limit(7).all()

    return render_template('employees/view.html',
                           employee=employee,
                           recent_payslips=recent_payslips,
                           recent_attendance=recent_attendance,
                           today=date.today())


@app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin'])
def employee_edit(employee_id):
    """Edit employee details"""
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        try:
            employee.first_name = request.form.get('first_name')
            employee.last_name = request.form.get('last_name')
            employee.email = request.form.get('email')
            employee.phone = request.form.get('phone')
            employee.address = request.form.get('address')
            employee.postal_code = request.form.get('postal_code')
            employee.position = request.form.get('position')
            employee.department = request.form.get('department')
            employee.employment_type = request.form.get('employment_type')
            employee.work_permit_type = request.form.get('work_permit_type')

            work_permit_expiry = request.form.get('work_permit_expiry')
            if work_permit_expiry:
                employee.work_permit_expiry = parse_date(work_permit_expiry)

            employee.basic_salary = float(request.form.get('basic_salary', 0))
            employee.allowances = float(request.form.get('allowances', 0))

            hourly_rate = request.form.get('hourly_rate')
            if hourly_rate:
                employee.hourly_rate = float(hourly_rate)

            employee.cpf_account = request.form.get('cpf_account')
            employee.bank_name = request.form.get('bank_name')
            employee.bank_account = request.form.get('bank_account')

            manager_id = request.form.get('manager_id')
            if manager_id:
                employee.manager_id = int(manager_id)
            else:
                employee.manager_id = None

            db.session.commit()
            flash('Employee updated successfully', 'success')
            return redirect(url_for('employee_view', employee_id=employee_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'error')

    managers = Employee.query.filter_by(is_active=True).filter(
        Employee.position.ilike('%manager%'), Employee.id
        != employee_id).all()

    return render_template('employees/form.html',
                           employee=employee,
                           managers=managers)


# Payroll Management Routes
@app.route('/payroll')
@require_role(['Super Admin', 'Admin', 'Manager'])
def payroll_list():
    """List payroll records"""
    page = request.args.get('page', 1, type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)

    query = Payroll.query.join(Employee)

    if month and year:
        query = query.filter(
            extract('month', Payroll.pay_period_end) == month,
            extract('year', Payroll.pay_period_end) == year)

    # Role-based filtering
    if current_user.role == 'Manager' and hasattr(current_user,
                                                  'employee_profile'):
        # Manager: Their own payroll + their team's payroll
        manager_id = current_user.employee_profile.id
        query = query.filter(
            db.or_(
                Payroll.employee_id == manager_id,  # Manager's own payroll
                Employee.manager_id == manager_id  # Team's payroll
            ))
    elif current_user.role == 'Admin' and hasattr(current_user,
                                                  'employee_profile'):
        # Admin: Their own payroll + all employees' payroll (they see everything anyway)
        pass  # No filtering - they can see all

    payrolls = query.order_by(Payroll.pay_period_end.desc()).paginate(
        page=page, per_page=20, error_out=False)

    return render_template('payroll/list.html',
                           payrolls=payrolls,
                           month=month,
                           year=year,
                           calendar=calendar)


@app.route('/payroll/generate', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin'])
def payroll_generate():
    """Generate payroll for selected period"""
    if request.method == 'POST':
        try:
            pay_period_start = parse_date(request.form.get('pay_period_start'))
            pay_period_end = parse_date(request.form.get('pay_period_end'))
            selected_employees = request.form.getlist('employees')

            generated_count = 0

            for emp_id in selected_employees:
                employee = Employee.query.get(int(emp_id))
                if not employee:
                    continue

                # Check if payroll already exists for this period
                existing = Payroll.query.filter_by(
                    employee_id=employee.id,
                    pay_period_start=pay_period_start,
                    pay_period_end=pay_period_end).first()

                if existing:
                    continue

                # Get attendance data for overtime calculation
                attendance_records = Attendance.query.filter_by(
                    employee_id=employee.id).filter(
                        Attendance.date.between(pay_period_start,
                                                pay_period_end)).all()

                total_overtime = sum(record.overtime_hours or 0
                                     for record in attendance_records)

                # Calculate payroll
                payroll_data = payroll_calc.calculate_payroll(
                    employee,
                    pay_period_start,
                    pay_period_end,
                    overtime_hours=total_overtime)

                # Create payroll record
                payroll = Payroll()
                payroll.employee_id = employee.id
                payroll.pay_period_start = pay_period_start
                payroll.pay_period_end = pay_period_end
                payroll.basic_pay = payroll_data['basic_pay']
                payroll.overtime_pay = payroll_data['overtime_pay']
                payroll.allowances = payroll_data['allowances']
                payroll.bonuses = payroll_data['bonuses']
                payroll.gross_pay = payroll_data['gross_pay']
                payroll.employee_cpf = payroll_data['employee_cpf']
                payroll.employer_cpf = payroll_data['employer_cpf']
                payroll.other_deductions = payroll_data['other_deductions']
                payroll.net_pay = payroll_data['net_pay']
                payroll.overtime_hours = total_overtime
                payroll.days_worked = len(attendance_records)
                payroll.generated_by = current_user.id

                db.session.add(payroll)
                generated_count += 1

            db.session.commit()
            flash(f'Generated payroll for {generated_count} employees',
                  'success')
            return redirect(url_for('payroll_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error generating payroll: {str(e)}', 'error')

    # Get active employees
    employees = Employee.query.filter_by(is_active=True).order_by(
        Employee.first_name).all()

    return render_template('payroll/form.html', employees=employees)


@app.route('/payroll/<int:payroll_id>/payslip')
@require_login
def payroll_payslip(payroll_id):
    """View/download payslip"""
    payroll = Payroll.query.get_or_404(payroll_id)

    # Check permission
    if current_user.role == 'Employee':
        if not (hasattr(current_user, 'employee_profile')
                and current_user.employee_profile.id == payroll.employee_id):
            return render_template('403.html'), 403
    elif current_user.role == 'Manager':
        if not (hasattr(current_user, 'employee_profile')
                and payroll.employee.manager_id
                == current_user.employee_profile.id):
            return render_template('403.html'), 403

    return render_template('payroll/payslip.html', payroll=payroll)


# Attendance Management Routes
@app.route('/attendance')
@require_login
def attendance_list():
    """List attendance records"""
    page = request.args.get('page', 1, type=int)
    date_filter = request.args.get('date', type=str)
    employee_filter = request.args.get('employee', type=int)

    query = Attendance.query.join(Employee)

    if date_filter:
        filter_date = parse_date(date_filter)
        if filter_date:
            query = query.filter(Attendance.date == filter_date)

    if employee_filter:
        query = query.filter(Attendance.employee_id == employee_filter)

    # Role-based filtering
    if current_user.role == 'Employee' and hasattr(current_user,
                                                   'employee_profile'):
        # Employee: Only their own attendance
        query = query.filter(
            Attendance.employee_id == current_user.employee_profile.id)
    elif current_user.role == 'Manager' and hasattr(current_user,
                                                    'employee_profile'):
        # Manager: Their own attendance + their team's attendance
        manager_id = current_user.employee_profile.id
        query = query.filter(
            db.or_(
                Attendance.employee_id ==
                manager_id,  # Manager's own attendance
                Employee.manager_id == manager_id  # Team's attendance
            ))
    elif current_user.role == 'Admin' and hasattr(current_user,
                                                  'employee_profile'):
        # Admin: Their own attendance + all employees' attendance (but they see everything anyway)
        pass  # No filtering - they can see all

    attendance_records = query.order_by(Attendance.date.desc()).paginate(
        page=page, per_page=20, error_out=False)

    # Get employees for filter (if admin/manager)
    employees = []
    if current_user.role in ['Super Admin', 'Admin', 'Manager']:
        employees = Employee.query.filter_by(is_active=True).order_by(
            Employee.first_name).all()

    return render_template('attendance/list.html',
                           attendance_records=attendance_records,
                           employees=employees,
                           date_filter=date_filter,
                           employee_filter=employee_filter)


@app.route('/attendance/mark', methods=['GET', 'POST'])
@require_login
def attendance_mark():
    """Mark attendance (for employees)"""
    if request.method == 'POST':
        try:
            if not hasattr(
                    current_user,
                    'employee_profile') or not current_user.employee_profile:
                flash('Employee profile required for attendance marking',
                      'error')
                return redirect(url_for('dashboard'))

            today = date.today()
            employee_id = current_user.employee_profile.id

            # Check if already marked today
            existing = Attendance.query.filter_by(employee_id=employee_id,
                                                  date=today).first()

            action = request.form.get(
                'action')  # clock_in, clock_out, break_start, break_end
            current_time = datetime.now().time()

            if action == 'clock_in':
                # Check for incomplete attendance from previous day(s)
                yesterday = today - timedelta(days=1)
                incomplete_attendance = Attendance.query.filter(
                    Attendance.employee_id == employee_id, Attendance.date
                    < today, Attendance.clock_out.is_(None)).order_by(
                        Attendance.date.desc()).first()

                if incomplete_attendance:
                    # Auto-complete previous day with default 6PM clock out
                    default_clock_out = time(18, 0)  # 6:00 PM
                    incomplete_attendance.clock_out = default_clock_out

                    # Calculate hours for the incomplete day
                    clock_in_dt = datetime.combine(
                        incomplete_attendance.date,
                        incomplete_attendance.clock_in)
                    clock_out_dt = datetime.combine(incomplete_attendance.date,
                                                    default_clock_out)
                    total_seconds = (clock_out_dt -
                                     clock_in_dt).total_seconds()

                    # Subtract break time if applicable
                    if incomplete_attendance.break_start and incomplete_attendance.break_end:
                        break_start_dt = datetime.combine(
                            incomplete_attendance.date,
                            incomplete_attendance.break_start)
                        break_end_dt = datetime.combine(
                            incomplete_attendance.date,
                            incomplete_attendance.break_end)
                        break_seconds = (break_end_dt -
                                         break_start_dt).total_seconds()
                        total_seconds -= break_seconds

                    total_hours = total_seconds / 3600

                    # Standard work day is 8 hours
                    if total_hours > 8:
                        incomplete_attendance.regular_hours = 8
                        incomplete_attendance.overtime_hours = total_hours - 8
                    else:
                        incomplete_attendance.regular_hours = total_hours
                        incomplete_attendance.overtime_hours = 0

                    incomplete_attendance.total_hours = total_hours
                    incomplete_attendance.notes = f"Auto-completed: Forgot to clock out on {incomplete_attendance.date.strftime('%Y-%m-%d')}"

                    flash(
                        f'Previous incomplete attendance for {incomplete_attendance.date.strftime("%B %d")} has been auto-completed with 6:00 PM clock out.',
                        'info')

                if not existing:
                    # Create new attendance record
                    attendance = Attendance()
                    attendance.employee_id = employee_id
                    attendance.date = today
                    attendance.clock_in = current_time
                    attendance.status = 'Present'

                    # Get location if provided
                    lat = request.form.get('latitude')
                    lng = request.form.get('longitude')
                    if lat and lng:
                        attendance.location_lat = lat
                        attendance.location_lng = lng

                    db.session.add(attendance)
                    flash('Clocked in successfully', 'success')
                else:
                    flash('Already clocked in for today', 'warning')
            elif existing:
                # Update existing record
                if action == 'clock_out':
                    existing.clock_out = current_time
                    # Calculate hours
                    if existing.clock_in:
                        clock_in_dt = datetime.combine(today,
                                                       existing.clock_in)
                        clock_out_dt = datetime.combine(today, current_time)
                        total_seconds = (clock_out_dt -
                                         clock_in_dt).total_seconds()

                        # Subtract break time if applicable
                        if existing.break_start and existing.break_end:
                            break_start_dt = datetime.combine(
                                today, existing.break_start)
                            break_end_dt = datetime.combine(
                                today, existing.break_end)
                            break_seconds = (break_end_dt -
                                             break_start_dt).total_seconds()
                            total_seconds -= break_seconds

                        total_hours = total_seconds / 3600

                        # Standard work day is 8 hours
                        if total_hours > 8:
                            existing.regular_hours = 8
                            existing.overtime_hours = total_hours - 8
                        else:
                            existing.regular_hours = total_hours
                            existing.overtime_hours = 0

                        existing.total_hours = total_hours

                    flash('Clocked out successfully', 'success')

                elif action == 'break_start':
                    existing.break_start = current_time
                    flash('Break started', 'success')

                elif action == 'break_end':
                    existing.break_end = current_time
                    flash('Break ended', 'success')
            else:
                # No existing record found for break/clock_out actions
                if action in ['break_start', 'break_end', 'clock_out']:
                    flash(
                        'Please clock in first before performing this action',
                        'warning')
                    return redirect(url_for('attendance_mark'))

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            flash(f'Error marking attendance: {str(e)}', 'error')

    # Get today's attendance record
    today_attendance = None
    if hasattr(current_user,
               'employee_profile') and current_user.employee_profile:
        today_attendance = Attendance.query.filter_by(
            employee_id=current_user.employee_profile.id,
            date=date.today()).first()
    else:
        flash(
            'You need an employee profile to mark attendance. Contact your administrator.',
            'warning')

    return render_template('attendance/form.html',
                           today_attendance=today_attendance)


@app.route('/attendance/correct/<int:attendance_id>', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def attendance_correct(attendance_id):
    """Correct incomplete attendance records (Manager only)"""
    attendance = Attendance.query.get_or_404(attendance_id)

    # Check if manager can access this employee's record
    if current_user.role == 'Manager':
        if not hasattr(current_user, 'employee_profile') or \
           attendance.employee.manager_id != current_user.employee_profile.id:
            flash('Access denied', 'error')
            return redirect(url_for('attendance_list'))

    if request.method == 'POST':
        try:
            # Update attendance record
            clock_out_str = request.form.get('clock_out')
            if clock_out_str:
                attendance.clock_out = datetime.strptime(
                    clock_out_str, '%H:%M').time()

                # Recalculate hours
                if attendance.clock_in:
                    clock_in_dt = datetime.combine(attendance.date,
                                                   attendance.clock_in)
                    clock_out_dt = datetime.combine(attendance.date,
                                                    attendance.clock_out)
                    total_seconds = (clock_out_dt -
                                     clock_in_dt).total_seconds()

                    # Subtract break time if applicable
                    if attendance.break_start and attendance.break_end:
                        break_start_dt = datetime.combine(
                            attendance.date, attendance.break_start)
                        break_end_dt = datetime.combine(
                            attendance.date, attendance.break_end)
                        break_seconds = (break_end_dt -
                                         break_start_dt).total_seconds()
                        total_seconds -= break_seconds

                    total_hours = total_seconds / 3600

                    # Standard work day is 8 hours
                    if total_hours > 8:
                        attendance.regular_hours = 8
                        attendance.overtime_hours = total_hours - 8
                    else:
                        attendance.regular_hours = total_hours
                        attendance.overtime_hours = 0

                    attendance.total_hours = total_hours

            # Add correction note
            correction_note = request.form.get('notes', '')
            if attendance.notes:
                attendance.notes += f"\nCorrected by {current_user.first_name} {current_user.last_name}: {correction_note}"
            else:
                attendance.notes = f"Corrected by {current_user.first_name} {current_user.last_name}: {correction_note}"

            db.session.commit()
            flash('Attendance record corrected successfully', 'success')
            return redirect(url_for('attendance_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error correcting attendance: {str(e)}', 'error')

    return render_template('attendance/correct.html', attendance=attendance)


def auto_complete_incomplete_attendance():
    """Auto-complete attendance records that are still incomplete after 24 hours"""
    yesterday = date.today() - timedelta(days=1)

    # Find all incomplete attendance records from yesterday
    incomplete_records = Attendance.query.filter(
        Attendance.date == yesterday, Attendance.clock_out.is_(None)).all()

    for record in incomplete_records:
        # Auto-complete with 6 PM clock out
        default_clock_out = time(18, 0)
        record.clock_out = default_clock_out

        # Calculate hours
        clock_in_dt = datetime.combine(record.date, record.clock_in)
        clock_out_dt = datetime.combine(record.date, default_clock_out)
        total_seconds = (clock_out_dt - clock_in_dt).total_seconds()

        # Subtract break time if applicable
        if record.break_start and record.break_end:
            break_start_dt = datetime.combine(record.date, record.break_start)
            break_end_dt = datetime.combine(record.date, record.break_end)
            break_seconds = (break_end_dt - break_start_dt).total_seconds()
            total_seconds -= break_seconds

        total_hours = total_seconds / 3600

        # Standard work day is 8 hours
        if total_hours > 8:
            record.regular_hours = 8
            record.overtime_hours = total_hours - 8
        else:
            record.regular_hours = total_hours
            record.overtime_hours = 0

        record.total_hours = total_hours
        record.notes = f"Auto-completed by system: Forgot to clock out on {record.date.strftime('%Y-%m-%d')}"

    if incomplete_records:
        db.session.commit()
        print(
            f"Auto-completed {len(incomplete_records)} incomplete attendance records"
        )


@app.route('/attendance/incomplete')
@require_role(['Super Admin', 'Admin', 'Manager'])
def attendance_incomplete():
    """View incomplete attendance records that need correction"""
    # Find incomplete attendance records from the last 7 days
    week_ago = date.today() - timedelta(days=7)

    query = Attendance.query.filter(
        Attendance.date >= week_ago,
        Attendance.clock_out.is_(None)).join(Employee)

    # Role-based filtering
    if current_user.role == 'Manager' and hasattr(current_user,
                                                  'employee_profile'):
        query = query.filter(
            Employee.manager_id == current_user.employee_profile.id)

    incomplete_records = query.order_by(Attendance.date.desc()).all()

    return render_template('attendance/incomplete.html',
                           incomplete_records=incomplete_records)


# Leave Management Routes
@app.route('/leave')
@require_login
def leave_list():
    """List leave requests"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', type=str)
    employee_filter = request.args.get('employee', type=int)

    query = Leave.query.join(Employee)

    if status_filter:
        query = query.filter(Leave.status == status_filter)

    if employee_filter:
        query = query.filter(Leave.employee_id == employee_filter)

    # Role-based filtering
    if current_user.role == 'Employee' and hasattr(current_user,
                                                   'employee_profile'):
        # Employee: Only their own leave requests
        query = query.filter(
            Leave.employee_id == current_user.employee_profile.id)
    elif current_user.role == 'Manager' and hasattr(current_user,
                                                    'employee_profile'):
        # Manager: Their own leave requests + their team's leave requests
        manager_id = current_user.employee_profile.id
        query = query.filter(
            db.or_(
                Leave.employee_id ==
                manager_id,  # Manager's own leave requests
                Employee.manager_id == manager_id  # Team's leave requests
            ))
    elif current_user.role == 'Admin' and hasattr(current_user,
                                                  'employee_profile'):
        # Admin: Their own leave requests + all employees' leave requests (they see everything anyway)
        pass  # No filtering - they can see all

    leave_requests = query.order_by(Leave.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)

    employees = []
    if current_user.role in ['Super Admin', 'Admin', 'Manager']:
        employees = Employee.query.filter_by(is_active=True).order_by(
            Employee.first_name).all()

    return render_template('leave/list.html',
                           leave_requests=leave_requests,
                           employees=employees,
                           status_filter=status_filter,
                           employee_filter=employee_filter)


@app.route('/leave/request', methods=['GET', 'POST'])
@require_login
def leave_request():
    """Submit leave request"""
    if request.method == 'POST':
        try:
            if not hasattr(
                    current_user,
                    'employee_profile') or not current_user.employee_profile:
                flash('Employee profile required for attendance marking',
                      'error')
                return redirect(url_for('dashboard'))

            leave = Leave()
            leave.employee_id = current_user.employee_profile.id
            leave.leave_type = request.form.get('leave_type')
            leave.start_date = parse_date(request.form.get('start_date'))
            leave.end_date = parse_date(request.form.get('end_date'))
            leave.reason = request.form.get('reason')
            leave.requested_by = current_user.id

            # Calculate days
            if leave.start_date and leave.end_date:
                days = (leave.end_date - leave.start_date).days + 1
                leave.days_requested = days

            db.session.add(leave)
            db.session.commit()

            flash('Leave request submitted successfully', 'success')
            return redirect(url_for('leave_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting leave request: {str(e)}', 'error')

    return render_template('leave/form.html')


@app.route('/leave/<int:leave_id>/approve', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def leave_approve(leave_id):
    """Approve/reject leave request"""
    leave = Leave.query.get_or_404(leave_id)

    # Check if manager can approve this leave
    if current_user.role == 'Manager':
        if not (hasattr(current_user, 'employee_profile') and
                leave.employee.manager_id == current_user.employee_profile.id):
            return render_template('403.html'), 403

    try:
        action = request.form.get('action')

        if action == 'approve':
            leave.status = 'Approved'
            leave.approved_by = current_user.id
            leave.approved_at = datetime.now()
            flash('Leave request approved', 'success')

        elif action == 'reject':
            leave.status = 'Rejected'
            leave.approved_by = current_user.id
            leave.approved_at = datetime.now()
            leave.rejection_reason = request.form.get('rejection_reason')
            flash('Leave request rejected', 'success')

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing leave request: {str(e)}', 'error')

    return redirect(url_for('leave_list'))


# Claims Management Routes
@app.route('/claims')
@require_login
def claims_list():
    """List claims"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', type=str)

    query = Claim.query.join(Employee)

    if status_filter:
        query = query.filter(Claim.status == status_filter)

    # Role-based filtering
    if current_user.role == 'Employee' and hasattr(current_user,
                                                   'employee_profile'):
        query = query.filter(
            Claim.employee_id == current_user.employee_profile.id)
    elif current_user.role == 'Manager' and hasattr(current_user,
                                                    'employee_profile'):
        query = query.filter(
            Employee.manager_id == current_user.employee_profile.id)

    claims = query.order_by(Claim.created_at.desc()).paginate(page=page,
                                                              per_page=20,
                                                              error_out=False)

    return render_template('claims/list.html',
                           claims=claims,
                           status_filter=status_filter)


@app.route('/claims/submit', methods=['GET', 'POST'])
@require_login
def claims_submit():
    """Submit new claim"""
    if request.method == 'POST':
        try:
            if not hasattr(
                    current_user,
                    'employee_profile') or not current_user.employee_profile:
                flash('Employee profile required for attendance marking',
                      'error')
                return redirect(url_for('dashboard'))

            claim = Claim()
            claim.employee_id = current_user.employee_profile.id
            claim.claim_type = request.form.get('claim_type')
            amount_str = request.form.get('amount')
            claim.amount = float(amount_str) if amount_str else 0.0
            claim.claim_date = parse_date(request.form.get('claim_date'))
            claim.description = request.form.get('description')
            claim.receipt_number = request.form.get('receipt_number')
            claim.submitted_by = current_user.id

            db.session.add(claim)
            db.session.commit()

            flash('Claim submitted successfully', 'success')
            return redirect(url_for('claims_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting claim: {str(e)}', 'error')

    return render_template('claims/form.html')


@app.route('/claims/<int:claim_id>/approve', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def claims_approve(claim_id):
    """Approve/reject claim"""
    claim = Claim.query.get_or_404(claim_id)

    try:
        action = request.form.get('action')

        if action == 'approve':
            claim.status = 'Approved'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            flash('Claim approved', 'success')

        elif action == 'reject':
            claim.status = 'Rejected'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            claim.rejection_reason = request.form.get('rejection_reason')
            flash('Claim rejected', 'success')

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')

    return redirect(url_for('claims_list'))


# Appraisal Management Routes
@app.route('/appraisal')
@require_login
def appraisal_list():
    """List appraisals"""
    page = request.args.get('page', 1, type=int)

    query = Appraisal.query.join(Employee)

    # Role-based filtering
    if current_user.role == 'Employee' and hasattr(current_user,
                                                   'employee_profile'):
        query = query.filter(
            Appraisal.employee_id == current_user.employee_profile.id)
    elif current_user.role == 'Manager' and hasattr(current_user,
                                                    'employee_profile'):
        query = query.filter(
            Employee.manager_id == current_user.employee_profile.id)

    appraisals = query.order_by(Appraisal.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)

    return render_template('appraisal/list.html', appraisals=appraisals)


@app.route('/appraisal/create', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def appraisal_create():
    """Create new appraisal"""
    if request.method == 'POST':
        try:
            appraisal = Appraisal()
            employee_id_str = request.form.get('employee_id')
            appraisal.employee_id = int(
                employee_id_str) if employee_id_str else 0
            appraisal.review_period_start = parse_date(
                request.form.get('review_period_start'))
            appraisal.review_period_end = parse_date(
                request.form.get('review_period_end'))
            appraisal.performance_rating = int(
                request.form.get('performance_rating', '0'))
            appraisal.goals_achievement = int(
                request.form.get('goals_achievement', '0'))
            appraisal.teamwork_rating = int(
                request.form.get('teamwork_rating', '0'))
            appraisal.communication_rating = int(
                request.form.get('communication_rating', '0'))

            # Calculate overall rating
            ratings = [
                appraisal.performance_rating, appraisal.goals_achievement,
                appraisal.teamwork_rating, appraisal.communication_rating
            ]
            appraisal.overall_rating = sum(ratings) / len(ratings)

            appraisal.manager_feedback = request.form.get('manager_feedback')
            appraisal.development_goals = request.form.get('development_goals')
            appraisal.training_recommendations = request.form.get(
                'training_recommendations')
            appraisal.reviewed_by = current_user.id
            appraisal.status = 'Completed'
            appraisal.completed_at = datetime.now()

            db.session.add(appraisal)
            db.session.commit()

            flash('Appraisal created successfully', 'success')
            return redirect(url_for('appraisal_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error creating appraisal: {str(e)}', 'error')

    # Get employees for appraisal
    employees = Employee.query.filter_by(is_active=True)
    if current_user.role == 'Manager' and hasattr(current_user,
                                                  'employee_profile'):
        employees = employees.filter(
            Employee.manager_id == current_user.employee_profile.id)
    employees = employees.order_by(Employee.first_name).all()

    return render_template('appraisal/form.html', employees=employees)


# Compliance and Reports
@app.route('/compliance')
@require_role(['Super Admin', 'Admin'])
def compliance_dashboard():
    """Compliance dashboard"""

    # Get current month for defaults
    current_month = datetime.now().month
    current_year = datetime.now().year

    # Recent compliance reports
    recent_reports = ComplianceReport.query.order_by(
        ComplianceReport.generated_at.desc()).limit(10).all()

    # Upcoming deadlines (simplified)
    deadlines = [{
        'type':
        'CPF Submission',
        'date':
        f"14/{current_month + 1 if current_month < 12 else 1}/{current_year if current_month < 12 else current_year + 1}"
    }, {
        'type': 'AIS Filing',
        'date': f"31/03/{current_year + 1}"
    }, {
        'type':
        'MOM OED',
        'date':
        f"15/{current_month + 1 if current_month < 12 else 1}/{current_year if current_month < 12 else current_year + 1}"
    }]

    return render_template('compliance/dashboard.html',
                           recent_reports=recent_reports,
                           deadlines=deadlines,
                           current_month=current_month,
                           current_year=current_year)


@app.route('/compliance/generate/<report_type>')
@require_role(['Super Admin', 'Admin'])
def compliance_generate(report_type):
    """Generate compliance reports"""
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)

    try:
        # Get payroll records for the period
        payrolls = Payroll.query.filter(
            extract('month', Payroll.pay_period_end) == month,
            extract('year', Payroll.pay_period_end) == year,
            Payroll.status == 'Approved').all()

        if not payrolls:
            flash('No approved payroll records found for the selected period',
                  'warning')
            return redirect(url_for('compliance_dashboard'))

        if report_type == 'cpf':
            data = payroll_calc.generate_cpf_file(payrolls, month, year)
            filename = f"CPF_Submission_{year}_{month:02d}.csv"

            # Prepare CSV data
            csv_data = []
            for record in data['records']:
                csv_data.append([
                    record['employee_id'], record['name'], record['nric'],
                    record['cpf_account'], record['gross_salary'],
                    record['employee_cpf'], record['employer_cpf'],
                    record['total_cpf']
                ])

            headers = [
                'Employee ID', 'Name', 'NRIC', 'CPF Account', 'Gross Salary',
                'Employee CPF', 'Employer CPF', 'Total CPF'
            ]

            return export_to_csv(csv_data, filename, headers)

        elif report_type == 'ais':
            data = payroll_calc.generate_ais_file(payrolls, year)
            filename = f"AIS_Report_{year}.csv"

            csv_data = []
            for record in data['records']:
                csv_data.append([
                    record['employee_id'], record['name'], record['nric'],
                    record['annual_income'], record['employment_period']
                ])

            headers = [
                'Employee ID', 'Name', 'NRIC', 'Annual Income',
                'Employment Period'
            ]

            return export_to_csv(csv_data, filename, headers)

        elif report_type == 'oed':
            data = payroll_calc.generate_oed_file(payrolls, month, year)
            filename = f"OED_Report_{year}_{month:02d}.csv"

            csv_data = []
            for record in data['records']:
                csv_data.append([
                    record['employee_id'], record['name'],
                    record['passport_number'], record['work_permit_type'],
                    record['work_permit_expiry'], record['gross_salary'],
                    record['nationality'], record['position']
                ])

            headers = [
                'Employee ID', 'Name', 'Passport/ID', 'Work Permit Type',
                'Work Permit Expiry', 'Gross Salary', 'Nationality', 'Position'
            ]

            return export_to_csv(csv_data, filename, headers)

        elif report_type == 'bank':
            data = payroll_calc.generate_bank_file(payrolls)
            filename = f"Bank_Transfer_{year}_{month:02d}.csv"

            csv_data = []
            for record in data['records']:
                csv_data.append([
                    record['employee_id'], record['name'],
                    record['bank_account'], record['bank_name'],
                    record['amount'], record['reference']
                ])

            headers = [
                'Employee ID', 'Name', 'Bank Account', 'Bank Name', 'Amount',
                'Reference'
            ]

            return export_to_csv(csv_data, filename, headers)

        else:
            flash('Invalid report type', 'error')
            return redirect(url_for('compliance_dashboard'))

    except Exception as e:
        flash(f'Error generating {report_type.upper()} report: {str(e)}',
              'error')
        return redirect(url_for('compliance_dashboard'))


# Export routes
@app.route('/users')
@require_role(['Super Admin', 'Admin'])
def user_management():
    """User management for admins"""
    users = User.query.order_by(User.first_name).all()
    return render_template('users/list.html', users=users)


@app.route('/users/<user_id>/role', methods=['POST'])
@require_role(['Super Admin', 'Admin'])
def update_user_role(user_id):
    """Update user role"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')

    if new_role in ['Super Admin', 'Admin', 'Manager', 'User']:
        user.role = new_role
        db.session.commit()
        flash(f'User role updated to {new_role}', 'success')
    else:
        flash('Invalid role specified', 'error')

    return redirect(url_for('user_management'))


@app.route('/export/employees')
@require_role(['Super Admin', 'Admin', 'Manager'])
def export_employees():
    """Export employees to CSV"""
    employees = Employee.query.filter_by(is_active=True).all()

    csv_data = []
    for emp in employees:
        csv_data.append([
            emp.employee_id, emp.first_name, emp.last_name, emp.email,
            emp.nric, emp.position, emp.department,
            format_date(emp.hire_date), emp.employment_type,
            emp.work_permit_type,
            format_currency(emp.basic_salary)
        ])

    headers = [
        'Employee ID', 'First Name', 'Last Name', 'Email', 'NRIC', 'Position',
        'Department', 'Hire Date', 'Employment Type', 'Work Permit Type',
        'Basic Salary'
    ]

    return export_to_csv(csv_data, 'employees_export.csv', headers)


# Mobile API routes for PWA functionality
@app.route('/api/attendance/check')
@require_login
def api_attendance_check():
    """Check today's attendance status for mobile"""
    if not hasattr(current_user, 'employee_profile'):
        return jsonify({'error': 'Employee profile not found'}), 400

    today = date.today()
    attendance = Attendance.query.filter_by(
        employee_id=current_user.employee_profile.id, date=today).first()

    if attendance:
        return jsonify({
            'clocked_in':
            attendance.clock_in is not None,
            'clocked_out':
            attendance.clock_out is not None,
            'on_break':
            attendance.break_start is not None
            and attendance.break_end is None,
            'clock_in_time':
            attendance.clock_in.strftime('%H:%M')
            if attendance.clock_in else None,
            'clock_out_time':
            attendance.clock_out.strftime('%H:%M')
            if attendance.clock_out else None
        })
    else:
        return jsonify({
            'clocked_in': False,
            'clocked_out': False,
            'on_break': False
        })


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


# Template filters
@app.template_filter('currency')
def currency_filter(amount):
    return format_currency(amount)


@app.template_filter('date')
def date_filter(date_obj):
    return format_date(date_obj)
