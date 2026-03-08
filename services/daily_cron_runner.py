#!/usr/bin/env python3
"""
Unified Daily Cron Runner
=========================
This script orchestrates the daily scheduled tasks in the correct order.

Sequence:
1. Auto-Close Open Shifts:
   - Finds employees with 'Incomplete' attendance from previous days.
   - Auto-closes them to prevent them from hanging indefinitely.
   - Uses `AttendanceService.auto_close_previous_days`.

2. EOD Attendance Processing:
   - Marks 'Absent' for employees with no records.
   - Calculates 'Late' / 'Half Day' status.
   - Uses `process_eod_attendance` from `daily_attendance_task.py`.

3. Trigger Scheduled Reports:
   - Finds all active report schedules.
   - Generates and emails them to recipients.
   - Uses `run_report_job` from `scheduler_service.py`.

Usage:
    python services/daily_cron_runner.py
"""

import sys
import os
from datetime import date, datetime

# Add the project root directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

from app import app, db
from core.models import Employee, JobExecutionLog, ReportSchedule
from services.attendance_service import AttendanceService
from services.daily_attendance_task import process_eod_attendance
from services.scheduler_service import run_report_job

def run_daily_cron():
    print("🚀 Starting Unified Daily Cron Job...")
    print(f"📅 Date: {datetime.now()}")
    
    with app.app_context():
        # ==================================================================
        # PHASE 1: Auto-Close Forgotten Shifts
        # ==================================================================
        print("\n[Phase 1] Auto-Closing Forgotten Shifts...")
        try:
            active_employees = Employee.query.filter_by(is_active=True).all()
            today = date.today()
            
            for emp in active_employees:
                # auto_close_previous_days checks for records BEFORE today
                AttendanceService.auto_close_previous_days(emp.id, today)
            
            db.session.commit()
            print("✅ Phase 1 Completed: All previous open shifts checked/closed.")
            
        except Exception as e:
            print(f"❌ Phase 1 Failed: {e}")
            # We continue to Phase 2 even if Phase 1 fails, as EOD is critical
            db.session.rollback()

        # ==================================================================
        # PHASE 2: EOD Attendance Processing (Absent/Late/Half-Day)
        # ==================================================================
        print("\n[Phase 2] Running EOD Processing...")
        try:
            # This function handles its own logging to JobExecutionLog
            result = process_eod_attendance() 
            
            if result['success']:
                print("✅ Phase 2 Completed Successfully.")
            else:
                print(f"❌ Phase 2 Ended with potential issues: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Phase 2 Critical Failure: {e}")

        # ==================================================================
        # PHASE 3: Trigger Scheduled Reports (Midnight Run)
        # ==================================================================
        print("\n[Phase 3] Triggering Scheduled Reports...")
        
        # Start Phase 3 Job Log
        phase3_log = JobExecutionLog(
            job_name="Daily Scheduled Reports Cron",
            status="Running",
            details={'started_at': str(datetime.now())}
        )
        db.session.add(phase3_log)
        db.session.commit()

        try:
            active_schedules = ReportSchedule.query.filter_by(is_active=True).all()
            print(f"Found {len(active_schedules)} active report schedules.")
            
            summary = []
            for schedule in active_schedules:
                print(f" - Running: {schedule.report_type} (ID: {schedule.id})")
                # run_report_job now (ideally) handles its own detailed logging
                # but we capture a high level summary here
                run_report_job(schedule.id)
                summary.append(f"Report ID {schedule.id} ({schedule.report_type}) triggered.")
                
            phase3_log.status = "Success"
            phase3_log.completed_at = datetime.now()
            phase3_log.details = {
                'schedules_found': len(active_schedules),
                'summary': summary
            }
            db.session.commit()
            print("✅ Phase 3 Completed: All active reports processed.")
            
        except Exception as e:
            print(f"❌ Phase 3 Failed: {e}")
            phase3_log.status = "Failed"
            phase3_log.completed_at = datetime.now()
            phase3_log.details = {'error': str(e)}
            db.session.commit()

    print("\n🏁 Daily Cron Job Finished.")

if __name__ == "__main__":
    run_daily_cron()
