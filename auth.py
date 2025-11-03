from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User
from constants import DEFAULT_USER_PASSWORD

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.session_protection = 'strong'  # Protect against session hijacking
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = 'Please log in again to access this page.'

@login_manager.user_loader
def load_user(user_id):
    """Load user from database by user_id stored in session"""
    if user_id is None:
        return None
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

def require_login(f):
    """Decorator to require login"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def require_role(allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        @require_login
        def decorated_function(*args, **kwargs):
            # Use role.name to compare with allowed roles (role is a relationship object)
            user_role = current_user.role.name if current_user.role else None
            if user_role not in allowed_roles:
                # For AJAX requests, return JSON error
                if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return {
                        'success': False,
                        'error': 'Access Denied',
                        'message': 'You do not have permission to access this operation!'
                    }, 403
                
                # For regular requests, show toaster notification and redirect back
                flash('You do not have permission to access this operation!', 'error')
                return redirect(request.referrer or url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def create_default_users():
    """Create default users if none exist"""
    from models import Employee, Role, Organization
    from datetime import date
    
    if User.query.count() == 0:
        # Get or create default organization
        org = Organization.query.first()
        if not org:
            org = Organization(name='Default Organization')
            db.session.add(org)
            db.session.flush()  # Get the org.id
        
        # Get or create default roles
        role_names = ['SUPER_ADMIN', 'ADMIN', 'HR_MANAGER', 'EMPLOYEE']
        roles = {}
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=f'{role_name} role')
                db.session.add(role)
                db.session.flush()  # Get the role.id
            roles[role_name] = role
        
        # Create Super Admin
        super_admin = User(
            username='superadmin',
            email='superadmin@hrm.com',
            first_name='Super',
            last_name='Admin',
            organization_id=org.id,
            role_id=roles['SUPER_ADMIN'].id,
            must_reset_password=False
        )
        super_admin.set_password(DEFAULT_USER_PASSWORD)
        
        # Create Regular Admin
        admin = User(
            username='admin',
            email='admin@hrm.com',
            first_name='System',
            last_name='Admin',
            organization_id=org.id,
            role_id=roles['ADMIN'].id,
            must_reset_password=False
        )
        admin.set_password(DEFAULT_USER_PASSWORD)
        
        # Create Manager
        manager = User(
            username='manager',
            email='manager@hrm.com',
            first_name='HR',
            last_name='Manager',
            organization_id=org.id,
            role_id=roles['HR_MANAGER'].id,
            must_reset_password=False
        )
        manager.set_password(DEFAULT_USER_PASSWORD)
        
        # Create Regular User
        user = User(
            username='user',
            email='user@hrm.com',
            first_name='Regular',
            last_name='User',
            organization_id=org.id,
            role_id=roles['EMPLOYEE'].id,
            must_reset_password=False
        )
        user.set_password(DEFAULT_USER_PASSWORD)
        
        db.session.add_all([super_admin, admin, manager, user])
        db.session.commit()
        
        # Create Employee profiles for each user
        employees = [
            Employee(
                employee_id='EMP001',
                first_name='Super',
                last_name='Admin',
                email='superadmin@hrm.com',
                nric='S1234567A',
                date_of_birth=date(1980, 1, 1),
                department='Executive',
                hire_date=date(2020, 1, 1),
                employment_type='Full-time',
                work_permit_type='Citizen',
                basic_salary=15000,
                user_id=super_admin.id
            ),
            Employee(
                employee_id='EMP002',
                first_name='System',
                last_name='Admin',
                email='admin@hrm.com',
                nric='S1234567B',
                date_of_birth=date(1985, 1, 1),
                department='IT',
                hire_date=date(2020, 1, 1),
                employment_type='Full-time',
                work_permit_type='Citizen',
                basic_salary=8000,
                user_id=admin.id
            ),
            Employee(
                employee_id='EMP003',
                first_name='HR',
                last_name='Manager',
                email='manager@hrm.com',
                nric='S1234567C',
                date_of_birth=date(1990, 1, 1),
                department='Human Resources',
                hire_date=date(2020, 1, 1),
                employment_type='Full-time',
                work_permit_type='Citizen',
                basic_salary=6000,
                user_id=manager.id
            ),
            Employee(
                employee_id='EMP004',
                first_name='Regular',
                last_name='User',
                email='user@hrm.com',
                nric='S1234567D',
                date_of_birth=date(1995, 1, 1),
                department='Operations',
                hire_date=date(2020, 1, 1),
                employment_type='Full-time',
                work_permit_type='Citizen',
                basic_salary=4000,
                user_id=user.id,
                manager_id=3  # Reports to HR Manager
            )
        ]
        
        db.session.add_all(employees)
        db.session.commit()
        
        return True
    return False