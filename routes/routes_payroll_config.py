"""
Routes for Payslip Configuration (Templates, Layouts, Images)
"""
import os
import secrets
from datetime import datetime
from functools import wraps
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload

from app import app, db
from core.models import Tenant, Company, PayslipTemplate, User

# Define allowed roles for this module
ALLOWED_ROLES = ['Super Admin', 'Tenant Admin', 'HR Manager']

def require_payslip_config_access(f):
    """Decorator to check if user has access to payslip configuration"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        user_role = current_user.role.name if current_user.role else None
        if user_role not in ALLOWED_ROLES:
            flash('You do not have permission to access Payslip Configuration.', 'error')
            return redirect(url_for('dashboard'))
            
        return f(*args, **kwargs)
    return decorated_function

@app.route('/payroll/config/templates', methods=['GET'])
@require_payslip_config_access
def payroll_config_templates_list():
    """List all payslip templates"""
    templates = []
    
    # Filter based on role
    if current_user.role.name == 'Super Admin':
        templates = PayslipTemplate.query.options(joinedload(PayslipTemplate.company)).all()
    elif current_user.role.name in ['Tenant Admin', 'HR Manager']:
        if current_user.tenant:
             templates = PayslipTemplate.query.filter_by(tenant_id=current_user.tenant.id).options(joinedload(PayslipTemplate.company)).all()
    
    return render_template('payroll/config/list.html', templates=templates)

@app.route('/payroll/config/templates/new', methods=['GET'])
@require_payslip_config_access
def payroll_config_template_new():
    """Show the visual editor for creating a new template"""
    companies = []
    if current_user.role.name == 'Super Admin':
        companies = Company.query.all()
    else:
        companies = current_user.get_accessible_companies()
        
    return render_template('payroll/config/editor.html', companies=companies, template=None)

@app.route('/payroll/config/templates/<int:template_id>/edit', methods=['GET'])
@require_payslip_config_access
def payroll_config_template_edit(template_id):
    """Show the visual editor for editing an existing template"""
    template = PayslipTemplate.query.get_or_404(template_id)
    
    # Permission check
    if current_user.role.name != 'Super Admin':
        if template.tenant_id != current_user.tenant.id:
            flash('Unauthorized access to this template.', 'error')
            return redirect(url_for('payroll_config_templates_list'))
            
    companies = []
    if current_user.role.name == 'Super Admin':
        companies = Company.query.all()
    else:
        companies = current_user.get_accessible_companies()
        
    return render_template('payroll/config/editor.html', companies=companies, template=template)

@app.route('/payroll/config/templates', methods=['POST'])
@require_payslip_config_access
def payroll_config_template_save():
    """Save or Update a template"""
    try:
        data = request.json
        template_id = data.get('id')
        
        name = data.get('name')
        description = data.get('description')
        company_id = data.get('company_id')
        layout_config = data.get('layout_config', [])
        field_config = data.get('field_config', {})
        
        # New Image Paths
        # New Image Paths
        logo_path = data.get('logo_path')
        left_logo_path = data.get('left_logo_path')
        right_logo_path = data.get('right_logo_path')
        watermark_path = data.get('watermark_path')
        footer_image_path = data.get('footer_image_path')
        is_default = data.get('is_default', False)
        
        if not name:
            return jsonify({'success': False, 'message': 'Template Name is required'}), 400
            
        if template_id:
            # Update
            template = PayslipTemplate.query.get(template_id)
            if not template:
                return jsonify({'success': False, 'message': 'Template not found'}), 404
            
            # Security check
            if current_user.role.name != 'Super Admin' and template.tenant_id != current_user.tenant.id:
                 return jsonify({'success': False, 'message': 'Unauthorized'}), 403
                 
            template.name = name
            template.description = description
            template.company_id = company_id if company_id else None
            template.layout_config = layout_config
            template.field_config = field_config
            template.is_default = is_default
            template.logo_path = logo_path
            template.left_logo_path = left_logo_path
            template.right_logo_path = right_logo_path
            template.watermark_path = watermark_path
            template.footer_image_path = footer_image_path
            template.updated_by = current_user.id
            template.updated_at = datetime.utcnow()
            
        else:
            # Create
            if not current_user.tenant:
                 return jsonify({'success': False, 'message': 'No tenant context found'}), 400
                 
            template = PayslipTemplate(
                tenant_id=current_user.tenant.id,
                company_id=company_id if company_id else None,
                name=name,
                description=description,
                layout_config=layout_config,
                field_config=field_config,
                is_default=is_default,
                logo_path=logo_path,
                left_logo_path=left_logo_path,
                right_logo_path=right_logo_path,
                watermark_path=watermark_path,
                footer_image_path=footer_image_path,
                created_by=current_user.id,
                updated_by=current_user.id
            )
            db.session.add(template)
            
        db.session.commit()
        
        flash('Template saved successfully', 'success')
        return jsonify({'success': True, 'redirect_url': url_for('payroll_config_templates_list')})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/payroll/config/upload-image', methods=['POST'])
@require_payslip_config_access
def payroll_config_upload_image():
    """Async image upload for editor"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file part'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No selected file'}), 400
            
        if file:
            # Secure filename logic
            ext = file.filename.rsplit('.', 1)[1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                 return jsonify({'success': False, 'message': 'Invalid file type'}), 400
                 
            filename = secrets.token_hex(8) + '.' + ext
            
            # Save to static/uploads/payslip_assets
            upload_folder = os.path.join(app.root_path, 'static', 'uploads', 'payslip_assets')
            os.makedirs(upload_folder, exist_ok=True)
            
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)
            
            # Return relative path for frontend
            relative_path = f'uploads/payslip_assets/{filename}'
            return jsonify({'success': True, 'path': relative_path})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/payroll/config/templates/<int:template_id>/delete', methods=['POST'])
@require_payslip_config_access
def payroll_config_template_delete(template_id):
    """Delete a template"""
    template = PayslipTemplate.query.get_or_404(template_id)
    
    if current_user.role.name != 'Super Admin' and template.tenant_id != current_user.tenant.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('payroll_config_templates_list'))
        
    db.session.delete(template)
    db.session.commit()
    flash('Template deleted successfully', 'success')
    return redirect(url_for('payroll_config_templates_list'))

@app.route('/payroll/config/templates/<int:template_id>/set-default', methods=['POST'])
@require_payslip_config_access
def payroll_config_template_default(template_id):
    """Set template as default for the company"""
    template = PayslipTemplate.query.get_or_404(template_id)
    
    if current_user.role.name != 'Super Admin' and template.tenant_id != current_user.tenant.id:
         flash('Unauthorized', 'error')
         return redirect(url_for('payroll_config_templates_list'))
    
    # Reset other defaults
    if template.company_id:
        PayslipTemplate.query.filter_by(company_id=template.company_id).update({'is_default': False})
    else:
        # Tenant level default ?
        pass 
        
    template.is_default = True
    db.session.commit()
    
    flash('Template set as default', 'success')
    return redirect(url_for('payroll_config_templates_list'))

@app.route('/payroll/config/templates/preview', methods=['POST'])
@require_payslip_config_access
def payroll_config_template_preview():
    """Preview Payslip Template"""
    try:
        data = request.json
        layout_config = data.get('layout_config', [])
        
        # Determine company context for dummy data
        company = None
        company_id = data.get('company_id')
        if company_id:
            company = Company.query.get(company_id)
        elif current_user.tenant:
            # Fallback to first company or dummy info
            if current_user.tenant.companies:
                company = current_user.tenant.companies[0]
        
        # Dummy Data Generation
        preview_data = {
            'layout_config': layout_config,
            'logo_path': data.get('logo_path'),
            'watermark_path': data.get('watermark_path'),
            'footer_image_path': data.get('footer_image_path'),
            
            'company': {
                'name': company.name if company else 'ACME Corp',
                'address': company.address if company and company.address else '123 Business Rd, Singapore 123456'
            },
            
            'employee': {
                'name': 'John Doe',
                'employee_code': 'EMP001',
                'department': 'Engineering',
                'designation': 'Software Engineer',
                'joining_date': '01-01-2023',
                'location': 'Singapore',
                'bank_name': 'DBS Bank',
                'bank_account': '123-456-789',
                'pan_number': 'ABCDE1234F',
                'pf_number': 'PF/123/456',
                'esi_number': 'ESI/987/654'
            },
            
            'payroll': {
                'period': 'JANUARY 2025',
                'paid_days': 31,
                'lop_days': 0,
                'total_earnings': '5,500.00',
                'total_deductions': '500.00',
                'net_pay': '5,000.00',
                'net_pay_words': 'FIVE THOUSAND ONLY'
            },
            
            'earnings': {
                'basic': '3,000.00',
                'hra': '1,500.00',
                'transport': '500.00',
                'other': '500.00',
                'regular_pay_rate': '3,000.00',
                'regular_pay_amount': '3,000.00',
                'overtime_pay_rate': '20.00',
                'overtime_amount': '100.00',
                'others': '500.00'
            },
            
            'deductions': {
                'pf': '300.00',
                'tax': '100.00',
                'others': '100.00',
                'provident_fund': '300.00',
                'income_tax': '100.00'
            }
        }
        
        # Render HTML
        preview_html = render_template('payroll/payslip_preview.html', **preview_data)
        
        return jsonify({'success': True, 'html': preview_html})
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
