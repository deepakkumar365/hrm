from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from core.models import EmailConfig, EmailLog, Tenant
from core.auth import require_role
from services.email_service import EmailService
from datetime import datetime

email_bp = Blueprint('email', __name__, url_prefix='/email')

# =====================================================================
# Email Configuration
# =====================================================================

@email_bp.route('/config', methods=['GET', 'POST'])
@login_required
def email_config():
    """Manage Email Configuration for Tenants"""
    try:
        if current_user.role.name not in ['Super Admin', 'Tenant Admin', 'HR Manager']:
            return "Unauthorized", 403

        # Scoping logic
        if current_user.role.name == 'Super Admin':
            tenants = Tenant.query.all()
            selected_tenant_id = request.args.get('tenant_id')
            if not selected_tenant_id and tenants:
                selected_tenant_id = str(tenants[0].id)
        else:
            # Tenant Admin / HR Manager can only see their own tenant
            tenant = getattr(current_user, 'tenant', None)
            if not tenant:
                flash('No tenant associated with user', 'danger')
                return redirect(url_for('index'))
            tenants = [tenant]
            selected_tenant_id = str(tenant.id)

        current_config = None
        if selected_tenant_id:
            current_config = EmailConfig.query.filter_by(tenant_id=selected_tenant_id).first()

        if request.method == 'POST':
            tenant_id = request.form.get('tenant_id')
            
            # Security check for POST
            if current_user.role.name != 'Super Admin':
                tenant_id = str(current_user.tenant.id)

            if not tenant_id:
                flash('Tenant ID is required', 'danger')
                return redirect(url_for('email.email_config'))
                
            config = EmailConfig.query.filter_by(tenant_id=tenant_id).first()
            if not config:
                config = EmailConfig(tenant_id=tenant_id)
                db.session.add(config)
            
            config.provider = request.form.get('provider', 'SMTP')
            
            # SMTP Fields
            config.smtp_host = request.form.get('smtp_host')
            config.smtp_port = int(request.form.get('smtp_port', 587)) if request.form.get('smtp_port') else None
            config.smtp_user = request.form.get('smtp_user')
            config.smtp_password = request.form.get('smtp_password')
            
            # AWS Fields
            config.aws_access_key = request.form.get('aws_access_key')
            config.aws_secret_key = request.form.get('aws_secret_key')
            config.aws_region = request.form.get('aws_region')
            config.aws_topic_arn = request.form.get('aws_topic_arn')

            config.from_email = request.form.get('from_email')
            config.from_name = request.form.get('from_name')
            config.use_tls = 'use_tls' in request.form
            config.use_ssl = 'use_ssl' in request.form
            config.is_active = 'is_active' in request.form
            
            db.session.commit()
            flash('Email Configuration updated successfully', 'success')
            return redirect(url_for('email.email_config', tenant_id=tenant_id))

        return render_template(
            'email/config.html',
            tenants=tenants if current_user.role.name == 'Super Admin' else [],
            selected_tenant_id=selected_tenant_id,
            config=current_config
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        flash(f'Error loading email config: {str(e)}', 'danger')
        return redirect(url_for('index'))

# =====================================================================
# Email Testing
# =====================================================================

@email_bp.route('/test', methods=['POST'])
@login_required
def send_test_email():
    try:
        if current_user.role.name not in ['Super Admin', 'Tenant Admin', 'HR Manager']:
            return "Unauthorized", 403

        tenant_id = request.form.get('tenant_id')
        
        # Security check for tenant_id
        if current_user.role.name != 'Super Admin':
            tenant_id = str(current_user.tenant.id)
        recipient = request.form.get('test_recipient')
        
        if not tenant_id or not recipient:
            return jsonify({'success': False, 'message': 'Tenant ID and Recipient are required'}), 400
            
        subject = "Test Email from HRM Email Service"
        body = f"<h3>Test Email</h3><p>This is a test email sent from the HRM Email Service configuration page.</p><p>Time: {datetime.now()}</p>"
        
        success, message = EmailService.send_email(tenant_id, recipient, subject, body)
        
        if success:
            return jsonify({'success': True, 'message': 'Test email sent successfully'})
        else:
            return jsonify({'success': False, 'message': f'Failed to send email: {message}'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# =====================================================================
# Email Dashboard
# =====================================================================

@email_bp.route('/dashboard', methods=['GET'])
@email_bp.route('/dashboard/logs', methods=['GET'])
@login_required
def email_dashboard():
    try:
        if current_user.role.name not in ['Super Admin', 'Tenant Admin', 'HR Manager']:
            return "Unauthorized", 403

        query = EmailLog.query
        if current_user.role.name != 'Super Admin':
             tenant = getattr(current_user, 'tenant', None)
             if not tenant:
                 flash('No tenant associated with user', 'danger')
                 return redirect(url_for('index'))
             query = query.filter_by(tenant_id=tenant.id)

        # Stats
        total_sent = query.filter_by(status='Sent').count()
        total_failed = query.filter_by(status='Failed').count()
        
        # Recent logs
        page = request.args.get('page', 1, type=int)
        per_page = 20
        logs = query.order_by(EmailLog.sent_at.desc()).paginate(page=page, per_page=per_page)
        
        return render_template(
            'email/dashboard.html',
            total_sent=total_sent,
            total_failed=total_failed,
            logs=logs
        )
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'danger')
        return redirect(url_for('index'))
