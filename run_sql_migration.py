"""
Script to run SQL migrations manually
"""
import os
from app import db

def run_sql_migration(sql_file_path):
    """Execute a SQL migration file"""
    print(f"📄 Reading SQL file: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print(f"🔄 Executing SQL migration...")
    
    try:
        # Execute the SQL
        db.session.execute(db.text(sql_content))
        db.session.commit()
        print("✅ SQL migration executed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error executing SQL migration: {e}")
        db.session.rollback()
        return False

if __name__ == '__main__':
    import sys
    from app import app
    
    # Set environment variable to skip DB init
    os.environ['FLASK_SKIP_DB_INIT'] = '1'
    
    sql_file = 'E:/Gobi/Pro/HRMS/hrm/migrations/versions/001_add_tenant_company_hierarchy.sql'
    
    with app.app_context():
        if run_sql_migration(sql_file):
            print("\n✅ Migration completed successfully!")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)