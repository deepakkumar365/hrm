#!/usr/bin/env python
"""Debug timezone conversion issue"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Employee, Company, Attendance
from timezone_utils import convert_utc_to_company_timezone, get_company_timezone
from datetime import datetime
import pytz

def debug_timezone():
    with app.app_context():
        # Find a Singapore company
        singapore_company = Company.query.filter_by(code='SG').first()
        
        if not singapore_company:
            # Try to find any company
            singapore_company = Company.query.first()
        
        if not singapore_company:
            print("❌ No companies found in database")
            return
        
        print(f"✅ Found company: {singapore_company.name} ({singapore_company.code})")
        print(f"   Timezone configured: {singapore_company.timezone}")
        print()
        
        # Find an employee in this company
        employee = Employee.query.filter_by(company_id=singapore_company.id, is_active=True).first()
        
        if not employee:
            print("❌ No employees found for this company")
            return
        
        print(f"✅ Found employee: {employee.first_name} {employee.last_name}")
        print(f"   Company: {employee.company.timezone}")
        print()
        
        # Find their recent attendance
        attendance = Attendance.query.filter_by(employee_id=employee.id).order_by(Attendance.date.desc()).first()
        
        if not attendance:
            print("❌ No attendance records found for this employee")
            return
        
        print(f"✅ Found attendance record from: {attendance.date}")
        print(f"   Clock In (UTC - raw from DB): {attendance.clock_in}")
        print(f"   Clock In Type: {type(attendance.clock_in)}")
        print()
        
        # Test conversion
        if attendance.clock_in:
            print("🔄 Testing timezone conversion...")
            print(f"   Company timezone: {employee.company.timezone}")
            
            converted = convert_utc_to_company_timezone(attendance.clock_in, employee.company)
            print(f"   Converted time: {converted}")
            print(f"   Converted type: {type(converted)}")
            print(f"   Converted timezone info: {converted.tzinfo if converted else 'None'}")
            
            if converted:
                # Format both for display
                print()
                print("📊 Display Format Comparison:")
                print(f"   UTC (original):   {attendance.clock_in.strftime('%I:%M %p') if hasattr(attendance.clock_in, 'strftime') else str(attendance.clock_in)}")
                print(f"   Local (converted): {converted.strftime('%I:%M %p')}")
                print(f"   Full UTC: {attendance.clock_in.strftime('%Y-%m-%d %H:%M:%S %Z') if hasattr(attendance.clock_in, 'strftime') else str(attendance.clock_in)}")
                print(f"   Full Local: {converted.strftime('%Y-%m-%d %H:%M:%S %Z')}")

if __name__ == '__main__':
    debug_timezone()