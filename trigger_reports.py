import logging
from app import app
from core.models import ReportSchedule
from services.scheduler_service import run_report_job

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("report-trigger")

def trigger_all_active_reports():
    """ Runs all active report jobs once. Suitable for Render Cron Jobs. """
    logger.info("🚀 Starting Manual Report Trigger Process...")
    
    with app.app_context():
        try:
            # 1. Fetch all active schedules
            schedules = ReportSchedule.query.filter_by(is_active=True).all()
            logger.info(f"Found {len(schedules)} active schedules.")
            
            for schedule in schedules:
                logger.info(f"Triggering report: {schedule.report_type} (ID: {schedule.id}) for Tenant: {schedule.tenant_id}")
                # We call the runner function directly
                run_report_job(schedule.id)
            
            logger.info("✅ All reports triggered successfully.")
                
        except Exception as e:
            logger.error(f"Critical error during report trigger: {e}")
            import traceback
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    trigger_all_active_reports()
