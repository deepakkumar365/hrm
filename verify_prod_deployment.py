#!/usr/bin/env python3
"""
Production Deployment Verification Script
Verifies database schema, master data, and application readiness
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Load environment variables
load_dotenv()

class DeploymentVerifier:
    def __init__(self, environment='prod'):
        self.environment = environment
        if environment == 'prod':
            self.db_url = os.getenv('PROD_DATABASE_URL')
        else:
            self.db_url = os.getenv('DEV_DATABASE_URL')
        
        self.engine = None
        self.checks_passed = 0
        self.checks_failed = 0
    
    def connect(self):
        """Establish database connection"""
        try:
            self.engine = create_engine(self.db_url, echo=False)
            self.engine.connect().close()
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def check_tables(self):
        """Verify all required tables exist"""
        print("\n📋 Checking Tables...")
        
        required_tables = [
            'hrm_users',
            'role',
            'organization',
            'employee',
            'designation',
            'leave_type',
            'leave_request',
            'attendance',
            'payroll',
            'payslip'
        ]
        
        inspector = inspect(self.engine)
        existing_tables = set(inspector.get_table_names())
        
        all_exist = True
        for table in required_tables:
            if table in existing_tables:
                print(f"  ✅ {table}")
                self.checks_passed += 1
            else:
                print(f"  ❌ {table} (MISSING)")
                all_exist = False
                self.checks_failed += 1
        
        return all_exist
    
    def check_master_data(self):
        """Verify master data exists"""
        print("\n📊 Checking Master Data...")
        
        master_tables = {
            'organization': 'Organizations',
            'role': 'Roles',
            'designation': 'Designations',
            'leave_type': 'Leave Types'
        }
        
        all_have_data = True
        
        try:
            with self.engine.connect() as conn:
                for table, display_name in master_tables.items():
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                    count = result.scalar()
                    
                    if count > 0:
                        print(f"  ✅ {display_name}: {count} records")
                        self.checks_passed += 1
                    else:
                        print(f"  ⚠️  {display_name}: {count} records (EMPTY)")
                        all_have_data = False
                        self.checks_failed += 1
        except Exception as e:
            print(f"  ❌ Error checking master data: {e}")
            self.checks_failed += 1
            return False
        
        return all_have_data
    
    def check_user_accounts(self):
        """Verify user accounts exist"""
        print("\n👥 Checking User Accounts...")
        
        try:
            with self.engine.connect() as conn:
                # Check total users
                result = conn.execute(text("SELECT COUNT(*) FROM hrm_users;"))
                user_count = result.scalar()
                
                print(f"  Total users: {user_count}")
                
                # Check active users
                result = conn.execute(text("SELECT COUNT(*) FROM hrm_users WHERE is_active = true;"))
                active_count = result.scalar()
                
                print(f"  Active users: {active_count}")
                
                # Check for admin users
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM hrm_users 
                    WHERE role_id IN (SELECT id FROM role WHERE name LIKE '%admin%' OR name LIKE '%superadmin%')
                """))
                admin_count = result.scalar()
                
                if admin_count > 0:
                    print(f"  ✅ Admin accounts: {admin_count} found")
                    self.checks_passed += 1
                else:
                    print(f"  ⚠️  Admin accounts: None found (may need setup)")
                    self.checks_failed += 1
                
                return user_count > 0
                
        except Exception as e:
            print(f"  ❌ Error checking users: {e}")
            self.checks_failed += 1
            return False
    
    def check_indexes(self):
        """Verify indexes are created"""
        print("\n🔍 Checking Indexes...")
        
        inspector = inspect(self.engine)
        
        tables_to_check = ['hrm_users', 'employee', 'organization']
        total_indexes = 0
        
        for table in tables_to_check:
            try:
                indexes = inspector.get_indexes(table)
                index_count = len(indexes)
                total_indexes += index_count
                
                if index_count > 0:
                    print(f"  ✅ {table}: {index_count} indexes")
                    self.checks_passed += 1
                else:
                    print(f"  ⚠️  {table}: No indexes (may impact performance)")
                    self.checks_failed += 1
            except Exception as e:
                print(f"  ⚠️  {table}: Could not check indexes ({e})")
        
        return total_indexes > 0
    
    def check_database_size(self):
        """Check database size and storage"""
        print("\n💾 Checking Database Size...")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT pg_size_pretty(pg_database_size(current_database()));
                """))
                db_size = result.scalar()
                
                print(f"  Database size: {db_size}")
                self.checks_passed += 1
                
                return True
        except Exception as e:
            print(f"  ⚠️  Could not determine database size: {e}")
            return False
    
    def check_schema_version(self):
        """Check Alembic schema version"""
        print("\n🔄 Checking Schema Version...")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 1;
                """))
                version = result.scalar()
                
                if version:
                    print(f"  ✅ Current schema version: {version}")
                    self.checks_passed += 1
                    return True
                else:
                    print(f"  ⚠️  No schema version found (migrations may not have run)")
                    return False
        except Exception as e:
            print(f"  ⚠️  Could not check schema version: {e}")
            return False
    
    def check_connections(self):
        """Check active database connections"""
        print("\n🔗 Checking Database Connections...")
        
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM pg_stat_activity;
                """))
                connection_count = result.scalar()
                
                print(f"  Active connections: {connection_count}")
                self.checks_passed += 1
                return True
        except Exception as e:
            print(f"  ⚠️  Could not check connections: {e}")
            return False
    
    def run_full_verification(self):
        """Run all verification checks"""
        print("=" * 60)
        print("🔍 PRODUCTION DEPLOYMENT VERIFICATION")
        print("=" * 60)
        print(f"Environment: {self.environment.upper()}")
        print(f"Timestamp: {datetime.now()}")
        
        if not self.connect():
            print("\n❌ VERIFICATION FAILED: Cannot connect to database")
            return False
        
        print("\n✅ Database connection successful")
        
        # Run all checks
        checks = [
            self.check_tables,
            self.check_master_data,
            self.check_user_accounts,
            self.check_indexes,
            self.check_database_size,
            self.check_schema_version,
            self.check_connections
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                print(f"❌ Check failed: {e}")
                self.checks_failed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"✅ Checks passed: {self.checks_passed}")
        print(f"❌ Checks failed: {self.checks_failed}")
        
        if self.checks_failed == 0:
            print("\n🎉 ALL CHECKS PASSED - DEPLOYMENT READY!")
            return True
        else:
            print(f"\n⚠️  {self.checks_failed} check(s) need attention")
            return False
    
    def generate_report(self):
        """Generate verification report"""
        report = f"""
DEPLOYMENT VERIFICATION REPORT
Generated: {datetime.now()}
Environment: {self.environment.upper()}

SUMMARY:
- Checks Passed: {self.checks_passed}
- Checks Failed: {self.checks_failed}
- Status: {'✅ READY FOR PRODUCTION' if self.checks_failed == 0 else '⚠️  REVIEW REQUIRED'}

RECOMMENDATIONS:
1. If all checks passed, proceed with production deployment
2. If any checks failed, review the detailed output above
3. For master data issues, run: python import_master_data.py --env prod
4. For schema issues, run: python db_migration_to_prod.py --mode schema-only

For questions, refer to: PRODUCTION_DB_MIGRATION_GUIDE.md
"""
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Production Deployment Verification')
    parser.add_argument('--env', choices=['prod', 'dev'], default='prod',
                       help='Environment to verify')
    parser.add_argument('--report', action='store_true',
                       help='Generate summary report')
    
    args = parser.parse_args()
    
    verifier = DeploymentVerifier(environment=args.env)
    success = verifier.run_full_verification()
    
    if args.report:
        print("\n" + verifier.generate_report())
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()