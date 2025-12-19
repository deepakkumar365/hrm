#!/usr/bin/env python3
"""
Initialize Production Database
Creates schema and imports master data if database is empty
"""

import os
import sys
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Load environment variables
load_dotenv()

class ProductionDatabaseInitializer:
    def __init__(self):
        self.prod_url = os.getenv('PROD_DATABASE_URL')
        self.engine = None
        
    def connect(self):
        """Connect to production database"""
        try:
            print("🔗 Connecting to production database...")
            self.engine = create_engine(self.prod_url, echo=False)
            self.engine.connect().close()
            print("✅ Production database connected")
            return True
        except Exception as e:
            print(f"❌ Failed to connect: {e}")
            return False
    
    def is_empty(self):
        """Check if database is empty"""
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            return len(tables) == 0
        except Exception as e:
            print(f"❌ Error checking database: {e}")
            return None
    
    def get_table_count(self):
        """Get count of tables"""
        try:
            inspector = inspect(self.engine)
            return len(inspector.get_table_names())
        except Exception as e:
            return 0
    
    def run_alembic_migrations(self):
        """Run Alembic to create schema"""
        print("\n🔄 Creating database schema...")
        
        env = os.environ.copy()
        env['DATABASE_URL'] = self.prod_url
        
        try:
            result = subprocess.run(
                ['alembic', 'upgrade', 'head'],
                cwd=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')),
                env=env,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Schema created successfully")
                if "No new upgrade" in result.stdout:
                    print("   (Already at latest version)")
                return True
            else:
                print(f"❌ Schema creation failed")
                print(result.stderr)
                return False
        except subprocess.TimeoutExpired:
            print("❌ Migration timed out (>60s)")
            return False
        except Exception as e:
            print(f"❌ Error running migrations: {e}")
            return False
    
    def verify_schema(self):
        """Verify schema was created"""
        print("\n📋 Verifying schema...")
        
        required_tables = [
            'hrm_users', 'organization', 'role', 'employee',
            'designation', 'leave_type', 'attendance', 'payroll'
        ]
        
        try:
            inspector = inspect(self.engine)
            existing_tables = set(inspector.get_table_names())
            
            all_exist = True
            for table in required_tables:
                if table in existing_tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ❌ {table} (MISSING)")
                    all_exist = False
            
            return all_exist
        except Exception as e:
            print(f"❌ Error verifying schema: {e}")
            return False
    
    def create_default_master_data(self):
        """Create default master data"""
        print("\n📊 Creating default master data...")
        
        sql_commands = """
BEGIN;

-- Insert default organization
INSERT INTO organization (name, company_registration_number, industry, country, is_active, created_at)
VALUES ('Default Organization', 'ORG-DEFAULT-001', 'General', 'SG', true, NOW())
ON CONFLICT (name) DO NOTHING;

-- Insert default roles
INSERT INTO role (name, description, is_active, created_at) VALUES
('Super Admin', 'System administrator with full access', true, NOW()),
('Tenant Admin', 'Organization administrator', true, NOW()),
('Manager', 'Department manager', true, NOW()),
('Employee', 'Regular employee', true, NOW()),
('HR Officer', 'HR department staff', true, NOW())
ON CONFLICT (name) DO NOTHING;

-- Insert default designations
INSERT INTO designation (name, organization_id, is_active, created_at)
SELECT 'Manager', id, true, NOW() FROM organization WHERE name = 'Default Organization'
WHERE NOT EXISTS (SELECT 1 FROM designation WHERE name = 'Manager');

INSERT INTO designation (name, organization_id, is_active, created_at)
SELECT 'Senior Developer', id, true, NOW() FROM organization WHERE name = 'Default Organization'
WHERE NOT EXISTS (SELECT 1 FROM designation WHERE name = 'Senior Developer');

INSERT INTO designation (name, organization_id, is_active, created_at)
SELECT 'Junior Developer', id, true, NOW() FROM organization WHERE name = 'Default Organization'
WHERE NOT EXISTS (SELECT 1 FROM designation WHERE name = 'Junior Developer');

INSERT INTO designation (name, organization_id, is_active, created_at)
SELECT 'HR Manager', id, true, NOW() FROM organization WHERE name = 'Default Organization'
WHERE NOT EXISTS (SELECT 1 FROM designation WHERE name = 'HR Manager');

-- Insert default leave types
INSERT INTO leave_type (name, description, default_days_per_year, is_active, created_at) VALUES
('Annual Leave', 'Paid annual leave', 21, true, NOW()),
('Medical Leave', 'Medical leave', 14, true, NOW()),
('Emergency Leave', 'Emergency leave', 5, true, NOW()),
('Unpaid Leave', 'Unpaid leave', 0, true, NOW())
ON CONFLICT (name) DO NOTHING;

-- Insert default bank
INSERT INTO bank (code, name, is_active, created_at) VALUES
('OCBC', 'OCBC Bank', true, NOW()),
('DBS', 'DBS Bank', true, NOW()),
('MAYBANK', 'Maybank', true, NOW()),
('UOB', 'UOB Bank', true, NOW()),
('CIMB', 'CIMB Bank', true, NOW())
ON CONFLICT (code) DO NOTHING;

COMMIT;
"""
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(sql_commands))
                conn.commit()
            print("✅ Default master data created")
            return True
        except Exception as e:
            print(f"⚠️  Could not create master data: {e}")
            # Don't fail, as this is optional
            return False
    
    def initialize(self):
        """Run full initialization"""
        print("=" * 60)
        print("🚀 PRODUCTION DATABASE INITIALIZATION")
        print("=" * 60)
        
        if not self.connect():
            return False
        
        # Check if already initialized
        is_empty = self.is_empty()
        if is_empty is None:
            return False
        
        table_count = self.get_table_count()
        
        if is_empty:
            print(f"\n📌 Database is empty ({table_count} tables)")
            print("Initializing production database...\n")
            
            if not self.run_alembic_migrations():
                print("\n❌ Initialization failed at schema creation")
                return False
            
            if not self.verify_schema():
                print("\n⚠️  Some tables may be missing")
                return False
            
            self.create_default_master_data()
            
            print("\n" + "=" * 60)
            print("✅ INITIALIZATION COMPLETE")
            print("=" * 60)
            print("\n📝 Next steps:")
            print("1. Import your master data: python import_master_data.py --env prod")
            print("2. Create admin user: python create_admin_user.py")
            print("3. Deploy application: git push origin master")
            
            return True
        else:
            print(f"\n📌 Database already has {table_count} tables")
            print("Initialization not needed (database already initialized)")
            return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize Production Database')
    parser.add_argument('--check', action='store_true', help='Only check if initialized')
    parser.add_argument('--force', action='store_true', help='Force initialization')
    
    args = parser.parse_args()
    
    initializer = ProductionDatabaseInitializer()
    
    if args.check:
        if initializer.connect():
            if initializer.is_empty():
                print("❌ Database is EMPTY - needs initialization")
                sys.exit(1)
            else:
                print(f"✅ Database is initialized ({initializer.get_table_count()} tables)")
                sys.exit(0)
    else:
        success = initializer.initialize()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()