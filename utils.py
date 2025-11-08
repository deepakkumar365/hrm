import csv
from io import StringIO, BytesIO
from flask import make_response
import pandas as pd
from datetime import datetime, date, timedelta
import logging
import phonenumbers
from phonenumbers import NumberParseException
from pytz import timezone, utc
from phonenumbers import PhoneNumberFormat


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
    Validate phone number based on country code.
    
    Args:
        phone_number (str): Phone number to validate
        country_code (str): ISO 3166-1 alpha-2 country code (e.g., 'SG', 'IN', 'AE')
    
    Returns:
        dict: {
            'is_valid': bool,
            'error_message': str or None,
            'formatted_number': str or None
        }
    """
    if not phone_number or not phone_number.strip():
        return {
            'is_valid': True,
            'error_message': None,
            'formatted_number': None
        }
    
    if not country_code or not str(country_code).strip():
        return {
            'is_valid': False,
            'error_message': 'Company country is not configured. Please contact administrator.',
            'formatted_number': None
        }
    
    try:
        parsed_number = phonenumbers.parse(phone_number, str(country_code).upper())
        
        if not phonenumbers.is_valid_number(parsed_number):
            return {
                'is_valid': False,
                'error_message': f'Phone number is invalid for {country_code.upper()}.',
                'formatted_number': None
            }
        
        formatted = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        
        return {
            'is_valid': True,
            'error_message': None,
            'formatted_number': formatted
        }
    
    except NumberParseException as e:
        return {
            'is_valid': False,
            'error_message': f'Phone number format is invalid for {country_code.upper()}.',
            'formatted_number': None
        }
    except Exception as e:
        return {
            'is_valid': False,
            'error_message': 'Unable to validate phone number. Please check the format.',
            'formatted_number': None
        }

def validate_and_format_phone(phone_string):
    """
    Validates a phone number string (expected in E.164 format) and returns
    the formatted number or an error. This is ideal for backend validation.
    
    Args:
        phone_string (str): The phone number, ideally starting with a '+'.
        
    Returns:
        tuple: (is_valid, result)
               If valid, result is the formatted E.164 number.
               If invalid, result is an error message.
    """
    if not phone_string or not phone_string.strip():
        return True, None # It's valid to have no phone number

    try:
        # The `None` for region tells the library to infer from the country code
        number = phonenumbers.parse(phone_string, None)

        if not phonenumbers.is_valid_number(number):
            return False, "The provided phone number is not valid."

        # Return the standardized E.164 format
        formatted_number = phonenumbers.format_number(number, PhoneNumberFormat.E164)
        return True, formatted_number

    except NumberParseException:
        return False, "The phone number could not be parsed. Please ensure it includes a country code (e.g., +1)."


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
    Convert a UTC time object to the employee's local timezone.

    Args:
        employee (Employee): The employee object with a timezone attribute.
        time_obj (datetime.time): The time object stored in UTC.
        event_date (datetime.date): The date of the event.

    Returns:
        str: Formatted time string in employee's local timezone, or empty string.
    """
    if not time_obj or not event_date:
        return ""

    try:
        # Combine date and time to create a UTC datetime object
        utc_dt = datetime.combine(event_date, time_obj, tzinfo=utc)

        # Get employee's timezone, default to UTC
        employee_tz_str = employee.timezone or 'UTC'
        employee_tz = timezone(employee_tz_str)

        # Convert to employee's local time and format it
        local_dt = utc_dt.astimezone(employee_tz)
        return local_dt.strftime('%I:%M %p')
    except Exception:
        # Fallback for invalid timezone or other errors
        return time_obj.strftime('%H:%M:%S UTC')
