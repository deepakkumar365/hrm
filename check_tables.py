"""Check database tables"""
import sys
sys.path.insert(0, 'E:/Gobi/Pro/HRMS/hrm')

from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    print('\n📊 Database Tables:')
    print('=' * 50)
    for table in sorted(tables):
        print(f'  ✓ {table}')
    print('=' * 50)
    print(f'\nTotal tables: {len(tables)}')