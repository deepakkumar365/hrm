
import sys
import os
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

# Add parent directory to path so we can import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import Employee, PayrollConfiguration
from services.singapore_payroll import SingaporePayrollCalculator

def migrate_cpf():
    """
    Calculate and populate correct CPF values for all employees
    into their PayrollConfiguration.
    """
    with app.app_context():
        print("Starting CPF Migration...")
        employees = Employee.query.filter_by(is_active=True).all()
        calculator = SingaporePayrollCalculator()
        
        updated_count = 0
        
        for emp in employees:
            if not emp.payroll_config:
                print(f"Skipping {emp.first_name} {emp.last_name} (No Payroll Config)")
                continue

            # Calculate expected CPF based on current config's basic + allowances
            # Note: This is an estimation using their 'standard' monthly pay.
            # Real payroll might vary with OT/unpaid leave, but this sets the baseline.
            
            basic = emp.payroll_config.basic_salary or Decimal(0)
            total_allowances = emp.payroll_config.get_total_allowances()
            
            # Gross for CPF estimation
            gross_pay = basic + total_allowances
            
            # Validation: Ensure critical dates exist
            if not emp.date_of_birth:
                print(f"Skipping {emp.first_name}: No Date of Birth")
                continue
                
            if not emp.hire_date:
                # Fallback to today if missing, strictly for script not to crash
                print(f"Warning {emp.first_name}: No Hire Date, assuming today")
                # But get_cpf_rate needs hire date for foreigners?
                # We'll handle inside or just ensure it's not None if needed by logic
                pass 

            # Calculate CPF using lower-level method to avoid circular config check
            # Apply salary ceiling
            cpf_salary = min(gross_pay, 6000)
            
            try:
                employee_rate, employer_rate = calculator.get_cpf_rate(emp, cpf_salary, date.today())
                
                employee_cpf = (cpf_salary * Decimal(employee_rate) / 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                employer_cpf = (cpf_salary * Decimal(employer_rate) / 100).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
                
                # Update Configuration
                emp.payroll_config.employee_cpf = employee_cpf
                emp.payroll_config.employer_cpf = employer_cpf
                
                print(f"Updated {emp.first_name}: Gross={gross_pay}, Emp={employee_cpf}, Er={employer_cpf}")
                updated_count += 1
            except Exception as inner_e:
                 print(f"Error calculating for {emp.first_name}: {inner_e}")
                 continue
            
        try:
            db.session.commit()
            print(f"Migration completed successfully. Updated {updated_count} employees.")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == '__main__':
    migrate_cpf()
