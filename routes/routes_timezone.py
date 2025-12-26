"""
Routes for Timezone Management
Provides timezone-related endpoints for frontend and API
"""

from flask import jsonify, request
from flask_login import login_required, current_user
from datetime import datetime
import pytz
from app import app
from core.models import Company, Employee
from core.timezone_utils import (
    get_current_time_in_company_timezone,
    get_company_timezone,
    format_time_for_display,
    get_all_timezones,
    validate_timezone,
    get_timezone_offset_str
)
from core.auth import require_role


# =====================================================
# TIMEZONE UTILITY ENDPOINTS
# =====================================================

@app.route('/api/supported-timezones', methods=['GET'])
def get_supported_timezones():
    """
    Get Supported Timezones
    ---
    tags:
      - Utilities
    responses:
      200:
        description: List of supported timezones
        schema:
          type: object
          properties:
            timezones:
              type: array
              items:
                type: string
    """
    try:
        timezones = get_all_timezones()
        return jsonify({
            'success': True,
            'timezones': timezones,
            'count': len(timezones)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/current-time-in-company-timezone', methods=['GET'])
@login_required
def get_current_time_in_user_company_timezone():
    """Get current time in user's company timezone
    
    Returns:
        JSON: Current time in company timezone and UTC
    """
    try:
        # Get user's company
        if not current_user.employee_profile or not current_user.employee_profile.company:
            return jsonify({
                'success': False,
                'error': 'No company associated with user'
            }), 400
        
        company = current_user.employee_profile.company
        company_timezone = get_company_timezone(company)
        
        # Get current time in company timezone
        current_time_company = get_current_time_in_company_timezone(company)
        current_time_utc = datetime.now(pytz.UTC)
        
        # Format for display
        display_company = format_time_for_display(current_time_company, "%Y-%m-%d %H:%M:%S")
        display_utc = format_time_for_display(current_time_utc, "%Y-%m-%d %H:%M:%S")
        offset = get_timezone_offset_str(company)
        
        return jsonify({
            'success': True,
            'timezone': company_timezone,
            'current_time': display_company,
            'current_time_company': display_company,
            'utc_time': display_utc,
            'offset': offset,
            'company_name': company.name,
            'company_id': str(company.id)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/timezone/<uuid:company_id>', methods=['GET'])
@login_required
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_company_timezone_info(company_id):
    """Get timezone information for a specific company
    
    Args:
        company_id: UUID of the company
        
    Returns:
        JSON: Timezone information for the company
    """
    try:
        company = Company.query.get_or_404(company_id)
        company_timezone = get_company_timezone(company)
        
        # Get current time in this timezone
        current_time = get_current_time_in_company_timezone(company)
        offset = get_timezone_offset_str(company)
        
        return jsonify({
            'success': True,
            'company_id': str(company.id),
            'company_name': company.name,
            'timezone': company_timezone,
            'offset': offset,
            'current_time': format_time_for_display(current_time, "%Y-%m-%d %H:%M:%S"),
            'description': f'Timezone: {company_timezone}, Offset: {offset}'
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/validate-timezone', methods=['POST'])
def validate_timezone_endpoint():
    """Validate if a timezone string is valid
    
    Expects JSON:
        {
            "timezone": "Asia/Singapore"
        }
        
    Returns:
        JSON: Validation result
    """
    try:
        data = request.get_json()
        timezone_str = data.get('timezone', '')
        
        if not timezone_str:
            return jsonify({
                'success': False,
                'valid': False,
                'error': 'Timezone string is required'
            }), 400
        
        is_valid = validate_timezone(timezone_str)
        
        response = {
            'success': True,
            'valid': is_valid,
            'timezone': timezone_str
        }
        
        if is_valid:
            # Get timezone object and get info
            tz = pytz.timezone(timezone_str)
            now = datetime.now(tz)
            offset = now.strftime('%z')
            offset_formatted = f"{offset[:3]}:{offset[3:]}" if offset else '+00:00'
            
            response.update({
                'offset': offset_formatted,
                'display_name': f"{timezone_str} {offset_formatted}"
            })
        else:
            response['error'] = f"Invalid timezone: {timezone_str}"
            
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/timezone-comparison', methods=['POST'])
@login_required
def get_timezone_comparison():
    """Compare time across multiple timezones
    
    Expects JSON:
        {
            "timezones": ["Asia/Singapore", "America/New_York", "Europe/London"]
        }
        
    Returns:
        JSON: Current time in each timezone
    """
    try:
        data = request.get_json()
        timezones = data.get('timezones', [])
        
        if not timezones:
            return jsonify({
                'success': False,
                'error': 'Timezones array is required'
            }), 400
        
        current_utc = datetime.now(pytz.UTC)
        comparison = []
        
        for tz_str in timezones:
            if validate_timezone(tz_str):
                tz = pytz.timezone(tz_str)
                local_time = current_utc.astimezone(tz)
                offset = local_time.strftime('%z')
                offset_formatted = f"{offset[:3]}:{offset[3:]}" if offset else '+00:00'
                
                comparison.append({
                    'timezone': tz_str,
                    'current_time': format_time_for_display(local_time, "%Y-%m-%d %H:%M:%S"),
                    'offset': offset_formatted,
                    'valid': True
                })
            else:
                comparison.append({
                    'timezone': tz_str,
                    'valid': False,
                    'error': 'Invalid timezone'
                })
        
        return jsonify({
            'success': True,
            'utc_time': format_time_for_display(current_utc, "%Y-%m-%d %H:%M:%S"),
            'comparisons': comparison,
            'count': len(comparison)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =====================================================
# COMPANY TIMEZONE MANAGEMENT
# =====================================================

@app.route('/api/companies/<uuid:company_id>/timezone', methods=['GET'])
@login_required
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def get_company_timezone_endpoint(company_id):
    """Get current timezone for a company
    
    Args:
        company_id: UUID of the company
        
    Returns:
        JSON: Company timezone information
    """
    try:
        company = Company.query.get_or_404(company_id)
        return jsonify({
            'success': True,
            'company_id': str(company.id),
            'company_name': company.name,
            'timezone': get_company_timezone(company),
            'offset': get_timezone_offset_str(company)
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404


@app.route('/api/companies/<uuid:company_id>/timezone', methods=['PUT'])
@login_required
@require_role(['Super Admin', 'Tenant Admin'])
def update_company_timezone_endpoint(company_id):
    """Update company timezone
    
    Args:
        company_id: UUID of the company
        
    Expects JSON:
        {
            "timezone": "Asia/Singapore"
        }
        
    Returns:
        JSON: Update result
    """
    try:
        company = Company.query.get_or_404(company_id)
        data = request.get_json()
        
        timezone_str = data.get('timezone', '')
        if not timezone_str:
            return jsonify({
                'success': False,
                'error': 'Timezone is required'
            }), 400
        
        # Validate timezone
        if not validate_timezone(timezone_str):
            return jsonify({
                'success': False,
                'error': f'Invalid timezone: {timezone_str}'
            }), 400
        
        # Update company timezone
        company.timezone = timezone_str
        from sqlalchemy import func
        from datetime import datetime
        company.modified_at = datetime.now()
        company.modified_by = current_user.email if current_user else 'system'
        
        from app import db
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Company timezone updated to {timezone_str}',
            'company_id': str(company.id),
            'company_name': company.name,
            'timezone': company.timezone,
            'offset': get_timezone_offset_str(company)
        }), 200
        
    except Exception as e:
        from app import db
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# =====================================================
# EMPLOYEE TIMEZONE PREFERENCES (Future Enhancement)
# =====================================================

@app.route('/api/my-timezone', methods=['GET'])
@login_required
def get_user_timezone():
    """Get current user's company timezone
    
    Returns:
        JSON: User's company timezone and current time
    """
    try:
        if not current_user.employee_profile or not current_user.employee_profile.company:
            return jsonify({
                'success': False,
                'error': 'No company associated with user'
            }), 400
        
        company = current_user.employee_profile.company
        current_time = get_current_time_in_company_timezone(company)
        
        return jsonify({
            'success': True,
            'user_id': current_user.id,
            'user_name': current_user.full_name,
            'company_id': str(company.id),
            'company_name': company.name,
            'timezone': get_company_timezone(company),
            'current_time': format_time_for_display(current_time, "%Y-%m-%d %H:%M:%S"),
            'offset': get_timezone_offset_str(company)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
