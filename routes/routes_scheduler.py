from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app import db
from core.models import ReportSchedule, Tenant
from core.auth import require_role
from services.scheduler_service import SchedulerService
from datetime import datetime

scheduler_bp = Blueprint('scheduler', __name__, url_prefix='/scheduler')

@scheduler_bp.route('/jobs', methods=['GET'])
@login_required
def list_jobs():
    try:
        if current_user.role.name not in ['Super Admin', 'Tenant Admin', 'HR Manager']:
            return "Unauthorized", 403

        # Scoping logic
        accessible_companies = current_user.get_accessible_companies()
        company_ids = [c.id for c in accessible_companies]
        
        query = ReportSchedule.query
        
        if current_user.role.name != 'Super Admin':
            # Restrict by tenant if not super admin
            tenant = current_user.tenant
            if tenant:
                query = query.filter(ReportSchedule.tenant_id == tenant.id)
            else:
                query = query.filter(ReportSchedule.id == None)

        # Filter by tenant if provided (Admin only or scoped)
        selected_tenant_id = request.args.get('tenant_id')
        if selected_tenant_id and current_user.role.name == 'Super Admin':
            query = query.filter_by(tenant_id=selected_tenant_id)
        elif not selected_tenant_id and current_user.role.name == 'Super Admin':
             pass # All for super admin
            
        schedules = query.order_by(ReportSchedule.created_at.desc()).all()
        
        from core.models import Tenant
        tenants = Tenant.query.all() if current_user.role.name == 'Super Admin' else []
        
        return render_template(
            'scheduler/index.html',
            schedules=schedules,
            tenants=tenants,
            selected_tenant_id=selected_tenant_id,
            companies=accessible_companies
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        flash(f'Error loading schedules: {str(e)}', 'danger')
        return redirect(url_for('index'))

@scheduler_bp.route('/jobs/add', methods=['POST'])
@login_required
def add_job():
    try:
        if current_user.role.name not in ['Super Admin', 'Tenant Admin', 'HR Manager']:
            return "Unauthorized", 403

        tenant_id = request.form.get('tenant_id')
        company_id = request.form.get('company_id')
        report_type = request.form.get('report_type')
        cron = request.form.get('cron_expression')
        date_filter = request.form.get('date_filter_type')
        recipients = request.form.get('recipients') # Comma separated
        
        # Security check for non-Super Admin
        if current_user.role.name != 'Super Admin':
            tenant = current_user.tenant
            if not tenant:
                flash('No tenant associated with user', 'danger')
                return redirect(url_for('scheduler.list_jobs'))
            tenant_id = str(tenant.id)
            
            # Ensure company_id is valid for this user
            if company_id:
                accessible_companies = current_user.get_accessible_companies()
                if not any(str(c.id) == company_id for c in accessible_companies):
                     flash('Invalid company selected', 'danger')
                     return redirect(url_for('scheduler.list_jobs'))

        if not tenant_id or not report_type or not cron or not recipients:
            flash('Basic fields (Tenant, Report Type, Cron, Recipients) are required', 'danger')
            return redirect(url_for('scheduler.list_jobs'))
            
        recipient_list = [r.strip() for r in recipients.split(',') if r.strip()]
        
        schedule = ReportSchedule(
            tenant_id=tenant_id,
            company_id=company_id if company_id else None,
            report_type=report_type,
            cron_expression=cron,
            date_filter_type=date_filter,
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
def delete_job(id):
    try:
        schedule = ReportSchedule.query.get_or_404(id)
        
        # Security Check
        if current_user.role.name != 'Super Admin':
            tenant = current_user.tenant
            if not tenant or schedule.tenant_id != tenant.id:
                 return "Unauthorized", 403

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

@scheduler_bp.route('/jobs/<int:id>', methods=['GET'])
@login_required
def get_job(id):
    try:
        schedule = ReportSchedule.query.get_or_404(id)
        
        # Security Check
        if current_user.role.name != 'Super Admin':
            tenant = current_user.tenant
            if not tenant or schedule.tenant_id != tenant.id:
                 return jsonify({'error': 'Unauthorized'}), 403

        return jsonify({
            'id': schedule.id,
            'tenant_id': str(schedule.tenant_id),
            'company_id': str(schedule.company_id) if schedule.company_id else '',
            'report_type': schedule.report_type,
            'cron_expression': schedule.cron_expression,
            'date_filter_type': schedule.date_filter_type,
            'recipients': ', '.join(schedule.recipients) if schedule.recipients else '',
            'is_active': schedule.is_active
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@scheduler_bp.route('/jobs/edit/<int:id>', methods=['POST'])
@login_required
def edit_job(id):
    try:
        if current_user.role.name not in ['Super Admin', 'Tenant Admin', 'HR Manager']:
            return "Unauthorized", 403

        schedule = ReportSchedule.query.get_or_404(id)
        
        # Security Check
        if current_user.role.name != 'Super Admin':
            tenant = current_user.tenant
            if not tenant or schedule.tenant_id != tenant.id:
                 return "Unauthorized", 403

        # Update fields
        if current_user.role.name == 'Super Admin':
            tenant_id = request.form.get('tenant_id')
            if tenant_id:
                schedule.tenant_id = tenant_id

        company_id = request.form.get('company_id')
        # Security check for company_id if not super admin
        if current_user.role.name != 'Super Admin' and company_id:
            accessible_companies = current_user.get_accessible_companies()
            if not any(str(c.id) == company_id for c in accessible_companies):
                 flash('Invalid company selected', 'danger')
                 return redirect(url_for('scheduler.list_jobs'))
        
        schedule.company_id = company_id if company_id else None
        schedule.report_type = request.form.get('report_type')
        schedule.cron_expression = request.form.get('cron_expression')
        schedule.date_filter_type = request.form.get('date_filter_type')
        
        recipients = request.form.get('recipients')
        if recipients:
            schedule.recipients = [r.strip() for r in recipients.split(',') if r.strip()]
        
        schedule.is_active = 'is_active' in request.form
        
        db.session.commit()
        
        # Refresh APScheduler Job
        SchedulerService.add_job(schedule)
        
        flash('Schedule updated successfully', 'success')
        return redirect(url_for('scheduler.list_jobs'))
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating schedule: {str(e)}', 'danger')
        return redirect(url_for('scheduler.list_jobs'))

@scheduler_bp.route('/trigger/<int:id>', methods=['POST'])
@login_required
def trigger_job(id):
    try:
        schedule = ReportSchedule.query.get_or_404(id)
        # Security Check
        if current_user.role.name != 'Super Admin':
            tenant = current_user.tenant
            if not tenant or schedule.tenant_id != tenant.id:
                 return "Unauthorized", 403

        # Manually trigger
        from services.scheduler_service import run_report_job
        run_report_job(id)
        
        flash('Job triggered manually', 'success')
        return redirect(url_for('scheduler.list_jobs'))
    except Exception as e:
        flash(f'Error triggering job: {str(e)}', 'danger')
        return redirect(url_for('scheduler.list_jobs'))
@scheduler_bp.route('/preview/<int:id>', methods=['GET'])
@login_required
def preview_job(id):
    try:
        schedule = ReportSchedule.query.get_or_404(id)
        
        # Security Check
        if current_user.role.name != 'Super Admin':
            tenant = current_user.tenant
            if not tenant or schedule.tenant_id != tenant.id:
                 return jsonify({'error': 'Unauthorized'}), 403

        from services.report_service import ReportService
        start_date, end_date = ReportService.get_dates_from_filter(schedule.date_filter_type or 'yesterday')
        
        data = []
        if schedule.report_type == 'Daily Attendance':
            data = ReportService.get_attendance_register_data(
                schedule.tenant_id, schedule.company_id, start_date, end_date
            )
        elif schedule.report_type == 'Absentee Report':
            data = ReportService.get_absentee_report_data(
                schedule.tenant_id, schedule.company_id, start_date
            )
        elif schedule.report_type == 'Overtime Report':
            data = ReportService.get_overtime_report_data(
                schedule.tenant_id, schedule.company_id, start_date, end_date
            )

        return jsonify({
            'report_type': schedule.report_type,
            'start_date': str(start_date),
            'end_date': str(end_date),
            'data': data
        })
    except Exception as e:
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500
