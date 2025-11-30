#!/usr/bin/env python
"""Check payslip status for employees"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Payroll, Employee, EmployeeDocument

def check_status():
    with app.app_context():
        print("📋 Payroll Status Report")
        print("=" * 60)
        
        # Get all payrolls
        all_payrolls = Payroll.query.all()
        print(f"\nTotal Payroll Records: {len(all_payrolls)}\n")
        
        # Count by status
        statuses = {}
        for p in all_payrolls:
            status = p.status or 'Unknown'
            statuses[status] = statuses.get(status, 0) + 1
            
        print("By Status:")
        for status, count in sorted(statuses.items()):
            print(f"  {status}: {count}")
        
        # Check AKSL093
        print("\n" + "=" * 60)
        print("Looking for employee AKSL093...")
        employee = Employee.query.filter_by(employee_id='AKSL093').first()
        
        if employee:
            print(f"\n✅ Found: {employee.first_name} {employee.last_name}")
            
            payrolls = Payroll.query.filter_by(employee_id=employee.id).all()
            print(f"   Payroll records: {len(payrolls)}")
            
            if payrolls:
                print("\n   Payroll Details:")
                for p in sorted(payrolls, key=lambda x: x.pay_period_start, reverse=True):
                    print(f"      {p.pay_period_start.strftime('%b %Y')}: Status = {p.status}")
                    
                    # Check for document
                    doc = EmployeeDocument.query.filter_by(
                        employee_id=employee.id,
                        document_type='Salary Slip',
                        month=p.pay_period_start.month,
                        year=p.pay_period_start.year
                    ).first()
                    print(f"         Document: {'✅ Yes' if doc else '❌ No'}")
            else:
                print("   No payroll records found")
        else:
            print("❌ Employee AKSL093 not found")
            
            # List all employee IDs
            print("\nAvailable Employee IDs (first 10):")
            employees = Employee.query.limit(10).all()
            for e in employees:
                print(f"  - {e.employee_id}: {e.first_name} {e.last_name}")


if __name__ == '__main__':
    check_status()