"""
Script to update all existing users with the default password
Run this script to set the default password for all existing users in the database
"""

import os
os.environ['FLASK_SKIP_DB_INIT'] = '1'  # Skip default data initialization

from app import app, db
from models import User
from constants import DEFAULT_USER_PASSWORD

def update_all_user_passwords():
    """Update all existing users with the default password"""
    try:
        with app.app_context():
            # Get all users
            users = User.query.all()
            
            if not users:
                print("No users found in the database.")
                return
            
            print(f"Found {len(users)} user(s) in the database.")
            print(f"Updating all users with default password: {DEFAULT_USER_PASSWORD}")
            print("-" * 60)
            
            updated_count = 0
            for user in users:
                try:
                    # Set the default password
                    user.set_password(DEFAULT_USER_PASSWORD)
                    # Optionally, you can set must_reset_password to False for existing users
                    # or True to force them to change password on next login
                    user.must_reset_password = False  # Change to True if you want to force password reset
                    
                    print(f"✓ Updated password for user: {user.username} ({user.email})")
                    updated_count += 1
                except Exception as e:
                    print(f"✗ Failed to update user {user.username}: {str(e)}")
            
            # Commit all changes
            db.session.commit()
            
            print("-" * 60)
            print(f"✅ Successfully updated {updated_count} out of {len(users)} user(s)")
            print(f"Default password set to: {DEFAULT_USER_PASSWORD}")
            
    except Exception as e:
        print(f"❌ Error updating passwords: {str(e)}")
        db.session.rollback()

if __name__ == '__main__':
    print("=" * 60)
    print("UPDATE ALL USER PASSWORDS")
    print("=" * 60)
    
    # Confirm before proceeding
    response = input(f"\nThis will update ALL user passwords to: {DEFAULT_USER_PASSWORD}\nDo you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        update_all_user_passwords()
    else:
        print("Operation cancelled.")