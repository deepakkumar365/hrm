from flask import current_app
from core.models import ReportSchedule, db
from app import scheduler

class SchedulerService:
    @staticmethod
    def schedule_existing_jobs():
        """Load all active schedules from DB and add to APScheduler"""
        with scheduler.app.app_context():
            schedules = ReportSchedule.query.filter_by(is_active=True).all()
            for sched in schedules:
                SchedulerService.add_job(sched)

    @staticmethod
    def add_job(schedule_obj):
        """Add a single job to the scheduler"""
        try:
            # Parse cron expression
            # Expected format: "minute hour day month day_of_week"
            # e.g. "30 18 * * 1-5"
            cron_parts = schedule_obj.cron_expression.split()
            if len(cron_parts) != 5:
                # Handle extended cron or errors; minimal fallback
                # For now assume simplified or standard cron 5 fields
                minute, hour, day, month, day_of_week = cron_parts
            else:
                minute, hour, day, month, day_of_week = cron_parts

            scheduler.add_job(
                id=str(schedule_obj.id),
                func='services.scheduler_service:run_report_job',
                args=[schedule_obj.id],
                trigger='cron',
                minute=minute,
                hour=hour,
                day=day,
                month=month,
                day_of_week=day_of_week,
                replace_existing=True
            )
            current_app.logger.info(f"Scheduled job {schedule_obj.id} for {schedule_obj.report_type}")
        except Exception as e:
            current_app.logger.error(f"Failed to schedule job {schedule_obj.id}: {str(e)}")

    @staticmethod
    def remove_job(schedule_id):
        try:
            scheduler.remove_job(str(schedule_id))
        except Exception as e:
            current_app.logger.warning(f"Could not remove job {schedule_id}: {str(e)}")

def run_report_job(schedule_id):
    """The function executed by the scheduler"""
    with scheduler.app.app_context():
        try:
            schedule = ReportSchedule.query.get(schedule_id)
            if not schedule or not schedule.is_active:
                return

            # Logic to generate and send report
            # This would likely call another service like ReportService
            # For now, we'll just log and maybe send a test email
            
            from services.email_service import EmailService
            
            current_app.logger.info(f"Running report {schedule.report_type} for Tenant {schedule.tenant_id}")
            
            # Example: Send email to recipients
            if schedule.recipients:
                subject = f"Scheduled Report: {schedule.report_type}"
                body = f"This is your scheduled report for {schedule.report_type}."
                
                # Iterate recipients (supports JSON list)
                recipients = schedule.recipients if isinstance(schedule.recipients, list) else []
                for recipient in recipients:
                    EmailService.send_email(schedule.tenant_id, recipient, subject, body)
            
            # Update last run
            schedule.last_run_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Error executing job {schedule_id}: {str(e)}")
from datetime import datetime
