
import logging
from app import app, db
from core.models import CompanyEmployeeIdConfig, Employee, Company
from sqlalchemy import func

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_employee_id_sequences():
    """
    Recalibrates the CompanyEmployeeIdConfig.last_sequence_number for all companies
    by checking the actual maximum employee ID used in the Employee table.
    """
    with app.app_context():
        logger.info("Starting employee ID sequence recalibration...")
        
        configs = CompanyEmployeeIdConfig.query.all()
        logger.info(f"Found {len(configs)} configuration records.")
        
        updated_count = 0
        
        for config in configs:
            company = Company.query.get(config.company_id)
            if not company:
                logger.warning(f"Config found for non-existent company ID: {config.company_id}")
                continue
                
            prefix = config.id_prefix
            logger.info(f"Processing Company: {company.name} (Prefix: {prefix})")
            
            # Find all employees with this prefix
            # Assuming format is {Prefix}{Number} e.g., ACME001
            # We want to find the max number.
            
            # Using regex to extract the numeric part. 
            # Pattern: ^PREFIX\d+$
            
            # Note: This query depends on the database specific SQL regex syntax if we do it in SQL.
            # For robustness and database independence (assuming reasonable dataset size), we can fetch IDs and parse in Python
            # or use a Like query.
            
            employees = Employee.query.filter(Employee.employee_id.like(f"{prefix}%")).all()
            
            max_sequence = 0
            count = 0
            
            for emp in employees:
                try:
                    # Strip prefix
                    if emp.employee_id and emp.employee_id.startswith(prefix):
                        numeric_part_str = emp.employee_id[len(prefix):]
                        if numeric_part_str.isdigit():
                            sequence_num = int(numeric_part_str)
                            if sequence_num > max_sequence:
                                max_sequence = sequence_num
                        count += 1
                except Exception as e:
                    logger.warning(f"Error parsing employee ID '{emp.employee_id}': {e}")
            
            logger.info(f"  - Found {count} employees with prefix '{prefix}'. Max sequence: {max_sequence}")
            
            if max_sequence > config.last_sequence_number:
                old_val = config.last_sequence_number
                config.last_sequence_number = max_sequence
                logger.info(f"  - UPDATING: last_sequence_number from {old_val} to {max_sequence}")
                updated_count += 1
            else:
                logger.info(f"  - OK: current config ({config.last_sequence_number}) >= max found ({max_sequence})")
                
        if updated_count > 0:
            db.session.commit()
            logger.info(f"Successfully updated {updated_count} configuration records.")
        else:
            logger.info("No updates needed. All sequences are in sync.")

if __name__ == "__main__":
    try:
        fix_employee_id_sequences()
        print("Script completed successfully.")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        print(f"Error: {e}")
