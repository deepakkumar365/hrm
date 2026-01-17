from flask import session, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from sqlalchemy import func, extract, and_, text
from datetime import datetime, date, time, timedelta
import calendar
import os
import time as pytime
import subprocess
from werkzeug.utils import secure_filename
from decimal import Decimal
import pytz

from app import app, db
from core.auth import require_login, require_role, create_default_users
from core.models import (Employee, Payroll, PayrollConfiguration, Attendance, Leave, Claim, Appraisal,
                     ComplianceReport, User, Role, Department, WorkingHours, WorkSchedule,
                     Company, Tenant, EmployeeBankInfo, EmployeeDocument, TenantPaymentConfig, TenantDocument, Designation,
                     Organization, OTDailySummary, EmployeeGroup, UserCompanyAccess, PayslipTemplate)
from sqlalchemy import tuple_
from core.forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user
from services.singapore_payroll import SingaporePayrollCalculator
from core.utils import (export_to_csv, format_currency, format_date, parse_date,
                   validate_nric, generate_employee_id, check_permission,
                   mobile_optimized_pagination, get_current_month_dates, get_employee_local_time)
from core.constants import DEFAULT_USER_PASSWORD
from core.constants import DEFAULT_USER_PASSWORD
from services.attendance_service import AttendanceService
from services.file_service import FileService

# Helper to validate image extension
def _allowed_image(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())

def get_current_user_tenant_id():
    """Get current user's tenant ID for multi-tenant filtering"""
    # Prioritize Tenant from Employee Profile
    if current_user and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        if current_user.employee_profile.company and current_user.employee_profile.company.tenant_id:
            return current_user.employee_profile.company.tenant_id

    # Fallback to Organization
    if current_user and current_user.organization:
        return current_user.organization.tenant_id
    return None

def get_overtime_groups(tenant_id=None):
    """
    Get available overtime groups from current tenant configuration.
    If 'By Group' calculation is enabled, use the configured group type.
    Otherwise fall back to defaults.
    """
    if not tenant_id:
        tenant_id = get_current_user_tenant_id()
    
    if not tenant_id:
        return ["Group 1", "Group 2", "Group 3"]
        
    try:
        from core.models import TenantConfiguration
        config = TenantConfiguration.query.filter_by(tenant_id=tenant_id).first()
        if config and config.overtime_calculation_method == 'By Group' and config.overtime_group_type:
            # If multiple groups were stored as comma-separated values
            if ',' in config.overtime_group_type:
                return [g.strip() for g in config.overtime_group_type.split(',')]
            return [config.overtime_group_type]
    except Exception as e:
        print(f"Error fetching overtime groups: {e}")
        
    return ["Group 1", "Group 2", "Group 3"]

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

@app.route('/sw.js')
def serve_sw():
    """Serve service worker from root to ensure it has correct scope"""
    return app.send_static_file('sw.js')

@app.route('/manifest.json')
def serve_manifest():
    """Serve manifest from root"""

    return app.send_static_file('manifest.json')

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
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        wh_columns = [col['name'] for col in inspector.get_columns('hrm_working_hours')]
        
        # Check if we can safely query WorkingHours (need grace_period if models say so)
        # In this specific case, we'll just check for grace_period as it's the known issue
        if 'grace_period' in wh_columns:
            if WorkingHours.query.count() == 0:
                from datetime import time
                working_hours = [
                    WorkingHours(name='Full-time Standard', start_time=time(9, 0), end_time=time(18, 0),
                               hours_per_day=8.0, hours_per_week=40.0,
                               description='Standard full-time working hours'),
                    WorkingHours(name='Part-time (Half Day)', start_time=time(9, 0), end_time=time(13, 0),
                               hours_per_day=4.0, hours_per_week=20.0,
                               description='Half day part-time schedule'),
                    WorkingHours(name='Extended Hours', start_time=time(8, 0), end_time=time(18, 0),
                               hours_per_day=9.0, hours_per_week=45.0,
                               description='Extended working hours with overtime'),
                    WorkingHours(name='Flexible Hours', start_time=time(9, 0), end_time=time(18, 0),
                               hours_per_day=8.0, hours_per_week=40.0,
                               description='Flexible working arrangement'),
                ]
                for wh in working_hours:
                    db.session.add(wh)
        else:
            print("[WARNING] 'grace_period' column missing in 'hrm_working_hours'. Skipping WorkingHours initialization.")

        # Create default work schedules if none exist
        if 'hrm_work_schedules' in tables:
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
                print("[WARNING] Database tables not yet created. Skipping default data initialization.")
                print("Run 'flask db upgrade' to create tables, then restart the application.")
                return

            if create_default_users():
                print("[OK] Default users created successfully!")
            if create_default_master_data():
                print("[OK] Default master data created successfully!")
    except Exception as e:
        print(f"[WARNING] Could not initialize default data: {e}")
        print("This is normal if the database is not yet set up or tables haven't been created.")

# Initialize database and data on startup (only if not skipped)
# NOTE: Moved to app.py or manual run to avoid import-time database queries
# if os.environ.get('FLASK_SKIP_DB_INIT') != '1':
#     # Initialize default data
#     initialize_default_data()


@app.before_request
def make_session_permanent():
    session.permanent = True


@app.route('/')
def index():
    """Landing page and dashboard"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    user_role = current_user.role.name if current_user.role else None
    if user_role in ['Employee', 'User']:
        return redirect(url_for('attendance_mark'))

    return redirect(url_for('dashboard'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        user_role = current_user.role.name if current_user.role else None
        if user_role in ['Employee', 'User']:
            return redirect(url_for('attendance_mark'))
        return redirect(url_for('dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user)
            
            # Store user timezone in session for easy access
            if user.employee_profile:
                session['user_timezone'] = user.employee_profile.timezone or 'UTC'
            else:
                session['user_timezone'] = 'UTC'
                
            next_page = request.args.get('next')
            
            # Redirect Employee/User to attendance page instead of dashboard
            user_role = user.role.name if user.role else None
            if not next_page and user_role in ['Employee', 'User']:
                return redirect(url_for('attendance_mark'))
                
            return redirect(next_page) if next_page else redirect(
                url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('auth/login.html', form=form, environment=os.environ.get('ENVIRONMENT', 'production'))


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
def logout():
    """User logout - clears session without database access"""
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
    """Main dashboard with HR metrics - Routes to role-specific dashboards"""

    # Check user role and route to appropriate dashboard
    user_role_name = current_user.role.name if current_user.role else None

    if user_role_name == 'Super Admin':
        # Render Super Admin Dashboard
        return render_super_admin_dashboard()

    elif user_role_name in ['HR Manager', 'Tenant Admin']:
        # Route to HR Manager Dashboard (handles both HR Manager and Tenant Admin roles)
        from routes.routes_hr_manager import hr_manager_dashboard
        return hr_manager_dashboard()

    # Get basic statistics (for Employee and other roles)
    stats = {
        'total_employees': Employee.query.filter_by(is_active=True).count(),
        'pending_leaves': Leave.query.filter_by(status='Pending').count(),
        'pending_claims': Claim.query.filter_by(status='Pending').count(),
        'this_month_attendance': 0,
        # Placeholders for missing models/logic
        'absent_days': 0,
        'annual_leave_balance': 11,
        'sick_leave_balance': 9.5,
        'comp_off_balance': 0
    }

    # Get Next Leave for current user
    if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        next_leave = Leave.query.filter(
            Leave.employee_id == current_user.employee_profile.id,
            Leave.start_date >= date.today(),
            Leave.status == 'Approved'
        ).order_by(Leave.start_date).first()
        
        if next_leave:
            stats['next_leave_date'] = format_date(next_leave.start_date)
            stats['next_leave_type'] = next_leave.leave_type
    
    # Get Upcoming Holidays (Placeholder as Holiday model missing)
    upcoming_holidays = [
        {'name': 'Christmas', 'date': date(2025, 12, 25), 'day': 'Thursday'},
        {'name': 'New Year', 'date': date(2026, 1, 1), 'day': 'Thursday'}
    ]

    # Get Upcoming Birthdays
    upcoming_birthdays = []
    today = date.today()
    # Logic to find birthdays in next 30 days
    employees = Employee.query.filter(Employee.is_active == True).all()
    for emp in employees:
        if emp.date_of_birth:
            dob_this_year = emp.date_of_birth.replace(year=today.year)
            if dob_this_year < today:
                dob_this_year = dob_this_year.replace(year=today.year + 1)
            
            days_until = (dob_this_year - today).days
            if 0 <= days_until <= 30:
                upcoming_birthdays.append({
                    'name': f"{emp.first_name} {emp.last_name}",
                    'designation': emp.designation.name if emp.designation else 'Employee',
                    'location': emp.location or 'Office',
                    'phone': emp.phone,
                    'date': dob_this_year,
                    'is_today': days_until == 0
                })
    
    # Sort birthdays by date
    upcoming_birthdays.sort(key=lambda x: x['date'])

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

    elif user_role_name == 'Manager':
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

    # Get recent attendance record for current user
    recent_attendance = None
    if hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        emp_id = current_user.employee_profile.id
        recent_attendance = Attendance.query.filter_by(employee_id=emp_id).order_by(
            Attendance.date.desc()).first()

    default_calendar_endpoint = 'leave_calendar' if 'leave_calendar' in app.view_functions else 'leave_request'
    leave_calendar_url = url_for(default_calendar_endpoint)

    return render_template('dashboard.html',
                           stats=stats,
                           recent_activities=recent_activities,
                           recent_attendance=recent_attendance,
                           upcoming_holidays=upcoming_holidays,
                           upcoming_birthdays=upcoming_birthdays,
                           moment=datetime.now,
                           leave_calendar_url=leave_calendar_url)


# Employee Management Routes
@app.route('/employees')
@require_login
def employee_list():
    """List all employees with search, pagination, and comprehensive filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '', type=str)
    
    # Filter Parameters
    status = request.args.get('status', 'active', type=str).lower()
    department = request.args.get('department', '', type=str)
    designation_id = request.args.get('designation_id', '', type=str)
    employment_type = request.args.get('employment_type', '', type=str)
    company_id = request.args.get('company_id', '', type=str)
    
    sort_by = request.args.get('sort_by', 'first_name', type=str)
    sort_order = request.args.get('sort_order', 'asc', type=str)

    print("\n[DEBUG] === Employee List Request ===")
    print(f"[DEBUG] Args: page={page}, search={search}, status={status}, dept={department}, desig={designation_id}, type={employment_type}")

    # Join with Company and Tenant to get tenant_name and company_name
    query = db.session.query(
        Employee,
        Company.name.label('company_name'),
        Tenant.name.label('tenant_name')
    ).join(
        Company, Employee.company_id == Company.id
    ).outerjoin(
        Tenant, Company.tenant_id == Tenant.id
    )

    # 1. Status Filter (Default: Active)
    if status == 'active':
        query = query.filter(Employee.is_active == True)
    elif status == 'inactive':
        query = query.filter(Employee.is_active == False)
    # If status is 'all', apply no is_active filter

    # 2. Search Filter
    if search:
        query = query.filter(
            db.or_(Employee.first_name.ilike(f'%{search}%'),
                   Employee.last_name.ilike(f'%{search}%'),
                   Employee.employee_id.ilike(f'%{search}%'),
                   Employee.email.ilike(f'%{search}%'),
                   Company.name.ilike(f'%{search}%'),
                   Tenant.name.ilike(f'%{search}%')))

    # 3. specific Field Filters
    if department:
        query = query.filter(Employee.department == department)
    
    if designation_id and designation_id.isdigit():
        query = query.filter(Employee.designation_id == int(designation_id))

    if employment_type:
        query = query.filter(Employee.employment_type == employment_type)

    if company_id:
        try:
            query = query.filter(Employee.company_id == company_id)
        except Exception:
            pass # Invalid UUID

    # 4. Role-based Access Control
    if (current_user.role.name if current_user.role else None) == 'Manager' and hasattr(current_user, 'employee_profile'):
        query = query.filter(Employee.manager_id == current_user.employee_profile.id)

    user_role = current_user.role.name if current_user.role else None
    accessible_companies = []
    
    if user_role in ['HR Manager', 'Tenant Admin']:
        accessible_companies = current_user.get_accessible_companies()
        company_ids = [c.id for c in accessible_companies]
        query = query.filter(Employee.company_id.in_(company_ids))
    elif user_role in ['Super Admin', 'Admin']:
         # Admins can see all companies, but we fetch them for the filter dropdown
        accessible_companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()

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
    elif sort_by == 'employment_type':
         sort_column = Employee.employment_type
    elif sort_by == 'email':
         sort_column = Employee.email
    else:
        sort_column = Employee.first_name

    if sort_order == 'desc':
        sort_column = sort_column.desc()
    
    # Apply default secondary sort needed for consistent pagination
    query = query.order_by(sort_column, Employee.id)

    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Extract employee objects with company and tenant names
    employees_data = []
    for item in pagination.items:
        employee = item[0]
        employee.company_name = item[1]
        employee.tenant_name = item[2]
        employees_data.append(employee)

    # Custom Pagination Wrapper
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
            self.iter_pages = pagination.iter_pages

    employees = CustomPagination(employees_data, pagination)

    # --- Load Master Data for Filters ---
    
    # 1. Departments (From Master + Distinct Existing)
    # First get master departments
    master_depts = [d.name for d in Department.query.filter_by(is_active=True).order_by(Department.name).all()]
    # Then get any other departments currently in use (in case of legacy data)
    existing_depts_query = db.session.query(Employee.department).distinct().filter(Employee.department.isnot(None))
    if status == 'active':
        existing_depts_query = existing_depts_query.filter(Employee.is_active==True)
    existing_depts = [d[0] for d in existing_depts_query.all()]
    # Combine and unique
    all_departments = sorted(list(set(master_depts + existing_depts)))
    
    # 2. Designations
    all_designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
    
    # 3. Employment Types
    emp_types_query = db.session.query(Employee.employment_type).distinct().filter(Employee.employment_type.isnot(None))
    all_employment_types = [t[0] for t in emp_types_query.all()]
    
    # 4. Status Options
    status_options = [
        {'value': 'active', 'label': 'Active'},
        {'value': 'inactive', 'label': 'Inactive'},
        {'value': 'all', 'label': 'All Status'}
    ]

    return render_template('employees/list.html',
                           employees=employees,
                           search=search,
                           current_filters={
                               'status': status,
                               'department': department,
                               'designation_id': int(designation_id) if designation_id and designation_id.isdigit() else '',
                               'employment_type': employment_type,
                               'company_id': company_id
                           },
                           filter_options={
                               'departments': all_departments,
                               'designations': all_designations,
                               'companies': accessible_companies,
                               'employment_types': all_employment_types,
                               'status_options': status_options
                           },
                           sort_by=sort_by,
                           sort_order=sort_order,
                           per_page=per_page)


@app.route('/employees/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin','HR Manager','Tenant Admin'])
def employee_add():
    # Get accessible companies (handles Super Admin, Tenant Admin, HR Manager scopes)
    all_companies = current_user.get_accessible_companies()
    companies = [c for c in all_companies if c.is_active]
    companies.sort(key=lambda x: x.name)

    # Load master data for all paths
    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
    user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
    managers = Employee.query.filter_by(is_active=True, is_manager=True).all()
    timezones = pytz.all_timezones
    leave_groups = EmployeeGroup.query.filter_by(is_active=True).all()
    # Determine tenant_id
    tenant_id = get_current_user_tenant_id()
    if not tenant_id and companies:
        # Fallback: use tenant from first accessible company if not explicitly set on user
        tenant_id = companies[0].tenant_id

    overtime_groups = get_overtime_groups(tenant_id)

    if request.method == 'POST':
        try:
            # Validate NRIC
            nric_raw = request.form.get('nric', '').strip().upper()
            nric = nric_raw if nric_raw else None
            if not validate_nric(nric):
                flash('Invalid NRIC format', 'error')
                return render_template('employees/form.html',
                                       form_data=request.form,
                                       roles=roles,
                                       user_roles=user_roles,
                                       designations=designations,
                                       departments=departments,
                                       working_hours=working_hours,
                                       work_schedules=work_schedules,
                                       managers=managers,
                                       companies=companies,
                                       timezones=timezones,
                                       leave_groups=leave_groups,
                                       overtime_groups=overtime_groups)

            # Check for duplicate NRIC
            if nric and Employee.query.filter_by(nric=nric).first():
                flash('Employee with this NRIC already exists', 'error')
                return render_template('employees/form.html',
                                       form_data=request.form,
                                       roles=roles,
                                       user_roles=user_roles,
                                       designations=designations,
                                       departments=departments,
                                       working_hours=working_hours,
                                       work_schedules=work_schedules,
                                       managers=managers,
                                       companies=companies,
                                       timezones=timezones,
                                       leave_groups=leave_groups,
                                       overtime_groups=overtime_groups)

            # Create new employee
            employee = Employee()
            # Organization is no longer used for employees
            # employee.organization_id = current_user.organization_id

            # Set company_id from form
            company_id = request.form.get('company_id')
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
            employee.phone = request.form.get('phone')
            employee.nric = nric
            employee.date_of_birth = parse_date(
                request.form.get('date_of_birth'))
            employee.gender = request.form.get('gender')
            employee.nationality = request.form.get('nationality')
            employee.address = request.form.get('address')
            employee.postal_code = request.form.get('postal_code')
            # Clean up department field
            dept_val = request.form.get('department')
            if dept_val:
                dept_val = dept_val.strip()
                # Validate it exists in master
                valid_dept = Department.query.filter_by(name=dept_val, is_active=True).first()
                if not valid_dept:
                    print(f"Warning: New Employee trying to save invalid department '{dept_val}'")
            
            employee.department = dept_val if dept_val else None
            # Position field removed - use designation_id instead
            employee.hire_date = parse_date(request.form.get('hire_date'))
            termination_date = request.form.get('termination_date')
            if termination_date:
                employee.termination_date = parse_date(termination_date)
            employee.employment_type = request.form.get('employment_type')
            employee.work_permit_type = request.form.get('work_permit_type')
            employee.timezone = request.form.get('timezone', 'UTC')
            employee.overtime_group_id = request.form.get('overtime_group_id')
            
            leave_group_id = request.form.get('employee_group_id')
            if leave_group_id:
                employee.employee_group_id = int(leave_group_id)

            work_permit_number = request.form.get('work_permit_number')
            if work_permit_number:
                employee.work_permit_number = work_permit_number

            work_permit_expiry = request.form.get('work_permit_expiry')
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

            # [NEW] Handle Certification Files (Add Mode) - require employee.id so we flush first if needed or allow FileService to use employee_id string
            # We already flush later for profile image, let's flush here if we have files.
            
            # Helper to upload cert file
            def upload_cert_file(file_key, file_cat, emp_obj, field_name):
                f_obj = request.files.get(file_key)
                if f_obj and f_obj.filename.strip():
                    if not emp_obj.id:
                        db.session.add(emp_obj)
                        db.session.flush()
                    
                    record = FileService.upload_file(
                        file_obj=f_obj,
                        module='HR',
                        tenant_id=tenant_id,
                        company_id=emp_obj.company_id,
                        employee_id=emp_obj.id,
                        file_category=file_cat
                    )
                    if record:
                        setattr(emp_obj, field_name, record.id)

            upload_cert_file('hazmat_file', 'hazmat', employee, 'hazmat_file_id')
            upload_cert_file('airport_pass_file', 'airport_pass', employee, 'airport_pass_file_id')
            upload_cert_file('psa_pass_file', 'psa_pass', employee, 'psa_pass_file_id')

            employee.basic_salary = float(request.form.get('basic_salary') or 0)
            employee.allowances = float(request.form.get('allowances') or 0)
            
            employee_cpf_rate = request.form.get('employee_cpf_rate')
            employee.employee_cpf_rate = float(employee_cpf_rate) if employee_cpf_rate else 20.00
            
            employer_cpf_rate = request.form.get('employer_cpf_rate')
            employee.employer_cpf_rate = float(employer_cpf_rate) if employer_cpf_rate else 17.00

            hourly_rate = request.form.get('hourly_rate')
            if hourly_rate and hourly_rate.strip():
                employee.hourly_rate = float(hourly_rate)

            employee.cpf_account = request.form.get('cpf_account')
            employee.bank_name = request.form.get('bank_name')
            employee.bank_account = request.form.get('bank_account')
            employee.account_holder_name = request.form.get('account_holder_name')
            employee.swift_code = request.form.get('swift_code')
            employee.ifsc_code = request.form.get('ifsc_code')

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
            employee.is_active = bool(request.form.get('is_active'))
            employee.timezone = request.form.get('timezone', 'UTC')

            # Handle profile image upload (optional)
            file = request.files.get('profile_image')
            if file and file.filename.strip():
                if not _allowed_image(file.filename):
                    return render_template('employees/form.html',
                                           form_data=request.form,
                                           roles=roles,
                                           user_roles=user_roles,
                                           designations=designations,
                                           departments=departments,
                                           working_hours=working_hours,
                                           work_schedules=work_schedules,
                                           managers=managers,
                                           companies=companies,
                                           timezones=timezones,
                                           leave_groups=leave_groups,
                                           overtime_groups=overtime_groups)

                # Save using FileService
                # Path: tenants/{id}/companies/{id}/employees/{id}/profile/
                file_record = FileService.upload_file(
                    file_obj=file,
                    module='HR',
                    tenant_id=tenant_id,
                    company_id=employee.company_id,
                    employee_id=employee.employee_id, # Use string ID for path if preferred, or object ID if available (object ID is None here before flush)
                    # Note: employee.id is None here. We can flush to get ID or use employee_id string.
                    # FileService expects ID. Let's use flush()
                    file_category='profile'
                )
                
                # To get employee.id, we need to add and flush
                # But we generally add at end.
                # Let's adjust approach: saving file AFTER flush/commit or accept using employee_id string in path?
                # FileService.upload_file takes `employee_id`. If we want integer ID, we must flush.
                
                # ALTERNATIVE: Use employee.employee_id (string) for the path logic in FileService if it supports it?
                # The Plan said: tenants/{tenant_id}/companies/{company_id}/employees/{employee_id}/
                # Standard practice usually implies DB ID, but String ID is more readable. 
                # Let's try to flush first.
                
                # However, if we flush, we might commit partial state? No, flush just assigns ID.
                db.session.add(employee)
                db.session.flush()
                
                # Retry upload with ID
                file_record = FileService.upload_file(
                    file_obj=file,
                    module='HR',
                    tenant_id=tenant_id,
                    company_id=employee.company_id,
                    employee_id=employee.id,
                    file_category='profile',
                    resize_to=(500, 500)
                )
                
                if file_record:
                    employee.profile_picture_id = file_record.id
                    employee.profile_image_path = file_record.file_path # Legacy support
                else:
                    flash('Failed to upload profile image', 'warning')

            if not employee.id: # If not flushed above
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
                
                # Handle email - required by DB but might be missing for employee
                if employee.email:
                    user.email = employee.email
                else:
                    # Auto-generate placeholder email to satisfy DB constraint
                    user.email = f"{username}@noemail.system"
                
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
                
                # --- Auto-Sync Access Control ---
                # Automatically grant access to the selected company
                if company_id:
                    # Check if access already exists (shouldn't for new user, but good practice)
                    existing_access = UserCompanyAccess.query.filter_by(
                        user_id=user.id,
                        company_id=company_id
                    ).first()
                    
                    if not existing_access:
                        new_access = UserCompanyAccess(
                            user_id=user.id,
                            company_id=company_id,
                            created_at=datetime.now(),
                            modified_at=datetime.now()
                        )
                        db.session.add(new_access)
                        db.session.commit()
                        print(f"Auto-granted access to company {company_id} for user {username}")

                flash(f'Employee added successfully. Login credentials created - Username: {username}, Password: {DEFAULT_USER_PASSWORD}', 'success')

            except Exception as user_error:
                # Employee was created but user creation failed
                flash(f'Employee added successfully, but user account creation failed: {str(user_error)}. Please create manually.', 'warning')

            return redirect(url_for('employee_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding employee: {str(e)}', 'error')
            return render_template('employees/form.html',
                                   form_data=request.form,
                                   roles=roles,
                                   user_roles=user_roles,
                                   designations=designations,
                                   departments=departments,
                                   working_hours=working_hours,
                                   work_schedules=work_schedules,
                                   managers=managers,
                                   companies=companies,
                                   timezones=timezones,
                                   leave_groups=leave_groups,
                                   overtime_groups=overtime_groups)

    return render_template('employees/form.html',
                           managers=managers,
                           roles=roles,
                           user_roles=user_roles,
                           designations=designations,
                           departments=departments,
                           working_hours=working_hours,
                           work_schedules=work_schedules,
                           companies=companies,
                           timezones=timezones,
                           leave_groups=leave_groups,
                           overtime_groups=overtime_groups)


@app.route('/employees/<int:employee_id>')
@require_login
def employee_view(employee_id):
    """View employee details"""
    employee = Employee.query.get_or_404(employee_id)

    # Check permission
    if (current_user.role.name if current_user.role else None) == 'Employee':
        if not (hasattr(current_user, 'employee_profile')
                and current_user.employee_profile.id == employee_id):
            flash('You do not have permission to view this employee.', 'error')
            return redirect(url_for('dashboard'))
    elif (current_user.role.name if current_user.role else None) == 'Manager':
        if not (hasattr(current_user, 'employee_profile') and
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


@app.route('/profile', methods=['GET', 'POST'])
@require_login
def profile():
    """User's own profile page"""
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        flash('Profile not found. Please contact your administrator.', 'error')
        return redirect(url_for('dashboard'))

    employee = current_user.employee_profile

    # Handle Profile Picture Upload
    if request.method == 'POST':
        file = request.files.get('profile_image')
        if file and file.filename.strip():
             if not _allowed_image(file.filename):
                 flash('Invalid image type.', 'error')
             else:
                 try:
                     tenant_id = employee.company.tenant_id if employee.company else get_current_user_tenant_id()
                     from services.file_service import FileService
                     
                     file_record = FileService.upload_file(
                         file_obj=file,
                         module='HR',
                         tenant_id=tenant_id,
                         company_id=employee.company_id,
                         employee_id=employee.id,
                         file_category='profile',
                         resize_to=(500, 500)
                     )
                     
                     if file_record:
                         if employee.profile_picture_id:
                             try:
                                 FileService.delete_file(employee.profile_picture_id)
                             except:
                                 pass
                         
                         employee.profile_picture_id = file_record.id
                         employee.profile_image_path = file_record.file_path
                         db.session.commit()
                         flash('Profile picture updated successfully', 'success')
                     else:
                         flash('Failed to upload profile picture', 'error')
                 except Exception as e:
                     db.session.rollback()
                     flash(f'Error uploading picture: {str(e)}', 'error')
        
        return redirect(url_for('profile'))

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

    return render_template('profile.html', employee=employee, stats=stats, activities=activities)


@app.route('/profile/edit', methods=['GET', 'POST'])
@require_login
def profile_edit():
    """User's profile edit page"""
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        flash('Profile not found.', 'error')
        return redirect(url_for('dashboard'))

    employee = current_user.employee_profile

    if request.method == 'POST':
        try:
            # Update personal info
            employee.phone = request.form.get('phone')
            employee.address = request.form.get('address')
            employee.postal_code = request.form.get('postal_code')
            
            # Update bank details
            employee.bank_name = request.form.get('bank_name')
            employee.bank_account = request.form.get('bank_account')
            employee.account_holder_name = request.form.get('account_holder_name')
            employee.swift_code = request.form.get('swift_code')
            employee.ifsc_code = request.form.get('ifsc_code')
            
            # Update general user info if needed
            # current_user.email = request.form.get('email') # Usually disabled in edit profile

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating profile: {str(e)}', 'error')

    return render_template('profile_edit.html', employee=employee)


@app.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager', 'Tenant Admin'])
def employee_edit(employee_id):
    """Edit employee details"""
    employee = Employee.query.get_or_404(employee_id)
    tenant_id = get_current_user_tenant_id()
    
    # Get accessible companies (handles Super Admin, Tenant Admin, HR Manager scopes)
    all_companies = current_user.get_accessible_companies()
    companies = [c for c in all_companies if c.is_active]
    companies.sort(key=lambda x: x.name)

    # Load master data for all paths
    roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
    user_roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
    departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
    working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
    work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
    managers = Employee.query.filter_by(is_active=True, is_manager=True).filter(Employee.id != employee_id).all()
    timezones = pytz.all_timezones
    leave_groups = EmployeeGroup.query.filter_by(is_active=True).all()
    overtime_groups = get_overtime_groups(tenant_id)

    if request.method == 'POST':
        try:
            # Update company_id from form
            company_id = request.form.get('company_id')
            if company_id:
                employee.company_id = company_id
            else:
                employee.company_id = None

            employee.first_name = request.form.get('first_name')
            employee.last_name = request.form.get('last_name')
            email = request.form.get('email', '').strip()
            employee.email = email if email else None
            employee.phone = request.form.get('phone')
            
            # Validate NRIC
            nric_raw = request.form.get('nric', '').strip().upper()
            nric = nric_raw if nric_raw else None
            if not validate_nric(nric):
                flash('Invalid NRIC format', 'error')
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
                                       companies=companies,
                                       timezones=timezones,
                                       leave_groups=leave_groups,
                                       overtime_groups=overtime_groups)

            # Check for duplicate NRIC
            if nric:
                duplicate = Employee.query.filter(Employee.nric == nric, Employee.id != employee_id).first()
                if duplicate:
                    flash('Employee with this NRIC already exists', 'error')
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
                                           companies=companies,
                                           timezones=timezones,
                                           leave_groups=leave_groups,
                                           overtime_groups=overtime_groups)
            employee.nric = nric
            employee.address = request.form.get('address')
            employee.postal_code = request.form.get('postal_code')
            # Clean up department field
            dept_val = request.form.get('department')
            if dept_val:
                dept_val = dept_val.strip()
                # Validate it exists in master
                valid_dept = Department.query.filter_by(name=dept_val, is_active=True).first()
                if not valid_dept:
                    print(f"Warning: Employee {employee_id} trying to save invalid department '{dept_val}'")
            
            employee.department = dept_val if dept_val else None
            # Position field removed - use designation_id instead
            employee.employment_type = request.form.get('employment_type')
            employee.work_permit_type = request.form.get('work_permit_type')

            work_permit_number = request.form.get('work_permit_number')
            if work_permit_number:
                employee.work_permit_number = work_permit_number

            # Handle additional personal fields
            employee.gender = request.form.get('gender')
            employee.nationality = request.form.get('nationality')

            # Handle date fields
            hire_date = request.form.get('hire_date')
            if hire_date:
                employee.hire_date = parse_date(hire_date)

            termination_date = request.form.get('termination_date')
            if termination_date:
                employee.termination_date = parse_date(termination_date)
            else:
                employee.termination_date = None

            date_of_birth = request.form.get('date_of_birth')
            if date_of_birth:
                employee.date_of_birth = parse_date(date_of_birth)

            work_permit_expiry = request.form.get('work_permit_expiry')
            if work_permit_expiry:
                employee.work_permit_expiry = parse_date(work_permit_expiry)

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

            # [NEW] Handle Certification Files (Edit Mode)
            def upload_cert_file_edit(file_key, file_cat, emp_obj, field_name):
                f_obj = request.files.get(file_key)
                if f_obj and f_obj.filename.strip():
                    # Determine tenant_id from company or context
                    t_id = emp_obj.company.tenant_id if emp_obj.company else get_current_user_tenant_id()
                    
                    record = FileService.upload_file(
                        file_obj=f_obj,
                        module='HR',
                        tenant_id=t_id,
                        company_id=emp_obj.company_id,
                        employee_id=emp_obj.id,
                        file_category=file_cat
                    )
                    if record:
                        setattr(emp_obj, field_name, record.id)

            upload_cert_file_edit('hazmat_file', 'hazmat', employee, 'hazmat_file_id')
            upload_cert_file_edit('airport_pass_file', 'airport_pass', employee, 'airport_pass_file_id')
            upload_cert_file_edit('psa_pass_file', 'psa_pass', employee, 'psa_pass_file_id')

            basic_salary = request.form.get('basic_salary')
            employee.basic_salary = float(basic_salary) if basic_salary and basic_salary.strip() else 0.0
            
            allowances = request.form.get('allowances')
            employee.allowances = float(allowances) if allowances and allowances.strip() else 0.0

            hourly_rate = request.form.get('hourly_rate')
            if hourly_rate and hourly_rate.strip():
                employee.hourly_rate = float(hourly_rate)
            else:
                employee.hourly_rate = 0.0

            employee.cpf_account = request.form.get('cpf_account')
            employee.bank_name = request.form.get('bank_name')
            employee.bank_account = request.form.get('bank_account')
            employee.account_holder_name = request.form.get('account_holder_name')
            employee.swift_code = request.form.get('swift_code')
            employee.ifsc_code = request.form.get('ifsc_code')

            employee.employee_cpf_rate = float(request.form.get('employee_cpf_rate', 20.00))
            employee.employer_cpf_rate = float(request.form.get('employer_cpf_rate', 17.00))

            # Validate mandatory banking field
            if not (employee.account_holder_name and employee.account_holder_name.strip()):
                flash('Account Holder Name is required', 'error')
                return render_template('employees/form.html',
                                       form_data=request.form,
                                       roles=roles,
                                       user_roles=user_roles,
                                       designations=designations,
                                       departments=departments,
                                       working_hours=working_hours,
                                       work_schedules=work_schedules,
                                       managers=managers,
                                       companies=companies,
                                       timezones=timezones,
                                       leave_groups=leave_groups,
                                       overtime_groups=overtime_groups)

            # Optional profile image replace on edit
            file = request.files.get('profile_image')
            if file and file.filename.strip():
                if not _allowed_image(file.filename):
                    flash('Invalid image type. Allowed: ' + ', '.join(sorted(app.config.get('ALLOWED_IMAGE_EXTENSIONS', []))), 'error')
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
                                           companies=companies,
                                           timezones=timezones,
                                           leave_groups=leave_groups,
                                           overtime_groups=overtime_groups)
                                           
                # Determine tenant_id (if not set on object, use current context or user)
                tenant_id = employee.company.tenant_id if employee.company else get_current_user_tenant_id()
                
                # Upload new file
                file_record = FileService.upload_file(
                    file_obj=file,
                    module='HR',
                    tenant_id=tenant_id,
                    company_id=employee.company_id,
                    employee_id=employee.id,
                    file_category='profile',
                    resize_to=(500, 500)
                )
                
                if file_record:
                    # Optional: Delete old file using Service if it was a FileStorage record
                    if employee.profile_picture_id:
                         FileService.delete_file(employee.profile_picture_id)
                    
                    # Update references
                    employee.profile_picture_id = file_record.id
                    employee.profile_image_path = file_record.file_path # Legacy match
                    
                else:
                    flash('Failed to upload new profile image', 'warning')

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
            employee.is_active = bool(request.form.get('is_active'))
            employee.timezone = request.form.get('timezone', 'UTC')

            # Update user role if changed
            user_role_id = request.form.get('user_role_id')
            if user_role_id:
                if employee.user:
                    try:
                        new_role_id = int(user_role_id)
                        # Verify the role exists and is a valid system role
                        new_role = Role.query.filter_by(id=new_role_id, is_active=True).first()
                        if new_role:
                            employee.user.role_id = new_role_id
                    except (ValueError, TypeError):
                        pass  # Invalid role_id, skip update
                else:
                    # Create user account for employee if it doesn't exist
                    try:
                        new_role_id = int(user_role_id)
                        new_role = Role.query.filter_by(id=new_role_id, is_active=True).first()
                        
                        if new_role:
                            # Create new user
                            user = User()
                            # Use employee_id as username
                            user.username = employee.employee_id
                            user.email = employee.email
                            user.first_name = employee.first_name
                            user.last_name = employee.last_name
                            
                            # Handle email - required by DB
                            if employee.email:
                                user.email = employee.email
                            else:
                                # Auto-generate placeholder email satisfy DB constraint
                                user.email = f"{user.username}@noemail.system"

                            user.organization_id = current_user.organization_id
                            user.role_id = new_role.id
                            user.set_password(DEFAULT_USER_PASSWORD)
                            user.must_reset_password = True
                            
                            db.session.add(user)
                            db.session.flush() # Get ID
                            
                            employee.user_id = user.id
                            
                            flash(f'User account created. Username: {user.username}, Password: {DEFAULT_USER_PASSWORD}', 'info')
                    except Exception as e:
                         # Log warning but allow employee update to proceed
                         print(f"Warning: Could not create user account: {e}")

            # --- Automatic Name Sync ---
            # If the employee has a linked user account, keep the names in sync
            if employee.user:
                employee.user.first_name = employee.first_name
                employee.user.last_name = employee.last_name
                
                # --- Auto-Sync Access Control ---
                # Ensure user has access to the assigned company
                if employee.company_id:
                     existing_access = UserCompanyAccess.query.filter_by(
                        user_id=employee.user.id,
                        company_id=employee.company_id
                    ).first()
                    
                     if not existing_access:
                        new_access = UserCompanyAccess(
                            user_id=employee.user.id,
                            company_id=employee.company_id,
                            created_at=datetime.now(),
                            modified_at=datetime.now()
                        )
                        db.session.add(new_access)
                        # We do NOT remove old access automatically to prevent blocking access to previous views if needed.
                        # Revocation should be manual via Access Control.
                        print(f"Auto-granted access to company {employee.company_id} for updated user {employee.user.username}")

            db.session.commit()
            flash('Employee updated successfully', 'success')
            return redirect(url_for('employee_list'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error updating employee: {str(e)}', 'error')
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
                                   companies=companies,
                                   timezones=timezones,
                                   leave_groups=leave_groups,
                                   overtime_groups=overtime_groups)

    return render_template('employees/form.html',
                           employee=employee,
                           managers=managers,
                           roles=roles,
                           user_roles=user_roles,
                           designations=designations,
                           departments=departments,
                           working_hours=working_hours,
                           work_schedules=work_schedules,
                           companies=companies,
                           timezones=timezones,
                           leave_groups=leave_groups,
                           overtime_groups=overtime_groups)


# Payroll Management Routes
@app.route('/payroll')
@require_role(['Super Admin', 'Admin', 'Manager', 'HR Manager', 'Tenant Admin'])
def payroll_list():
    """List payroll records"""
    from uuid import UUID

    page = request.args.get('page', 1, type=int)
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    company_id = request.args.get('company_id', type=str)
    employee_id = request.args.get('employee_id', type=int)

    query = Payroll.query.join(Employee)

    # Get accessible companies for HR Manager and Tenant Admin
    accessible_companies = []
    accessible_company_ids = []
    if (current_user.role.name if current_user.role else None) in ['HR Manager', 'Tenant Admin']:
        accessible_companies = current_user.get_accessible_companies()
        accessible_company_ids = [c.id for c in accessible_companies]
        
        # Filter query to only include employees from accessible companies
        query = query.filter(Employee.company_id.in_(accessible_company_ids))

    if month and year:
        query = query.filter(
            extract('month', Payroll.pay_period_end) == month,
            extract('year', Payroll.pay_period_end) == year)

    # Company filter for HR Manager / Tenant Admin
    if company_id and (current_user.role.name if current_user.role else None) in ['HR Manager', 'Tenant Admin']:
        try:
            company_uuid = UUID(company_id)
            if company_uuid in accessible_company_ids:
                query = query.filter(Employee.company_id == company_uuid)
        except (ValueError, TypeError):
            pass

    # Employee filter for HR Manager / Tenant Admin
    if employee_id and (current_user.role.name if current_user.role else None) in ['HR Manager', 'Tenant Admin']:
        try:
            emp_id = int(employee_id)
            query = query.filter(Payroll.employee_id == emp_id)
        except (ValueError, TypeError):
            pass

    # Role-based filtering
    if (current_user.role.name if current_user.role else None) == 'Manager' and hasattr(current_user,
                                                  'employee_profile'):
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

    # Get years for filter dropdown - last 30 years
    from datetime import datetime
    current_year = datetime.now().year
    years = list(range(current_year, current_year - 30, -1))

    # Get employees for filter dropdown (HR Manager / Tenant Admin only)
    employees = []
    if (current_user.role.name if current_user.role else None) in ['HR Manager', 'Tenant Admin']:
        employees = Employee.query.filter(
            Employee.company_id.in_(accessible_company_ids),
            Employee.is_active == True
        ).order_by(Employee.first_name).all()

    payrolls = query.order_by(Payroll.pay_period_end.desc()).paginate(
        page=page, per_page=20, error_out=False)

    return render_template('payroll/list.html',
                           payrolls=payrolls,
                           month=month,
                           year=year,
                           company_id=company_id,
                           employee_id=employee_id,
                           calendar=calendar,
                           companies=accessible_companies,
                           employees=employees,
                           years=years)


@app.route('/payroll/generate', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager', 'Tenant Admin'])
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
                    if existing.status != 'Draft':
                        skipped_count += 1
                        continue
                    # If Draft, proceed to recalculate and overwrite

                # Get payroll config
                config = employee.payroll_config

                # Calculate fixed allowances
                fixed_allowances = 0
                if config:
                    fixed_allowances = float(config.get_total_allowances())

                # Get Approved OT Data (Hours, Amount, Allowances)
                ot_summaries = OTDailySummary.query.filter_by(
                    employee_id=employee.id,
                    status='Approved'
                ).filter(
                    extract('month', OTDailySummary.ot_date) == month,
                    extract('year', OTDailySummary.ot_date) == year
                ).all()

                # Aggregate Approved OT Data
                total_overtime = sum(float(s.ot_hours or 0) for s in ot_summaries)
                calculated_overtime_pay = sum(float(s.ot_amount or 0) for s in ot_summaries)
                ot_allowances = sum(float(s.total_allowances or 0) for s in ot_summaries)
                
                # Apply Override Logic if enabled
                overtime_pay = calculated_overtime_pay
                if existing and existing.ot_override_amount and existing.ot_override_amount > 0:
                     overtime_pay = float(existing.ot_override_amount)

                # Total Allowances
                total_allowances = fixed_allowances + ot_allowances
                
                # Get attendance records (strictly for days worked count)
                attendance_records = Attendance.query.filter_by(
                    employee_id=employee.id).filter(
                        Attendance.date.between(pay_period_start,
                                                pay_period_end)).all()

                # Calculate gross pay
                # Use Payroll Configuration as master source
                basic_pay = float(employee.payroll_config.basic_salary or 0) if employee.payroll_config else 0.0
                gross_pay = basic_pay + total_allowances + overtime_pay

                # Calculate CPF (from Configuration)
                employee_cpf = 0.0
                employer_cpf = 0.0
                
                if config:
                    if config.employee_cpf is not None:
                        employee_cpf = float(config.employee_cpf)
                    if config.employer_cpf is not None:
                         employer_cpf = float(config.employer_cpf)

                # Calculate net pay
                net_pay = gross_pay - employee_cpf

                # Create or Update payroll record
                payroll = existing if existing else Payroll()
                
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

                if not existing:
                    db.session.add(payroll)
                generated_count += 1

            db.session.commit()

            # Create salary slip documents for newly generated payrolls
            for emp_id in selected_employees:
                employee = Employee.query.get(int(emp_id))
                if not employee:
                    continue

                # Check if salary slip document already exists for this period
                existing_doc = EmployeeDocument.query.filter_by(
                    employee_id=employee.id,
                    document_type='Salary Slip',
                    month=month,
                    year=year
                ).first()

                # Create salary slip document if it doesn't exist
                if not existing_doc:
                    salary_slip_doc = EmployeeDocument(
                        employee_id=employee.id,
                        document_type='Salary Slip',
                        file_path=f'payroll/{year}/{month:02d}/{employee.id}',
                        issue_date=datetime.now().date(),
                        month=month,
                        year=year,
                        description=f"Salary Slip for {datetime(year, month, 1).strftime('%B %Y')}",
                        uploaded_by=current_user.id
                    )
                    db.session.add(salary_slip_doc)

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

    # Get companies for current user's organization/tenant or accessible companies
    companies = []
    if (current_user.role.name if current_user.role else None) in ['HR Manager', 'Tenant Admin']:
        companies = current_user.get_accessible_companies()
    elif current_user and current_user.organization:
        tenant_id = current_user.organization.tenant_id
        if tenant_id:
            companies = Company.query.filter_by(
                tenant_id=tenant_id,
                is_active=True
            ).order_by(Company.name).all()

    return render_template('payroll/generate.html',
                         current_month=current_month,
                         current_year=current_year,
                         companies=companies)




@app.route('/payroll/config')
@require_role(['Super Admin', 'Admin', 'HR Manager', 'Tenant Admin'])
def payroll_config():
    """Payroll configuration page - manage employee salary allowances and OT rates"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    # Filter params
    company_id = request.args.get('company_id', '', type=str)
    department = request.args.get('department', '', type=str)
    manager_id = request.args.get('manager_id', '', type=str)

    # Query active employees
    query = Employee.query.filter_by(is_active=True)

    # Scoping for HR Manager / Tenant Admin
    user_role = current_user.role.name if current_user.role else None
    accessible_companies = []
    
    if user_role in ['HR Manager', 'Tenant Admin']:
        accessible_companies = current_user.get_accessible_companies()
        company_ids = [c.id for c in accessible_companies]
        query = query.filter(Employee.company_id.in_(company_ids))
    elif user_role in ['Super Admin', 'Admin']:
         # Admins can see all companies
        accessible_companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()

    # Apply Filters
    if company_id:
        query = query.filter(Employee.company_id == company_id)
    
    if department:
        query = query.filter(Employee.department == department)
        
    if manager_id and manager_id.isdigit():
        query = query.filter(Employee.manager_id == int(manager_id))

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
        
    # --- Load Data for Filters ---
    
    # Departments (From Master + Distinct Existing)
    master_depts = [d.name for d in Department.query.filter_by(is_active=True).order_by(Department.name).all()]
    existing_depts = [d[0] for d in db.session.query(Employee.department).distinct().filter(Employee.department.isnot(None), Employee.is_active==True).all()]
    all_departments = sorted(list(set(master_depts + existing_depts)))
    
    # Managers (Active employees who are managers)
    managers_query = Employee.query.filter_by(is_active=True, is_manager=True)
    if user_role in ['HR Manager', 'Tenant Admin']:
        # Limit managers to accessible companies
        acc_company_ids = [c.id for c in accessible_companies]
        managers_query = managers_query.filter(Employee.company_id.in_(acc_company_ids))
        
    all_managers = managers_query.order_by(Employee.first_name).all()

    return render_template('payroll/config.html', 
                           employees=employees, 
                           search=search,
                           current_filters={
                               'company_id': company_id,
                               'department': department,
                               'manager_id': int(manager_id) if manager_id and manager_id.isdigit() else ''
                           },
                           filter_options={
                               'companies': accessible_companies,
                               'departments': all_departments,
                               'managers': all_managers
                           })


@app.route('/payroll/config/update', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'HR Manager', 'Tenant Admin'])
def payroll_config_update():
    """Update payroll configuration for an employee (AJAX endpoint)"""
    try:
        data = request.get_json()
        employee_id = data.get('employee_id')
        month = data.get('month')
        year = data.get('year')

        employee = Employee.query.get_or_404(employee_id)

        # Access Control Check
        if (current_user.role.name if current_user.role else None) in ['HR Manager', 'Tenant Admin']:
             accessible_companies = current_user.get_accessible_companies()
             accessible_company_ids = [c.id for c in accessible_companies]
             if not employee.company_id or employee.company_id not in accessible_company_ids:
                 return jsonify({
                    'success': False,
                    'message': 'You do not have permission to update this employee.'
                 }), 403
        
        # 1. Update Master Configuration (Basic & Allowances)
        config = employee.payroll_config

        if not config:
            config = PayrollConfiguration(employee_id=employee_id)
            db.session.add(config)

        # Update base salary (on PayrollConfiguration model)
        if 'basic_salary' in data:
            config.basic_salary = Decimal(str(data['basic_salary'])) if data['basic_salary'] else Decimal(0)

        # Update allowances
        if 'allowance_1_amount' in data:
            config.allowance_1_amount = Decimal(str(data['allowance_1_amount'])) if data['allowance_1_amount'] else Decimal(0)
        if 'allowance_2_amount' in data:
            config.allowance_2_amount = Decimal(str(data['allowance_2_amount'])) if data['allowance_2_amount'] else Decimal(0)
        if 'allowance_3_amount' in data:
            config.allowance_3_amount = Decimal(str(data['allowance_3_amount'])) if data['allowance_3_amount'] else Decimal(0)
        if 'allowance_4_amount' in data:
            config.allowance_4_amount = Decimal(str(data['allowance_4_amount'])) if data['allowance_4_amount'] else Decimal(0)

        # Update OT rate (Optional, mostly removed from UI but kept for backend compat)
        if 'ot_rate_per_hour' in data:
            config.ot_rate_per_hour = Decimal(str(data['ot_rate_per_hour'])) if data['ot_rate_per_hour'] else None

        # Update CPF Configuration (Master)
        if 'employee_cpf' in data:
            config.employee_cpf = Decimal(str(data['employee_cpf'])) if data['employee_cpf'] is not None and data['employee_cpf'] != '' else Decimal(0)
        
        if 'employer_cpf' in data:
            config.employer_cpf = Decimal(str(data['employer_cpf'])) if data['employer_cpf'] is not None and data['employer_cpf'] != '' else Decimal(0)

        # Recalculate Net Salary (Estimated)
        # Net = Basic + Allowances - Employee CPF
        total_allowances = config.get_total_allowances()
        config.net_salary = (config.basic_salary or Decimal(0)) + total_allowances - (config.employee_cpf or Decimal(0))

        config.updated_by = current_user.id
        config.updated_at = datetime.now()
        
        # 2. Update Monthly Overrides (OT Hours, CPF) -> Stored in Draft Payroll Record
        if month and year: # removed 'ot_hours' in data check to allow just updating CPF if needed
            try:
                 # Calculate pay period range
                from calendar import monthrange
                pay_period_start = date(int(year), int(month), 1)
                last_day = monthrange(int(year), int(month))[1]
                pay_period_end = date(int(year), int(month), last_day)
                
                # Check for existing payroll record
                payroll = Payroll.query.filter_by(
                    employee_id=employee_id,
                    pay_period_start=pay_period_start,
                    pay_period_end=pay_period_end
                ).first()
                
                if not payroll:
                    payroll = Payroll(
                        employee_id=employee_id,
                        pay_period_start=pay_period_start,
                        pay_period_end=pay_period_end,
                        status='Draft',
                        # Initialize required fields with defaults to avoid NOT NULL errors
                        basic_pay=0, gross_pay=0, net_pay=0 
                    )
                    db.session.add(payroll)
                
                payroll.status = 'Draft'
                
                # Update OT Hours Override
                if 'ot_hours' in data:
                    payroll.overtime_hours = float(data['ot_hours'])
                    # Default: Recalculate amount based on rate (unless overridden below)
                    ot_rate = float(config.ot_rate_per_hour) if config.ot_rate_per_hour else float(employee.hourly_rate or 0)
                    payroll.overtime_pay = payroll.overtime_hours * ot_rate
                
                # Update OT Amount Override (Prioritize over calculation)
                if 'ot_amount' in data:
                    # Treat 'ot_amount' from frontend as the override amount
                    # Use a new field ot_override_amount for explicit storage
                    payroll.ot_override_amount = float(data['ot_amount'])
                    
                    # Also update final pay if override is active (>0) or we want to force it
                    # Logic: If user types 0, it might mean "Reset" or "No OT".
                    # Let's assume if they send it, it's an override.
                    payroll.overtime_pay = float(data['ot_amount'])
                
                # Update CPF Override
                if 'cpf_deduction' in data:
                    payroll.employee_cpf = float(data['cpf_deduction'])
                
                # Update Employer CPF Override (Does NOT affect Net Pay)
                if 'employer_cpf' in data:
                    payroll.employer_cpf = float(data['employer_cpf'])
                
            except ValueError:
                pass # Ignore invalid month/year

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
@require_role(['Super Admin', 'Admin', 'HR Manager', 'Tenant Admin'])
def payroll_preview_api():
    """API endpoint to preview payroll data for selected month"""
    try:
        month = request.args.get('month', type=int)
        year = request.args.get('year', type=int)
        company_id = request.args.get('company_id', type=str)
        employee_id = request.args.get('employee_id', type=int)

        if not month or not year:
            return jsonify({
                'success': False,
                'message': 'Month and year are required'
            }), 400

        if not company_id and not employee_id:
            return jsonify({
                'success': False,
                'message': 'Company ID is required'
            }), 400

        # Calculate pay period
        from calendar import monthrange
        pay_period_start = date(year, month, 1)
        last_day = monthrange(year, month)[1]
        pay_period_end = date(year, month, last_day)

        # Get active employees
        query = Employee.query.filter_by(is_active=True)
        
        if employee_id:
            query = query.filter_by(id=employee_id)
        elif company_id:
            query = query.filter_by(company_id=company_id)
            
        employees = query.all()

        employee_data = []
        for emp in employees:
            # Get payroll config
            config = emp.payroll_config

            # Calculate fixed allowances
            allowance_1 = float(config.allowance_1_amount) if config else 0
            allowance_2 = float(config.allowance_2_amount) if config else 0
            allowance_3 = float(config.allowance_3_amount) if config else 0
            allowance_4 = float(config.allowance_4_amount) if config else 0
            fixed_allowances = allowance_1 + allowance_2 + allowance_3 + allowance_4

            # ---------------------------------------------------------
            # DATA SOURCES STRATEGY:
            # 1. Calculated (Source 2) - Always calculates "Original"
            # 2. Override (Source 1) - Checks for manual override in DB
            # ---------------------------------------------------------
            
            # Step 1: Calculate "Original" from Daily Summaries (Live Data)
            ot_summaries = OTDailySummary.query.filter_by(
                employee_id=emp.id,
                status='Approved'
            ).filter(
                extract('month', OTDailySummary.ot_date) == month,
                extract('year', OTDailySummary.ot_date) == year
            ).all()

            calculated_ot_hours = sum(float(s.ot_hours or 0) for s in ot_summaries)
            calculated_ot_amount = sum(float(s.ot_amount or 0) for s in ot_summaries)
            calculated_ot_allowances = sum(float(s.total_allowances or 0) for s in ot_summaries)
            
            payroll_record = Payroll.query.filter_by(
                employee_id=emp.id,
                pay_period_start=pay_period_start,
                pay_period_end=pay_period_end
            ).first()
            
            total_ot_hours = calculated_ot_hours
            ot_amount = calculated_ot_amount # Default to calculated
            ot_allowances = calculated_ot_allowances
            
            ot_override_amount = 0.0
            
            cpf_override = None 
            employer_cpf = 0.0 
            
            if payroll_record:
                # Get Override Amount
                ot_override_amount = float(payroll_record.ot_override_amount or 0)
                
                # Logic: If override > 0, use it. Else use calculated.
                # Note: User requirement "if the over ride amount is grated than zero it should take the overided amount else the original calculated amount"
                if ot_override_amount > 0:
                    ot_amount = ot_override_amount
                    # Note: We don't automatically adjust hours if amount is overridden, 
                    # but we could keep calculated hours or use stored hours if we wanted.
                    # For now, keeping calculated hours is safer for display unless explicitly overridden too.
                
                # Use persisted CPF only if record is finalized
                if payroll_record.status in ['Approved', 'Paid']:
                    if payroll_record.employee_cpf is not None:
                         cpf_override = float(payroll_record.employee_cpf)
                    if payroll_record.employer_cpf is not None:
                        employer_cpf = float(payroll_record.employer_cpf)
                        
                # Note: For 'Draft' or 'Generated', we intentionally IGNORE the stored 
                # Payroll.employee_cpf/employer_cpf and fall through to use the
                # PayrollConfiguration (Master) values below. This ensures that
                # clicking "Load Data" always reflects the latest Configuration.
                        
                # If record is finalized (Approved/Paid), strictly use stored values?
                # Actually, user said "regenerate whenever", implying Draft should always auto-update calculated part.
                # If finalized, we probably shouldn't change it.
                if payroll_record.status in ['Approved', 'Paid']:
                     # For finalized records, stick to what's in DB completely
                     total_ot_hours = float(payroll_record.overtime_hours or 0)
                     ot_amount = float(payroll_record.overtime_pay or 0)
                     ot_override_amount = float(payroll_record.ot_override_amount or 0) # Keep historical override logic if needed

            # Total Allowances = Fixed + OT Allowances
            total_allowances = fixed_allowances + ot_allowances

            # Get attendance data for the month (only for days worked count)
            attendance_records = Attendance.query.filter_by(
                employee_id=emp.id
            ).filter(
                Attendance.date.between(pay_period_start, pay_period_end)
            ).all()

            attendance_days = len(attendance_records)

            # OT Rate is just for display/reference now (taken from config or calculated average)
            # Since amount is sum of daily variable rates, a single rate might be misleading but we keep it for UI
            ot_rate = float(config.ot_rate_per_hour) if config and config.ot_rate_per_hour else float(emp.hourly_rate or 0)

            # Calculate gross salary
            # Use Payroll Configuration
            basic_salary = float(emp.payroll_config.basic_salary or 0) if emp.payroll_config else 0.0
            gross_salary = basic_salary + total_allowances + ot_amount

            # Calculate CPF deductions
            if cpf_override is not None:
                cpf_deduction = cpf_override
            else:
                # Use Configuration values as default
                if config and config.employee_cpf is not None:
                    cpf_deduction = float(config.employee_cpf)
                else:
                    cpf_deduction = 0.0
                
                # Also ensure Employer CPF is set from config if not overridden (and not already set by payroll record)
                # Note: We check if it's already set (from Approved/Paid record above). 
                # If it's 0.0 (default) or we are in Draft mode (where we ignored persisted values), we load from config.
                if payroll_record and payroll_record.status in ['Approved', 'Paid'] and payroll_record.employer_cpf is not None:
                     pass # Already handled above
                elif config and config.employer_cpf is not None:
                     employer_cpf = float(config.employer_cpf)

            # Calculate net salary
            total_deductions = cpf_deduction
            net_salary = gross_salary - total_deductions

            # Validation checks
            has_bank_info = bool(emp.bank_account and emp.bank_name)
            
            # Calculate attendance rate
            # Assuming standard 22 working days for simple percentage if no schedule
            working_days_in_month = 22 # Default approximation or calculate from schedule
            attendance_rate = min(100, int((attendance_days / working_days_in_month) * 100)) if working_days_in_month > 0 else 0

            employee_data.append({
                'id': emp.id,
                'employee_id': emp.employee_id,
                'name': f"{emp.first_name} {emp.last_name}",
                'designation': emp.designation.name if emp.designation else 'Employee',
                'basic_salary': basic_salary,
                'allowance_1': allowance_1,
                'allowance_2': allowance_2,
                'allowance_3': allowance_3,
                'allowance_4': allowance_4,
                'total_allowances': total_allowances,
                'ot_hours': total_ot_hours,
                'ot_rate': ot_rate,
                'ot_amount': ot_amount,
                'ot_override_amount': ot_override_amount,
                'original_ot_amount': calculated_ot_amount,
                'attendance_days': attendance_days,
                'attendance_rate': attendance_rate,
                'gross_salary': gross_salary,
                'cpf_deduction': cpf_deduction,
                'employer_cpf': employer_cpf,
                'total_deductions': total_deductions,
                'net_salary': net_salary,
                'has_bank_info': has_bank_info,
                'profile_image': emp.profile_image_path or None
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
@require_login
def payroll_payslip(payroll_id):
    """View/download payslip"""
    payroll = Payroll.query.get_or_404(payroll_id)

    # Check permission
    if (current_user.role.name if current_user.role else None) == 'Employee':
        if not (hasattr(current_user, 'employee_profile')
                and current_user.employee_profile.id == payroll.employee_id):
            flash('You do not have permission to view this payslip.', 'error')
            return redirect(url_for('dashboard'))
    elif (current_user.role.name if current_user.role else None) == 'Manager':
        if not (hasattr(current_user, 'employee_profile')
                and payroll.employee.manager_id
                == current_user.employee_profile.id):
            flash('You do not have permission to view this payslip.', 'error')
            return redirect(url_for('dashboard'))
    elif (current_user.role.name if current_user.role else None) in ['Admin', 'Super Admin']:
        # Admin and Super Admin: Can view all payslips
        pass  # No restriction - they can see all

    # Prepare data for template
    employee = payroll.employee
    company = employee.company
    if not company:
        # Fallback to organization if company is not linked directly, though unusual for payslip context
        company = employee.organization
        
    if not company:
        flash('Employee is not associated with a valid company.', 'error')
        return redirect(url_for('dashboard'))
    
    # Calculate pay date (end of pay period)
    pay_date = payroll.pay_period_end.strftime('%d-%b-%Y')
    
    # Calculate worked days (Paid days)
    # Use payroll.days_worked if available, otherwise calculate from date range
    from core.utils import calculate_working_days
    if payroll.days_worked:
        paid_days = payroll.days_worked
    else:
        # Fallback
        paid_days = calculate_working_days(payroll.pay_period_start, payroll.pay_period_end)
        
    lop_days = payroll.lop_days or 0
    
    # Get Employee Bank Info (prefer EmployeeBankInfo model if exists, else Employee columns)
    bank_name = employee.bank_name or 'N/A'
    bank_account = employee.bank_account or 'N/A'
    if hasattr(employee, 'bank_info') and employee.bank_info:
        bank_name = employee.bank_info.bank_name or bank_name
        bank_account = employee.bank_info.bank_account_number or bank_account

    # Prepare earnings breakdown
    earnings_breakdown = []
    
    # 1. Basic Pay
    earnings_breakdown.append({
        'label': 'Basic Salary', 
        'amount': f"{float(payroll.basic_pay):,.2f}"
    })

    # 2. Allowances from Configuration
    config = employee.payroll_config
    total_config_allowances = 0
    if config:
        # Helper to add allowance if > 0
        def add_allowance(name, amount):
            if amount and amount > 0:
                earnings_breakdown.append({
                    'label': name, 
                    'amount': f"{float(amount):,.2f}"
                })
                return float(amount)
            return 0

        total_config_allowances += add_allowance(config.allowance_1_name or 'Transport Allowance', config.allowance_1_amount)
        total_config_allowances += add_allowance(config.allowance_2_name or 'Housing Allowance', config.allowance_2_amount)
        total_config_allowances += add_allowance(config.allowance_3_name or 'Meal Allowance', config.allowance_3_amount)
        total_config_allowances += add_allowance(config.allowance_4_name or 'Other Allowance', config.allowance_4_amount)
        total_config_allowances += add_allowance(config.levy_allowance_name or 'Levy Allowance', config.levy_allowance_amount)

    # 3. Overtime Pay
    if payroll.overtime_pay and payroll.overtime_pay > 0:
         earnings_breakdown.append({
            'label': 'Overtime Pay', 
            'amount': f"{float(payroll.overtime_pay):,.2f}"
        })

    # 4. Bonuses
    if payroll.bonuses and payroll.bonuses > 0:
         earnings_breakdown.append({
            'label': 'Bonuses', 
            'amount': f"{float(payroll.bonuses):,.2f}"
        })
        
    # 5. Any other difference in allowances (e.g. from OT daily allowances)
    # Total recorded allowances in payroll vs what we found in config
    recorded_allowances = float(payroll.allowances or 0)
    remaining_allowances = recorded_allowances - total_config_allowances
    if remaining_allowances > 0.01: # Tolerance for float comparison
        earnings_breakdown.append({
            'label': 'Additional Allowances', 
            'amount': f"{remaining_allowances:,.2f}"
        })

    # Legacy mappings for template compatibility (if needed, though we will update template)
    earnings = {
        'basic': f"{float(payroll.basic_pay):,.2f}",
        'hra': "0.00", 
        'transport': "0.00",
        'other': f"{float(payroll.allowances + payroll.bonuses + payroll.overtime_pay):,.2f}",
        'breakdown': earnings_breakdown, # Passing the new list
        # Legacy keys for backward compatibility
        'regular_pay_rate': f"{float(employee.basic_salary):,.2f}",
        'regular_pay_amount': f"{float(payroll.basic_pay):,.2f}",
        'overtime_pay_rate': f"{float(employee.hourly_rate or 0):,.2f}" if employee.hourly_rate else "0.00",
        'overtime_hours': f"{float(payroll.overtime_hours):,.2f}",
        'overtime_amount': f"{float(payroll.overtime_pay):,.2f}",
        'holiday_pay': "0.00",
        'vacation_pay': "0.00",
        'others': f"{float(payroll.allowances + payroll.bonuses):,.2f}"
    }

    # Prepare deductions data (Mapped for payslip_preview.html)
    deductions = {
        'pf': f"{float(payroll.employee_cpf):,.2f}", # Renamed/Label update handled in template, this key is for data
        'cpf': f"{float(payroll.employee_cpf):,.2f}", # New key for clarity
        'tax': "0.00", # Set to 0 or remove from template display
        # Legacy keys
        'income_tax': f"{float(payroll.income_tax):,.2f}",
        'medical': "0.00",
        'life_insurance': "0.00", 
        'provident_fund': f"{float(payroll.employee_cpf):,.2f}",
        'others': f"{float(payroll.other_deductions):,.2f}"
    }

    # Prepare Employer Contributions (Not Deducted)
    employer_contributions = {
        'cpf': f"{float(payroll.employer_cpf or 0):,.2f}"
    }

    # Prepare employee data
    employee_data = {
        'name': f"{employee.first_name} {employee.last_name}",
        'employee_code': employee.employee_id,
        'joining_date': employee.hire_date.strftime('%d-%b-%Y') if employee.hire_date else 'N/A',
        'nric': employee.nric, # Used as PAN replacement if needed
        'pan_number': employee.nric or 'N/A', # Using NRIC as PAN placeholder
        'esi_number': 'N/A', # Placeholder
        'pf_number': employee.cpf_account or 'N/A',
        'nationality': employee.nationality or 'N/A',
        'designation': employee.designation.name if employee.designation else 'N/A',
        'department': employee.department if employee.department else 'N/A',
        'location': employee.location or 'Singapore', # Default to Singapore if empty
        'bank_name': bank_name,
        'bank_account': bank_account
    }

    # Prepare company data
    company_data = {
        'name': company.name,
        'address': company.address or 'N/A',
        'uen': company.uen or 'N/A'
    }

    # Prepare payroll summary
    from core.utils import num_to_words
    net_pay_val = float(payroll.net_pay)
    
    payroll_data = {
        'pay_date': pay_date,
        'period': f"{payroll.pay_period_start.strftime('%B %Y')}",
        'lop_days': lop_days,
        'paid_days': paid_days,
        'total_earnings': f"{float(payroll.gross_pay):,.2f}",
        'total_deductions': f"{float(payroll.employee_cpf + payroll.income_tax + payroll.other_deductions):,.2f}",
        'net_pay': f"{net_pay_val:,.2f}",
        'net_pay_words': num_to_words(net_pay_val)
    }


    # Check for default template
    # 1. Company level default
    template = PayslipTemplate.query.filter_by(
        company_id=employee.company_id,
        is_default=True
    ).first()
    
    # 2. Tenant level default (if no company specific)
    if not template and company.tenant_id:
        template = PayslipTemplate.query.filter_by(
            tenant_id=company.tenant_id,
            company_id=None,
            is_default=True
        ).first()

    if template:
        # Dynamic injection of 'employer_contributions' section
        layout_config = list(template.layout_config) # Copy to avoid mutating DB object in session if that happens
        if 'employer_contributions' not in layout_config:
            # Insert before earnings_table if exists, else append
            if 'earnings_table' in layout_config:
                idx = layout_config.index('earnings_table')
                layout_config.insert(idx, 'employer_contributions')
            else:
                layout_config.append('employer_contributions')
        
        # [NEW] Resolve Asset URLs
        def get_asset_url(file_id, legacy_path):
             if file_id:
                  try:
                       from services.file_service import FileService
                       return FileService.get_file_url(file_id)
                  except:
                       pass
             if legacy_path:
                  if legacy_path.startswith('http'): return legacy_path
                  if 'tenants/' in legacy_path:
                       try:
                           from services.s3_service import S3Service
                           return S3Service().generate_presigned_url(legacy_path)
                       except:
                           pass
                  return url_for('static', filename=legacy_path)
             return None

        logo_path = get_asset_url(template.logo_id, template.logo_path)
        left_logo_path = get_asset_url(template.left_logo_id, template.left_logo_path)
        right_logo_path = get_asset_url(template.right_logo_id, template.right_logo_path)
        watermark_path = get_asset_url(template.watermark_id, template.watermark_path)
        footer_image_path = get_asset_url(template.footer_image_id, template.footer_image_path)
        header_image_path = get_asset_url(template.header_image_id, template.header_image_path) #[NEW]

        return render_template('payroll/payslip_preview.html',
                             layout_config=layout_config,
                             logo_path=logo_path,
                             left_logo_path=left_logo_path,
                             right_logo_path=right_logo_path,
                             header_image_path=header_image_path, #[NEW]
                             watermark_path=watermark_path,
                             footer_image_path=footer_image_path,
                             payroll=payroll_data,
                             employee=employee_data,
                             company=company_data,
                             earnings=earnings,
                             deductions=deductions,
                             employer_contributions=employer_contributions)

    # 6. Fetch Payslip Logo (Tenant Configuration)
    logo_url = None
    try:
        from core.models import TenantConfiguration
        from services.file_service import FileService
        from services.s3_service import S3Service
        
        # Determine Tenant ID
        tenant_id = None
        if company and company.tenant_id:
            tenant_id = company.tenant_id
        
        if tenant_id:
            # Fetch Config
            tenant_config = TenantConfiguration.query.filter_by(tenant_id=tenant_id).first()
            if tenant_config:
                # 1. Try FileStorage [NEW]
                if tenant_config.payslip_logo_id:
                    logo_url = FileService.get_file_url(tenant_config.payslip_logo_id)
                
                # 2. Fallback to Legacy Path
                elif tenant_config.payslip_logo_path:
                    if 'tenant_logos/' in tenant_config.payslip_logo_path or tenant_config.payslip_logo_path.startswith('tenants/'):
                        s3 = S3Service()
                        logo_url = s3.generate_presigned_url(tenant_config.payslip_logo_path)
                    else:
                        logo_url = url_for('static', filename=tenant_config.payslip_logo_path.replace('\\', '/'))
    except Exception as e:
        print(f"Error loading payslip logo: {e}")

    return render_template('payroll/payslip.html',
                         payroll=payroll_data,
                         employee=employee_data,
                         company=company_data,
                         earnings=earnings,
                         deductions=deductions,
                         employer_contributions=employer_contributions,
                         logo_url=logo_url)



@app.route('/payroll/<int:payroll_id>/approve', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Tenant Admin', 'HR Manager'])
def payroll_approve(payroll_id):
    """Approve payroll record (Draft -> Approved)"""
    payroll = Payroll.query.get_or_404(payroll_id)

    try:
        if payroll.status == 'Draft':
            payroll.status = 'Approved'
            db.session.commit()

            # ✅ Create EmployeeDocument record when approved so payslip appears in Documents menu
            try:
                existing_doc = EmployeeDocument.query.filter_by(
                    employee_id=payroll.employee_id,
                    document_type='Salary Slip',
                    month=payroll.pay_period_start.month,
                    year=payroll.pay_period_start.year
                ).first()

                if not existing_doc:
                    salary_slip_doc = EmployeeDocument(
                        employee_id=payroll.employee_id,
                        document_type='Salary Slip',
                        file_path=f'payroll/{payroll.id}',  # Virtual path for payroll view
                        issue_date=datetime.now(),
                        month=payroll.pay_period_start.month,
                        year=payroll.pay_period_start.year,
                        description=f"Salary Slip for {payroll.pay_period_start.strftime('%B %Y')}",
                        uploaded_by=current_user.id if current_user.is_authenticated else None
                    )
                    db.session.add(salary_slip_doc)
                    db.session.commit()
            except Exception as doc_error:
                # Log but don't fail payroll approval if document creation fails
                print(f"Warning: Could not create salary slip document: {doc_error}")

            return jsonify({'success': True, 'message': 'Payroll approved successfully'}), 200
        else:
            return jsonify({'success': False, 'message': f'Cannot approve. Payroll status is {payroll.status}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/payroll/<int:payroll_id>/finalize', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Tenant Admin', 'HR Manager'])
def payroll_finalize(payroll_id):
    """Finalize payroll record (Approved -> Finalized)"""
    payroll = Payroll.query.get_or_404(payroll_id)

    try:
        if payroll.status == 'Approved':
            payroll.status = 'Finalized'
            payroll.finalized_at = datetime.now()
            payroll.finalized_by = current_user.username if hasattr(current_user, 'username') else str(current_user.id)
            db.session.commit()

            # ✅ Create EmployeeDocument record so payslip appears in Documents menu
            try:
                existing_doc = EmployeeDocument.query.filter_by(
                    employee_id=payroll.employee_id,
                    document_type='Salary Slip',
                    month=payroll.pay_period_start.month,
                    year=payroll.pay_period_start.year
                ).first()

                if not existing_doc:
                    salary_slip_doc = EmployeeDocument(
                        employee_id=payroll.employee_id,
                        document_type='Salary Slip',
                        file_path=f'payroll/{payroll.id}',  # Virtual path for payroll view
                        issue_date=datetime.now(),
                        month=payroll.pay_period_start.month,
                        year=payroll.pay_period_start.year,
                        description=f"Salary Slip for {payroll.pay_period_start.strftime('%B %Y')}",
                        uploaded_by=current_user.id if current_user.is_authenticated else None
                    )
                    db.session.add(salary_slip_doc)
                    db.session.commit()
            except Exception as doc_error:
                # Log but don't fail payroll finalization if document creation fails
                print(f"Warning: Could not create salary slip document: {doc_error}")

            return jsonify({'success': True, 'message': 'Payroll finalized successfully'}), 200
        else:
            return jsonify({'success': False, 'message': f'Cannot finalize. Payroll must be Approved. Current status: {payroll.status}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


# Attendance Management Routes
@app.route('/attendance', endpoint='attendance_list_view')
@require_login
def attendance_list():
    """List attendance records with comprehensive filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Filter Parameters
    date_range = request.args.get('date_range', 'month')
    employee_search = request.args.get('employee', '')
    status = request.args.get('status', '', type=str)
    department = request.args.get('department', '', type=str)
    designation_id = request.args.get('designation_id', '', type=str)
    employment_type = request.args.get('employment_type', '', type=str)
    company_id = request.args.get('company_id', '', type=str)

    query = Attendance.query.join(Employee)

    # 1. Date Range Filtering
    from core.utils import get_current_user_timezone
    import pytz
    user_tz = pytz.timezone(get_current_user_timezone())
    today = datetime.now(pytz.utc).astimezone(user_tz).date()
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    if date_range == 'today':
        query = query.filter(Attendance.date == today)
    elif date_range == 'week':
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        query = query.filter(Attendance.date.between(start_week, end_week))
    elif date_range == 'last_month':
        first_of_this_month = today.replace(day=1)
        last_day_of_last_month = first_of_this_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        query = query.filter(Attendance.date.between(first_day_of_last_month, last_day_of_last_month))
    elif date_range == 'custom' and start_date and end_date:
        try:
            s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date.between(s_date, e_date))
        except (ValueError, TypeError):
            # Fallback to current month if dates are invalid
            start_month = today.replace(day=1)
            _, last_day = calendar.monthrange(today.year, today.month)
            end_month = today.replace(day=last_day)
            query = query.filter(Attendance.date.between(start_month, end_month))
    else:  # Default to month
        start_month = today.replace(day=1)
        _, last_day = calendar.monthrange(today.year, today.month)
        end_month = today.replace(day=last_day)
        query = query.filter(Attendance.date.between(start_month, end_month))

    # 2. Employee Search
    if employee_search:
        if employee_search.isdigit():
            query = query.filter(Attendance.employee_id == int(employee_search))
        else:
            query = query.filter(
                db.or_(
                    Employee.first_name.ilike(f'%{employee_search}%'),
                    Employee.last_name.ilike(f'%{employee_search}%')
                )
            )

    # 3. New Filters
    if status:
        query = query.filter(Attendance.status == status)
    
    if department:
        query = query.filter(Employee.department == department)

    if designation_id and designation_id.isdigit():
        query = query.filter(Employee.designation_id == int(designation_id))

    if employment_type:
        query = query.filter(Employee.employment_type == employment_type)

    if company_id:
        try:
            query = query.filter(Employee.company_id == company_id)
        except Exception:
            pass

    # 4. Role-based filtering
    user_role = current_user.role.name if current_user.role else None
    accessible_companies = []

    if user_role in ['User', 'Employee'] and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        # Employee: Only their own attendance
        employee_id = current_user.employee_profile.id
        query = query.filter(Attendance.employee_id == employee_id)

    elif user_role == 'Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        # Manager: Their own attendance + their team's attendance
        manager_id = current_user.employee_profile.id
        query = query.filter(
            db.or_(
                Attendance.employee_id == manager_id,  # Manager's own attendance
                Employee.manager_id == manager_id      # Team's attendance
            )
        )

    elif user_role == 'Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        # Admin: Only their own attendance (as per requirement)
        admin_id = current_user.employee_profile.id
        query = query.filter(Attendance.employee_id == admin_id)
        # Admin can view all companies in dropdown
        accessible_companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()

    elif user_role in ['HR Manager', 'Tenant Admin']:
        # HR Manager / Tenant Admin: Scoped by accessible companies
        accessible_companies = current_user.get_accessible_companies()
        company_ids = [c.id for c in accessible_companies]
        query = query.filter(Employee.company_id.in_(company_ids))

    elif user_role == 'Super Admin':
        # Super Admin: Can see all attendance records
        accessible_companies = Company.query.filter_by(is_active=True).order_by(Company.name).all()

    # Pagination
    attendance_records = query.order_by(Attendance.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False)

    # Process records to add display times converting to employee's timezone
    for record in attendance_records.items:
        if record.employee:
            # Prefer clock_in_time (DateTime) as it's our standardized UTC source
            clock_in_src = record.clock_in_time if record.clock_in_time else record.clock_in
            if clock_in_src:
                record.clock_in_display = get_employee_local_time(
                    record.employee, clock_in_src, record.date)
            else:
                record.clock_in_display = None
            
            # Prefer clock_out_time (DateTime)
            clock_out_src = record.clock_out_time if record.clock_out_time else record.clock_out
            if clock_out_src:
                record.clock_out_display = get_employee_local_time(
                    record.employee, clock_out_src, record.date)
            else:
                record.clock_out_display = None
        else:
            record.clock_in_display = None
            record.clock_out_display = None

    # Fetch related OT Daily Summaries (Existing Logic)
    ot_summaries_map = {}
    if attendance_records.items:
        keys = [(r.employee_id, r.date) for r in attendance_records.items]
        ot_summaries = OTDailySummary.query.filter(
            tuple_(OTDailySummary.employee_id, OTDailySummary.ot_date).in_(keys)
        ).all()
        for ot in ot_summaries:
            ot_summaries_map[(ot.employee_id, ot.ot_date)] = ot

    # --- Load Master Data for Filters ---
    
    # Departments
    master_depts = [d.name for d in Department.query.filter_by(is_active=True).order_by(Department.name).all()]
    existing_depts = [d[0] for d in db.session.query(Employee.department).distinct().filter(Employee.department.isnot(None)).all()]
    all_departments = sorted(list(set(master_depts + existing_depts)))
    
    # Designations
    all_designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
    
    # Employment Types
    all_employment_types = [t[0] for t in db.session.query(Employee.employment_type).distinct().filter(Employee.employment_type.isnot(None)).all()]
    
    # Status Options
    status_options = [
        {'value': 'Present', 'label': 'Present'},
        {'value': 'Incomplete', 'label': 'Incomplete'},
        {'value': 'Absent', 'label': 'Absent'},
        {'value': 'Leave', 'label': 'Leave'}
    ]

    return render_template('attendance/list.html',
                           attendance_records=attendance_records,
                           current_filters={
                               'date_range': date_range,
                               'start_date': start_date,
                               'end_date': end_date,
                               'employee': employee_search,
                               'status': status,
                               'department': department,
                               'designation_id': int(designation_id) if designation_id and designation_id.isdigit() else '',
                               'employment_type': employment_type,
                               'company_id': company_id
                           },
                           filter_options={
                               'departments': all_departments,
                               'designations': all_designations,
                               'companies': accessible_companies,
                               'employment_types': all_employment_types,
                               'status_options': status_options
                           },
                            ot_summaries_map=ot_summaries_map,
                            per_page=per_page)


@app.route('/attendance/export', endpoint='attendance_export')
@require_login
def attendance_export():
    """Export attendance records to CSV based on current filters"""
    # Filter Parameters (Same as list view)
    date_range = request.args.get('date_range', 'month')
    employee_search = request.args.get('employee', '')
    status = request.args.get('status', '', type=str)
    department = request.args.get('department', '', type=str)
    designation_id = request.args.get('designation_id', '', type=str)
    employment_type = request.args.get('employment_type', '', type=str)
    company_id = request.args.get('company_id', '', type=str)

    query = Attendance.query.join(Employee)

    # 1. Date Range Filtering
    from core.utils import get_current_user_timezone
    import pytz
    user_tz = pytz.timezone(get_current_user_timezone())
    today = datetime.now(pytz.utc).astimezone(user_tz).date()
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    if date_range == 'today':
        query = query.filter(Attendance.date == today)
    elif date_range == 'week':
        start_week = today - timedelta(days=today.weekday())
        end_week = start_week + timedelta(days=6)
        query = query.filter(Attendance.date.between(start_week, end_week))
    elif date_range == 'last_month':
        first_of_this_month = today.replace(day=1)
        last_day_of_last_month = first_of_this_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)
        query = query.filter(Attendance.date.between(first_day_of_last_month, last_day_of_last_month))
    elif date_range == 'custom' and start_date and end_date:
        try:
            s_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            e_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Attendance.date.between(s_date, e_date))
        except (ValueError, TypeError):
            start_month = today.replace(day=1)
            _, last_day = calendar.monthrange(today.year, today.month)
            end_month = today.replace(day=last_day)
            query = query.filter(Attendance.date.between(start_month, end_month))
    else:  # Default to month
        start_month = today.replace(day=1)
        _, last_day = calendar.monthrange(today.year, today.month)
        end_month = today.replace(day=last_day)
        query = query.filter(Attendance.date.between(start_month, end_month))

    # 2. Employee Search
    if employee_search:
        if employee_search.isdigit():
            query = query.filter(Attendance.employee_id == int(employee_search))
        else:
            query = query.filter(
                db.or_(
                    Employee.first_name.ilike(f'%{employee_search}%'),
                    Employee.last_name.ilike(f'%{employee_search}%')
                )
            )

    # 3. New Filters
    if status:
        query = query.filter(Attendance.status == status)
    
    if department:
        query = query.filter(Employee.department == department)

    if designation_id and designation_id.isdigit():
        query = query.filter(Employee.designation_id == int(designation_id))

    if employment_type:
        query = query.filter(Employee.employment_type == employment_type)

    if company_id:
        try:
            query = query.filter(Employee.company_id == company_id)
        except Exception:
            pass

    # 4. Role-based filtering
    user_role = current_user.role.name if current_user.role else None

    if user_role in ['User', 'Employee'] and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        employee_id = current_user.employee_profile.id
        query = query.filter(Attendance.employee_id == employee_id)

    elif user_role == 'Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        manager_id = current_user.employee_profile.id
        query = query.filter(
            db.or_(
                Attendance.employee_id == manager_id,
                Employee.manager_id == manager_id
            )
        )

    elif user_role == 'Admin' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        admin_id = current_user.employee_profile.id
        query = query.filter(Attendance.employee_id == admin_id)

    elif user_role in ['HR Manager', 'Tenant Admin']:
        accessible_companies = current_user.get_accessible_companies()
        company_ids = [c.id for c in accessible_companies]
        query = query.filter(Employee.company_id.in_(company_ids))

    # Fetch all records (no pagination)
    records = query.order_by(Attendance.date.desc()).all()

    # Prepare data for CSV
    data = []
    for record in records:
        employee = record.employee
        
        # Format times
        clock_in_str = ''
        clock_out_str = ''
        
        if employee:
            # Re-use logic to get displayed time using employee's timezone
            clock_in_src = record.clock_in_time if record.clock_in_time else record.clock_in
            if clock_in_src:
                dt = get_employee_local_time(employee, clock_in_src, record.date)
                clock_in_str = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ''
            
            clock_out_src = record.clock_out_time if record.clock_out_time else record.clock_out
            if clock_out_src:
                dt = get_employee_local_time(employee, clock_out_src, record.date)
                clock_out_str = dt.strftime('%Y-%m-%d %H:%M:%S') if dt else ''

        data.append({
            'Employee ID': employee.employee_id if employee else '',
            'Name': f"{employee.first_name} {employee.last_name}" if employee else 'Unknown',
            'Date': record.date.strftime('%Y-%m-%d'),
            'Status': record.status,
            'Sub Status': record.sub_status or '',
            'Clock In': clock_in_str,
            'Clock Out': clock_out_str,
            'Regular Hours': f"{record.regular_hours:.2f}" if record.regular_hours else '0.00',
            'Overtime Hours': f"{record.overtime_hours:.2f}" if record.overtime_hours else '0.00',
            'Total Hours': f"{record.total_hours:.2f}" if record.total_hours else '0.00'
        })

    filename = f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    headers = ['Employee ID', 'Name', 'Date', 'Status', 'Sub Status', 'Clock In', 'Clock Out', 'Regular Hours', 'Overtime Hours', 'Total Hours']
    
    return export_to_csv(data, filename, headers)


@app.route('/attendance/mark', methods=['GET', 'POST'])
@require_login
def attendance_mark():
    """Mark attendance (for employees)"""
    employee_profile = current_user.employee_profile if hasattr(current_user, 'employee_profile') else None
    
    from core.utils import get_current_user_timezone
    user_tz_str = get_current_user_timezone()
    company_timezone = user_tz_str
    
    try:
        tz = pytz.timezone(user_tz_str)
        utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
        local_now = utc_now.astimezone(tz)
        offset_seconds = local_now.utcoffset().total_seconds()
        hours = int(offset_seconds // 3600)
        minutes = int((offset_seconds % 3600) // 60)
        timezone_offset = f"{'+' if hours >= 0 else '-'}{abs(hours):02d}:{abs(minutes):02d}"
    except Exception as e:
        print(f"Error with timezone '{user_tz_str}': {e}. Defaulting to UTC.")
        local_now = datetime.utcnow()

    company_local_date = local_now.date()
    company_local_date_str = company_local_date.strftime("%A, %B %d, %Y")

    if request.method == 'POST':
        try:
            if not employee_profile:
                flash('Employee profile required for attendance marking', 'error')
                return redirect(url_for('dashboard'))

            employee_id = employee_profile.id
            action = request.form.get('action')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            remarks = request.form.get('remarks')

            if action == 'clock_in':
                success, message, _ = AttendanceService.clock_in(
                    employee_id, latitude=latitude, longitude=longitude, remarks=remarks
                )
            elif action == 'clock_out':
                success, message, _ = AttendanceService.clock_out(
                    employee_id, latitude=latitude, longitude=longitude, remarks=remarks
                )
            elif action == 'break_start':
                success, message, _ = AttendanceService.start_break(
                    employee_id, remarks=remarks
                )
            elif action == 'break_end':
                success, message, _ = AttendanceService.end_break(
                    employee_id, remarks=remarks
                )
            else:
                flash(f'Unknown action: {action}', 'error')
                return redirect(url_for('attendance_mark'))

            if success:
                flash(message, 'success')
            else:
                flash(message, 'error')

            return redirect(url_for('attendance_mark'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error marking attendance: {str(e)}', 'error')

    today_attendance = None
    recent_records = []
    if employee_profile:
        # Today's attendance
        today_attendance = Attendance.query.filter_by(
            employee_id=employee_profile.id,
            date=company_local_date
        ).first()

        if today_attendance:
            # Auto-calculate if clock_out exists but stats are zero (legacy correction)
            if today_attendance.clock_out and (not today_attendance.total_hours or today_attendance.total_hours == 0):
                # Calculate hours
                clock_in_dt = datetime.combine(today_attendance.date, today_attendance.clock_in)
                clock_out_dt = datetime.combine(today_attendance.date, today_attendance.clock_out)
                total_seconds = (clock_out_dt - clock_in_dt).total_seconds()

                # Subtract break time if applicable
                if today_attendance.break_start and today_attendance.break_end:
                    break_start_dt = datetime.combine(today_attendance.date, today_attendance.break_start)
                    break_end_dt = datetime.combine(today_attendance.date, today_attendance.break_end)
                    break_seconds = (break_end_dt - break_start_dt).total_seconds()
                    total_seconds -= break_seconds

                total_hours = total_seconds / 3600
                
                # Get standard working hours from employee profile or default to 8
                standard_hours = 8.0
                if employee_profile.working_hours and employee_profile.working_hours.hours_per_day:
                    standard_hours = float(employee_profile.working_hours.hours_per_day)

                if total_hours > standard_hours:
                    today_attendance.regular_hours = standard_hours
                    today_attendance.overtime_hours = total_hours - standard_hours
                    today_attendance.has_overtime = True
                    today_attendance.overtime_approved = False
                else:
                    today_attendance.regular_hours = total_hours
                    today_attendance.overtime_hours = 0
                    today_attendance.has_overtime = False
                    
                today_attendance.total_hours = total_hours
                db.session.commit()

            clock_in_time = get_employee_local_time(employee_profile, today_attendance.clock_in, today_attendance.date)
            clock_out_time = get_employee_local_time(employee_profile, today_attendance.clock_out, today_attendance.date)
            break_start_time = get_employee_local_time(employee_profile, today_attendance.break_start, today_attendance.date)
            break_end_time = get_employee_local_time(employee_profile, today_attendance.break_end, today_attendance.date)
            
            today_attendance.clock_in_display = clock_in_time.strftime('%H:%M:%S') if clock_in_time else None
            today_attendance.clock_out_display = clock_out_time.strftime('%H:%M:%S') if clock_out_time else None
            today_attendance.break_start_display = break_start_time.strftime('%H:%M:%S') if break_start_time else None
            today_attendance.break_end_display = break_end_time.strftime('%H:%M:%S') if break_end_time else None

        # Fetch last 7 days history (excluding today)
        recent_records = Attendance.query.filter(
            Attendance.employee_id == employee_profile.id,
            Attendance.date < company_local_date,
            Attendance.date >= (company_local_date - timedelta(days=7))
        ).order_by(Attendance.date.desc()).all()

        # Format times for recent records
        for record in recent_records:
            r_clock_in = get_employee_local_time(employee_profile, record.clock_in, record.date)
            r_clock_out = get_employee_local_time(employee_profile, record.clock_out, record.date)
            record.clock_in_display = r_clock_in.strftime('%H:%M') if r_clock_in else '-'
            record.clock_out_display = r_clock_out.strftime('%H:%M') if r_clock_out else '-'
            
    else:
        flash('You need an employee profile to mark attendance.', 'warning')

    return render_template('attendance/form.html',
                           today_attendance=today_attendance,
                           recent_records=recent_records,
                           company_timezone=company_timezone,
                           timezone_offset=timezone_offset,
                           company_local_date_str=company_local_date_str)


@app.route('/attendance/correct/<int:attendance_id>', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def attendance_correct(attendance_id):
    """Correct incomplete attendance records (Manager only)"""
    attendance = Attendance.query.get_or_404(attendance_id)

    # Check if manager can access this employee's record
    if (current_user.role.name if current_user.role else None) == 'Manager':
        if not hasattr(current_user, 'employee_profile') or \
           attendance.employee.manager_id != current_user.employee_profile.id:
            flash('Access denied', 'error')
            return redirect(url_for('attendance_list'))

    if request.method == 'POST':
        try:
            # Update attendance record
            clock_out_str = request.form.get('clock_out')
            if clock_out_str:
                from pytz import timezone, utc
                company_tz = timezone(attendance.employee.company.timezone if attendance.employee.company else 'UTC')
                
                # Parse local time from form
                local_time = datetime.strptime(clock_out_str, '%H:%M').time()
                attendance.clock_out = local_time # Local time for legacy
                
                # Create localized datetime and convert to UTC for storage
                local_dt = company_tz.localize(datetime.combine(attendance.date, local_time))
                utc_dt = local_dt.astimezone(utc).replace(tzinfo=None)
                attendance.clock_out_time = utc_dt
                
                # Recalculate hours (logic should be robust)
                if attendance.clock_in_time:
                    # Use standardized UTC timestamps for calculation
                    clock_in_utc = attendance.clock_in_time.replace(tzinfo=utc) if attendance.clock_in_time.tzinfo is None else attendance.clock_in_time
                    total_seconds = (local_dt.astimezone(utc) - clock_in_utc).total_seconds()

                    # Subtract break time if applicable
                    if attendance.break_start and attendance.break_end:
                        # Break times are currently stored as local time objects
                        break_start_dt = company_tz.localize(datetime.combine(attendance.date, attendance.break_start))
                        break_end_dt = company_tz.localize(datetime.combine(attendance.date, attendance.break_end))
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
                attendance.updated_at = datetime.utcnow()

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
        from pytz import timezone, utc
        employee = record.employee
        company = employee.company
        tz_str = company.timezone if company else 'UTC'
        tz = timezone(tz_str)
        
        # Auto-complete with 6 PM clock out or shift end
        default_clock_out = time(18, 0)
        if employee.working_hours and employee.working_hours.end_time:
             default_clock_out = employee.working_hours.end_time
             
        # Localize and convert to UTC
        clock_out_local = tz.localize(datetime.combine(record.date, default_clock_out))
        clock_out_utc = clock_out_local.astimezone(utc).replace(tzinfo=None)
        
        record.clock_out = default_clock_out
        record.clock_out_time = clock_out_utc
        record.status = 'Present'
        record.sub_status = 'Auto Completed'
        record.updated_at = datetime.utcnow()
        
        # Calculate hours using UTC timestamps if possible
        if record.clock_in_time:
            clock_in_utc = record.clock_in_time.replace(tzinfo=utc) if record.clock_in_time.tzinfo is None else record.clock_in_time
            total_seconds = (clock_out_local.astimezone(utc) - clock_in_utc).total_seconds()
            
            # Subtract break time if applicable
            if record.break_start and record.break_end:
                break_start_dt = tz.localize(datetime.combine(record.date, record.break_start))
                break_end_dt = tz.localize(datetime.combine(record.date, record.break_end))
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
    if (current_user.role.name if current_user.role else None) == 'Manager' and hasattr(current_user,
                                                  'employee_profile'):
        query = query.filter(
            Employee.manager_id == current_user.employee_profile.id)

    incomplete_records = query.order_by(Attendance.date.desc()).all()

    return render_template('attendance/incomplete.html',
                           incomplete_records=incomplete_records)


@app.route('/attendance/bulk', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def attendance_mark_absent():
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
            if (current_user.role.name if current_user.role else None) == 'Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
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
                        attendance.clock_in_time = None
                        attendance.clock_out_time = None
                        attendance.sub_status = None
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
    if (current_user.role.name if current_user.role else None) == 'Manager' and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
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
                                                   'employee_profile'):
        query = query.filter(
            Claim.employee_id == current_user.employee_profile.id)
    elif (current_user.role.name if current_user.role else None) == 'Manager' and hasattr(current_user,
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
    if (current_user.role.name if current_user.role else None) == 'Employee' and hasattr(current_user,
                                                   'employee_profile'):
        query = query.filter(
            Appraisal.employee_id == current_user.employee_profile.id)
    elif (current_user.role.name if current_user.role else None) == 'Manager' and hasattr(current_user,
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
    if (current_user.role.name if current_user.role else None) == 'Manager' and hasattr(current_user,
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
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def user_management():
    """User management for admins and HR managers"""
    try:
        # Get users based on role
        if current_user.role and current_user.role.name == 'Super Admin':
            # Super Admin sees all users
            users = User.query.order_by(User.first_name, User.last_name).all()
        else:
            # Admin/HR Manager see only users from their tenant
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

        return render_template('users/list.html', users=users)
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return redirect(url_for('index'))


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





# Mobile API routes for PWA functionality
@app.route('/api/attendance/check')
@require_login
def api_attendance_check():
    """Check today's attendance status for mobile"""
    if not hasattr(current_user, 'employee_profile'):
        return jsonify({'error': 'Employee profile not found'}), 400

    # Get localized today
    import pytz
    from core.utils import get_current_user_timezone, get_employee_local_time
    user_tz = pytz.timezone(get_current_user_timezone())
    today = datetime.now(pytz.utc).astimezone(user_tz).date()

    # Priority 1: Check if there is an open session (Night shift support)
    attendance = Attendance.query.filter_by(
        employee_id=current_user.employee_profile.id, 
        status='Incomplete',
        sub_status='Pending Out'
    ).order_by(Attendance.date.desc()).first()

    # Priority 2: Fallback to today's record
    if not attendance:
        attendance = Attendance.query.filter_by(
            employee_id=current_user.employee_profile.id, date=today).first()

    if attendance:
        # Standardize times for display
        c_in_src = attendance.clock_in_time if attendance.clock_in_time else attendance.clock_in
        c_out_src = attendance.clock_out_time if attendance.clock_out_time else attendance.clock_out
        
        c_in_local = get_employee_local_time(current_user.employee_profile, c_in_src, attendance.date) if c_in_src else None
        c_out_local = get_employee_local_time(current_user.employee_profile, c_out_src, attendance.date) if c_out_src else None

        return jsonify({
            'clocked_in': attendance.clock_in is not None or attendance.clock_in_time is not None,
            'clocked_out': attendance.clock_out is not None and attendance.status == 'Present',
            'on_break': attendance.break_start is not None and attendance.break_end is None,
            'clock_in_time': c_in_local.strftime('%H:%M') if c_in_local else None,
            'clock_out_time': c_out_local.strftime('%H:%M') if c_out_local else None,
            'date': attendance.date.isoformat(),
            'status': attendance.status
        })
    else:
        return jsonify({
            'clocked_in': False,
            'clocked_out': False,
            'on_break': False,
            'date': today.isoformat()
        })


@app.route('/attendance/bulk-manage', methods=['GET', 'POST'])
@require_role(['HR Manager', 'Tenant Admin', 'Super Admin'])
def attendance_bulk_manage():
    """Manage bulk attendance for multiple employees"""
    from datetime import datetime
    
    # Get localized today for default
    from core.utils import get_current_user_timezone
    import pytz
    user_tz = pytz.timezone(get_current_user_timezone())
    today = datetime.now(pytz.utc).astimezone(user_tz).date()
    
    # Get query parameters
    selected_date_str = request.args.get('date', today.isoformat())
    selected_company = request.args.get('company', '')
    
    try:
        filter_date = datetime.fromisoformat(selected_date_str).date()
    except (ValueError, TypeError):
        filter_date = today
    
    selected_date_str = filter_date.isoformat()
    
    # Get available companies using accessible scope (Tenant Admin vs HR Manager)
    available_companies = current_user.get_accessible_companies()
    # Sort by name for dropdown
    available_companies.sort(key=lambda x: x.name)
    
    accessible_company_ids = [c.id for c in available_companies]

    # Get employees for selected company or all accessible companies
    if selected_company:
        try:
            # Check if selected company is accessible
            # We robustly check ID match using string comparison to handle UUIDs
            is_accessible = any(str(c.id) == str(selected_company) for c in available_companies)
            
            if is_accessible:
                 from sqlalchemy.orm import joinedload
                 employees = Employee.query.options(joinedload(Employee.company)).filter_by(
                     company_id=selected_company, 
                     is_active=True
                 ).order_by(Employee.first_name).all()
            else:
                 employees = [] # Not accessible
                 flash('Access Denied to selected company', 'danger')

        except Exception as e:
            employees = []
            flash(f'Error filtering by company: {str(e)}', 'error')
    else:
        # Load employees from ALL accessible companies
        if accessible_company_ids:
            from sqlalchemy.orm import joinedload
            employees = Employee.query.options(joinedload(Employee.company)).filter(
                Employee.company_id.in_(accessible_company_ids),
                Employee.is_active == True
            ).order_by(Employee.first_name).all()
        else:
            employees = []
    
    # Get attendance records for the selected date
    attendance_records = {}
    from core.utils import get_employee_local_time
    for emp in employees:
        att = Attendance.query.filter_by(employee_id=emp.id, date=filter_date).first()
        if att:
            # Prepare localized display times
            clock_in_src = att.clock_in_time if att.clock_in_time else att.clock_in
            if clock_in_src:
                att.clock_in_display = get_employee_local_time(emp, clock_in_src, att.date)
            else:
                att.clock_in_display = None

            clock_out_src = att.clock_out_time if att.clock_out_time else att.clock_out
            if clock_out_src:
                att.clock_out_display = get_employee_local_time(emp, clock_out_src, att.date)
            else:
                att.clock_out_display = None
        
        attendance_records[emp.id] = att
    
    # Handle form submission for bulk updates
    if request.method == 'POST':
        from core.timezone_utils import convert_local_time_to_utc
        from datetime import time as dt_time
        from core.models import AttendanceSegment

        action = request.form.get('action')
        try:
            if action == 'bulk_log':
                # Bulk log for all employees in the selected view
                bulk_status = request.form.get('bulk_status', 'Present')
                
                # Validate bulk_status enum value
                valid_statuses = ['Present', 'Incomplete', 'Absent', 'Leave']
                if bulk_status not in valid_statuses:
                    if bulk_status == 'Half Day':
                        bulk_status = 'Present'
                    else:
                        bulk_status = 'Absent'
                bulk_clock_in = request.form.get('bulk_clock_in')
                bulk_clock_out = request.form.get('bulk_clock_out')
                

                
                count = 0
                for emp in employees:
                    att = Attendance.query.filter_by(employee_id=emp.id, date=filter_date).first()
                    if not att:
                        att = Attendance(employee_id=emp.id, date=filter_date)
                    
                    att.status = bulk_status
                    
                    # Parse times safely
                    in_time = None
                    out_time = None
                    if bulk_clock_in:
                        try:
                            in_time = dt_time.fromisoformat(bulk_clock_in)
                            att.clock_in = in_time
                            # Convert local entered time to UTC for storage
                            local_dt = datetime.combine(filter_date, in_time)
                            att.clock_in_time = convert_local_time_to_utc(local_dt, employee=emp)
                        except (ValueError, TypeError): pass
                        
                    if bulk_clock_out:
                        try:
                            out_time = dt_time.fromisoformat(bulk_clock_out)
                            att.clock_out = out_time
                            # Convert local entered time to UTC for storage
                            local_dt = datetime.combine(filter_date, out_time)
                            att.clock_out_time = convert_local_time_to_utc(local_dt, employee=emp)
                        except (ValueError, TypeError): pass
                    
                    # Calculate hours
                    if att.clock_in_time and att.clock_out_time:
                        duration = (att.clock_out_time - att.clock_in_time).total_seconds() / 3600
                        att.regular_hours = round(max(0, duration), 2)
                        att.total_hours = att.regular_hours
                    
                    db.session.add(att)
                    db.session.flush() # Get ID for segments
                    
                    # Create/Update Segment for consistency with AttendanceService
                    if att.clock_in_time:
                        seg = AttendanceSegment.query.filter_by(attendance_id=att.id).first()
                        if not seg:
                            seg = AttendanceSegment(attendance_id=att.id, segment_type='Work')
                        
                        seg.clock_in = att.clock_in_time
                        seg.clock_out = att.clock_out_time
                        if att.total_hours:
                            seg.duration_minutes = int(att.total_hours * 60)
                        db.session.add(seg)
                    
                    count += 1
                    
                db.session.commit()
                flash(f'Bulk attendance logged for {count} employees', 'success')

            elif action == 'bulk_delete':
                # Delete all attendance records for the selected view
                count = 0
                for emp in employees:
                    att = Attendance.query.filter_by(employee_id=emp.id, date=filter_date).first()
                    if att:
                        # Deleting segments first
                        from core.models import AttendanceSegment
                        AttendanceSegment.query.filter_by(attendance_id=att.id).delete()
                        db.session.delete(att)
                        count += 1
                db.session.commit()
                flash(f'Deleted {count} attendance records for {filter_date}', 'success')

            elif action == 'bulk_ot_approve':
                # Approve all OT for the selected view
                count = 0
                for emp in employees:
                    att = Attendance.query.filter_by(employee_id=emp.id, date=filter_date).first()
                    if att and att.status == 'Present' and att.overtime_hours > 0:
                        att.overtime_approved = True
                        att.overtime_approved_by = current_user.id
                        att.overtime_approved_at = datetime.utcnow()
                        db.session.add(att)
                        count += 1
                db.session.commit()
                flash(f'Approved Overtime for {count} employees', 'success')

            elif action == 'bulk_mark_lop':
                # Mark all Absent as LOP for the selected view
                count = 0
                for emp in employees:
                    att = Attendance.query.filter_by(employee_id=emp.id, date=filter_date).first()
                    if att and att.status == 'Absent':
                        att.lop = True
                        db.session.add(att)
                        count += 1
                db.session.commit()
                flash(f'Marked {count} absent records as LOP', 'success')

            else:
                # Individual employee updates or unauthorized bulk action
                # Get bulk times for common application
                bulk_clock_in_str = request.form.get('bulk_clock_in')
                bulk_clock_out_str = request.form.get('bulk_clock_out')


                count = 0
                for emp in employees:
                    emp_id = emp.id
                    status = request.form.get(f'status_{emp_id}')
                    if not status: continue
                    
                    # Validate status enum value
                    valid_statuses = ['Present', 'Incomplete', 'Absent', 'Leave']
                    if status not in valid_statuses:
                        if status == 'Half Day': status = 'Present'
                        else: status = 'Absent'
                    
                    att = Attendance.query.filter_by(employee_id=emp_id, date=filter_date).first()
                    if not att:
                        att = Attendance(employee_id=emp_id, date=filter_date)
                    
                    att.status = status
                    att.lop = request.form.get(f'lop_{emp_id}') == 'on'

                    # Apply common bulk times if status is 'Present'
                    if status == 'Present' and (bulk_clock_in_str or bulk_clock_out_str):
                        if bulk_clock_in_str:
                            try:
                                in_time = dt_time.fromisoformat(bulk_clock_in_str)
                                att.clock_in = in_time
                                # Convert local entered time to UTC for storage
                                local_dt = datetime.combine(filter_date, in_time)
                                att.clock_in_time = convert_local_time_to_utc(local_dt, employee=emp)
                            except (ValueError, TypeError): pass
                        
                        if bulk_clock_out_str:
                            try:
                                out_time = dt_time.fromisoformat(bulk_clock_out_str)
                                att.clock_out = out_time
                                # Convert local entered time to UTC for storage
                                local_dt = datetime.combine(filter_date, out_time)
                                att.clock_out_time = convert_local_time_to_utc(local_dt, employee=emp)
                            except (ValueError, TypeError): pass

                        # Calculate hours if we have both times
                        if att.clock_in_time and att.clock_out_time:
                            duration = (att.clock_out_time - att.clock_in_time).total_seconds() / 3600
                            att.regular_hours = round(max(0, duration), 2)
                            att.total_hours = att.regular_hours
                        elif not att.total_hours:
                            att.total_hours = 8.0 # Fallback
                        
                        db.session.add(att)
                        db.session.flush()

                        # Synchronize Segment
                        if att.clock_in_time:
                            seg = AttendanceSegment.query.filter_by(attendance_id=att.id).first()
                            if not seg:
                                seg = AttendanceSegment(attendance_id=att.id, segment_type='Work')
                            seg.clock_in = att.clock_in_time
                            seg.clock_out = att.clock_out_time
                            seg.duration_minutes = int(att.total_hours * 60)
                            db.session.add(seg)
                    
                    db.session.add(att)
                    count += 1
                db.session.commit()
                flash(f'Attendance records updated successfully for {filter_date}', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing attendance: {str(e)}', 'error')
        
        return redirect(url_for('attendance_bulk_manage', date=filter_date.isoformat(), company=selected_company))
    
    return render_template('attendance/bulk_manage.html',
                         selected_date=selected_date_str,
                         filter_date=filter_date,
                         selected_company=selected_company,
                         available_companies=available_companies,
                         employees=employees,
                         attendance_records=attendance_records,
                         date=date)


# Master Data Management Routes
# Role routes moved to `routes_masters.py` to avoid duplicate endpoint
# registrations. See `routes_masters.py` for the canonical implementations
# of role_list, role_add, role_edit and role_delete.

# Department routes moved to `routes_masters.py` to avoid duplicate endpoint
# registrations. See `routes_masters.py` for the canonical implementations
# of department_list, department_add, department_edit and department_delete.
# Note: Working Hours Management Routes have been moved to routes_masters.py

