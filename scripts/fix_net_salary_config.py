
import sys
import os
from decimal import Decimal

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import PayrollConfiguration

def fix_net_salary():
    """
    Recalculate and update net_salary for all PayrollConfiguration records.
    Formula: Basic + Allowances - Employee CPF
    """
    with app.app_context():
        print("Starting Net Salary Fix...")
        configs = PayrollConfiguration.query.all()
        updated_count = 0
        
        for config in configs:
            basic = config.basic_salary or Decimal(0)
            allowances = config.get_total_allowances() or Decimal(0)
            emp_cpf = config.employee_cpf or Decimal(0)
            
            # Simple Net Calculation for Configuration Preview
            # Note: This doesn't include taxes/deductions which are runtime calculations
            estimated_net = basic + allowances - emp_cpf
            
            config.net_salary = estimated_net
            updated_count += 1
            # print(f"Updated config {config.id}: Net {estimated_net}")
            
        try:
            db.session.commit()
            print(f"Successfully updated net_salary for {updated_count} configurations.")
        except Exception as e:
            db.session.rollback()
            print(f"Failed to update net_salary: {e}")

if __name__ == '__main__':
    fix_net_salary()
