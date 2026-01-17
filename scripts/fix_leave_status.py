import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db
from core.models import Leave

def fix_leave_status():
    with app.app_context():
        # Find leaves with lowercase 'pending'
        pending_leaves = Leave.query.filter_by(status='pending').all()
        
        count = len(pending_leaves)
        print(f"Found {count} leave requests with status 'pending' (lowercase).")
        
        if count > 0:
            print("Updating them to 'Pending'...")
            for leave in pending_leaves:
                leave.status = 'Pending'
            
            db.session.commit()
            print("Update complete.")
        else:
            print("No legacy records found needing update.")

        # Verify
        remaining = Leave.query.filter_by(status='pending').count()
        print(f"Remaining 'pending' records: {remaining}")
        
        corrected = Leave.query.filter_by(status='Pending').count()
        print(f"Total 'Pending' records: {corrected}")

if __name__ == "__main__":
    fix_leave_status()
