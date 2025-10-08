"""Check which tenant-related tables exist in the database"""
import os
from app import db, app

os.environ['FLASK_SKIP_DB_INIT'] = '1'

with app.app_context():
    result = db.session.execute(db.text("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name LIKE '%tenant%' 
        ORDER BY table_name
    """))
    
    print("Tenant-related tables in database:")
    for row in result:
        print(f"  - {row[0]}")