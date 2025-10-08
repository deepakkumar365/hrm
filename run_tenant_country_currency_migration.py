"""
Script to add country_code and currency_code columns to hrm_tenant table
This fixes the schema mismatch error:
  sqlalchemy.exc.ProgrammingError: column hrm_tenant.country_code does not exist
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
    
    sql_file = 'E:/Gobi/Pro/HRMS/hrm/migrations/versions/003_add_tenant_country_currency.sql'
    
    print("=" * 60)
    print("🔧 Adding country_code and currency_code to hrm_tenant table")
    print("=" * 60)
    
    with app.app_context():
        if run_sql_migration(sql_file):
            print("\n✅ Migration completed successfully!")
            print("\nThe following columns have been added to hrm_tenant:")
            print("  - country_code (VARCHAR(10))")
            print("  - currency_code (VARCHAR(10))")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)