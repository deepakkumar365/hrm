from functools import wraps
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import app, db
from models import User

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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
                return render_template("403.html"), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def create_default_users():
    """Create default users if none exist"""
    from models import Employee
    from datetime import date
    
    if User.query.count() == 0:
        # Create Super Admin
        super_admin = User(
            username='superadmin',
            email='superadmin@hrm.com',
            first_name='Super',
            last_name='Admin',
            role='Super Admin'
        )
        super_admin.set_password('superadmin123')
        
        # Create Regular Admin
        admin = User(
            username='admin',
            email='admin@hrm.com',
            first_name='System',
            last_name='Admin',
            role='Admin'
        )
        admin.set_password('admin123')
        
        # Create Manager
        manager = User(
            username='manager',
            email='manager@hrm.com',
            first_name='HR',
            last_name='Manager',
            role='Manager'
        )
        manager.set_password('manager123')
        
        # Create Regular User
        user = User(
            username='user',
            email='user@hrm.com',
            first_name='Regular',
            last_name='User',
            role='User'
        )
        user.set_password('user123')
        
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
                position='Chief Executive',
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
                position='System Administrator',
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
                position='HR Manager',
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
                position='Executive',
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