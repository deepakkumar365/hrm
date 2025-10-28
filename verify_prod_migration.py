#!/usr/bin/env python3
"""
Production Migration Verification Script
Validates database migration success and data integrity
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text, MetaData, Table
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Load environment variables
load_dotenv()

class MigrationVerifier:
    def __init__(self):
        self.dev_url = os.getenv('DEV_DATABASE_URL')
        self.prod_url = os.getenv('PROD_DATABASE_URL')
        self.dev_engine = None
        self.prod_engine = None
        self.errors = []
        self.warnings = []
        self.info = []
        
    def connect(self):
        """Establish database connections"""
        try:
            print("🔗 Connecting to databases...")
            self.dev_engine = create_engine(self.dev_url, echo=False)
            self.dev_engine.connect().close()
            print("  ✅ Development database connected")
            
            self.prod_engine = create_engine(self.prod_url, echo=False)
            self.prod_engine.connect().close()
            print("  ✅ Production database connected")
            
            return True
        except Exception as e:
            self.errors.append(f"Connection failed: {e}")
            print(f"  ❌ Connection error: {e}")
            return False
    
    def verify_schemas(self, detailed=False):
        """Verify table existence and structure"""
        print("\n📋 Verifying database schemas...")
        
        dev_inspector = inspect(self.dev_engine)
        prod_inspector = inspect(self.prod_engine)
        
        dev_tables = set(dev_inspector.get_table_names())
        prod_tables = set(prod_inspector.get_table_names())
        
        print(f"  Development tables: {len(dev_tables)}")
        print(f"  Production tables: {len(prod_tables)}")
        
        if not dev_tables:
            self.warnings.append("Development database is empty")
            print("  ⚠️  Development database has no tables")
            return False
        
        if not prod_tables:
            self.warnings.append("Production database is empty")
            print("  ⚠️  Production database has no tables")
            return False
        
        # Check for missing tables
        missing_tables = dev_tables - prod_tables
        if missing_tables:
            self.errors.append(f"Missing tables in production: {missing_tables}")
            print(f"  ❌ Missing in production: {missing_tables}")
            return False
        
        if detailed:
            print(f"  ✅ All {len(dev_tables)} tables present in production")
            for table in sorted(dev_tables):
                dev_cols = len(dev_inspector.get_columns(table))
                prod_cols = len(prod_inspector.get_columns(table))
                if dev_cols != prod_cols:
                    self.warnings.append(f"Column count mismatch in {table}: dev={dev_cols}, prod={prod_cols}")
                    print(f"    ⚠️  {table}: columns dev={dev_cols} prod={prod_cols}")
                else:
                    print(f"    ✅ {table}: {dev_cols} columns")
        else:
            print(f"  ✅ All tables present")
        
        return True
    
    def verify_data_integrity(self, detailed=False):
        """Verify critical master data tables are populated"""
        print("\n📊 Verifying data integrity...")
        
        critical_tables = {
            'organization': 'Organizations',
            'role': 'Roles',
            'designation': 'Designations',
            'leave_type': 'Leave Types',
        }
        
        all_ok = True
        
        for table_name, display_name in critical_tables.items():
            try:
                with self.prod_engine.connect() as conn:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    
                    if count == 0:
                        self.warnings.append(f"{display_name} table is empty")
                        print(f"  ⚠️  {display_name}: 0 records")
                        all_ok = False
                    else:
                        print(f"  ✅ {display_name}: {count} records")
                        self.info.append(f"{display_name}: {count}")
            except Exception as e:
                self.errors.append(f"Error querying {table_name}: {e}")
                print(f"  ❌ {display_name}: Query error - {e}")
                all_ok = False
        
        return all_ok
    
    def verify_foreign_keys(self):
        """Verify foreign key relationships"""
        print("\n🔗 Verifying foreign key constraints...")
        
        try:
            with self.prod_engine.connect() as conn:
                # Get all foreign key constraints
                query = """
                    SELECT constraint_name, table_name, column_name, 
                           foreign_table_name, foreign_column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu 
                        ON tc.constraint_name = kcu.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                    ORDER BY table_name
                """
                result = conn.execute(text(query))
                fk_count = 0
                
                for row in result:
                    fk_count += 1
                    if fk_count <= 5:  # Show first 5
                        print(f"  ✅ {row[1]}.{row[2]} → {row[3]}.{row[4]}")
                
                if fk_count > 5:
                    print(f"  ✅ ... and {fk_count - 5} more constraints")
                
                if fk_count == 0:
                    self.warnings.append("No foreign key constraints found")
                    print("  ⚠️  No foreign key constraints detected")
                
                self.info.append(f"Foreign keys: {fk_count}")
                
        except Exception as e:
            self.warnings.append(f"Foreign key verification: {e}")
            print(f"  ⚠️  Could not verify foreign keys: {e}")
        
        return True
    
    def verify_indexes(self):
        """Verify indexes are created"""
        print("\n⚡ Verifying indexes...")
        
        try:
            with self.prod_engine.connect() as conn:
                query = """
                    SELECT indexname, tablename 
                    FROM pg_indexes 
                    WHERE schemaname = 'public'
                    ORDER BY tablename
                """
                result = conn.execute(text(query))
                indexes = list(result)
                
                if indexes:
                    print(f"  ✅ {len(indexes)} indexes found")
                    for idx in indexes[:5]:
                        print(f"    • {idx[1]}: {idx[0]}")
                    if len(indexes) > 5:
                        print(f"    ... and {len(indexes) - 5} more")
                    self.info.append(f"Indexes: {len(indexes)}")
                else:
                    self.warnings.append("No indexes found")
                    print("  ⚠️  No indexes detected")
                
        except Exception as e:
            self.warnings.append(f"Index verification: {e}")
            print(f"  ⚠️  Could not verify indexes: {e}")
        
        return True
    
    def verify_users_table(self):
        """Verify users table for login readiness"""
        print("\n👥 Verifying users table...")
        
        try:
            with self.prod_engine.connect() as conn:
                # Check users count
                result = conn.execute(text("SELECT COUNT(*) FROM hrm_users"))
                user_count = result.scalar()
                
                if user_count == 0:
                    self.warnings.append("No users in production database")
                    print("  ⚠️  No users found - may need to setup users")
                else:
                    print(f"  ✅ {user_count} users in database")
                    
                    # Check for active users
                    result = conn.execute(text("SELECT COUNT(*) FROM hrm_users WHERE is_active = true"))
                    active_count = result.scalar()
                    print(f"  ✅ {active_count} active users")
                    
                    # Check for test users
                    result = conn.execute(text("SELECT COUNT(*) FROM hrm_users WHERE password_hash IS NOT NULL"))
                    pwd_count = result.scalar()
                    print(f"  ✅ {pwd_count} users with passwords set")
                    
                    self.info.append(f"Users: {user_count} (active: {active_count})")
                
                return user_count > 0
                
        except Exception as e:
            self.warnings.append(f"User table verification: {e}")
            print(f"  ⚠️  Could not verify users: {e}")
            return False
    
    def generate_report(self):
        """Generate final verification report"""
        print("\n" + "="*60)
        print("📋 MIGRATION VERIFICATION REPORT")
        print("="*60)
        print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.info:
            print("\n✅ SUCCESS INDICATORS:")
            for item in self.info:
                print(f"  • {item}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for item in self.warnings:
                print(f"  • {item}")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for item in self.errors:
                print(f"  • {item}")
        
        # Overall status
        print("\n" + "-"*60)
        if self.errors:
            status = "❌ MIGRATION NEEDS ATTENTION"
            color = "red"
        elif self.warnings:
            status = "⚠️  MIGRATION PARTIAL SUCCESS"
            color = "yellow"
        else:
            status = "✅ MIGRATION SUCCESSFUL"
            color = "green"
        
        print(f"\n{status}")
        print("-"*60)
        
        return len(self.errors) == 0
    
    def run_quick_verification(self):
        """Run quick verification (connection + schemas + data)"""
        print("🚀 QUICK VERIFICATION MODE\n")
        
        if not self.connect():
            return False
        
        if not self.verify_schemas():
            return False
        
        if not self.verify_data_integrity():
            return False
        
        return self.generate_report()
    
    def run_detailed_verification(self):
        """Run detailed verification (all checks)"""
        print("🔍 DETAILED VERIFICATION MODE\n")
        
        if not self.connect():
            return False
        
        if not self.verify_schemas(detailed=True):
            return False
        
        if not self.verify_data_integrity(detailed=True):
            return False
        
        if not self.verify_foreign_keys():
            return False
        
        if not self.verify_indexes():
            return False
        
        if not self.verify_users_table():
            return False
        
        return self.generate_report()


def main():
    parser = argparse.ArgumentParser(description='Verify HRMS Production Database Migration')
    parser.add_argument('--quick', action='store_true', help='Quick verification only')
    parser.add_argument('--detailed', action='store_true', help='Detailed verification')
    parser.add_argument('--stats', action='store_true', help='Database statistics')
    
    args = parser.parse_args()
    
    verifier = MigrationVerifier()
    
    if args.detailed:
        success = verifier.run_detailed_verification()
    else:
        # Default to quick verification
        success = verifier.run_quick_verification()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()