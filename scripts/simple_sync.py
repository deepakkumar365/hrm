import sys
import os

# Add parent directory to path to import app correctly
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from app import app, db
from core.models import User, Employee

def sync_names():
    with app.app_context():
        print("Starting name synchronization...")
        
        users = User.query.filter(User.employee_profile != None).all()
        updated_count = 0
        
        for user in users:
            employee = user.employee_profile
            
            # Helper to normalize strings
            u_first = (user.first_name or "").strip()
            u_last = (user.last_name or "").strip()
            e_first = (employee.first_name or "").strip()
            e_last = (employee.last_name or "").strip()
            
            # Check for mismatch
            if u_first != e_first or u_last != e_last:
                print(f"Mismatch found for User: {user.username}")
                print(f"  User Name:     '{u_first} {u_last}'")
                print(f"  Employee Name: '{e_first} {e_last}'")
                
                # Update Employee to match User
                employee.first_name = u_first
                employee.last_name = u_last
                
                print(f"  -> UPDATED Employee record to match User.")
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print(f"\nSuccessfully synchronized {updated_count} employee records.")
        else:
            print("\nNo name mismatches found. All synced.")

if __name__ == "__main__":
    sync_names()
