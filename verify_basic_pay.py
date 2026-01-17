from app import app, db
from core.models import Employee, Payroll, PayrollConfiguration
from datetime import date

def verify_basic_pay():
    with app.app_context():
        # Find the employee from the screenshot
        print("--- Verifying Basic Pay Data ---")
        # Trying exact first name match from screenshot "DEEPAKKUMAR S"
        # It might be First Name: DEEPAKKUMAR S, Last Name: ... or split.
        # Let's try searching generically again but print all matches
        
        employees = Employee.query.filter(Employee.first_name.ilike('%Deepak%')).all()
        
        if not employees:
            print("No employees found matching 'Deepak'.")
            return

        for employee in employees:
            print(f"\nChecking Employee: {employee.first_name} {employee.last_name} (ID: {employee.id}, EmpID: {employee.employee_id})")
            
            # Check Payroll Configuration
            config = PayrollConfiguration.query.filter_by(employee_id=employee.id).first()
            if config:
                print(f"  > Current Payroll Config Basic Salary: {config.basic_salary}")
            else:
                print("  > No Payroll Configuration found.")

            # Check Payroll Records
            payrolls = Payroll.query.filter_by(employee_id=employee.id).order_by(Payroll.pay_period_end.desc()).all()
            
            if payrolls:
                print(f"  > Found {len(payrolls)} payroll records:")
                for p in payrolls:
                    print(f"    - Period: {p.pay_period_end}, Status: {p.status}, Saved Basic Pay: {p.basic_pay}, Gross: {p.gross_pay}")
            else:
                print("  > No payroll records found.")

if __name__ == "__main__":
    verify_basic_pay()
