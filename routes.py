from flask import session, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import current_user
from sqlalchemy import func, extract, and_, text
import uuid
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
                    Company, Tenant, EmployeeBankInfo, EmployeeDocument, TenantPaymentConfig, TenantDocument, Designation, EmployeeGroup,
                    OTType, OTAttendance, OTRequest, OTApproval, PayrollOTSummary, OTDailySummary)
from forms import LoginForm, RegisterForm
from flask_login import login_user, logout_user
from singapore_payroll import SingaporePayrollCalculator
from utils import (export_to_csv, format_currency, format_date, parse_date,
                   validate_nric, validate_email, generate_employee_id, get_company_employee_id, check_permission,
                   mobile_optimized_pagination, get_current_month_dates, validate_phone_number)
from constants import DEFAULT_USER_PASSWORD

logger = logging.getLogger(__name__)

def get_current_user_email():
    """Get current user's email for audit fields"""
    if current_user and current_user.is_authenticated:
        return current_user.email
    return 'system'

# Helper to validate image extension
def _allowed_image(filename: str) -> bool:
    if not filename or '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in app.config.get('ALLOWED_IMAGE_EXTENSIONS', set())

# Initialize payroll calculator
payroll_calc = SingaporePayrollCalculator()

# A list of common timezones for dropdowns
common_timezones = [
    "UTC", "Asia/Singapore", "Asia/Kolkata", "Asia/Dubai", "Asia/Shanghai",
    "Asia/Tokyo", "Europe/London", "Europe/Paris", "Europe/Berlin",
    "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles",
    "Australia/Sydney", "Australia/Perth"
]


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

@app.context_processor
def inject_user_profile_info():
    """
    Injects user profile information into the context of all templates.
    This makes `profile_image_path` and `user_full_name` available globally.
    """
    profile_image_path = None
    user_full_name = None
    if current_user.is_authenticated and hasattr(current_user, 'employee_profile') and current_user.employee_profile:
        profile_image_path = current_user.employee_profile.profile_image_path
        user_full_name = f"{current_user.employee_profile.first_name} {current_user.employee_profile.last_name}"

    return dict(profile_image_path=profile_image_path, user_full_name=user_full_name)

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
        user.last_name = form.first_name.data
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
            .filter(Company.tenant_id == tenant.id).scalar()
        recent_tenants.append({
            'name': tenant.name,
            'created_at': tenant.created_at,
            'companies': company_count,
            'users': user_count
        })

    return render_template('dashboard/super_admin.html',
                         total_tenants=total_tenants,
                         active_tenants=active_tenants,
                         total_companies=total_companies,
                         total_users=total_users,
                         active_users=active_users,
                         company_labels=company_labels,
                         company_counts=company_counts,
                         payslip_months=payslip_months,
                         payslip_counts=payslip_counts,
                         payslips_this_month=payslips_this_month,
                         monthly_revenue=monthly_revenue,
                         quarterly_revenue=quarterly_revenue,
                         yearly_revenue=yearly_revenue,
                         collected_revenue=collected_revenue,
                         quarterly_collected=quarterly_collected,
                         yearly_collected=yearly_collected,
                         pending_payments=pending_payments,
                         overdue_payments=overdue_payments,
                         recent_tenants=recent_tenants)


@app.route('/dashboard')
@require_login
def dashboard():
    """Main dashboard with role-based content"""
    if current_user.role and current_user.role.name == 'Super Admin':
        return render_super_admin_dashboard()

    # Employee dashboard - get today's attendance
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(
        employee_id=current_user.employee_profile.id if current_user.employee_profile else None,
        date=today
    ).first() if current_user.employee_profile else None

    # Get recent attendance records
    recent_attendance = Attendance.query.filter_by(
        employee_id=current_user.employee_profile.id if current_user.employee_profile else None
    ).order_by(Attendance.date.desc()).limit(7).all() if current_user.employee_profile else []

    # Get leave balance
    leave_balance = None
    if current_user.employee_profile:
        # This is a simplified calculation - you might want to implement proper leave balance logic
        total_leaves = Leave.query.filter_by(employee_id=current_user.employee_profile.id).count()
        leave_balance = 14 - total_leaves  # Assuming 14 annual leave days

    return render_template('dashboard/employee.html',
                         today_attendance=today_attendance,
                         recent_attendance=recent_attendance,
                         leave_balance=leave_balance)


@app.route('/attendance', methods=['GET', 'POST'])
@require_login
def attendance():
    """Mark attendance with GPS location tracking"""
    if not current_user.employee_profile:
        flash('Employee profile not found. Please contact HR.', 'error')
        return redirect(url_for('dashboard'))

    today = datetime.now().date()
    employee_id = current_user.employee_profile.id

    # Check if already clocked in today
    existing_attendance = Attendance.query.filter_by(
        employee_id=employee_id,
        date=today
    ).first()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'clock_in' and not existing_attendance:
            # Clock in with location data
            attendance = Attendance(
                employee_id=employee_id,
                date=today,
                clock_in=datetime.now().time(),
                location_lat=request.form.get('location_lat'),
                location_lng=request.form.get('location_lng'),
                location_address=request.form.get('location_address'),
                created_by=get_current_user_email()
            )
            db.session.add(attendance)
            db.session.commit()
            flash('Successfully clocked in!', 'success')

        elif action == 'clock_out' and existing_attendance and not existing_attendance.clock_out:
            # Clock out
            existing_attendance.clock_out = datetime.now().time()
            existing_attendance.total_hours = (
                datetime.combine(today, existing_attendance.clock_out) -
                datetime.combine(today, existing_attendance.clock_in)
            ).total_seconds() / 3600
            existing_attendance.updated_by = get_current_user_email()
            db.session.commit()
            flash('Successfully clocked out!', 'success')

        return redirect(url_for('attendance'))

    # Get today's attendance records for timeline
    today_records = Attendance.query.filter_by(
        employee_id=employee_id,
        date=today
    ).all()

    return render_template('attendance/form.html', today_records=today_records)


@app.route('/attendance/calendar')
@require_login
def attendance_calendar():
    """Get attendance data for calendar view"""
    if not current_user.employee_profile:
        return jsonify([])

    employee_id = current_user.employee_profile.id

    # Get attendance records for current month
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    if start_date and end_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')).date()
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00')).date()
    else:
        # Default to current month
        now = datetime.now()
        start = now.replace(day=1).date()
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

    records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= start,
        Attendance.date <= end
    ).all()

    events = []
    for record in records:
        if record.clock_in:
            event = {
                'title': f"Clock In: {record.clock_in.strftime('%H:%M')}",
                'start': f"{record.date}T{record.clock_in}",
                'backgroundColor': '#28a745',
                'borderColor': '#28a745'
            }

            # Add location address if available
            if record.location_address:
                event['title'] += f" - {record.location_address}"

            events.append(event)

        if record.clock_out:
            event = {
                'title': f"Clock Out: {record.clock_out.strftime('%H:%M')}",
                'start': f"{record.date}T{record.clock_out}",
                'backgroundColor': '#dc3545',
                'borderColor': '#dc3545'
            }
            events.append(event)

    return jsonify(events)

# Placeholder for additional routes - add them as needed
# This minimal routes.py includes the essential functionality for GPS location tracking
# Additional routes can be added from your backup or recreated based on your application needs