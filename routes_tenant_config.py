"""
Routes for Tenant Administration and Configuration
Handles tenant-level settings, payslip customization, and advanced features
"""
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
from models import Tenant, TenantConfiguration, Employee, Organization
from datetime import datetime
import os
from functools import wraps

def require_login(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(roles):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in first', 'warning')
                return redirect(url_for('login'))
            
            user_role = current_user.role.name if current_user.role else None
            if user_role not in roles:
                flash('You do not have permission to access this operation!', 'error')
                return redirect(request.referrer or url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==================== TENANT CONFIGURATION ROUTES ====================

@app.route('/tenant/configuration', methods=['GET'])
@require_login
@require_role(['Tenant Admin'])
def tenant_configuration():
    """Tenant configuration management page"""
    try:
        # Get tenant from current user's organization
        if not current_user.organization or not current_user.organization.tenant_id:
            flash('No tenant associated with your organization', 'error')
            return redirect(url_for('dashboard'))
        
        tenant_id = current_user.organization.tenant_id
        tenant = Tenant.query.get(tenant_id)
        
        if not tenant:
            flash('Tenant not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Get or create tenant configuration
        config = TenantConfiguration.query.filter_by(tenant_id=tenant_id).first()
        if not config:
            config = TenantConfiguration(tenant_id=tenant_id)
            db.session.add(config)
            db.session.commit()
        
        return render_template('tenant_configuration.html', 
                             tenant=tenant, 
                             config=config)
    
    except Exception as e:
        flash(f'Error loading configuration: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


@app.route('/tenant/configuration/update', methods=['POST'])
@require_login
@require_role(['Tenant Admin'])
def tenant_configuration_update():
    """Update tenant configuration"""
    try:
        if not current_user.organization or not current_user.organization.tenant_id:
            return jsonify({'success': False, 'message': 'No tenant found'}), 400
        
        tenant_id = current_user.organization.tenant_id
        config = TenantConfiguration.query.filter_by(tenant_id=tenant_id).first()
        
        if not config:
            config = TenantConfiguration(tenant_id=tenant_id)
            db.session.add(config)
        
        # Update Employee ID Configuration
        config.employee_id_prefix = request.form.get('employee_id_prefix', 'EMP')
        config.employee_id_company_code = request.form.get('employee_id_company_code', '')
        config.employee_id_format = request.form.get('employee_id_format', 'prefix-company-number')
        config.employee_id_separator = request.form.get('employee_id_separator', '-')
        config.employee_id_pad_length = int(request.form.get('employee_id_pad_length', 4))
        config.employee_id_suffix = request.form.get('employee_id_suffix', '')
        
        # Update Overtime Configuration
        config.overtime_enabled = request.form.get('overtime_enabled') == 'on'
        config.overtime_calculation_method = request.form.get('overtime_calculation_method', 'By User')
        config.overtime_group_type = request.form.get('overtime_group_type', '')
        
        # Update Overtime Charges
        config.general_overtime_rate = float(request.form.get('general_overtime_rate', 1.5))
        config.holiday_overtime_rate = float(request.form.get('holiday_overtime_rate', 2.0))
        config.weekend_overtime_rate = float(request.form.get('weekend_overtime_rate', 1.5))
        
        config.updated_by = current_user.username
        config.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Configuration updated successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating configuration: {str(e)}'}), 500


@app.route('/tenant/configuration/logo-upload', methods=['POST'])
@require_login
@require_role(['Tenant Admin'])
def tenant_logo_upload():
    """Upload payslip logo"""
    try:
        if not current_user.organization or not current_user.organization.tenant_id:
            return jsonify({'success': False, 'message': 'No tenant found'}), 400
        
        if 'logo_file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['logo_file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Check file extension
        allowed_extensions = {'jpg', 'jpeg', 'png', 'svg'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return jsonify({'success': False, 'message': 'Invalid file format. Allowed: JPG, PNG, SVG'}), 400
        
        # Check file size (max 2MB)
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        if file_size > 2 * 1024 * 1024:  # 2MB
            return jsonify({'success': False, 'message': 'File size exceeds 2MB limit'}), 400
        file.seek(0)  # Reset to beginning
        
        # Save file
        import secrets
        tenant_id = current_user.organization.tenant_id
        filename = secrets.token_hex(8) + '_' + file.filename
        upload_dir = os.path.join('static', 'uploads', 'tenant_logos')
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Update configuration
        config = TenantConfiguration.query.filter_by(tenant_id=tenant_id).first()
        if not config:
            config = TenantConfiguration(tenant_id=tenant_id)
            db.session.add(config)
        
        # Delete old logo if exists
        if config.payslip_logo_path and os.path.exists(config.payslip_logo_path):
            try:
                os.remove(config.payslip_logo_path)
            except:
                pass  # Ignore if can't delete
        
        config.payslip_logo_path = file_path
        config.payslip_logo_filename = filename
        config.payslip_logo_uploaded_by = current_user.username
        config.payslip_logo_uploaded_at = datetime.now()
        config.updated_by = current_user.username
        config.updated_at = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Logo uploaded successfully',
            'logo_path': f'/static/{file_path.replace(chr(92), "/")}'  # Convert backslashes to forward slashes
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error uploading logo: {str(e)}'}), 500


@app.route('/tenant/configuration/generate-employee-id', methods=['POST'])
@require_login
@require_role(['Tenant Admin'])
def generate_employee_id_preview():
    """Generate preview of employee ID format"""
    try:
        prefix = request.form.get('prefix', 'EMP')
        company_code = request.form.get('company_code', 'ACME')
        separator = request.form.get('separator', '-')
        pad_length = int(request.form.get('pad_length', 4))
        suffix = request.form.get('suffix', '')
        
        # Generate sample number
        sample_number = str(1).zfill(pad_length)
        
        # Build sample ID based on format
        parts = [prefix, company_code, sample_number]
        if suffix:
            parts.append(suffix)
        
        sample_id = separator.join(filter(None, parts))
        
        return jsonify({'success': True, 'sample_id': sample_id})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating preview: {str(e)}'}), 500