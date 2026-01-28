from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from core.models import ReportSchedule, Tenant
from core.auth import require_role
from services.scheduler_service import SchedulerService
from datetime import datetime

scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/scheduler')

@scheduler_bp.route('/jobs', methods=['GET'])
@login_required
@require_role('Super Admin')
def list_jobs():
    try:
        tenants = Tenant.query.all()
        # Filter by tenant if provided
        selected_tenant_id = request.args.get('tenant_id')
        
        query = ReportSchedule.query
        if selected_tenant_id:
            query = query.filter_by(tenant_id=selected_tenant_id)
            
        schedules = query.order_by(ReportSchedule.created_at.desc()).all()
        
        return render_template(
            'scheduler/index.html',
            schedules=schedules,
            tenants=tenants,
            selected_tenant_id=selected_tenant_id
        )
    except Exception as e:
        flash(f'Error loading schedules: {str(e)}', 'danger')
        return redirect(url_for('index'))

@scheduler_bp.route('/jobs/add', methods=['POST'])
@login_required
@require_role('Super Admin')
def add_job():
    try:
        tenant_id = request.form.get('tenant_id')
        report_type = request.form.get('report_type')
        cron = request.form.get('cron_expression')
        recipients = request.form.get('recipients') # Comma separated
        
        if not tenant_id or not report_type or not cron or not recipients:
            flash('All fields are required', 'danger')
            return redirect(url_for('scheduler.list_jobs'))
            
        recipient_list = [r.strip() for r in recipients.split(',') if r.strip()]
        
        schedule = ReportSchedule(
            tenant_id=tenant_id,
            report_type=report_type,
            cron_expression=cron,
            recipients=recipient_list,
            created_by=current_user.id
        )
        db.session.add(schedule)
        db.session.commit()
        
        # Add to APScheduler
        SchedulerService.add_job(schedule)
        
        flash('Schedule created successfully', 'success')
        return redirect(url_for('scheduler.list_jobs', tenant_id=tenant_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding schedule: {str(e)}', 'danger')
        return redirect(url_for('scheduler.list_jobs'))

@scheduler_bp.route('/jobs/delete/<int:id>', methods=['POST'])
@login_required
@require_role('Super Admin')
def delete_job(id):
    try:
        schedule = ReportSchedule.query.get_or_404(id)
        tenant_id = schedule.tenant_id
        
        # Remove from APScheduler
        SchedulerService.remove_job(schedule.id)
        
        db.session.delete(schedule)
        db.session.commit()
        
        flash('Schedule deleted successfully', 'success')
        return redirect(url_for('scheduler.list_jobs', tenant_id=tenant_id))
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting schedule: {str(e)}', 'danger')
        return redirect(url_for('scheduler.list_jobs'))

@scheduler_bp.route('/trigger/<int:id>', methods=['POST'])
@login_required
@require_role('Super Admin')
def trigger_job(id):
    try:
        # Manually trigger
        from services.scheduler_service import run_report_job
        run_report_job(id)
        
        flash('Job triggered manually', 'success')
        return redirect(url_for('scheduler.list_jobs'))
    except Exception as e:
        flash(f'Error triggering job: {str(e)}', 'danger')
        return redirect(url_for('scheduler.list_jobs'))
