import csv
from io import StringIO, BytesIO
from flask import make_response
import pandas as pd
from datetime import datetime, date, timedelta
import logging

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
    """Basic NRIC validation for Singapore"""
    if not nric or len(nric) != 9:
        return False
    
    if nric[0] not in ['S', 'T', 'F', 'G', 'M']:
        return False
    
    if not nric[1:8].isdigit():
        return False
    
    return True

def generate_employee_id():
    """Generate unique employee ID"""
    from datetime import datetime
    return f"EMP{datetime.now().strftime('%Y%m%d%H%M%S')}"

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
