from app import app, db
from core.models import Organization

with app.app_context():
    orgs = Organization.query.all()
    print(f"Total Organizations: {len(orgs)}")
    for o in orgs:
        print(f"ID: {o.id}, Name: {o.name}")
