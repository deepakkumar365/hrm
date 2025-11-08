from flask import session, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import current_user
from sqlalchemy import func, extract, and_, text
from datetime import datetime, date, time, timedelta
import calendar
import os
import time as pytime
from werkzeug.utils import secure_filename
from io import BytesIO
import logging



from app import app, db
from auth import require_login, require_role, create_default_users
from models import (Employee, Payroll, PayrollConfiguration, Attendance, Leave, Claim, Appraisal,
                    ComplianceReport, User, Role, Department, WorkingHours, WorkSchedule,
                    Company, Tenant, EmployeeBankInfo, EmployeeDocument, TenantPaymentConfig, TenantDocument, Designation)
from forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user
from singapore_payroll import SingaporePayrollCalculator
from utils import (export_to_csv, format_currency, format_date, parse_date,
                   validate_nric, generate_employee_id, check_permission,
                   mobile_optimized_pagination, get_current_month_dates, validate_phone_number)
from constants import DEFAULT_USER_PASSWORD

# Helper to validate image extension
def _allowed_image(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())

# Initialize payroll calculator
payroll_calc = SingaporePayrollCalculator()


@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Simple database connectivity check
        db.session.execute(text('SELECT 1'))
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 503

# Create default users and master data on first run
def create_default_master_data():
    """Create default master data if it doesn't exist"""
    try:
        # Create default roles if none exist
        if Role.query.count() == 0:
            roles = [
                Role(name='Software Engineer', description='Develops and maintains software applications'),
                Role(name='Senior Developer', description='Senior software development role with leadership responsibilities'),
                Role(name='Team Lead', description='Leads development teams and manages projects'),
                Role(name='HR Manager', description='Manages human resources operations'),
                Role(name='Sales Executive', description='Responsible for sales activities and client relationships'),
                Role(name='Marketing Specialist', description='Handles marketing campaigns and brand management'),
                Role(name='Accountant', description='Manages financial records and accounting operations'),
                Role(name='Operations Manager', description='Oversees daily business operations'),
            ]
            for role in roles:
                db.session.add(role)

        # Create default departments if none exist
        if Department.query.count() == 0:
            departments = [
                Department(name='Information Technology', description='Software development and IT services'),
                Department(name='Human Resources', description='Employee relations and HR operations'),
                Department(name='Sales & Marketing', description='Sales and marketing activities'),
                Department(name='Finance & Accounting', description='Financial planning and accounting'),
                Department(name='Operations', description='Business operations and logistics'),
                Department(name='Administration', description='General administration and support'),
            ]
            for dept in departments:
                db.session.add(dept)

        # Create default working hours if none exist
        if WorkingHours.query.count() == 0:
            working_hours = [
                WorkingHours(name='Full-time Standard', hours_per_day=8.0, hours_per_week=40.0,
                           description='Standard full-time working hours'),
                WorkingHours(name='Part-time (Half Day)', hours_per_day=4.0, hours_per_week=20.0,
                           description='Half day part-time schedule'),
                WorkingHours(name='Extended Hours', hours_per_day=9.0, hours_per_week=45.0,
                           description='Extended working hours with overtime'),
                WorkingHours(name='Flexible Hours', hours_per_day=8.0, hours_per_week=40.0,
                           description='Flexible working arrangement'),
            ]
            for wh in working_hours:
                db.session.add(wh)

        # Create default work schedules if none exist
        if WorkSchedule.query.count() == 0:
            from datetime import time
            schedules = [
                WorkSchedule(name='Standard Hours', start_time=time(9, 0), end_time=time(18, 0),
                           break_duration=60, description='Standard 9-to-6 schedule'),
                WorkSchedule(name='Early Shift', start_time=time(7, 0), end_time=time(16, 0),
                           break_duration=60, description='Early morning shift'),
                WorkSchedule(name='Late Shift', start_time=time(14, 0), end_time=time(23, 0),
                           break_duration=60, description='Afternoon to evening shift'),
                WorkSchedule(name='Flexible Hours', start_time=time(8, 0), end_time=time(17, 0),
                           break_duration=60, description='Flexible timing schedule'),
            ]
            for schedule in schedules:
                db.session.add(schedule)

        db.session.commit()
        return True
    except Exception as e:
        print(f"Error creating master data: {e}")
        db.session.rollback()
        return False

def initialize_default_data():
    """Initialize default users and master data - call this after ensuring DB is ready"""
    try:
        with app.app_context():
            # Check if tables exist before trying to query them
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()

            # Only proceed if the hrm_users table exists
            if 'hrm_users' not in tables:
                print("⚠️  Database tables not yet created. Skipping default data initialization.")
                print("Run 'flask db upgrade' to create tables, then restart the application.")
                return

            if create_default_users():
                print("✅ Default users created successfully!")
            if create_default_master_data():
                print("✅ Default master data created successfully!")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize default data: {e}")
        print("This is normal if the database is not yet set up or tables haven't been created.")
        print("Run 'flask db upgrade' to create tables, then restart the application.")

# Only initialize default data if we're running the app (not during imports for migrations, etc.)
if os.environ.get('FLASK_SKIP_DB_INIT') != '1':
    initialize_default_data()


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
        user_role_name = current_user.role.name if current_user.role else None
        user.role = form.role.data if user_role_name in [
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
    return redirect(url_for('login'))


def render_super_admin_dashboard():
    """Render Super Admin specific dashboard with tenant metrics"""
    from sqlalchemy import func, extract
    from datetime import datetime, timedelta
    from dateutil.relativedelta import relativedelta

    # Get tenant statistics
    total_tenants = Tenant.query.count()
    active_tenants = Tenant.query.filter_by(is_active=True).count()

    # Get company statistics
    total_companies = Company.query.count()

    # Get user statistics
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()

    # Get users by company (top 10 companies)
    company_user_counts = db.session.query(
        Company.name,
        func.count(Employee.id).label('user_count')
    ).join(Employee, Company.id == Employee.company_id)\
     .group_by(Company.name)\
     .order_by(func.count(Employee.id).desc())\
     .limit(10).all()

    company_labels = [c[0] for c in company_user_counts]
    company_counts = [c[1] for c in company_user_counts]

    # Get payroll statistics (last 6 months)
    six_months_ago = datetime.now() - relativedelta(months=6)
    payslip_stats = db.session.query(
        extract('year', Payroll.pay_period_end).label('year'),
        extract('month', Payroll.pay_period_end).label('month'),
        func.count(Payroll.id).label('count')
    ).filter(Payroll.pay_period_end >= six_months_ago)\
     .group_by('year', 'month')\
     .order_by('year', 'month').all()

    payslip_months = []
    payslip_counts = []
    for stat in payslip_stats:
        month_name = datetime(int(stat.year), int(stat.month), 1).strftime('%b %Y')
        payslip_months.append(month_name)
        payslip_counts.append(stat.count)

    # Get current month payslips
    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    payslips_this_month = Payroll.query.filter(
        Payroll.pay_period_end >= current_month_start
    ).count()

    # Calculate revenue from payment configurations
    payment_configs = TenantPaymentConfig.query.all()
    monthly_revenue = float(sum(config.monthly_charges or 0 for config in payment_configs))
    quarterly_revenue = monthly_revenue * 3
    yearly_revenue = monthly_revenue * 12

    # Mock data for collected/pending (can be enhanced with actual payment tracking)
    collected_revenue = monthly_revenue * 0.7  # 70% collected
    quarterly_collected = quarterly_revenue * 0.7  # 70% collected
    yearly_collected = yearly_revenue * 0.7  # 70% collected
    pending_payments = monthly_revenue * 0.25  # 25% pending
    overdue_payments = monthly_revenue * 0.05  # 5% overdue

    # Get recent tenants with their stats
    recent_tenants = []
    tenants = Tenant.query.order_by(Tenant.created_at.desc()).limit(5).all()
    for tenant in tenants:
        company_count = Company.query.filter_by(tenant_id=tenant.id).count()
        user_count = db.session.query(func.count(Employee.id))\
            .join(Company, Employee.company_id == Company.id)\
            .filter(Company.tenant_id == tenant.id).scalar() or 0

        payment_config = TenantPaymentConfig.query.filter_by(tenant_id=tenant.id).first()
        payment_type = payment_config.payment_type if payment_config else None

        recent_tenants.append({
            'name': tenant.name,
            'code': tenant.code,
            'is_active': tenant.is_active,
            'company_count': company_count,
            'user_count': user_count,
            'payment_type': payment_type
        })

    # Recent activities
    recent_activities = [
        {
            'icon': 'sitemap',
            'icon_class': 'primary',
            'title': f'{active_tenants} Active Tenants',
            'description': f'Out of {total_tenants} total tenants'
        },
        {
            'icon': 'building',
            'icon_class': 'success',
            'title': f'{total_companies} Companies',
            'description': 'Across all tenants'
        },
        {
            'icon': 'users',
            'icon_class': 'info',
            'title': f'{active_users} Active Users',
            'description': f'Out of {total_users} total users'
        },
        {
            'icon': 'file-invoice-dollar',
            'icon_class': 'warning',
            'title': f'{payslips_this_month} Payslips',
            'description': 'Generated this month'
        }
    ]

    stats = {
        'total_tenants': total_tenants,
        'active_tenants': active_tenants,
        'total_companies': total_companies,
        'total_users': total_users,
        'active_users': active_users,
        'company_labels': company_labels,
        'company_user_counts': company_counts,
        'payslip_months': payslip_months,
        'payslip_counts': payslip_counts,
        'payslips_this_month': payslips_this_month,
        'monthly_revenue': monthly_revenue,
        'quarterly_revenue': quarterly_revenue,
        'quarterly_collected': quarterly_collected,
        'yearly_revenue': yearly_revenue,
        'yearly_collected': yearly_collected,
        'collected_revenue': collected_revenue,
        'pending_payments': pending_payments,
        'overdue_payments': overdue_payments
    }

    return render_template('super_admin_dashboard.html',
                         stats=stats,
                         recent_tenants=recent_tenants,
                         recent_activities=recent_activities)


@app.route('/dashboard')
@require_login
def dashboard():
    """Main dashboard with HR metrics"""

    # Check if user is Super Admin
    user_role_name = current_user.role.name if current_user.role else None

    if user_role_name == 'Super Admin':
        # Render Super Admin Dashboard
        return render_super_admin_dashboard()

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

    if user_role_name in ['Admin']:
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

    elif user_role_name == 'HR Manager':
        # Team member activities
        if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
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

    default_calendar_endpoint = 'leave_calendar' if 'leave_calendar' in app.view_functions else 'leave_request'
    leave_calendar_url = url_for(default_calendar_endpoint)

    return render_template('dashboard.html',
                           stats=stats,
                           recent_activities=recent_activities,
                           moment=datetime.now,
                           leave_calendar_url=leave_calendar_url)


# Employee Management Routes
@app.route('/employees')
@require_login
def employee_list():
    """List all employees with search and pagination"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    department = request.args.get('department', '', type=str)
    sort_by = request.args.get('sort_by', 'id', type=str)
    sort_order = request.args.get('sort_order', 'desc', type=str)

    # Join with Company and Tenant to get tenant_name and company_name
    query = db.session.query(
        Employee,
        Company.name.label('company_name'),
        Tenant.name.label('tenant_name')
    ).join(
        Company, Employee.company_id == Company.id
    ).join(
        Tenant, Company.tenant_id == Tenant.id
    ).filter(Employee.is_active == True)

    if search:
        query = query.filter(
            db.or_(Employee.first_name.ilike(f'%{search}%'),
                   Employee.last_name.ilike(f'%{search}%'),
                   Employee.employee_id.ilike(f'%{search}%'),
                   Employee.email.ilike(f'%{search}%'),
                   Company.name.ilike(f'%{search}%'),
                   Tenant.name.ilike(f'%{search}%')))

    if department:
        query = query.filter(Employee.department == department)

    # Role-based filtering
    if (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user,
                                                  'employee_profile') and current_user.employee_profile:
        query = query.filter(
            Employee.organization_id == current_user.organization_id)

    # Sorting
    if sort_by == 'tenant_name':
        sort_column = Tenant.name
    elif sort_by == 'company_name':
        sort_column = Company.name
    elif sort_by == 'employee_id':
        sort_column = Employee.employee_id
    elif sort_by == 'designation':
        sort_column = Employee.designation_id
    elif sort_by == 'department':
        sort_column = Employee.department
    elif sort_by == 'id':
        sort_column = Employee.id
    else:
        sort_column = Employee.first_name

    if sort_order == 'desc':
        sort_column = sort_column.desc()

    query = query.order_by(sort_column)

    # Paginate the results
    pagination = query.paginate(page=page, per_page=20, error_out=False)

    # Extract employee objects with company and tenant names
    employees_data = []
    for item in pagination.items:
        employee = item[0]
        employee.company_name = item[1]
        employee.tenant_name = item[2]
        employees_data.append(employee)

    # Create a custom pagination object
    class CustomPagination:
        def __init__(self, items, pagination):
            self.items = items
            self.page = pagination.page
            self.pages = pagination.pages
            self.total = pagination.total
            self.has_prev = pagination.has_prev
            self.has_next = pagination.has_next
            self.prev_num = pagination.prev_num
            self.next_num = pagination.next_num

        def iter_pages(self, left_edge=2, left_current=2, right_current=3, right_edge=2):
            last = 0
            for num in range(1, self.pages + 1):
                if num <= left_edge or \
                   (num > self.page - left_current - 1 and num < self.page + right_current) or \
                   num > self.pages - right_edge:
                    if last + 1 != num:
                        yield None
                    yield num
                    last = num

    employees = CustomPagination(employees_data, pagination)

    # Get departments for filter
    departments = db.session.query(Employee.department).distinct().filter(
        Employee.department.isnot(None), Employee.is_active == True).all()
    departments = [d[0] for d in departments]

    return render_template('employees/list.html',
                           employees=employees,
                           search=search,
                           department=department,
                           departments=departments,
                           sort_by=sort_by,
                           sort_order=sort_order)


@app.route('/employees/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin','HR Manager','Tenant Admin'])
def employee_add():
    """Add new employee"""
    if request.method == 'POST':
        try:
            # Validate NRIC (optional field)
            nric = request.form.get('nric', '').upper()
            if nric and not validate_nric(nric):
                flash('Invalid NRIC format', 'error')
                # Load master data and preserve form data for re-rendering
                roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                return render_template('employees/form.html',
                                       form_data=request.form,
                                       roles=roles,
                                       user_roles=user_roles,
                                       designations=designations,
                                       departments=departments,
                                       working_hours=working_hours,
                                       work_schedules=work_schedules,
                                       managers=managers,
                                       companies=companies)

            # Check for duplicate NRIC (only if NRIC is provided)
            if nric and Employee.query.filter_by(nric=nric).first():
                flash('Employee with this NRIC already exists', 'error')
                # Load master data and preserve form data for re-rendering
                roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                # Position field removed - use designation_id instead
                managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                return render_template('employees/form.html',
                                       form_data=request.form,
                                       roles=roles,
                                       user_roles=user_roles,
                                       designations=designations,
                                       departments=departments,
                                       working_hours=working_hours,
                                       work_schedules=work_schedules,
                                       managers=managers,
                                       companies=companies)

            # Get company_id from form to retrieve country code for phone validation
            company_id = request.form.get('company_id')
            company = Company.query.get(company_id) if company_id else None
            country_code = company.tenant.country_code if company and company.tenant else None

            # Validate phone number (optional field)
            phone = request.form.get('phone', '').strip()
            if phone:
                phone_validation = validate_phone_number(phone, country_code)
                if not phone_validation['is_valid']:
                    flash(phone_validation['error_message'], 'error')
                    # Load master data and preserve form data for re-rendering
                    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                    return render_template('employees/form.html',
                                           form_data=request.form,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies)

            # Create new employee
            employee = Employee()
            employee.organization_id = current_user.organization_id

            # Set company_id from form
            if company_id:
                employee.company_id = company_id

            # Get employee_id from form (auto-generated by frontend)
            # Format: <CompanyCode><ID> (e.g., ACME001)
            employee_id_from_form = request.form.get('employee_id', '').strip()
            if employee_id_from_form:
                employee.employee_id = employee_id_from_form
            else:
                # Fallback if employee_id not provided in form
                company = Company.query.get(company_id) if company_id else None
                company_code = company.code if company else 'EMP'
                employee.employee_id = generate_employee_id(company_code)

            employee.first_name = request.form.get('first_name')
            employee.last_name = request.form.get('last_name')
            email = request.form.get('email', '').strip()
            employee.email = email if email else None
            employee.phone = phone if phone else None
            employee.nric = nric
            employee.date_of_birth = parse_date(
                request.form.get('date_of_birth'))
            employee.gender = request.form.get('gender')
            employee.nationality = request.form.get('nationality')
            employee.address = request.form.get('address')
            employee.postal_code = request.form.get('postal_code')
            employee.department = request.form.get('department')
            # Position field removed - use designation_id instead
            employee.hire_date = parse_date(request.form.get('hire_date'))
            employee.employment_type = request.form.get('employment_type')
            employee.work_permit_type = request.form.get('work_permit_type')

            work_permit_number = request.form.get('work_permit_number', '').strip()
            work_permit_expiry = request.form.get('work_permit_expiry', '').strip()
            permit_type = employee.work_permit_type

            types_without_permit_fields = ['Nil', 'Citizen', 'PR']
            if permit_type not in types_without_permit_fields:
                if not work_permit_number:
                    flash('Work Permit Number is required for this permit type', 'error')
                    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                    return render_template('employees/form.html',
                                           form_data=request.form,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies)
                if not work_permit_expiry:
                    flash('Work Permit Expiry Date is required for this permit type', 'error')
                    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                    return render_template('employees/form.html',
                                           form_data=request.form,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies)

            if work_permit_number:
                employee.work_permit_number = work_permit_number

            if work_permit_expiry:
                employee.work_permit_expiry = parse_date(work_permit_expiry)

            # Handle certifications and pass renewals
            hazmat_expiry = request.form.get('hazmat_expiry')
            if hazmat_expiry:
                employee.hazmat_expiry = parse_date(hazmat_expiry)

            airport_pass_expiry = request.form.get('airport_pass_expiry')
            if airport_pass_expiry:
                employee.airport_pass_expiry = parse_date(airport_pass_expiry)

            psa_pass_number = request.form.get('psa_pass_number')
            if psa_pass_number:
                employee.psa_pass_number = psa_pass_number

            psa_pass_expiry = request.form.get('psa_pass_expiry')
            if psa_pass_expiry:
                employee.psa_pass_expiry = parse_date(psa_pass_expiry)

            basic_salary = request.form.get('basic_salary', '').strip()
            if basic_salary:
                employee.basic_salary = float(basic_salary)
            else:
                employee.basic_salary = 0.0
            
            allowances = request.form.get('allowances', '').strip()
            if allowances:
                employee.allowances = float(allowances)
            else:
                employee.allowances = 0.0

            hourly_rate = request.form.get('hourly_rate')
            if hourly_rate:
                employee.hourly_rate = float(hourly_rate)

            cpf_account = request.form.get('cpf_account', '').strip()
            if cpf_account:
                employee.cpf_account = cpf_account
            
            bank_name = request.form.get('bank_name', '').strip()
            if bank_name:
                employee.bank_name = bank_name
            
            bank_account = request.form.get('bank_account', '').strip()
            if bank_account:
                employee.bank_account = bank_account
            
            account_holder_name = request.form.get('account_holder_name', '').strip()
            if account_holder_name:
                employee.account_holder_name = account_holder_name
            
            swift_code = request.form.get('swift_code', '').strip()
            if swift_code:
                employee.swift_code = swift_code
            
            ifsc_code = request.form.get('ifsc_code', '').strip()
            if ifsc_code:
                employee.ifsc_code = ifsc_code

            # Handle master data relationships
            designation_id = request.form.get('designation_id')
            if designation_id:
                employee.designation_id = int(designation_id)

            working_hours_id = request.form.get('working_hours_id')
            if working_hours_id:
                employee.working_hours_id = int(working_hours_id)

            work_schedule_id = request.form.get('work_schedule_id')
            if work_schedule_id:
                employee.work_schedule_id = int(work_schedule_id)

            manager_id = request.form.get('manager_id')
            if manager_id:
                employee.manager_id = int(manager_id)

            # Set manager flag
            employee.is_manager = bool(request.form.get('is_manager'))

            # Handle profile image upload (optional)
            file = request.files.get('profile_image')
            if file and file.filename.strip():
                if not _allowed_image(file.filename):
                    flash('Invalid image type. Allowed: ' + ', '.join(sorted(app.config.get('ALLOWED_IMAGE_EXTENSIONS', []))), 'error')
                    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                    return render_template('employees/form.html',
                                           form_data=request.form,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies)

                # Save image with unique name based on employee_id and timestamp
                original = secure_filename(file.filename)
                ext = original.rsplit('.', 1)[1].lower()
                unique_name = f"{employee.employee_id}_{int(pytime.time())}.{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                file.save(save_path)
                employee.profile_image_path = f"uploads/employees/{unique_name}"

            db.session.add(employee)
            db.session.commit()

            # Create user account for the new employee
            try:
                # Generate username from employee_id (case sensitive)
                username = employee.employee_id

                # Check if username already exists (should be unique)
                if User.query.filter_by(username=username).first():
                    raise ValueError(f"User account with username '{username}' already exists")

                # Create user account
                user = User()
                user.username = username
                user.email = employee.email
                user.first_name = employee.first_name
                user.last_name = employee.last_name
                user.organization_id = current_user.organization_id

                # Get role from form selection
                user_role_id = request.form.get('user_role_id')
                if user_role_id:
                    user.role_id = int(user_role_id)
                else:
                    # Fallback: Get default role for new employees (try to find 'User' or 'Employee' role)
                    default_role = Role.query.filter(
                        (Role.name == 'User') | (Role.name == 'Employee')
                    ).filter_by(is_active=True).first()

                    if not default_role:
                        # If no default role found, get any active role
                        default_role = Role.query.filter_by(is_active=True).first()

                    if default_role:
                        user.role_id = default_role.id
                    else:
                        raise ValueError("No active roles found in the system. Please create roles first.")

                # Set default password for all new users
                user.set_password(DEFAULT_USER_PASSWORD)
                user.must_reset_password = True  # Force password change on first login

                db.session.add(user)
                db.session.commit()

                # Link employee to user account
                employee.user_id = user.id
                db.session.commit()

                flash(f'Employee added successfully. Login credentials created - Username: {username}, Password: {DEFAULT_USER_PASSWORD}', 'success')

            except Exception as user_error:
                # Employee was created but user creation failed
                flash(f'Employee added successfully, but user account creation failed: {str(user_error)}. Please create manually.', 'warning')

            return redirect(url_for('employee_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')
            # Load master data and preserve form data for re-rendering
            roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
            user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
            designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
            departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
            working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
            work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
            managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
            companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
            return render_template('employees/form.html',
                                   form_data=request.form,
                                   roles=roles,
                                   user_roles=user_roles,
                                   designations=designations,
                                   departments=departments,
                                   working_hours=working_hours,
                                   work_schedules=work_schedules,
                                   managers=managers,
                                   companies=companies)

    # Get managers for dropdown
    # Load master data for dropdowns
    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
    user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()

    return render_template('employees/form.html',
                           managers=managers,
                           roles=roles,
                           user_roles=user_roles,
                           designations=designations,
                           departments=departments,
                           working_hours=working_hours,
                           work_schedules=work_schedules,
                           companies=companies)


@app.route('/employees/<int:employee_id>')
@require_login
def employee_view(employee_id):
    """View employee details"""
    employee = Employee.query.get_or_404(employee_id)

    # Check permission
    if (current_user.role.name if current_user.role else None) == 'Employee':
        if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile
                and current_user.employee_profile.id == employee_id):
            flash('You do not have permission to view this employee.', 'error')
            return redirect(url_for('dashboard'))
    elif (current_user.role.name if current_user.role else None) == 'HR Manager':
        if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile and
                (current_user.employee_profile.id == employee_id
                 or employee.manager_id == current_user.employee_profile.id)):
            flash('You do not have permission to view this employee.', 'error')
            return redirect(url_for('dashboard'))

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


@app.route('/profile')
@require_login
def profile():
    """User's own profile page"""
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        flash('Profile not found. Please contact your administrator.', 'error')
        return redirect(url_for('dashboard'))

    employee = current_user.employee_profile

    # Get attendance stats
    today = date.today()
    first_day = today.replace(day=1)
    last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])

    total_days = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.date.between(first_day, last_day)
    ).count()

    present_days = Attendance.query.filter(
        Attendance.employee_id == employee.id,
        Attendance.date.between(first_day, last_day),
        Attendance.status == 'Present'
    ).count()

    attendance_rate = round((present_days / total_days * 100) if total_days > 0 else 0)

    # Get pending claims
    pending_claims = Claim.query.filter_by(
        employee_id=employee.id,
        status='Pending'
    ).count()

    # Get leave balance
    leave_balance = employee.leave_balance if hasattr(employee, 'leave_balance') else 0

    # Compile stats
    stats = {
        'attendance_rate': attendance_rate,
        'leave_balance': leave_balance,
        'pending_claims': pending_claims,
        'completed_tasks': 0  # Placeholder for future task tracking feature
    }

    # Get recent activities
    activities = []

    # Add recent attendance
    attendance_records = Attendance.query.filter_by(
        employee_id=employee.id
    ).order_by(Attendance.date.desc()).limit(5).all()

    for record in attendance_records:
        activities.append({
            'icon': 'fa-clock',
            'color': 'success' if record.status == 'Present' else 'warning',
            'message': f"Marked {record.status} at {record.clock_in.strftime('%I:%M %p') if record.clock_in else 'N/A'}",
            'time': record.date.strftime('%d %b %Y')
        })


    # Working Hours routes moved to `routes_masters.py` to avoid duplicate endpoint
    # registrations. See `routes_masters.py` for the canonical implementations
    # of working_hours_list, working_hours_add, working_hours_edit and
    # working_hours_delete.

    return redirect(url_for('profile'))


@app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin','HR Manager'])
def employee_edit(employee_id):
    """Edit employee details"""
    employee = Employee.query.get_or_404(employee_id)

    if request.method == 'POST':
        try:
            # Update company_id from form
            company_id = request.form.get('company_id')
            if company_id:
                employee.company_id = company_id
            else:
                employee.company_id = None

            # Get country code from company's tenant for phone validation
            company = Company.query.get(company_id) if company_id else None
            country_code = company.tenant.country_code if company and company.tenant else None

            # Validate phone number (optional field)
            phone = request.form.get('phone', '').strip()
            if phone:
                phone_validation = validate_phone_number(phone, country_code)
                if not phone_validation['is_valid']:
                    flash(phone_validation['error_message'], 'error')
                    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    user_roles = Role.query.filter(Role.name.in_(['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User'])).filter_by(is_active=True).order_by(Role.name).all()
                    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                    return render_template('employees/form.html',
                                           form_data=request.form,
                                           employee=employee,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies)

            employee.first_name = request.form.get('first_name')
            employee.last_name = request.form.get('last_name')
            email = request.form.get('email', '').strip()
            employee.email = email if email else None
            employee.phone = phone if phone else None
            
            # Validate NRIC (optional field)
            nric = request.form.get('nric', '').upper()
            if nric and not validate_nric(nric):
                flash('Invalid NRIC format', 'error')
                roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                user_roles = Role.query.filter(Role.name.in_(['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User'])).filter_by(is_active=True).order_by(Role.name).all()
                designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                return render_template('employees/form.html',
                                       form_data=request.form,
                                       employee=employee,
                                       roles=roles,
                                       user_roles=user_roles,
                                       designations=designations,
                                       departments=departments,
                                       working_hours=working_hours,
                                       work_schedules=work_schedules,
                                       managers=managers,
                                       companies=companies)
            
            employee.nric = nric if nric else None
            employee.address = request.form.get('address')
            employee.postal_code = request.form.get('postal_code')
            employee.department = request.form.get('department')
            # Position field removed - use designation_id instead
            employee.employment_type = request.form.get('employment_type')
            employee.work_permit_type = request.form.get('work_permit_type')

            work_permit_number = request.form.get('work_permit_number', '').strip()
            work_permit_expiry = request.form.get('work_permit_expiry', '').strip()
            permit_type = employee.work_permit_type

            types_without_permit_fields = ['Nil', 'Citizen', 'PR']
            if permit_type not in types_without_permit_fields:
                if not work_permit_number:
                    flash('Work Permit Number is required for this permit type', 'error')
                    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    user_roles = Role.query.filter(Role.name.in_(['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User'])).filter_by(is_active=True).order_by(Role.name).all()
                    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                    return render_template('employees/form.html',
                                           form_data=request.form,
                                           employee=employee,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies)
                if not work_permit_expiry:
                    flash('Work Permit Expiry Date is required for this permit type', 'error')
                    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    user_roles = Role.query.filter(Role.name.in_(['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User'])).filter_by(is_active=True).order_by(Role.name).all()
                    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                    return render_template('employees/form.html',
                                           form_data=request.form,
                                           employee=employee,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies)

            if work_permit_number:
                employee.work_permit_number = work_permit_number
            else:
                employee.work_permit_number = None

            # Handle additional personal fields
            employee.gender = request.form.get('gender')
            employee.nationality = request.form.get('nationality')

            # Handle date fields
            hire_date = request.form.get('hire_date')
            if hire_date:
                employee.hire_date = parse_date(hire_date)

            date_of_birth = request.form.get('date_of_birth')
            if date_of_birth:
                employee.date_of_birth = parse_date(date_of_birth)

            if work_permit_expiry:
                employee.work_permit_expiry = parse_date(work_permit_expiry)
            else:
                employee.work_permit_expiry = None

            # Handle certifications and pass renewals
            hazmat_expiry = request.form.get('hazmat_expiry')
            if hazmat_expiry:
                employee.hazmat_expiry = parse_date(hazmat_expiry)
            else:
                employee.hazmat_expiry = None

            airport_pass_expiry = request.form.get('airport_pass_expiry')
            if airport_pass_expiry:
                employee.airport_pass_expiry = parse_date(airport_pass_expiry)
            else:
                employee.airport_pass_expiry = None

            psa_pass_number = request.form.get('psa_pass_number')
            if psa_pass_number:
                employee.psa_pass_number = psa_pass_number
            else:
                employee.psa_pass_number = None

            psa_pass_expiry = request.form.get('psa_pass_expiry')
            if psa_pass_expiry:
                employee.psa_pass_expiry = parse_date(psa_pass_expiry)
            else:
                employee.psa_pass_expiry = None

            employee.basic_salary = float(request.form.get('basic_salary', 0))
            employee.allowances = float(request.form.get('allowances', 0))

            hourly_rate = request.form.get('hourly_rate')
            if hourly_rate:
                employee.hourly_rate = float(hourly_rate)

            employee.cpf_account = request.form.get('cpf_account')
            employee.bank_name = request.form.get('bank_name')
            employee.bank_account = request.form.get('bank_account')
            employee.account_holder_name = request.form.get('account_holder_name')
            employee.swift_code = request.form.get('swift_code')
            employee.ifsc_code = request.form.get('ifsc_code')

            # Validate mandatory banking field
            if not (employee.account_holder_name and employee.account_holder_name.strip()):
                flash('Account Holder Name is required', 'error')
                roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                user_roles = Role.query.filter(Role.name.in_(['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User'])).filter_by(is_active=True).order_by(Role.name).all()
                designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                # Position field removed - use designation_id instead
                managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                return render_template('employees/form.html',
                                       form_data=request.form,
                                       roles=roles,
                                       user_roles=user_roles,
                                       designations=designations,
                                       departments=departments,
                                       working_hours=working_hours,
                                       work_schedules=work_schedules,
                                       managers=managers,
                                       companies=companies)

            # Optional profile image replace on edit
            file = request.files.get('profile_image')
            if file and file.filename.strip():
                if not _allowed_image(file.filename):
                    flash('Invalid image type. Allowed: ' + ', '.join(sorted(app.config.get('ALLOWED_IMAGE_EXTENSIONS', []))), 'error')
                    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
                    user_roles = Role.query.filter(Role.name.in_(['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User'])).filter_by(is_active=True).order_by(Role.name).all()
                    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
                    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
                    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
                    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
                    # Position field removed - use designation_id instead
                    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
                    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
                    return render_template('employees/form.html',
                                           employee=employee,
                                           form_data=request.form,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies)
                # Save new image
                original = secure_filename(file.filename)
                ext = original.rsplit('.', 1)[1].lower()
                unique_name = f"{employee.employee_id}_{int(pytime.time())}.{ext}"
                save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
                file.save(save_path)
                # Optionally remove old file
                try:
                    if employee.profile_image_path:
                        old_abs = os.path.join(app.root_path, 'static', employee.profile_image_path)
                        if os.path.isfile(old_abs):
                            os.remove(old_abs)
                except Exception:
                    pass
                employee.profile_image_path = f"uploads/employees/{unique_name}"

            # Handle master data relationships
            designation_id = request.form.get('designation_id')
            if designation_id:
                employee.designation_id = int(designation_id)
            else:
                employee.designation_id = None

            working_hours_id = request.form.get('working_hours_id')
            if working_hours_id:
                employee.working_hours_id = int(working_hours_id)
            else:
                employee.working_hours_id = None

            work_schedule_id = request.form.get('work_schedule_id')
            if work_schedule_id:
                employee.work_schedule_id = int(work_schedule_id)
            else:
                employee.work_schedule_id = None

            manager_id = request.form.get('manager_id')
            if manager_id:
                employee.manager_id = int(manager_id)
            else:
                employee.manager_id = None

            # Set manager flag
            employee.is_manager = bool(request.form.get('is_manager'))

            # Update user role if changed
            user_role_id = request.form.get('user_role_id')
            if user_role_id and employee.user:
                try:
                    new_role_id = int(user_role_id)
                    # Verify the role exists and is a valid system role
                    new_role = Role.query.filter_by(id=new_role_id, is_active=True).first()
                    if new_role and new_role.name in ['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User']:
                        employee.user.role_id = new_role_id
                except (ValueError, TypeError):
                    pass  # Invalid role_id, skip update

            db.session.commit()
            flash('Employee updated successfully', 'success')
            return redirect(url_for('employee_view', employee_id=employee_id))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'error')
            # Load master data and preserve form data for re-rendering
            roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
            user_roles = Role.query.filter(Role.name.in_(['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User'])).filter_by(is_active=True).order_by(Role.name).all()
            designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
            departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
            working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
            work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
            managers = Employee.query.filter_by(is_active=True, is_manager=True).filter(Employee.id != employee_id).all()
            companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()
            return render_template('employees/form.html',
                                   employee=employee,
                                   form_data=request.form,
                                   managers=managers,
                                   roles=roles,
                                   user_roles=user_roles,
                                   designations=designations,
                                   departments=departments,
                                   working_hours=working_hours,
                                   work_schedules=work_schedules,
                                   companies=companies)

    # Load master data for dropdowns
    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
    user_roles = Role.query.filter(Role.name.in_(['Super Admin', 'Admin', 'HR Manager', 'Manager', 'User'])).filter_by(is_active=True).order_by(Role.name).all()
    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
    managers = Employee.query.filter_by(is_active=True, is_manager=True).filter(Employee.id != employee_id).all()
    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()

    return render_template('employees/form.html',
                           employee=employee,
                           managers=managers,
                           roles=roles,
                           user_roles=user_roles,
                           designations=designations,
                           departments=departments,
                           working_hours=working_hours,
                           work_schedules=work_schedules,
                           companies=companies)


# Payroll Management Routes
@app.route('/payroll')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
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
    if (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user,
                                                  'employee_profile') and current_user.employee_profile:
        # Manager: Their own payroll + their team's payroll
        manager_id = current_user.employee_profile.id
        query = query.filter(
            db.or_(
                Payroll.employee_id == manager_id,  # Manager's own payroll
                Employee.manager_id == manager_id  # Team's payroll
            ))
    elif (current_user.role.name if current_user.role else None) in ['Admin', 'Super Admin']:
        # Admin and Super Admin: Can see all payroll records
        pass  # No filtering - they can see all

    payrolls = query.order_by(Payroll.pay_period_end.desc()).paginate(
        page=page, per_page=20, error_out=False)

    return render_template('payroll/list.html',
                           payrolls=payrolls,
                           month=month,
                           year=year,
                           calendar=calendar)


@app.route('/payroll/generate', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def payroll_generate():
    """Generate payroll for selected period"""
    if request.method == 'POST':
        try:
            month = int(request.form.get('month'))
            year = int(request.form.get('year'))
            selected_employees = request.form.getlist('employees')

            # Calculate pay period
            from calendar import monthrange
            pay_period_start = date(year, month, 1)
            last_day = monthrange(year, month)[1]
            pay_period_end = date(year, month, last_day)

            generated_count = 0
            skipped_count = 0

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
                    skipped_count += 1
                    continue

                # Get payroll config
                config = employee.payroll_config

                # Calculate allowances
                total_allowances = 0
                if config:
                    total_allowances = float(config.get_total_allowances())

                # Get attendance data for overtime calculation
                attendance_records = Attendance.query.filter_by(
                    employee_id=employee.id).filter(
                        Attendance.date.between(pay_period_start,
                                                pay_period_end)).all()

                total_overtime = sum(float(record.overtime_hours or 0)
                                     for record in attendance_records)

                # Calculate OT pay
                ot_rate = float(config.ot_rate_per_hour) if config and config.ot_rate_per_hour else float(employee.hourly_rate or 0)
                overtime_pay = total_overtime * ot_rate

                # Calculate gross pay
                basic_pay = float(employee.basic_salary)
                gross_pay = basic_pay + total_allowances + overtime_pay

                # Calculate CPF (simplified)
                employee_cpf = gross_pay * (float(employee.employee_cpf_rate) / 100)
                employer_cpf = gross_pay * (float(employee.employer_cpf_rate) / 100)

                # Calculate net pay
                net_pay = gross_pay - employee_cpf

                # Create payroll record
                payroll = Payroll()
                payroll.employee_id = employee.id
                payroll.pay_period_start = pay_period_start
                payroll.pay_period_end = pay_period_end
                payroll.basic_pay = basic_pay
                payroll.overtime_pay = overtime_pay
                payroll.allowances = total_allowances
                payroll.bonuses = 0
                payroll.gross_pay = gross_pay
                payroll.employee_cpf = employee_cpf
                payroll.employer_cpf = employer_cpf
                payroll.income_tax = 0
                payroll.other_deductions = 0
                payroll.net_pay = net_pay
                payroll.overtime_hours = total_overtime
                payroll.days_worked = len(attendance_records)
                payroll.generated_by = current_user.id
                payroll.status = 'Draft'

                db.session.add(payroll)
                generated_count += 1

            db.session.commit()

            message = f'Generated payroll for {generated_count} employee(s)'
            if skipped_count > 0:
                message += f'. Skipped {skipped_count} employee(s) with existing payroll.'

            flash(message, 'success')
            return redirect(url_for('payroll_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error generating payroll: {str(e)}', 'error')

    # GET request - show form
    from datetime import datetime as dt
    current_month = dt.now().month
    current_year = dt.now().year

    # Fetch active companies for dropdown
    companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()

    return render_template('payroll/generate.html',
                         current_month=current_month,
                         current_year=current_year,
                         companies=companies)


@app.route('/payroll/config')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def payroll_config():
    """Payroll configuration page - manage employee salary allowances and OT rates"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)

    # Query active employees
    query = Employee.query.filter_by(is_active=True)

    if search:
        query = query.filter(
            db.or_(
                Employee.first_name.ilike(f'%{search}%'),
                Employee.last_name.ilike(f'%{search}%'),
                Employee.employee_id.ilike(f'%{search}%')
            )
        )

    employees = query.order_by(Employee.employee_id).paginate(
        page=page, per_page=20, error_out=False
    )

    # Get or create payroll configurations for each employee
    for employee in employees.items:
        if not employee.payroll_config:
            config = PayrollConfiguration(employee_id=employee.id)
            db.session.add(config)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating payroll configs: {e}")

    return render_template('payroll/config.html', employees=employees, search=search)


@app.route('/payroll/config/update', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def payroll_config_update():
    """Update payroll configuration for an employee (AJAX endpoint)"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')

        employee = Employee.query.get_or_404(employee_id)
        config = employee.payroll_config

        if not config:
            config = PayrollConfiguration(employee_id=employee_id)
            db.session.add(config)

        # Update base salary (on Employee model)
        if 'basic_salary' in data:
            employee.basic_salary = float(data['basic_salary'])

        # Update allowances
        if 'allowance_1_amount' in data:
            config.allowance_1_amount = float(data['allowance_1_amount']) if data['allowance_1_amount'] else 0
        if 'allowance_2_amount' in data:
            config.allowance_2_amount = float(data['allowance_2_amount']) if data['allowance_2_amount'] else 0
        if 'allowance_3_amount' in data:
            config.allowance_3_amount = float(data['allowance_3_amount']) if data['allowance_3_amount'] else 0
        if 'allowance_4_amount' in data:
            config.allowance_4_amount = float(data['allowance_4_amount']) if data['allowance_4_amount'] else 0

        # Update OT rate
        if 'ot_rate_per_hour' in data:
            config.ot_rate_per_hour = float(data['ot_rate_per_hour']) if data['ot_rate_per_hour'] else None

        config.updated_by = current_user.id
        config.updated_at = datetime.now()

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Payroll configuration updated successfully',
            'total_allowances': float(config.get_total_allowances())
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Error updating configuration: {str(e)}'
        }), 400


@app.route('/api/payroll/preview')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def payroll_preview_api():
    """API endpoint to preview payroll data for selected month"""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)

        if not month or not year:
            return jsonify({
                'success': False,
                'message': 'Month and year are required'
            }), 400

        # Calculate pay period
        from calendar import monthrange
        pay_period_start = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        pay_period_end = date(year, month, last_day)

        # Get all active employees
        employees = Employee.query.filter_by(is_active=True).all()

        employee_data = []
        for emp in employees:
            # Get payroll config
            config = emp.payroll_config

            # Calculate allowances
            allowance_1 = float(config.allowance_1_amount) if config else 0
            allowance_2 = float(config.allowance_2_amount) if config else 0
            allowance_3 = float(config.allowance_3_amount) if config else 0
            allowance_4 = float(config.allowance_4_amount) if config else 0
            total_allowances = allowance_1 + allowance_2 + allowance_3 + allowance_4

            # Get attendance data for the month
            attendance_records = Attendance.query.filter_by(
                employee_id=emp.id
            ).filter(
                Attendance.date.between(pay_period_start, pay_period_end)
            ).all()

            attendance_days = len(attendance_records)
            total_ot_hours = sum(float(record.overtime_hours or 0) for record in attendance_records)

            # Calculate OT amount
            ot_rate = float(config.ot_rate_per_hour) if config and config.ot_rate_per_hour else float(emp.hourly_rate or 0)
            ot_amount = total_ot_hours * ot_rate

            # Calculate gross salary
            basic_salary = float(emp.basic_salary)
            gross_salary = basic_salary + total_allowances + ot_amount

            # Calculate CPF deductions (simplified - using employee rate)
            cpf_deduction = gross_salary * (float(emp.employee_cpf_rate) / 100)

            # Calculate net salary
            total_deductions = cpf_deduction
            net_salary = gross_salary - total_deductions

            employee_data.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'name': f"{emp.first_name} {emp.last_name}",
                'basic_salary': basic_salary,
                'allowance_1': allowance_1,
                'allowance_2': allowance_2,
                'allowance_3': allowance_3,
                'allowance_4': allowance_4,
                'total_allowances': total_allowances,
                'ot_hours': total_ot_hours,
                'ot_rate': ot_rate,
                'ot_amount': ot_amount,
                'attendance_days': attendance_days,
                'gross_salary': gross_salary,
                'cpf_deduction': cpf_deduction,
                'total_deductions': total_deductions,
                'net_salary': net_salary
            })

        return jsonify({
            'success': True,
            'employees': employee_data,
            'month': month,
            'year': year
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error loading payroll preview: {str(e)}'
        }), 500


@app.route('/payroll/<int:payroll_id>/payslip')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
@require_login
def payroll_payslip(payroll_id):
    """View/download payslip"""
    payroll = Payroll.query.get_or_404(payroll_id)

    # Check permission
    user_role = current_user.role.name if current_user.role else None

    if user_role == 'Employee':
        # Employees can only view their own payslips
        if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile
                and current_user.employee_profile.id == payroll.employee_id):
            flash('You do not have permission to view this payslip.', 'error')
            return redirect(url_for('dashboard'))
    elif user_role in ['HR Manager', 'Admin', 'Super Admin']:
        # HR Manager, Admin and Super Admin: Can view all payslips
        pass  # No restriction - they can see all
    else:
        # Any other role cannot view payslips
        flash('You do not have permission to view this payslip.', 'error')
        return redirect(url_for('dashboard'))

    # Prepare data for template
    employee = payroll.employee
    company = employee.organization

    # Calculate pay date (end of pay period)
    pay_date = payroll.pay_period_end.strftime('%d %b %Y')

    # Prepare earnings data
    earnings = {
        'regular_pay_rate': f"{float(employee.basic_salary):,.2f}",
        'regular_pay_amount': f"{float(payroll.basic_pay):,.2f}",
        'overtime_pay_rate': f"{float(employee.hourly_rate or 0):,.2f}" if employee.hourly_rate else "0.00",
        'overtime_hours': f"{float(payroll.overtime_hours):,.2f}",
        'overtime_amount': f"{float(payroll.overtime_pay):,.2f}",
        'holiday_pay': "0.00",  # Not in current model
        'vacation_pay': "0.00",  # Not in current model
        'others': f"{float(payroll.allowances + payroll.bonuses):,.2f}"
    }

    # Prepare deductions data
    deductions = {
        'income_tax': f"{float(payroll.income_tax):,.2f}",
        'medical': "0.00",  # Not in current model
        'life_insurance': "0.00",  # Not in current model
        'provident_fund': f"{float(payroll.employee_cpf):,.2f}",
        'others': f"{float(payroll.other_deductions):,.2f}"
    }

    # Prepare employee data
    employee_data = {
        'name': f"{employee.first_name} {employee.last_name}",
        'nric': employee.nric,
        'nationality': employee.nationality or 'N/A',
        'designation': employee.designation.name if employee.designation else 'N/A'
    }

    # Prepare company data
    company_data = {
        'name': company.name,
        'address': company.address or 'N/A',
        'uen': company.uen or 'N/A'
    }

    # Prepare payroll summary
    payroll_data = {
        'pay_date': pay_date,
        'total_earnings': f"{float(payroll.gross_pay):,.2f}",
        'total_deductions': f"{float(payroll.employee_cpf + payroll.income_tax + payroll.other_deductions):,.2f}",
        'net_pay': f"{float(payroll.net_pay):,.2f}"
    }

    return render_template('payroll/payslip.html',
                         payroll=payroll_data,
                         employee=employee_data,
                         company=company_data,
                         earnings=earnings,
                         deductions=deductions)


@app.route('/payroll/<int:payroll_id>/download-pdf')
@require_role(['Super Admin', 'Admin', 'HR Manager', 'Employee'])
@require_login
def payroll_download_pdf(payroll_id):
    """Download payslip as PDF (or view as printable HTML)"""

    payroll = Payroll.query.get_or_404(payroll_id)

    # Check permission
    user_role = current_user.role.name if current_user.role else None

    if user_role == 'Employee':
        # Employees can only download their own payslips
        if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile
                and current_user.employee_profile.id == payroll.employee_id):
            return jsonify({'error': 'Permission denied'}), 403
    elif user_role in ['HR Manager', 'Admin', 'Super Admin']:
        # HR Manager, Admin and Super Admin: Can download all payslips
        pass
    else:
        return jsonify({'error': 'Permission denied'}), 403

    try:
        # Prepare data for template
        employee = payroll.employee
        company = employee.organization

        # Calculate pay date (end of pay period)
        pay_date = payroll.pay_period_end.strftime('%d %b %Y')

        # Prepare employee data
        employee_data = {
            'name': f"{employee.first_name} {employee.last_name}",
            'employee_id': employee.employee_id,
            'designation': employee.designation.name if employee.designation else 'N/A',
            'department': employee.department.name if employee.department else 'N/A',
            'nric': employee.nric or 'N/A'
        }

        # Prepare earnings data
        earnings = {
            'regular_pay_rate': f"{float(employee.basic_salary):,.2f}",
            'regular_pay_amount': f"{float(payroll.basic_pay):,.2f}",
            'overtime_pay_rate': f"{float(employee.hourly_rate or 0):,.2f}" if employee.hourly_rate else "0.00",
            'overtime_hours': f"{float(payroll.overtime_hours):,.2f}",
            'overtime_amount': f"{float(payroll.overtime_pay):,.2f}",
            'holiday_pay': "0.00",
            'vacation_pay': "0.00",
            'others': f"{float(payroll.allowances + payroll.bonuses):,.2f}"
        }

        # Prepare deductions data
        deductions = {
            'income_tax': f"{float(payroll.income_tax):,.2f}",
            'medical': "0.00",
            'life_insurance': "0.00",
            'provident_fund': f"{float(payroll.employee_cpf):,.2f}",
            'others': f"{float(payroll.other_deductions):,.2f}"
        }

        # Prepare company data
        company_data = {
            'name': company.name,
            'address': company.address or 'N/A',
            'uen': company.uen or 'N/A'
        }

        # Prepare payroll summary
        payroll_data = {
            'pay_date': pay_date,
            'total_earnings': f"{float(payroll.gross_pay):,.2f}",
            'total_deductions': f"{float(payroll.employee_cpf + payroll.income_tax + payroll.other_deductions):,.2f}",
            'net_pay': f"{float(payroll.net_pay):,.2f}"
        }

        # Render HTML
        html_string = render_template('payroll/payslip.html',
                                     payroll=payroll_data,
                                     employee=employee_data,
                                     company=company_data,
                                     earnings=earnings,
                                     deductions=deductions,
                                     is_printable=True)

        # Return printable HTML view
        # User can print to PDF using Ctrl+P or browser print menu
        return render_template('payroll/payslip_print.html',
                             payroll=payroll_data,
                             employee=employee_data,
                             company=company_data,
                             earnings=earnings,
                             deductions=deductions,
                             can_print=True)

    except Exception as e:
        logging.error(f"Payroll PDF download failed: {str(e)}")
        return jsonify({'error': f'Download failed: {str(e)}'}), 500


@app.route('/payroll/<int:payroll_id>/approve', methods=['POST'])
@require_role(['Super Admin', 'Admin'])
def payroll_approve(payroll_id):
    """Approve payroll record"""
    payroll = Payroll.query.get_or_404(payroll_id)

    try:
        if payroll.status == 'Draft':
            payroll.status = 'Approved'
            db.session.commit()
            return jsonify({'success': True, 'message': 'Payroll approved successfully'}), 200
        else:
            return jsonify({'success': False, 'message': f'Payroll is already {payroll.status}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


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
    if (current_user.role.name if current_user.role else None) in ['User', 'Employee'] and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        # Employee: Only their own attendance
        employee_id = current_user.employee_profile.id
        query = query.filter(Attendance.employee_id == employee_id)
    elif (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        # Manager: Their own attendance + their team's attendance
        manager_id = current_user.employee_profile.id
        query = query.filter(
            db.or_(
                Attendance.employee_id == manager_id,  # Manager's own attendance
                Employee.manager_id == manager_id      # Team's attendance
            )
        )
    elif (current_user.role.name if current_user.role else None) == 'Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        # Admin: Only their own attendance (as per requirement)
        admin_id = current_user.employee_profile.id
        query = query.filter(Attendance.employee_id == admin_id)
    elif (current_user.role.name if current_user.role else None) == 'Super Admin':
        # Super Admin: Can see all attendance records
        pass

    attendance_records = query.order_by(Attendance.date.desc()).paginate(
        page=page, per_page=20, error_out=False)

    # Get employees for filter dropdown based on role
    employees = []
    if (current_user.role.name if current_user.role else None) == 'Super Admin':
        # Super Admin can filter by all employees
        employees = Employee.query.filter_by(is_active=True).order_by(
            Employee.first_name).all()
    elif (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        # Manager can filter by themselves and their team
        manager_id = current_user.employee_profile.id
        employees = Employee.query.filter(
            db.or_(
                Employee.id == manager_id,
                Employee.manager_id == manager_id
            )
        ).filter_by(is_active=True).order_by(Employee.first_name).all()

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
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def attendance_correct(attendance_id):
    """Correct incomplete attendance records (Manager only)"""
    attendance = Attendance.query.get_or_404(attendance_id)

    # Check if manager can access this employee's record
    if (current_user.role.name if current_user.role else None) == 'HR Manager':
        if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile) or \
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
                    clock_out_dt = datetime.combine(attendance.date, attendance.clock_out)
                    total_seconds = (clock_out_dt - clock_in_dt).total_seconds()

                    # Subtract break time if applicable
                    if attendance.break_start and attendance.break_end:
                        break_start_dt = datetime.combine(
                            attendance.date, attendance.break_start)
                        break_end_dt = datetime.combine(
                            attendance.date, attendance.break_end)
                        break_seconds = (break_end_dt - break_start_dt).total_seconds()
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
            corrector_name = current_user.full_name  # Use property that gets name from employee profile
            if attendance.notes:
                attendance.notes += f"\nCorrected by {corrector_name}: {correction_note}"
            else:
                attendance.notes = f"Corrected by {corrector_name}: {correction_note}"

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
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def attendance_incomplete():
    """View incomplete attendance records that need correction"""
    # Find incomplete attendance records from the last 7 days
    week_ago = date.today() - timedelta(days=7)

    query = Attendance.query.filter(
        Attendance.date >= week_ago,
        Attendance.clock_out.is_(None)).join(Employee)

    # Role-based filtering
    if (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user,
                                                  'employee_profile') and current_user.employee_profile:
        query = query.filter(
            Employee.organization_id == current_user.organization_id)

    incomplete_records = query.order_by(Attendance.date.desc()).all()

    return render_template('attendance/incomplete.html',
                           incomplete_records=incomplete_records)


@app.route('/attendance/bulk', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def attendance_bulk_manage():
    """Bulk attendance management - mark employees as absent for a specific date"""
    selected_date = request.args.get('date') or request.form.get('date')
    if not selected_date:
        selected_date = date.today().strftime('%Y-%m-%d')

    try:
        filter_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format', 'error')
        filter_date = date.today()
        selected_date = filter_date.strftime('%Y-%m-%d')

    if request.method == 'POST':
        try:
            # Get list of employee IDs marked as absent
            absent_employee_ids = request.form.getlist('absent_employees')
            absent_employee_ids = [int(emp_id) for emp_id in absent_employee_ids if emp_id.isdigit()]

            # Get all employees based on role permissions
            employees_query = Employee.query.filter_by(is_active=True)

            # Apply role-based filtering
            if (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
                # Manager: Can manage their team + themselves
                manager_id = current_user.employee_profile.id
                employees_query = employees_query.filter(
                    db.or_(
                        Employee.id == manager_id,
                        Employee.manager_id == manager_id
                    )
                )

            all_employees = employees_query.all()

            # Ensure attendance records exist for all employees for this date
            create_daily_attendance_records(filter_date, all_employees)

            # Update attendance status for all employees
            for employee in all_employees:
                attendance = Attendance.query.filter_by(
                    employee_id=employee.id,
                    date=filter_date
                ).first()

                if attendance:
                    if employee.id in absent_employee_ids:
                        attendance.status = 'Absent'
                        attendance.remarks = f'Marked absent by {current_user.full_name}'  # Use property that gets name from employee profile
                        # Clear time fields for absent employees
                        attendance.clock_in = None
                        attendance.clock_out = None
                        attendance.break_start = None
                        attendance.break_end = None
                        attendance.regular_hours = 0
                        attendance.overtime_hours = 0
                        attendance.total_hours = 0
                    else:
                        attendance.status = 'Present'
                        # For present employees, set default 8 hours if not manually clocked
                        if not attendance.clock_in and not attendance.clock_out:
                            attendance.regular_hours = 8
                            attendance.total_hours = 8
                            attendance.overtime_hours = 0

            db.session.commit()

            present_count = len(all_employees) - len(absent_employee_ids)
            absent_count = len(absent_employee_ids)

            flash(f'Attendance updated for {filter_date.strftime("%B %d, %Y")}: {present_count} Present, {absent_count} Absent', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating attendance: {str(e)}', 'error')

    # Get employees and their attendance for the selected date
    employees_query = Employee.query.filter_by(is_active=True)

    # Apply role-based filtering for display
    if (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        manager_id = current_user.employee_profile.id
        employees_query = employees_query.filter(
            db.or_(
                Employee.id == manager_id,
                Employee.manager_id == manager_id
            )
        )

    employees = employees_query.order_by(Employee.first_name, Employee.last_name).all()

    # Ensure attendance records exist for all employees for this date
    create_daily_attendance_records(filter_date, employees)

    # Get attendance records for the selected date
    attendance_records = {}
    for employee in employees:
        attendance = Attendance.query.filter_by(
            employee_id=employee.id,
            date=filter_date
        ).first()
        attendance_records[employee.id] = attendance

    return render_template('attendance/bulk_manage.html',
                         employees=employees,
                         attendance_records=attendance_records,
                         selected_date=selected_date,
                         filter_date=filter_date,
                         date=date)


def create_daily_attendance_records(target_date, employees=None):
    """Create attendance records for all active employees for a specific date"""
    if employees is None:
        employees = Employee.query.filter_by(is_active=True).all()

    created_count = 0
    for employee in employees:
        # Check if attendance record already exists
        existing = Attendance.query.filter_by(
            employee_id=employee.id,
            date=target_date
        ).first()

        if not existing:
            # Create new attendance record with default Present status
            attendance = Attendance()
            attendance.employee_id = employee.id
            attendance.date = target_date
            attendance.status = 'Present'
            attendance.regular_hours = 8  # Default 8 hours for present employees
            attendance.total_hours = 8
            attendance.overtime_hours = 0
            attendance.remarks = 'Auto-generated attendance record'

            db.session.add(attendance)
            created_count += 1

    if created_count > 0:
        db.session.commit()
        print(f"Created {created_count} attendance records for {target_date}")

    return created_count


def auto_create_daily_attendance():
    """Auto-create attendance records for all active employees for today"""
    today = date.today()
    employees = Employee.query.filter_by(is_active=True).all()
    return create_daily_attendance_records(today, employees)


@app.route('/attendance/auto-create', methods=['POST'])
@require_role(['Super Admin', 'Admin'])
def attendance_auto_create():
    """Manual trigger for creating daily attendance records - useful for Render deployment"""
    try:
        target_date_str = request.form.get('date')
        if target_date_str:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        else:
            target_date = date.today()

        # Get all active employees
        employees = Employee.query.filter_by(is_active=True).all()

        # Create attendance records
        created_count = create_daily_attendance_records(target_date, employees)

        if created_count > 0:
            flash(f'Successfully created attendance records for {created_count} employees on {target_date}', 'success')
        else:
            flash(f'Attendance records already exist for all employees on {target_date}', 'info')

    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
    except Exception as e:
        flash(f'Error creating attendance records: {str(e)}', 'error')

    return redirect(url_for('attendance_bulk_manage'))


@app.route('/api/attendance/auto-create', methods=['POST'])
def api_attendance_auto_create():
    """API endpoint for creating daily attendance records - for external cron services"""
    try:
        # Simple API key authentication (you should set this in environment variables)
        api_key = request.headers.get('X-API-Key') or request.form.get('api_key')
        expected_api_key = os.environ.get('ATTENDANCE_API_KEY', 'your-secret-api-key-here')

        if api_key != expected_api_key:
            return {'error': 'Invalid API key'}, 401

        target_date_str = request.form.get('date') or request.json.get('date') if request.is_json else None
        if target_date_str:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        else:
            target_date = date.today()

        # Get all active employees
        employees = Employee.query.filter_by(is_active=True).all()

        # Create attendance records
        created_count = create_daily_attendance_records(target_date, employees)

        return {
            'success': True,
            'message': f'Created attendance records for {created_count} employees on {target_date}',
            'date': target_date.strftime('%Y-%m-%d'),
            'created_count': created_count
        }, 200

    except ValueError:
        return {'error': 'Invalid date format. Please use YYYY-MM-DD format.'}, 400
    except Exception as e:
        return {'error': f'Error creating attendance records: {str(e)}'}, 500


# Leave Management Routes have been moved to routes_leave.py
# See routes_leave.py for leave_list, leave_request, leave_edit, leave_approve


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
    if (current_user.role.name if current_user.role else None) == 'Employee' and hasattr(current_user,
                                                   'employee_profile') and current_user.employee_profile:
        query = query.filter(
            Claim.employee_id == current_user.employee_profile.id)
    elif (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user,
                                                    'employee_profile') and current_user.employee_profile:
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
@require_role(['Super Admin', 'Admin', 'HR Manager'])
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
    if (current_user.role.name if current_user.role else None) == 'Employee' and hasattr(current_user,
                                                   'employee_profile') and current_user.employee_profile:
        query = query.filter(
            Appraisal.employee_id == current_user.employee_profile.id)
    elif (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user,
                                                    'employee_profile') and current_user.employee_profile:
        query = query.filter(
            Employee.manager_id == current_user.employee_profile.id)

    appraisals = query.order_by(Appraisal.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)

    return render_template('appraisal/list.html', appraisals=appraisals)


@app.route('/appraisal/create', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager'])
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
    if (current_user.role.name if current_user.role else None) == 'HR Manager' and hasattr(current_user,
                                                  'employee_profile') and current_user.employee_profile:
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
                    record['nationality'], record['designation']
                ])

            headers = [
                'Employee ID', 'Name', 'Passport/ID', 'Work Permit Type',
                'Work Permit Expiry', 'Gross Salary', 'Nationality', 'Designation'
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

    if new_role in ['Super Admin', 'Admin', 'HR Manager', 'User']:
        user.role = new_role
        db.session.commit()
        flash(f'User role updated to {new_role}', 'success')
    else:
        flash('Invalid role specified', 'error')

    return redirect(url_for('user_management'))


@app.route('/export/employees')
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def export_employees():
    """Export employees to CSV"""
    employees = Employee.query.filter_by(is_active=True).all()

    csv_data = []
    for emp in employees:
        csv_data.append([
            emp.employee_id, emp.first_name, emp.last_name, emp.email,
            emp.nric, emp.designation.name if emp.designation else '', emp.department,
            format_date(emp.hire_date), emp.employment_type,
            emp.work_permit_type,
            format_currency(emp.basic_salary)
        ])

    headers = [
        'Employee ID', 'First Name', 'Last Name', 'Email', 'NRIC', 'Designation',
        'Department', 'Hire Date', 'Employment Type', 'Work Permit Type',
        'Basic Salary'
    ]

    return export_to_csv(csv_data, 'employees_export.csv', headers)


# Mobile API routes for PWA functionality
@app.route('/api/attendance/check')
@require_login
def api_attendance_check():
    """Check today's attendance status for mobile"""
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
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


# Master Data Management Routes
# Role routes moved to `routes_masters.py` to avoid duplicate endpoint
# registrations. See `routes_masters.py` for the canonical implementations
# of role_list, role_add, role_edit and role_delete.

# Department routes moved to `routes_masters.py` to avoid duplicate endpoint
# registrations. See `routes_masters.py` for the canonical implementations
# of department_list, department_add, department_edit and department_delete.
# Note: Working Hours Management Routes have been moved to routes_masters.py
