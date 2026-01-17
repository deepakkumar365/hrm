#!/usr/bin/env python3
"""
Render-Compatible Cron Service for Daily Attendance Creation

This script can be used with Render's Cron Jobs feature or external cron services
like GitHub Actions, Heroku Scheduler, or external cron services.

For Render Cron Jobs:
1. Create a new Cron Job service in Render
2. Set the command: python render_cron.py
3. Set the schedule: 0 0 * * * (daily at midnight)

For external services, you can call the HTTP endpoint:
POST /attendance/auto-create

Environment Variables Required:
- DATABASE_URL (automatically provided by Render)
"""

import os
import sys
import requests
from datetime import date, datetime

def create_attendance_via_api():
    """Create attendance records via HTTP API call"""
    try:
        # Get the app URL from environment or use localhost for testing
        app_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
        
        # API endpoint
        endpoint = f"{app_url}/attendance/auto-create"
        
        # Prepare data
        data = {
            'date': date.today().strftime('%Y-%m-%d')
        }
        
        # You would need to implement API authentication here
        # For now, this is a placeholder for the concept
        print(f"Would call: POST {endpoint} with data: {data}")
        print("Note: This requires proper API authentication implementation")
        
        return True
        
    except Exception as e:
        print(f"Error calling API: {e}")
        return False

def create_attendance_direct():
    """Create attendance records directly (requires app context)"""
    try:
        # Add the project directory to Python path
        project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_dir)
        
        # Import Flask app and models
        from app import app, db
        from core.models import Employee, Attendance
        from services.daily_attendance_task import process_eod_attendance
        from services.attendance_service import AttendanceService
        from datetime import date, datetime
        
        with app.app_context():
            print(f"🚀 Starting Render Daily Cron Job at {datetime.now()}")
            
            # 1. AUTO-CLOSE SHIFTS (Phase 1)
            print("\n[Phase 1] Auto-Closing Forgotten Shifts...")
            try:
                active_employees = Employee.query.filter_by(is_active=True).all()
                today = date.today()
                for emp in active_employees:
                    AttendanceService.auto_close_previous_days(emp.id, today)
                db.session.commit()
                print("✅ Phase 1 Completed.")
            except Exception as e:
                print(f"❌ Phase 1 Failed: {e}")
                db.session.rollback()

            # 2. PROCESS EOD ATTENDANCE (Phase 2)
            print("\n[Phase 2] Running EOD Processing...")
            target_date = date.today() # Render cron usually runs EOD for *current* day if scheduled effectively late, or yesterday if scheduled at 00:00
            # If standard schedule is 00:00, it should process YESTERDAY. A None arg defaults to yesterday.
            # However, if user wants parity with "Run EOD Task Now", let's be careful.
            # daily_attendance_task.process_eod_attendance() defaults to yesterday.
            # If user runs this manual command, presumably they want it NOW. but usually cron runs for "yesterday".
            # Let's keep it default (yesterday) to be safe for midnight runs.
            
            result = process_eod_attendance() 
            
            if result.get('success'):
                print("✅ Phase 2 Completed Successfully.")
                return True
            else:
                print(f"❌ Phase 2 Ended with issues: {result.get('error')}")
                return False
        
    except Exception as e:
        print(f"Error in direct creation: {e}")
        return False

if __name__ == "__main__":
    print("========================================")
    print("Render Daily Attendance Auto-Creation")
    print("========================================")
    print(f"Starting at {datetime.now()}")
    print()
    
    # Try direct creation first (works when running as part of the app)
    success = create_attendance_direct()
    
    if success:
        print("Task completed successfully!")
    else:
        print("Task failed!")
    
    print(f"Finished at {datetime.now()}")
