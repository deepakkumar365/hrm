import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app,db
from core.models import User, Employee

def sync_names():
    app = create_app()
    with app.app_context():
        print("Starting name synchronization...")
        
        users = User.query.filter(User.employee_profile != None).all()
        updated_count = 0
        
        for user in users:
            employee = user.employee_profile
            
            # Check for mismatch
            if employee.first_name != user.first_name or employee.last_name != user.last_name:
                print(f"Mismatch found for User: {user.username} ({user.full_name}) vs Employee: {employee.first_name} {employee.last_name}")
                
                old_name = f"{employee.first_name} {employee.last_name}"
                
                # Update Employee to match User
                employee.first_name = user.first_name
                employee.last_name = user.last_name
                
                print(f"  -> Updated: {old_name} -> {user.full_name}")
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print(f"\nSuccessfully synchronized {updated_count} employee records.")
        else:
            print("\nNo name mismatches found. All synced.")

if __name__ == "__main__":
    sync_names()
