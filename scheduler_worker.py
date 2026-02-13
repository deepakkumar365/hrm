import os
import time
import logging
from app import app
from services.scheduler_service import SchedulerService

# Configure logging for the worker
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("scheduler-worker")

def run_worker():
    """ Runs the scheduler in a dedicated process. """
    logger.info("🚀 Starting Dedicated Scheduler Worker...")
    
    # Ensure scheduler is enabled for this process
    os.environ["ENABLE_SCHEDULER"] = "true"
    
    with app.app_context():
        try:
            # 1. Initialize and load existing jobs from DB
            logger.info("Loading existing jobs from database...")
            SchedulerService.schedule_existing_jobs()
            
            logger.info("Scheduler started. Press Ctrl+C to exit.")
            
            # 2. Keep the process alive
            # APScheduler's BackgroundScheduler runs in its own threads,
            # so we just need to keep the main thread from exiting.
            while True:
                time.sleep(60)
                
        except (KeyboardInterrupt, SystemExit):
            logger.info("Stopping scheduler worker...")
        except Exception as e:
            logger.error(f"Critical error in scheduler worker: {e}")
            import traceback
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    run_worker()
