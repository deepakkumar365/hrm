"""
Script to create hrm_tenant_payment_config and hrm_tenant_documents tables
This fixes the schema mismatch error:
  sqlalchemy.exc.ProgrammingError: relation "hrm_tenant_payment_config" does not exist
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
    
    sql_file = 'E:/Gobi/Pro/HRMS/hrm/migrations/versions/004_add_tenant_payment_and_documents.sql'
    
    print("=" * 70)
    print("🔧 Creating Tenant Payment Config and Documents Tables")
    print("=" * 70)
    
    with app.app_context():
        if run_sql_migration(sql_file):
            print("\n✅ Migration completed successfully!")
            print("\nThe following tables have been created:")
            print("  - hrm_tenant_payment_config")
            print("  - hrm_tenant_documents")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)