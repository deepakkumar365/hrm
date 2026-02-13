from app import app, db
from core.models import ReportSchedule, Tenant, Company, User, EmailLog
from services.scheduler_service import run_report_job
from datetime import datetime, timedelta
import uuid

def verify_report_flow():
    with app.app_context():
        try:
            print(">>> Starting Verification...")
            
            # 1. Get/Create Test Data
            tenant = Tenant.query.first()
            if not tenant:
                print("Error: No tenant found in DB.")
                return
            
            company = Company.query.filter_by(tenant_id=tenant.id).first()
            user = User.query.first()
            
            print(f"Using Tenant: {tenant.name}, Company: {company.name if company else 'None'}")
            
            # 2. Create a Mock Schedule
            print("Creating mock schedule...")
            test_schedule = ReportSchedule(
                tenant_id=tenant.id,
                company_id=company.id if company else None,
                report_type='Daily Attendance',
                cron_expression='0 0 * * *',
                date_filter_type='yesterday',
                recipients=['test_manager@example.com'],
                created_by=user.id if user else None
            )
            db.session.add(test_schedule)
            db.session.commit()
            schedule_id = test_schedule.id
            print(f"Schedule created with ID: {schedule_id}")
            
            # 3. Trigger Job Manually
            print("Triggering run_report_job...")
            run_report_job(schedule_id)
            
            # 4. Verify Results
            # Check if an EmailLog was created
            print("Checking EmailLog...")
            log = EmailLog.query.filter_by(recipient='test_manager@example.com').order_by(EmailLog.sent_at.desc()).first()
            
            if log:
                print(f"Success: EmailLog found. Status: {log.status}, Subject: {log.subject}")
                if log.status == 'Sent':
                    print("Verification PASSED: Report generated and email 'sent' (logged).")
                else:
                    print(f"Verification WARNING: EmailLog found but status is {log.status}. Error: {log.error_message}")
            else:
                print("Verification FAILED: No EmailLog found for recipient.")
            
            # 5. Cleanup
            print("Cleaning up...")
            db.session.delete(test_schedule)
            db.session.commit()
            print("Cleanup complete.")
            
        except Exception as e:
            print(f"Error during verification: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

if __name__ == "__main__":
    verify_report_flow()
