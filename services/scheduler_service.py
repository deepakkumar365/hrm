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

            from services.email_service import EmailService
            from services.report_service import ReportService
            from core.models import Company, User
            
            current_app.logger.info(f"Running report {schedule.report_type} (ID: {schedule.id}) for Tenant {schedule.tenant_id}")
            
            # 1. Determine Date Range
            start_date, end_date = ReportService.get_dates_from_filter(schedule.date_filter_type or 'yesterday')
            
            # 2. Determine scope
            is_consolidated = (schedule.scope == 'consolidated')
            
            if is_consolidated:
                # Get all accessible companies for this schedule
                companies_to_report = []
                if schedule.created_by:
                    creator = User.query.get(schedule.created_by)
                    if creator:
                        companies_to_report = creator.get_accessible_companies()
                
                # Fallback: all companies in the tenant
                if not companies_to_report:
                    companies_to_report = Company.query.filter_by(tenant_id=schedule.tenant_id).all()
                
                if not companies_to_report:
                    current_app.logger.warning(f"No companies found for consolidated report {schedule.id}")
                    return
                
                # Generate a single combined CSV with Company column
                from services.report_service import ReportService
                all_data = []
                for comp in companies_to_report:
                    if schedule.report_type == 'Daily Attendance':
                        rows = ReportService.get_attendance_register_data(
                            schedule.tenant_id, comp.id, start_date, end_date, include_company_name=True
                        )
                    elif schedule.report_type == 'Absentee Report':
                        rows = ReportService.get_absentee_report_data(
                            schedule.tenant_id, comp.id, start_date, include_company_name=True
                        )
                    elif schedule.report_type == 'Overtime Report':
                        rows = ReportService.get_overtime_report_data(
                            schedule.tenant_id, comp.id, start_date, end_date, include_company_name=True
                        )
                    else:
                        rows = []
                    all_data.extend(rows)
                
                if not all_data:
                    current_app.logger.warning(f"No data generated for consolidated report {schedule.id}")
                    return
                
                # Write single CSV
                import io, csv
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=all_data[0].keys())
                writer.writeheader()
                writer.writerows(all_data)
                csv_content = output.getvalue()
                
                filename = f"consolidated_{schedule.report_type.lower().replace(' ', '_')}_{start_date}_to_{end_date}.csv"
                attachments = [{
                    'filename': filename,
                    'data': csv_content.encode('utf-8'),
                    'content_type': 'text/csv'
                }]
                
                subject = f"Consolidated Report: {schedule.report_type} ({start_date} to {end_date})"
                company_list = ', '.join([c.name for c in companies_to_report])
                body = f"""
                <p>Hello,</p>
                <p>Please find attached the consolidated <b>{schedule.report_type}</b> for the period <b>{start_date}</b> to <b>{end_date}</b>.</p>
                <p>This report covers <b>{len(companies_to_report)}</b> companies: {company_list}</p>
                <p>Regards,<br>HR Manager System</p>
                """
            else:
                # Single-company mode (existing behavior)
                csv_content = _generate_report_csv(
                    schedule.report_type, schedule.tenant_id, schedule.company_id,
                    start_date, end_date, include_company_name=False
                )
                
                if not csv_content:
                    current_app.logger.warning(f"No content generated for report {schedule.id}")
                    return
                
                filename = f"report_{schedule.report_type.lower().replace(' ', '_')}_{start_date}.csv"
                attachments = [{
                    'filename': filename,
                    'data': csv_content.encode('utf-8'),
                    'content_type': 'text/csv'
                }]
                
                subject = f"Scheduled Report: {schedule.report_type} ({start_date})"
                body = f"""
                <p>Hello,</p>
                <p>Please find attached the scheduled <b>{schedule.report_type}</b> for the period <b>{start_date}</b> to <b>{end_date}</b>.</p>
                <p>Regards,<br>HR Manager System</p>
                """

            # 3. Send email to recipients
            if schedule.recipients:
                recipients = schedule.recipients if isinstance(schedule.recipients, list) else []
                for recipient in recipients:
                    EmailService.send_email(schedule.tenant_id, recipient, subject, body, attachments=attachments)
            
            # 4. Update last run
            schedule.last_run_at = datetime.utcnow()
            db.session.commit()
            
        except Exception as e:
            current_app.logger.error(f"Error executing job {schedule_id}: {str(e)}")
            import traceback
            current_app.logger.error(traceback.format_exc())


def _generate_report_csv(report_type, tenant_id, company_id, start_date, end_date, include_company_name=False):
    """Helper to generate CSV content for a single report type and company."""
    from services.report_service import ReportService
    
    if report_type == 'Daily Attendance':
        return ReportService.generate_attendance_register_csv(
            tenant_id, company_id, start_date, end_date
        )
    elif report_type == 'Absentee Report':
        return ReportService.generate_absentee_report_csv(
            tenant_id, company_id, start_date
        )
    elif report_type == 'Overtime Report':
        return ReportService.generate_overtime_report_csv(
            tenant_id, company_id, start_date, end_date
        )
    return None

from datetime import datetime

