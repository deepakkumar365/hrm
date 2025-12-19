#!/usr/bin/env python3
"""
Daily Attendance Auto-Creation Task

This script should be run daily (preferably at midnight) to automatically create
attendance records for all active employees with default "Present" status.

Usage:
    python daily_attendance_task.py

For Windows Task Scheduler:
    - Program: python
    - Arguments: "E:/Gobi/Pro/HRMS/hrm/daily_attendance_task.py"
    - Start in: E:/Gobi/Pro/HRMS/hrm

For Linux/Unix Cron:
    Add to crontab: 0 0 * * * cd /path/to/hrm && python daily_attendance_task.py
"""

import sys
import os
from datetime import date, datetime

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

# Import Flask app and models
from app import app, db
from core.models import Employee, Attendance

def create_daily_attendance_records(target_date=None):
    """Create attendance records for all active employees for a specific date"""
    if target_date is None:
        target_date = date.today()
    
    with app.app_context():
        try:
            # Get all active employees
            employees = Employee.query.filter_by(is_active=True).all()
            
            created_count = 0
            updated_count = 0
            
            for employee in employees:
                # Check if attendance record already exists
                existing = Attendance.query.filter_by(
                    employee_id=employee.id,
                    date=target_date
                ).first()
                
                if not existing:
                    # Create new attendance record with default Pending status
                    attendance = Attendance()
                    attendance.employee_id = employee.id
                    attendance.date = target_date
                    attendance.status = 'Pending'
                    attendance.regular_hours = 0  # No hours assigned for pending status
                    attendance.total_hours = 0
                    attendance.overtime_hours = 0
                    attendance.remarks = 'Auto-generated attendance record'
                    attendance.created_at = datetime.now()
                    attendance.updated_at = datetime.now()
                    
                    db.session.add(attendance)
                    created_count += 1
                else:
                    # Update existing record if it's still in default state (Pending or Present with no clock records)
                    if existing.status in ['Pending', 'Present'] and not existing.clock_in and not existing.clock_out:
                        existing.regular_hours = 8
                        existing.total_hours = 8
                        existing.overtime_hours = 0
                        existing.updated_at = datetime.now()
                        updated_count += 1
            
            # Commit all changes
            db.session.commit()
            
            print(f"✅ Daily attendance task completed for {target_date}")
            print(f"   📊 Created: {created_count} new records")
            print(f"   🔄 Updated: {updated_count} existing records")
            print(f"   👥 Total employees: {len(employees)}")
            
            return {
                'success': True,
                'created': created_count,
                'updated': updated_count,
                'total_employees': len(employees),
                'date': target_date
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating daily attendance records: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'date': target_date
            }

def main():
    """Main function to run the daily attendance task"""
    print(f"🚀 Starting daily attendance auto-creation task...")
    print(f"📅 Date: {date.today()}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Create attendance records for today
    result = create_daily_attendance_records()
    
    if result['success']:
        print(f"\n🎉 Task completed successfully!")
        return 0
    else:
        print(f"\n💥 Task failed: {result['error']}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
