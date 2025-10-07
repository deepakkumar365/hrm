"""
Auto-run Tenant-Company Hierarchy Migration (No user input required)
This script executes the SQL migration to add tenant and company tables
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_db_connection():
    """Get database connection from DATABASE_URL"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        raise RuntimeError("DATABASE_URL not found in environment variables")
    
    logger.info("Connecting to database...")
    return psycopg2.connect(database_url)


def run_migration_file(conn, filepath):
    """Execute SQL migration file"""
    logger.info(f"Running migration: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(sql_content)
            conn.commit()
            logger.info(f"✅ Migration completed: {filepath}")
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Migration failed: {filepath}")
        logger.error(f"Error: {str(e)}")
        return False


def verify_tables(conn):
    """Verify that tables were created successfully"""
    logger.info("Verifying table creation...")
    
    tables_to_check = ['hrm_tenant', 'hrm_company']
    
    try:
        with conn.cursor() as cursor:
            for table in tables_to_check:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table,))
                exists = cursor.fetchone()[0]
                
                if exists:
                    # Count rows
                    cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table)
                    ))
                    count = cursor.fetchone()[0]
                    logger.info(f"✅ Table '{table}' exists with {count} rows")
                else:
                    logger.warning(f"⚠️  Table '{table}' does not exist")
            
            # Check for new columns in existing tables
            logger.info("Checking for new columns in existing tables...")
            
            # Check hrm_employee.company_id
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'hrm_employee' AND column_name = 'company_id'
                );
            """)
            if cursor.fetchone()[0]:
                logger.info("✅ Column 'company_id' added to hrm_employee")
            else:
                logger.warning("⚠️  Column 'company_id' not found in hrm_employee")
            
            # Check organization.tenant_id
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.columns 
                    WHERE table_name = 'organization' AND column_name = 'tenant_id'
                );
            """)
            if cursor.fetchone()[0]:
                logger.info("✅ Column 'tenant_id' added to organization")
            else:
                logger.warning("⚠️  Column 'tenant_id' not found in organization")
        
        return True
        
    except Exception as e:
        logger.error(f"Error verifying tables: {str(e)}")
        return False


def main():
    """Main migration execution"""
    logger.info("=" * 60)
    logger.info("HRMS Tenant-Company Hierarchy Migration (AUTO)")
    logger.info("=" * 60)
    
    # Get migration files
    migrations_dir = Path(__file__).parent / 'migrations' / 'versions'
    migration_file = migrations_dir / '001_add_tenant_company_hierarchy.sql'
    test_data_file = migrations_dir / '002_test_data_tenant_company.sql'
    
    if not migration_file.exists():
        logger.error(f"Migration file not found: {migration_file}")
        sys.exit(1)
    
    try:
        # Connect to database
        conn = get_db_connection()
        logger.info("✅ Database connection established")
        
        # Run migration
        logger.info("\n" + "=" * 60)
        logger.info("STEP 1: Running schema migration")
        logger.info("=" * 60)
        if not run_migration_file(conn, migration_file):
            logger.error("Migration failed. Exiting.")
            sys.exit(1)
        
        # Verify tables
        logger.info("\n" + "=" * 60)
        logger.info("STEP 2: Verifying table creation")
        logger.info("=" * 60)
        verify_tables(conn)
        
        # Automatically insert test data
        logger.info("\n" + "=" * 60)
        logger.info("STEP 3: Inserting test data")
        logger.info("=" * 60)
        
        if test_data_file.exists():
            logger.info("Inserting test data automatically...")
            run_migration_file(conn, test_data_file)
        else:
            logger.warning(f"Test data file not found: {test_data_file}")
        
        # Close connection
        conn.close()
        logger.info("\n" + "=" * 60)
        logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Restart your Flask application: python main.py")
        logger.info("2. Access the web UI:")
        logger.info("   - http://localhost:5000/tenants")
        logger.info("   - http://localhost:5000/companies")
        logger.info("3. Access the API endpoints:")
        logger.info("   - GET  /api/tenants")
        logger.info("   - POST /api/tenants")
        logger.info("   - GET  /api/companies")
        logger.info("   - POST /api/companies")
        
    except Exception as e:
        logger.error(f"❌ Migration failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()