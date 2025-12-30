"""
Mobile App JSON API Routes
Provides REST API endpoints for mobile application
Supports both session-based and token-based authentication
Uses simple token mechanism without external JWT dependencies
"""

from flask import request, jsonify, current_app
from flask_login import current_user, login_user, logout_user
from functools import wraps
from datetime import datetime, timedelta, date
import logging
import json
import base64
import hmac
import hashlib
from app import app, db
from core.models import (
    User, Employee, Attendance, Leave, Payroll, Role, 
    Department, Company, Designation, EmployeeGroup, OTRequest,
    OTType, OTAttendance, OTApproval
)
from sqlalchemy.orm import joinedload
from core.auth import login_manager

logger = logging.getLogger(__name__)

# ============================================================================
# Token Management (Simple Base64 + HMAC)
# ============================================================================

def generate_token(user_id, expires_in=86400):
    """Generate a simple token for user (valid for 24 hours by default)"""
    try:
        exp_time = datetime.utcnow() + timedelta(seconds=expires_in)
        payload = {
            'user_id': user_id,
            'exp': exp_time.isoformat(),
            'iat': datetime.utcnow().isoformat()
        }
        # Encode payload as JSON then base64
        payload_json = json.dumps(payload)
        payload_b64 = base64.b64encode(payload_json.encode()).decode()
        
        # Create signature using HMAC
        secret = current_app.config.get('SECRET_KEY', 'default-secret')
        signature = hmac.new(
            secret.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Combine as: payload.signature
        token = f"{payload_b64}.{signature}"
        return token
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return None


def verify_token(token):
    """Verify and decode token, return user_id if valid"""
    try:
        if not token or '.' not in token:
            return None
            
        payload_b64, signature = token.rsplit('.', 1)
        
        # Verify signature
        secret = current_app.config.get('SECRET_KEY', 'default-secret')
        expected_signature = hmac.new(
            secret.encode(),
            payload_b64.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if signature != expected_signature:
            return None
        
        # Decode payload
        payload_json = base64.b64decode(payload_b64).decode()
        payload = json.loads(payload_json)
        
        # Check expiration
        exp_time = datetime.fromisoformat(payload['exp'])
        if datetime.utcnow() > exp_time:
            return None
        
        return payload.get('user_id')
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return None


def token_required(f):
    """Decorator to require valid token for API endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')
            try:
                token = auth_header.split(" ")[1]  # Format: "Bearer <token>"
            except IndexError:
                return jsonify({'status': 'error', 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'status': 'error', 'message': 'Token is missing'}), 401
        
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'status': 'error', 'message': 'Invalid or expired token'}), 401
        
        # Load user from database
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return jsonify({'status': 'error', 'message': 'User not found or inactive'}), 401
        
        return f(*args, **kwargs)
    
    return decorated


def api_response(status='success', message='', data=None, code=200):
    """Standardized API response format"""
    response = {
        'status': status,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), code


def get_user_from_token_or_session():
    """Get user from token or session"""
    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers.get('Authorization')
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            pass
    
    if token:
        user_id = verify_token(token)
        if user_id:
            return User.query.get(user_id)
    
    if current_user.is_authenticated:
        return current_user
    
    return None


# ============================================================================
# AUTHENTICATION API ENDPOINTS
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def mobile_api_login():
    """
    Mobile App Login
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: Email or Username
              example: user@example.com
            password:
              type: string
              description: User Password
              example: password123
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                token:
                  type: string
                user_id:
                  type: integer
      401:
        description: Invalid credentials
    """
    try:
        if not request.is_json:
            return api_response('error', 'Content-Type must be application/json', None, 400)
        
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return api_response('error', 'Username and password are required', None, 400)
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return api_response('error', 'Invalid username or password', None, 401)
        
        if not user.is_active:
            return api_response('error', 'User account is inactive', None, 403)
        
        # Log user in (creates session)
        login_user(user)
        
        # Generate token
        token = generate_token(user.id)
        
        # Get user's employee profile for additional info
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        user_data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role.name if user.role else None,
            'role_id': user.role_id,
            'company_id': user.company_id if hasattr(user, 'company_id') else None,
            'employee_id': employee.id if employee else None,
            'profile_image_path': employee.profile_image_path if employee else None,
            'token': token,
            'expires_in': 86400
        }
        
        return api_response('success', 'Login successful', user_data, 200)
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return api_response('error', f'Login failed: {str(e)}', None, 500)


@app.route('/api/auth/logout', methods=['POST'])
@token_required
def mobile_api_logout():
    """
    Mobile App Logout
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
    """
    try:
        logout_user()
        return api_response('success', 'Logout successful', None, 200)
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return api_response('error', f'Logout failed: {str(e)}', None, 500)


@app.route('/api/auth/register', methods=['POST'])
def mobile_api_register():
    """
    User Registration
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - username
            - email
            - password
            - first_name
            - last_name
          properties:
            username:
              type: string
            email:
              type: string
            password:
              type: string
            first_name:
              type: string
            last_name:
              type: string
            company_id:
              type: integer
    responses:
      201:
        description: Registration successful
      409:
        description: Username or Email already exists
    """
    try:
        if not request.is_json:
            return api_response('error', 'Content-Type must be application/json', None, 400)
        
        data = request.get_json()
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
        
        for field in required_fields:
            if not data.get(field, '').strip():
                return api_response('error', f'{field} is required', None, 400)
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return api_response('error', 'Username already exists', None, 409)
        
        if User.query.filter_by(email=data['email']).first():
            return api_response('error', 'Email already registered', None, 409)
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            company_id=data.get('company_id')
        )
        user.set_password(data['password'])
        
        # Assign default role if not specified
        default_role = Role.query.filter_by(name='Employee').first()
        if default_role:
            user.role_id = default_role.id
        
        db.session.add(user)
        db.session.commit()
        
        return api_response('success', 'Registration successful', {
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }, 201)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {e}")
        return api_response('error', f'Registration failed: {str(e)}', None, 500)


@app.route('/api/auth/refresh-token', methods=['POST'])
@token_required
def mobile_api_refresh_token():
    """
    Refresh Token
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Token refreshed
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                token:
                  type: string
    """
    try:
        user = get_user_from_token_or_session()
        if not user:
            return api_response('error', 'User not found', None, 401)
        
        new_token = generate_token(user.id)
        
        return api_response('success', 'Token refreshed', {
            'token': new_token,
            'expires_in': 86400
        }, 200)
    
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        return api_response('error', f'Token refresh failed: {str(e)}', None, 500)


# ============================================================================
# USER PROFILE API ENDPOINTS
# ============================================================================

@app.route('/api/user/profile', methods=['GET'])
@token_required
def mobile_api_get_profile():
    """
    Get User Profile
    ---
    tags:
      - User
    security:
      - Bearer: []
    responses:
      200:
        description: User profile details
        schema:
          type: object
          properties:
            data:
              type: object
              properties:
                username:
                  type: string
                email:
                  type: string
                role:
                  type: string
    """
    try:
        user = get_user_from_token_or_session()
        if not user:
            return api_response('error', 'User not found', None, 401)
        
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        profile_data = {
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'full_name': f"{user.first_name} {user.last_name}",
            'role': user.role.name if user.role else None,
            'phone': employee.phone if employee else None,
            'profile_image_path': employee.profile_image_path if employee else None,
            'designation': employee.designation.name if employee and employee.designation else None,
            'department': employee.department.name if employee and employee.department else None,
            'company': user.company.name if hasattr(user, 'company') and user.company else None
        }
        
        return api_response('success', 'Profile retrieved', profile_data, 200)
    
    except Exception as e:
        logger.error(f"Get profile error: {e}")
        return api_response('error', f'Failed to retrieve profile: {str(e)}', None, 500)


# ============================================================================
# EMPLOYEE MANAGEMENT API ENDPOINTS
# ============================================================================

@app.route('/api/employees', methods=['GET'])
@token_required
def mobile_api_get_employees():
    """
    List Employees
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 20
      - name: search
        in: query
        type: string
    responses:
      200:
        description: List of employees
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        status = request.args.get('status', 'active')
        
        query = Employee.query
        
        # Apply filters
        if search:
            query = query.filter(
                (Employee.first_name.ilike(f'%{search}%')) |
                (Employee.last_name.ilike(f'%{search}%')) |
                (Employee.email.ilike(f'%{search}%'))
            )
        
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
        
        # Apply role-based filtering (if needed)
        user = get_user_from_token_or_session()
        if user and user.company_id:
            query = query.filter_by(company_id=user.company_id)
        
        # Paginate
        paginated = query.paginate(page=page, per_page=per_page)
        
        employees = []
        for emp in paginated.items:
            employees.append({
                'id': emp.id,
                'first_name': emp.first_name,
                'last_name': emp.last_name,
                'email': emp.email,
                'employee_id': emp.employee_id,
                'phone': emp.phone,
                'designation': emp.designation.name if emp.designation else None,
                'department': emp.department.name if emp.department else None,
                'status': 'active' if emp.is_active else 'inactive'
            })
        
        return api_response('success', 'Employees retrieved', {
            'employees': employees,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, 200)
    
    except Exception as e:
        logger.error(f"Get employees error: {e}")
        return api_response('error', f'Failed to retrieve employees: {str(e)}', None, 500)


@app.route('/api/employees/<int:employee_id>', methods=['GET'])
@token_required
def mobile_api_get_employee(employee_id):
    """
    Get Employee Detail
    ---
    tags:
      - Employees
    security:
      - Bearer: []
    parameters:
      - name: employee_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Employee details
      404:
        description: Employee not found
    """
    try:
        employee = Employee.query.get(employee_id)
        if not employee:
            return api_response('error', 'Employee not found', None, 404)
        
        emp_data = {
            'id': employee.id,
            'first_name': employee.first_name,
            'last_name': employee.last_name,
            'email': employee.email,
            'phone': employee.phone,
            'employee_id': employee.employee_id,
            'nric': employee.nric,
            'date_of_birth': employee.date_of_birth.isoformat() if employee.date_of_birth else None,
            'designation': employee.designation.name if employee.designation else None,
            'department': employee.department.name if employee.department else None,
            'company': employee.company.name if employee.company else None,
            'joining_date': employee.joining_date.isoformat() if employee.joining_date else None,
            'status': 'active' if employee.is_active else 'inactive',
            'profile_image_path': employee.profile_image_path
        }
        
        return api_response('success', 'Employee details retrieved', emp_data, 200)
    
    except Exception as e:
        logger.error(f"Get employee error: {e}")
        return api_response('error', f'Failed to retrieve employee: {str(e)}', None, 500)


# ============================================================================
# ATTENDANCE API ENDPOINTS
# ============================================================================

@app.route('/api/attendance', methods=['GET'])
@token_required
def mobile_api_get_attendance():
    """
    list Attendance
    ---
    tags:
      - Attendance
    security:
      - Bearer: []
    parameters:
      - name: employee_id
        in: query
        type: integer
      - name: from_date
        in: query
        type: string
        format: date
      - name: to_date
        in: query
        type: string
        format: date
    responses:
      200:
        description: Attendance history
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        employee_id = request.args.get('employee_id', type=int)
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        query = Attendance.query
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        if from_date:
            try:
                from_dt = datetime.fromisoformat(from_date).date()
                query = query.filter(Attendance.date >= from_dt)
            except:
                pass
        
        if to_date:
            try:
                to_dt = datetime.fromisoformat(to_date).date()
                query = query.filter(Attendance.date <= to_dt)
            except:
                pass
        
        paginated = query.order_by(Attendance.date.desc()).paginate(page=page, per_page=per_page)
        
        attendance_records = []
        for att in paginated.items:
            attendance_records.append({
                'id': att.id,
                'employee_id': att.employee_id,
                'date': att.date.isoformat() if att.date else None,
                'check_in': att.check_in.isoformat() if att.check_in else None,
                'check_out': att.check_out.isoformat() if att.check_out else None,
                'status': att.status,
                'duration_hours': att.duration_hours if hasattr(att, 'duration_hours') else None
            })
        
        return api_response('success', 'Attendance records retrieved', {
            'records': attendance_records,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, 200)
    
    except Exception as e:
        logger.error(f"Get attendance error: {e}")
        return api_response('error', f'Failed to retrieve attendance: {str(e)}', None, 500)


@app.route('/api/attendance/mark', methods=['POST'])
@token_required
def mobile_api_mark_attendance():
    """
    Mark Attendance
    ---
    tags:
      - Attendance
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - employee_id
            - action
          properties:
            employee_id:
              type: integer
            action:
              type: string
              enum: [check_in, check_out]
            latitude:
              type: number
            longitude:
              type: number
    responses:
      200:
        description: Attendance marked successfully
    """
    try:
        if not request.is_json:
            return api_response('error', 'Content-Type must be application/json', None, 400)
        
        data = request.get_json()
        employee_id = data.get('employee_id')
        action = data.get('action')  # 'check_in' or 'check_out'
        
        if not employee_id or not action:
            return api_response('error', 'employee_id and action are required', None, 400)
        
        employee = Employee.query.get(employee_id)
        if not employee:
            return api_response('error', 'Employee not found', None, 404)
        
        # Get company timezone for consistent date calculation
        from pytz import timezone, utc
        company = employee.company
        timezone_str = company.timezone if company else 'UTC'
        company_tz = timezone(timezone_str)
        
        # Get today's date in company timezone
        now_utc = datetime.now(utc)
        today = now_utc.astimezone(company_tz).date()
        current_time = now_utc.astimezone(company_tz)
        
        attendance = Attendance.query.filter_by(
            employee_id=employee_id,
            date=today
        ).first()
        
        if not attendance:
            attendance = Attendance(
                employee_id=employee_id,
                date=today,
                status='Incomplete', # Default start
                sub_status='Pending Out',
                timezone=timezone_str
            )
            db.session.add(attendance)
        else:
            # Update timezone on existing records
            attendance.timezone = timezone_str
        
        if action == 'check_in':
            attendance.clock_in = current_time.time()
            attendance.clock_in_time = current_time
            attendance.status = 'Incomplete'
            attendance.sub_status = 'Pending Out'
            
        elif action == 'check_out':
            attendance.clock_out = current_time.time()
            attendance.clock_out_time = current_time
            
            # Determine status
            has_in = attendance.clock_in is not None or attendance.clock_in_time is not None
            if has_in:
                attendance.status = 'Present'
                attendance.sub_status = None
            else:
                attendance.status = 'Incomplete'
                attendance.sub_status = 'Pending In'
        else:
            return api_response('error', 'Invalid action. Must be check_in or check_out', None, 400)
        
        db.session.commit()
        
        return api_response('success', f'Attendance {action} recorded', {
            'employee_id': attendance.employee_id,
            'date': attendance.date.isoformat(),
            'clock_in': attendance.clock_in.isoformat() if attendance.clock_in else None,
            'clock_out': attendance.clock_out.isoformat() if attendance.clock_out else None
        }, 200)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Mark attendance error: {e}")
        return api_response('error', f'Failed to mark attendance: {str(e)}', None, 500)


# ============================================================================
# OT MANAGEMENT API ENDPOINTS
# ============================================================================

@app.route('/api/ot/types', methods=['GET'])
@token_required
def mobile_api_get_ot_types():
    """
    Get OT Types
    ---
    tags:
      - Overtime
    security:
      - Bearer: []
    responses:
      200:
        description: List of available OT types
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  multiplier:
                    type: number
    """
    try:
        user = get_user_from_token_or_session()
        if not user:
             return api_response('error', 'User not found', None, 401)
        
        # Get company ID (handle both direct user.company_id and employee profile)
        company_id = user.company_id
        if not company_id and hasattr(user, 'employee_profile') and user.employee_profile:
             company_id = user.employee_profile.company_id
             
        if not company_id:
             return api_response('error', 'Company not found for user', None, 400)

        # Get company to find tenant
        company = Company.query.get(company_id)
        tenant_id = company.tenant_id if company else None
        
        ot_types = []
        if tenant_id:
            # Find all companies in this tenant to get shared OT types (or specific ones)
            # Simplified: Just match company_id or share logic if needed. 
            # For now, following logic in routes_ot.py: match company_id in list of tenant companies.
            company_ids = db.session.query(Company.id).filter_by(tenant_id=tenant_id).subquery()
            types = OTType.query.filter(
                OTType.company_id.in_(company_ids),
                OTType.is_active == True
            ).order_by(OTType.display_order).all()
            
            for t in types:
                ot_types.append({
                    'id': t.id,
                    'name': t.name,
                    'multiplier': float(t.rate_multiplier) if t.rate_multiplier else 1.0,
                    'code': t.code
                })
        
        return api_response('success', 'OT Types retrieved', ot_types, 200)

    except Exception as e:
        logger.error(f"Get OT types error: {e}")
        return api_response('error', f'Failed to retrieve OT types: {str(e)}', None, 500)


@app.route('/api/ot/request', methods=['POST'])
@token_required
def mobile_api_create_ot_request():
    """
    Create OT Request
    ---
    tags:
      - Overtime
    description: Logs OT and immediately submits it for approval
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - ot_date
            - ot_type_id
            - quantity
          properties:
            ot_date:
              type: string
              format: date
              example: "2024-01-15"
            ot_type_id:
              type: integer
            quantity:
              type: number
              description: Number of hours
            notes:
              type: string
    responses:
      200:
        description: OT submitted successfully
    """
    try:
        user = get_user_from_token_or_session()
        employee = Employee.query.filter_by(user_id=user.id).first()
        
        if not employee:
            return api_response('error', 'Employee profile not found', None, 404)
            
        data = request.get_json()
        if not data:
             return api_response('error', 'No input data provided', None, 400)
             
        ot_date_str = data.get('ot_date')
        ot_type_id = data.get('ot_type_id')
        quantity = data.get('quantity')
        notes = data.get('notes', '')
        
        if not ot_date_str or not ot_type_id or not quantity:
            return api_response('error', 'Missing required fields: ot_date, ot_type_id, quantity', None, 400)

        # 1. Parse Data
        try:
             ot_date = datetime.strptime(ot_date_str, '%Y-%m-%d').date()
             quantity = float(quantity)
             ot_type_id = int(ot_type_id)
        except ValueError:
             return api_response('error', 'Invalid date or number format', None, 400)

        # 2. Validation
        ot_type = OTType.query.get(ot_type_id)
        if not ot_type:
             return api_response('error', 'Invalid OT Type', None, 400)
             
        if not employee.manager_id:
             return api_response('error', 'No reporting manager assigned to your profile', None, 400)
             
        manager = Employee.query.options(joinedload(Employee.user)).filter_by(id=employee.manager_id).first()
        if not manager or not manager.user_id:
             return api_response('error', 'Reporting manager has no user account', None, 400)

        # 3. Calculate Amount (Logic from routes_ot.py)
        base_rate = 0
        if employee.payroll_config and employee.payroll_config.ot_rate_per_hour:
             base_rate = float(employee.payroll_config.ot_rate_per_hour)
        elif employee.hourly_rate:
             base_rate = float(employee.hourly_rate)
        elif employee.basic_salary:
             base_rate = float(employee.basic_salary) / 173.33
             
        multiplier = float(ot_type.rate_multiplier) if ot_type.rate_multiplier else 1.0
        effective_rate = round(base_rate * multiplier, 2)
        total_amount = round(effective_rate * quantity, 2)

        # 4. Create OT Request (Directly to Pending Manager)
        # We skip the "Draft" state of OTAttendance and go straight to OTRequest if possible,
        # BUT the logic in routes_ot.py uses OTAttendance as the base record.
        # So we follow: Create OTAttendance (Submitted) -> Create OTRequest -> Create OTApproval
        
        # Step A: Create OTAttendance
        new_attendance = OTAttendance(
            employee_id=employee.id,
            company_id=employee.company_id,
            ot_date=ot_date,
            ot_type_id=ot_type_id,
            quantity=quantity,
            rate=effective_rate,
            amount=total_amount,
            status='Submitted',
            notes=notes,
            created_by=user.username,
            ot_hours=quantity
        )
        db.session.add(new_attendance)
        db.session.flush()

        # Step B: Create OTRequest
        ot_request = OTRequest(
            employee_id=employee.id,
            company_id=employee.company_id,
            ot_date=ot_date,
            ot_type_id=ot_type_id,
            requested_hours=quantity,
            reason=notes or 'Mobile OT Submission',
            status='pending_manager',
            created_by=user.username
        )
        db.session.add(ot_request)
        db.session.flush()

        # Step C: Create Approval 
        ot_approval = OTApproval(
            ot_request_id=ot_request.id,
            approver_id=manager.user_id,
            approval_level=1,
            status='pending_manager',
            comments='Submitted via Mobile App'
        )
        db.session.add(ot_approval)
        
        db.session.commit()
        
        return api_response('success', 'OT request submitted successfully', {
            'id': ot_request.id,
            'status': 'pending_manager',
            'amount': total_amount
        }, 200)

    except Exception as e:
        db.session.rollback()
        logger.error(f"Create OT request error: {e}")
        return api_response('error', f'Failed to create OT request: {str(e)}', None, 500)


# ============================================================================
# LEAVE MANAGEMENT API ENDPOINTS
# ============================================================================

@app.route('/api/leave/requests', methods=['GET'])
@token_required
def mobile_api_get_leave_requests():
    """
    List Leave Requests
    ---
    tags:
      - Leave
    security:
      - Bearer: []
    parameters:
      - name: status
        in: query
        type: string
        enum: [pending, approved, rejected]
    responses:
      200:
        description: List of leave requests
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        employee_id = request.args.get('employee_id', type=int)
        status = request.args.get('status')
        
        query = Leave.query
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        if status:
            query = query.filter_by(status=status)
        
        paginated = query.order_by(Leave.created_at.desc()).paginate(page=page, per_page=per_page)
        
        leave_requests = []
        for leave in paginated.items:
            leave_requests.append({
                'id': leave.id,
                'employee_id': leave.employee_id,
                'employee_name': f"{leave.employee.first_name} {leave.employee.last_name}" if leave.employee else None,
                'from_date': leave.from_date.isoformat() if leave.from_date else None,
                'to_date': leave.to_date.isoformat() if leave.to_date else None,
                'leave_type': leave.leave_type,
                'reason': leave.reason,
                'status': leave.status,
                'created_at': leave.created_at.isoformat() if leave.created_at else None
            })
        
        return api_response('success', 'Leave requests retrieved', {
            'requests': leave_requests,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, 200)
    
    except Exception as e:
        logger.error(f"Get leave requests error: {e}")
        return api_response('error', f'Failed to retrieve leave requests: {str(e)}', None, 500)


@app.route('/api/leave/request', methods=['POST'])
@token_required
def mobile_api_create_leave_request():
    """
    Create Leave Request
    ---
    tags:
      - Leave
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        schema:
          type: object
          required:
            - employee_id
            - from_date
            - to_date
            - leave_type
          properties:
            employee_id:
              type: integer
            from_date:
              type: string
              format: date
            to_date:
              type: string
              format: date
            leave_type:
              type: string
            reason:
              type: string
    responses:
      201:
        description: Leave request created
    """
    try:
        if not request.is_json:
            return api_response('error', 'Content-Type must be application/json', None, 400)
        
        data = request.get_json()
        required_fields = ['employee_id', 'from_date', 'to_date', 'leave_type']
        
        for field in required_fields:
            if not data.get(field):
                return api_response('error', f'{field} is required', None, 400)
        
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return api_response('error', 'Employee not found', None, 404)
        
        try:
            from_date = datetime.fromisoformat(data['from_date']).date()
            to_date = datetime.fromisoformat(data['to_date']).date()
        except:
            return api_response('error', 'Invalid date format. Use YYYY-MM-DD', None, 400)
        
        leave_request = Leave(
            employee_id=data['employee_id'],
            from_date=from_date,
            to_date=to_date,
            leave_type=data['leave_type'],
            reason=data.get('reason', ''),
            status='pending'
        )
        
        db.session.add(leave_request)
        db.session.commit()
        
        return api_response('success', 'Leave request created', {
            'id': leave_request.id,
            'employee_id': leave_request.employee_id,
            'from_date': leave_request.from_date.isoformat(),
            'to_date': leave_request.to_date.isoformat(),
            'status': leave_request.status
        }, 201)
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Create leave request error: {e}")
        return api_response('error', f'Failed to create leave request: {str(e)}', None, 500)


# ============================================================================
# PAYROLL API ENDPOINTS
# ============================================================================

@app.route('/api/payroll/payslips', methods=['GET'])
@token_required
def mobile_api_get_payslips():
    """
    Get Payslips
    ---
    tags:
      - Payroll
    security:
      - Bearer: []
    responses:
      200:
        description: List of payslips
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        employee_id = request.args.get('employee_id', type=int)
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        
        query = Payroll.query
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        if from_date:
            try:
                from_dt = datetime.fromisoformat(from_date).date()
                query = query.filter(Payroll.pay_period_end >= from_dt)
            except:
                pass
        
        if to_date:
            try:
                to_dt = datetime.fromisoformat(to_date).date()
                query = query.filter(Payroll.pay_period_end <= to_dt)
            except:
                pass
        
        paginated = query.order_by(Payroll.pay_period_end.desc()).paginate(page=page, per_page=per_page)
        
        payslips = []
        for payroll in paginated.items:
            payslips.append({
                'id': payroll.id,
                'employee_id': payroll.employee_id,
                'pay_period_start': payroll.pay_period_start.isoformat() if payroll.pay_period_start else None,
                'pay_period_end': payroll.pay_period_end.isoformat() if payroll.pay_period_end else None,
                'basic_salary': float(payroll.basic_salary) if payroll.basic_salary else 0,
                'total_earnings': float(payroll.total_earnings) if payroll.total_earnings else 0,
                'total_deductions': float(payroll.total_deductions) if payroll.total_deductions else 0,
                'net_salary': float(payroll.net_salary) if payroll.net_salary else 0,
                'status': payroll.status if hasattr(payroll, 'status') else 'draft'
            })
        
        return api_response('success', 'Payslips retrieved', {
            'payslips': payslips,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': paginated.total,
                'pages': paginated.pages
            }
        }, 200)
    
    except Exception as e:
        logger.error(f"Get payslips error: {e}")
        return api_response('error', f'Failed to retrieve payslips: {str(e)}', None, 500)


# ============================================================================
# DASHBOARD/STATISTICS API ENDPOINTS
# ============================================================================

@app.route('/api/dashboard/stats', methods=['GET'])
@token_required
def mobile_api_get_dashboard_stats():
    """
    Dashboard Stats
    ---
    tags:
      - Dashboard
    security:
      - Bearer: []
    responses:
      200:
        description: Dashboard statistics
    """
    try:
        user = get_user_from_token_or_session()
        if not user:
            return api_response('error', 'User not found', None, 401)
        
        # Get company ID from user
        company_id = user.company_id if hasattr(user, 'company_id') else None
        
        query_filter = {}
        if company_id:
            query_filter['company_id'] = company_id
        
        # Count statistics
        total_employees = Employee.query.filter_by(is_active=True, **query_filter).count()
        total_attendance_today = Attendance.query.filter_by(date=date.today()).count()
        
        # Leave requests pending
        pending_leaves = Leave.query.filter_by(status='pending', **query_filter).count()
        
        # Today's check-ins
        today_checkins = Attendance.query.filter(
            Attendance.date == date.today(),
            Attendance.check_in.isnot(None)
        ).count()
        
        stats = {
            'total_employees': total_employees,
            'present_today': today_checkins,
            'pending_leave_requests': pending_leaves,
            'attendance_rate': round((today_checkins / total_employees * 100), 2) if total_employees > 0 else 0
        }
        
        return api_response('success', 'Dashboard statistics retrieved', stats, 200)
    
    except Exception as e:
        logger.error(f"Get dashboard stats error: {e}")
        return api_response('error', f'Failed to retrieve dashboard stats: {str(e)}', None, 500)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/api/health', methods=['GET'])
def mobile_api_health_check():
    """
    Health Check
    ---
    tags:
      - System
    responses:
      200:
        description: API is healthy
    """
    try:
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        return api_response('success', 'API is healthy', {
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }, 200)
    
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return api_response('error', 'API is unhealthy', {'error': str(e)}, 503)


# ============================================================================
# ERROR HANDLERS FOR API
# ============================================================================

@app.errorhandler(404)
def mobile_api_not_found(error):
    """Handle 404 errors"""
    if request.path.startswith('/api'):
        return api_response('error', 'Endpoint not found', None, 404)
    return error


@app.errorhandler(500)
def mobile_api_internal_error(error):
    """Handle 500 errors"""
    if request.path.startswith('/api'):
        logger.error(f"Internal server error: {error}")
        return api_response('error', 'Internal server error', None, 500)
    return error
