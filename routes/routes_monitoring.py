from flask import Blueprint, render_template, request, flash, redirect, url_for
from app import db
from core.models import JobExecutionLog
from core.utils import export_to_csv # Keep if needed, or remove
from core.auth import require_role
from services.daily_attendance_task import process_eod_attendance
from datetime import datetime, date

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/monitoring/jobs')
@require_role(['Super Admin'])
def job_logs():
    page = request.args.get('page', 1, type=int)
    logs = JobExecutionLog.query.order_by(JobExecutionLog.started_at.desc()).paginate(page=page, per_page=20)
    return render_template('monitoring/job_logs.html', logs=logs)

@monitoring_bp.route('/monitoring/jobs/run/<job_name>', methods=['POST'])
@require_role(['Super Admin'])
def run_job(job_name):
    if job_name == 'daily_attendance_eod':
        date_str = request.form.get('date')
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
        
        # Manually trigger the task
        try:
            result = process_eod_attendance(target_date)
            
            if result.get('success'):
                 flash(f"Job {job_name} completed successfully for {target_date}.", 'success')
            else:
                 flash(f"Job {job_name} failed: {result.get('error')}", 'error')
        except Exception as e:
            flash(f"Critical error running job: {str(e)}", 'error')
             
    else:
        flash(f"Unknown job: {job_name}", 'error')
        
    return redirect(url_for('monitoring.job_logs'))
