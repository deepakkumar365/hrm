
import sys
import os
from decimal import Decimal

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import Employee, PayrollConfiguration
from services.singapore_payroll import SingaporePayrollCalculator

def verify_cpf_config():
    """
    Verify that payroll calculator prioritizes configuration values.
    """
    with app.app_context():
        # Get any active employee
        emp = Employee.query.filter_by(is_active=True).first()
        if not emp:
            print("No active employee found for testing.")
            return

        print(f"Testing with Employee: {emp.first_name} {emp.last_name}")
        
        # Ensure they have config
        if not emp.payroll_config:
            config = PayrollConfiguration(employee_id=emp.id)
            db.session.add(config)
            db.session.commit()
            print("Created missing payroll config.")
            
        # 1. Set specific non-standard CPF values
        test_emp_cpf = Decimal('123.45')
        test_employer_cpf = Decimal('678.90')
        
        emp.payroll_config.employee_cpf = test_emp_cpf
        emp.payroll_config.employer_cpf = test_employer_cpf
        db.session.commit()
        
        print(f"Set Config: Emp={test_emp_cpf}, Er={test_employer_cpf}")
        
        # 2. Run Calculator
        calculator = SingaporePayrollCalculator()
        gross_pay = Decimal('5000.00') # Arbitrary
        
        res_emp, res_er = calculator.calculate_cpf_contribution(emp, gross_pay)
        
        print(f"Calculator Result: Emp={res_emp}, Er={res_er}")
        
        # 3. Assert
        if res_emp == test_emp_cpf and res_er == test_employer_cpf:
            print("SUCCESS: Calculator used configured values!")
        else:
            print("FAILURE: Calculator ignored configured values.")

if __name__ == '__main__':
    verify_cpf_config()
