
import os
import sys
from datetime import date, timedelta

# Add current directory to path
sys.path.append(os.getcwd())

from app import app, db
from core.models import Employee, Attendance, Company, Tenant
from services.report_service import ReportService

def verify_report():
    with app.app_context():
        # Get a tenant and company
        tenant = Tenant.query.first()
        if not tenant:
            print("No tenant found!")
            return
            
        company = Company.query.filter_by(tenant_id=tenant.id).first()
        if not company:
            print(f"No company found for tenant {tenant.id}!")
            return
            
        # Get active employees for this company
        employees = Employee.query.filter_by(company_id=company.id, is_active=True).all()
        num_employees = len(employees)
        print(f"Active employees: {num_employees}")
        
        # Test range: Last 7 days
        end_date = date.today()
        start_date = end_date - timedelta(days=6) # 7 days inclusive
        num_days = 7
        
        print(f"Range: {start_date} to {end_date} ({num_days} days)")
        
        # Call report service
        data = ReportService.get_attendance_register_data(
            tenant_id=tenant.id,
            company_id=company.id,
            start_date=start_date,
            end_date=end_date
        )
        
        expected_rows = num_employees * num_days
        actual_rows = len(data)
        
        print(f"Expected rows: {expected_rows}")
        print(f"Actual rows: {actual_rows}")
        
        if expected_rows == actual_rows:
            print("SUCCESS: Row count matches!")
        else:
            print("FAILURE: Row count mismatch!")
            
        # Check for status 'Absent' in some rows (likely to have some missing records in dev/test)
        absent_count = sum(1 for row in data if row['Status'] == 'Absent')
        print(f"Absent/Missing rows: {absent_count}")
        
        # Verify specific dates for one employee
        if employees:
            emp = employees[0]
            emp_rows = [row for row in data if row['Employee ID'] == emp.employee_id]
            print(f"Rows for employee {emp.employee_id}: {len(emp_rows)}")
            
            dates_found = set(row['Date'] for row in emp_rows)
            if len(dates_found) == num_days:
                print(f"SUCCESS: All {num_days} dates found for employee {emp.employee_id}")
            else:
                print(f"FAILURE: Only {len(dates_found)} dates found for employee {emp.employee_id}")

if __name__ == "__main__":
    verify_report()
