from app import app, db
from core.models import User, Organization

with app.app_context():
    user_count = User.query.count()
    org = Organization.query.first()
    print(f"Final User Count: {user_count}")
    if org:
        print(f"Final Org: {org.name}")
    
    superadmin = User.query.filter_by(username='superadmin@noltrion.com').first()
    if superadmin:
        print(f"Superadmin found: {superadmin.email}")
    else:
        print("Superadmin NOT found!")
