from app import app, db
from core.models import User, Employee

# app = create_app() # removed

with app.app_context():
    users = User.query.all()
    with open('debug_paths.md', 'w') as f:
        f.write(f"Found {len(users)} users.\n")
        for user in users:
            if user.employee_profile and user.employee_profile.profile_image_path:
                f.write(f"User: {user.username}, Employee ID: {user.employee_profile.employee_id}\n")
                f.write(f"  Profile Image Path (DB): {user.employee_profile.profile_image_path}\n")
                
                # Check if photo_url property works
                try:
                    f.write(f"  Photo URL (Property): {user.employee_profile.photo_url}\n")
                except Exception as e:
                    f.write(f"  Error getting photo_url: {e}\n")
                    
                # Check what base.html would generate
                from flask import url_for
                try:
                    generated_url = url_for('static', filename=user.employee_profile.profile_image_path)
                    f.write(f"  Base.html generated URL: {generated_url}\n")
                except Exception as e:
                    f.write(f"  Error generating static URL: {e}\n")
                f.write("-" * 30 + "\n")

