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
        project_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_dir)
        
        # Import Flask app and models
        from app import app, db
        from core.models import Employee, Attendance
        from datetime import date, datetime
        
        def create_daily_attendance_records(target_date=None):
            """Create attendance records for all active employees for a specific date"""
            if target_date is None:
                target_date = date.today()
            
            with app.app_context():
                try:
                    # Get all active employees
                    employees = Employee.query.filter_by(is_active=True).all()
                    created_count = 0
                    
                    for employee in employees:
                        # Check if attendance record already exists
                        existing_attendance = Attendance.query.filter_by(
                            employee_id=employee.id,
                            date=target_date
                        ).first()
                        
                        if not existing_attendance:
                            # Create new attendance record with default "Pending" status
                            attendance = Attendance(
                                employee_id=employee.id,
                                date=target_date,
                                status='Pending',
                                regular_hours=0,  # No hours assigned for pending status
                                total_hours=0,
                                overtime_hours=0,
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            db.session.add(attendance)
                            created_count += 1
                    
                    db.session.commit()
                    print(f"Successfully created attendance records for {created_count} employees on {target_date}")
                    return created_count
                    
                except Exception as e:
                    db.session.rollback()
                    print(f"Error creating attendance records: {e}")
                    return 0
        
        # Create attendance records for today
        return create_daily_attendance_records()
        
    except Exception as e:
        print(f"Error in direct creation: {e}")
        return 0

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
