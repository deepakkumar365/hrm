"""Check current role table data"""
import os
os.environ['FLASK_SKIP_DB_INIT'] = '1'

from app import app, db
from models import Role
from sqlalchemy import inspect, text

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print('=== Database Tables ===')
    print(f"role table exists: {'role' in tables}")
    print(f"hrm_roles table exists: {'hrm_roles' in tables}")
    
    if 'role' in tables:
        print('\n=== Current roles in role table ===')
        roles = Role.query.all()
        print(f'Total roles: {len(roles)}')
        for r in roles:
            print(f'  - ID: {r.id}, Name: {r.name}, Description: {r.description}, Active: {r.is_active}')
        
        # Check how many users reference these roles
        result = db.session.execute(text('SELECT COUNT(*) FROM hrm_users WHERE role_id IS NOT NULL'))
        user_count = result.scalar()
        print(f'\nTotal users with roles: {user_count}')