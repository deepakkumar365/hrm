import csv
from io import StringIO
from flask import make_response
from datetime import datetime, date, time, timedelta
import logging
from pytz import timezone, utc
import re

def export_to_csv(data, filename, headers=None):
    """Export data to CSV and return as downloadable response"""
    output = StringIO()

    if headers:
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    else:
        writer = csv.writer(output)
        for row in data:
            writer.writerow(row)

    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "text/csv"

    return response

def calculate_working_days(start_date, end_date):
    """Calculate working days between two dates (excluding weekends)"""
    working_days = 0
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday is 0, Sunday is 6
            working_days += 1
        current_date += timedelta(days=1)

    return working_days

def format_currency(amount):
    """Format amount as Singapore currency"""
    if amount is None:
        return "S$ 0.00"
    return f"S$ {amount:,.2f}"

def format_date(date_obj):
    """Format date for display"""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%d/%m/%Y")

def parse_date(date_string):
    """Parse date from string"""
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.strptime(date_string, "%d/%m/%Y").date()
        except ValueError:
            return None

def get_current_month_dates():
    """Get start and end dates of current month"""
    today = date.today()
    start_date = date(today.year, today.month, 1)

    if today.month == 12:
        end_date = date(today.year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(today.year, today.month + 1, 1) - timedelta(days=1)

    return start_date, end_date

def validate_nric(nric):
    """Basic NRIC validation for Singapore - optional field"""
    # Validation removed as per request.
    return True

def validate_phone_number(phone_number, country_code):
    """
    Placeholder for phone number validation. Always returns valid.
    """
    # Phone number validation has been removed.
    return {
        'is_valid': True,
        'error_message': None,
        'formatted_number': phone_number
    }

def validate_and_format_phone(phone_string):
    """
    Placeholder for phone number validation. Always returns valid.
    """
    return True, phone_string

def validate_email(email):
    """
    Validate email format using regex pattern.

    Args:
        email: Email string to validate

    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    # Basic email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email.strip()))


def generate_employee_id(company_code=None, employee_db_id=None):
    """
    Generate employee ID in format: <CompanyCode><hrm_employee_id>

    Args:
        company_code: Code of the company (e.g., 'ACME')
        employee_db_id: ID from hrm_employee table (auto-incremented integer)

    Returns:
        Formatted employee ID (e.g., 'ACME001') or None if company_code not provided
    """
    if not company_code:
        # Fallback for backward compatibility if company code not available
        from datetime import datetime
        return f"EMP{datetime.now().strftime('%Y%m%d%H%M%S')}"

    if employee_db_id:
        # Format: CompanyCode + ID with zero-padding (e.g., ACME001)
        return f"{company_code}{str(employee_db_id).zfill(3)}"

    # If only company_code provided, use timestamp for backward compatibility
    from datetime import datetime
    return f"{company_code}{datetime.now().strftime('%Y%m%d%H%M%S')}"

def get_company_employee_id(company_id, company_code, db_session):
    """
    Generate a company-specific employee ID using the CompanyEmployeeIdConfig table.
    Each company has its own sequence starting from 1.

    Format: CompanyCode + Sequential Number (e.g., ACME001, ACME002, ACME003)

    Args:
        company_id: UUID of the company
        company_code: Code of the company (e.g., 'ACME')
        db_session: SQLAlchemy database session

    Returns:
        Formatted employee ID (e.g., 'ACME001')

    Raises:
        ValueError: If company_code is not provided
    """
    if not company_code:
        raise ValueError("Company code is required to generate employee ID")

    # Import here to avoid circular imports
    from core.models import CompanyEmployeeIdConfig

    # Get or create the configuration for this company
    config = CompanyEmployeeIdConfig.query.filter_by(company_id=company_id).first()

    if not config:
        # Create new configuration entry for this company
        config = CompanyEmployeeIdConfig(
            company_id=company_id,
            id_prefix=company_code,
            last_sequence_number=0,
            created_by='system'
        )
        db_session.add(config)
        db_session.flush()  # Flush to ensure the config is created before we use it

    # Get the next employee ID
    return config.get_next_employee_id()

def check_permission(user, required_permission):
    """Check if user has required permission"""
    if not user or not user.is_authenticated:
        return False

    role_permissions = {
        'Admin': ['all'],
        'Manager': ['view_team', 'approve_leave', 'approve_claims', 'view_payroll'],
        'Employee': ['view_self', 'submit_leave', 'submit_claims', 'view_payslip']
    }

    user_permissions = role_permissions.get(user.role, [])

    return 'all' in user_permissions or required_permission in user_permissions

def mobile_optimized_pagination(page, per_page, total):
    """Generate mobile-friendly pagination info"""
    total_pages = (total + per_page - 1) // per_page

    return {
        'page': page,
        'per_page': per_page,
        'total': total,
        'total_pages': total_pages,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < total_pages else None
    }

class MobileDetector:
    """Simple mobile device detection"""

    @staticmethod
    def is_mobile(user_agent):
        mobile_agents = [
            'Mobile', 'Android', 'iPhone', 'iPad', 'iPod',
            'BlackBerry', 'Windows Phone', 'Opera Mini'
        ]

        return any(agent in str(user_agent) for agent in mobile_agents)

def get_employee_local_time(employee, time_obj, event_date):
    """
    Returns the time object for display, converted to company local time if it's a UTC datetime.
    
    Args:
        employee (Employee): The employee object.
        time_obj (datetime.time or datetime.datetime): The time or datetime object.
        event_date (datetime.date): The date of the event.

    Returns:
        datetime.time: The localized time object.
    """
    if not time_obj:
        return None
    
    # If it's already a time object, assume it's legacy local time storage
    if isinstance(time_obj, time):
        return time_obj
        
    # If it's a datetime, it's our new standardized UTC storage
    if isinstance(time_obj, datetime):
        from core.timezone_utils import convert_utc_to_company_timezone
        localized_dt = convert_utc_to_company_timezone(time_obj, employee.company)
        return localized_dt.time()
        
    return time_obj

# =====================================================================
# UTILITY: Check Role Access to Module/Menu
# =====================================================================

def check_module_access(user_role, module_name, menu_name=None, sub_menu_name=None):
    """
    Check if a role has access to a module/menu/sub-menu
    Returns: 'Editable', 'View Only', 'Hidden'
    """
    try:
        from core.models import RoleAccessControl
        
        query = RoleAccessControl.query.filter_by(module_name=module_name)
        
        if menu_name:
            query = query.filter_by(menu_name=menu_name)
        if sub_menu_name:
            query = query.filter_by(sub_menu_name=sub_menu_name)
        
        ac = query.first()
        if not ac:
            return 'Hidden'  # Default to hidden if not found
        
        # Map role to column name
        role_column_map = {
            'Super Admin': 'super_admin_access',
            'Tenant Admin': 'tenant_admin_access',
            'HR Manager': 'hr_manager_access',
            'Employee': 'employee_access',
        }
        
        column = role_column_map.get(user_role, 'employee_access')
        access_level = getattr(ac, column, 'Hidden')
        
        return access_level
    except Exception as e:
        print(f"Error checking module access: {str(e)}")
        return 'Hidden'


def check_ui_access(user_role, module_name, menu_name=None, sub_menu_name=None):
    """
    Check if UI element should be visible based on role access
    Returns 'Editable', 'View Only', or 'Hidden'
    """
    return check_module_access(user_role, module_name, menu_name, sub_menu_name)
