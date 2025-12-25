from app import app, db
from core.models import User, Company, Organization

with app.app_context():
    users = User.query.all()
    print("--- USERS ---")
    for u in users:
        print(f"User: {u.username}, Role: {u.role.name if u.role else 'None'}, Org: {u.organization.name if u.organization else 'None'}, Tenant ID: {u.organization.tenant_id if u.organization else 'None'}")
    
    print("\n--- COMPANIES ---")
    companies = Company.query.all()
    for c in companies:
        print(f"Company: {c.name}, Tenant ID: {c.tenant_id}, Active: {c.is_active}")
