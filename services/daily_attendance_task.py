#!/usr/bin/env python3
"""
Daily Attendance EOD Processing Task

This script should be run daily (e.g., at midnight) to process attendance for the previous day.
It evaluates punches, checks for leave approvals, and assigns statuses (Present, Incomplete, Absent, Leave).

Usage:
    python daily_attendance_task.py [YYYY-MM-DD]
    (If date not provided, processes for Yesterday)

"""

import sys
import os
from datetime import date, datetime, timedelta
import argparse

# Add the project directory to Python path
# Add the project root directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Import Flask app and models
from app import app, db
from core.models import Employee, Attendance, Leave

def process_eod_attendance(target_date=None):
    """
    Process End-Of-Day attendance status for all active employees.
    
    Logic:
    1. Check Approved Leave -> Status: Leave
    2. Check Punches:
       - Both In/Out -> Status: Present
       - Partial -> Status: Incomplete (Pending Out)
       - None -> Status: Absent
    """
    if target_date is None:
        # Default to yesterday if running at midnight for the previous day
        target_date = date.today() - timedelta(days=1)
    
    print(f"🔄 Processing EOD Attendance for: {target_date}")
    
    with app.app_context():
        try:
            employees = Employee.query.filter_by(is_active=True).all()
            
            stats = {
                'total': len(employees),
                'present': 0,
                'incomplete': 0,
                'absent': 0,
                'leave': 0,
                'updated': 0,
                'created': 0
            }
            
            for employee in employees:
                # 1. Check for Approved Leave
                approved_leave = Leave.query.filter(
                    Leave.employee_id == employee.id,
                    Leave.status == 'Approved',
                    Leave.start_date <= target_date,
                    Leave.end_date >= target_date
                ).first()
                
                # 2. Get or Create Attendance Record
                attendance = Attendance.query.filter_by(
                    employee_id=employee.id,
                    date=target_date
                ).first()
                
                is_new = False
                if not attendance:
                    attendance = Attendance(
                        employee_id=employee.id,
                        date=target_date
                    )
                    is_new = True
                    stats['created'] += 1
                else:
                    stats['updated'] += 1

                # 3. Determine Status
                
                # Priority 1: Leave Override
                if approved_leave:
                    attendance.status = 'Leave'
                    attendance.leave_id = approved_leave.id
                    attendance.sub_status = None
                    # Use leave type as sub_status if desired, or keep None
                    # attendance.sub_status = approved_leave.leave_type 
                    stats['leave'] += 1
                
                # Priority 2: Punches Logic
                else:
                    # Check punches
                    # Use clock_in_time if available, fall back to clock_in (time) + date
                    has_in = attendance.clock_in_time is not None or attendance.clock_in is not None
                    has_out = attendance.clock_out_time is not None or attendance.clock_out is not None
                    
                    if has_in and has_out:
                        attendance.status = 'Present'
                        attendance.sub_status = None
                        stats['present'] += 1
                        
                        # Calculate hours if not set (Basic logic)
                        if attendance.total_hours == 0:
                            # TODO: Implement accurate hours calculation using timestamps
                            attendance.total_hours = 8 # Placeholder standard day
                            attendance.regular_hours = 8
                            
                    elif has_in and not has_out:
                        attendance.status = 'Incomplete'
                        attendance.sub_status = 'Pending Out'
                        stats['incomplete'] += 1
                        
                    elif not has_in and has_out:
                         # Rare case: Clocked out but no clock in
                        attendance.status = 'Incomplete'
                        attendance.sub_status = 'Pending In'
                        stats['incomplete'] += 1
                        
                    else:
                        # No punches
                        attendance.status = 'Absent'
                        attendance.sub_status = None
                        attendance.lop = True # Auto-mark LOP (user: "auto-mark as Absent/LOP")
                        stats['absent'] += 1

                if is_new:
                    db.session.add(attendance)
            
            db.session.commit()
            
            print(f"✅ EOD Processing Completed for {target_date}")
            print(f"   📊 Stats: {stats}")
            
            return {
                'success': True,
                'stats': stats,
                'date': target_date
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error in EOD processing: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'date': target_date
            }

def main():
    parser = argparse.ArgumentParser(description='Run Daily EOD Attendance Task')
    parser.add_argument('date', nargs='?', help='Target date (YYYY-MM-DD)', default=None)
    args = parser.parse_args()
    
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
            
    result = process_eod_attendance(target_date)
    
    sys.exit(0 if result['success'] else 1)

if __name__ == '__main__':
    main()
