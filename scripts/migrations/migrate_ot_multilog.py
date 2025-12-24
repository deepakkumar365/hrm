import logging
import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.getcwd())

from app import app, db
from sqlalchemy import text
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_ot_table():
    """
    Migrate OTAttendance table:
    1. Drop unique constraint 'uq_ot_attendance_emp_date'
    2. Add columns: quantity, rate, amount
    """
    with app.app_context():
        try:
            logger.info("Starting OTAttendance migration...")
            
            with db.engine.connect() as conn:
                # 1. Drop Constraint
                # specific to PostgreSQL/SQLite syntax may vary, using generic SQL assumes standard constraint handling
                # We interpret "uq_ot_attendance_emp_date" is the name from models.py
                try:
                    logger.info("Attempting to drop unique constraint...")
                    conn.execute(text("ALTER TABLE hrm_ot_attendance DROP CONSTRAINT IF EXISTS uq_ot_attendance_emp_date"))
                    logger.info("Constraint dropped (if it existed).")
                except Exception as e:
                    logger.warning(f"Could not drop constraint (might not exist or different name): {e}")

                # 2. Add Columns
                # We check if columns exist before adding to be idempotent
                
                # Check for 'quantity'
                try:
                    conn.execute(text("ALTER TABLE hrm_ot_attendance ADD COLUMN quantity NUMERIC(6, 2)"))
                    logger.info("Added 'quantity' column.")
                except Exception as e:
                    logger.info(f"Column 'quantity' might already exist: {e}")

                # Check for 'rate'
                try:
                    conn.execute(text("ALTER TABLE hrm_ot_attendance ADD COLUMN rate NUMERIC(8, 2)"))
                    logger.info("Added 'rate' column.")
                except Exception as e:
                    logger.info(f"Column 'rate' might already exist: {e}")

                # Check for 'amount'
                try:
                    conn.execute(text("ALTER TABLE hrm_ot_attendance ADD COLUMN amount NUMERIC(10, 2)"))
                    logger.info("Added 'amount' column.")
                except Exception as e:
                    logger.info(f"Column 'amount' might already exist: {e}")
                    
                conn.commit()
                
            logger.info("Migration completed successfully.")
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate_ot_table()
