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
from core.models import Employee, Attendance, Leave, Holiday, WorkingHours, JobExecutionLog

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
        # Start Job Log
        job_log = JobExecutionLog(
            job_name="Daily Attendance EOD",
            status="Running",
            details={'target_date': str(target_date)}
        )
        db.session.add(job_log)
        db.session.commit()

        try:
            employees = Employee.query.filter_by(is_active=True).all()
            
            stats = {
                'total': len(employees),
                'present': 0,
                'incomplete': 0,
                'absent': 0,
                'leave': 0,
                'holiday': 0,
                'weekly_off': 0,
                'half_day': 0,
                'updated': 0,
                'created': 0
            }
            
            # Pre-fetch Holiday for today (Global)
            # Validating against company-specific holidays inside loop for accuracy
            
            for employee in employees:
                # 0. Get Company/Working Hours Config
                working_hours = employee.working_hours
                half_day_threshold = float(working_hours.half_day_threshold) if working_hours and working_hours.half_day_threshold else 240 # Default 4h
                weekend_days = [int(d) for d in working_hours.weekend_days.split(',')] if working_hours and working_hours.weekend_days else [5, 6] # Default Sat,Sun

                # 1. Check for Approved Leave
                approved_leave = Leave.query.filter(
                    Leave.employee_id == employee.id,
                    Leave.status == 'Approved',
                    Leave.start_date <= target_date,
                    Leave.end_date >= target_date
                ).first()
                
                # Check for Holiday
                holiday = Holiday.query.filter(
                    Holiday.date == target_date,
                    db.or_(Holiday.company_id == employee.company_id, Holiday.company_id == None)
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
                
                # Priority 2: Holiday (unless worked?)
                # If punches exist on holiday -> Present (OD/OT logic handled elsewhere or marked as Present with OT)
                # Here we assume if no punches and it is holiday -> Holiday
                elif holiday and not (attendance.clock_in_time or attendance.clock_in):
                    attendance.status = 'Holiday'
                    attendance.sub_status = holiday.name
                    attendance.lop = False
                    stats['holiday'] += 1

                # Priority 3: Weekly Off (unless worked?)
                elif target_date.weekday() in weekend_days and not (attendance.clock_in_time or attendance.clock_in):
                    attendance.status = 'Weekly Off'
                    attendance.sub_status = None
                    attendance.lop = False
                    stats['weekly_off'] += 1
                
                # Priority 4: Punches Logic
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
                        
                        # Half Day Logic
                        # If total hours < threshold (e.g. 4.5h i.e. 270 mins)
                        # We use 60 * total_hours if calculated, or fallback/force calc
                        actual_minutes = float(attendance.total_hours) * 60
                        
                        if actual_minutes < half_day_threshold:
                            attendance.status = 'Half Day'
                            attendance.sub_status = 'Short Duration'
                            attendance.lop = True # Or configurable to deduce 0.5 day
                            stats['half_day'] += 1
                            stats['present'] -= 1 # Adjust count since we added to present initially
                            
                            
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
            
            # Update Job Log
            job_log.status = "Success"
            job_log.completed_at = datetime.now()
            job_log.details = {
                'target_date': str(target_date),
                'stats': stats
            }
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
            
            # Log failure
            try:
                error_log = JobExecutionLog.query.get(job_log.id)
                if error_log:
                    error_log.status = "Failed"
                    error_log.completed_at = datetime.now()
                    error_log.details = {'error': str(e), 'target_date': str(target_date)}
                    db.session.commit()
            except Exception as log_err:
                print(f"Failed to log error: {log_err}")

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
