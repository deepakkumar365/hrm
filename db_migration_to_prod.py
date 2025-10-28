#!/usr/bin/env python3
"""
Production Database Migration Script
Handles schema migration and master data migration from Dev to Prod
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Load environment variables
load_dotenv()

class DatabaseMigrator:
    def __init__(self):
        self.dev_url = os.getenv('DEV_DATABASE_URL')
        self.prod_url = os.getenv('PROD_DATABASE_URL')
        self.dev_engine = None
        self.prod_engine = None
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def connect(self):
        """Establish database connections"""
        try:
            print("🔗 Connecting to development database...")
            self.dev_engine = create_engine(self.dev_url, echo=False)
            self.dev_engine.connect().close()
            print("✅ Development database connected")
        except Exception as e:
            print(f"❌ Failed to connect to development database: {e}")
            return False
            
        try:
            print("🔗 Connecting to production database...")
            self.prod_engine = create_engine(self.prod_url, echo=False)
            self.prod_engine.connect().close()
            print("✅ Production database connected")
        except Exception as e:
            print(f"❌ Failed to connect to production database: {e}")
            return False
            
        return True
    
    def verify_schemas(self):
        """Verify table existence in both databases"""
        print("\n📋 Verifying database schemas...")
        
        dev_inspector = inspect(self.dev_engine)
        prod_inspector = inspect(self.prod_engine)
        
        dev_tables = set(dev_inspector.get_table_names())
        prod_tables = set(prod_inspector.get_table_names())
        
        print(f"Development tables: {len(dev_tables)}")
        print(f"Production tables: {len(prod_tables)}")
        
        if dev_tables:
            print(f"✅ Development database has {len(dev_tables)} tables")
        else:
            print("⚠️  Warning: Development database appears to be empty")
            return False
            
        return True
    
    def run_alembic_migrations(self):
        """Run Alembic migrations on production database"""
        print("\n🔄 Running Alembic migrations on production database...")
        
        # Set production database URL for migration
        env = os.environ.copy()
        env['DATABASE_URL'] = self.prod_url
        
        try:
            # Run alembic upgrade
            result = subprocess.run(
                ['alembic', 'upgrade', 'head'],
                cwd='migrations',
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Alembic migrations completed successfully")
                if result.stdout:
                    print("Output:", result.stdout[:200])
                return True
            else:
                print(f"❌ Alembic migration failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error running Alembic: {e}")
            return False
    
    def export_master_data(self):
        """Export master data (organizations, roles, designations, etc.)"""
        print("\n💾 Exporting master data from development database...")
        
        master_tables = [
            'organization',
            'role',
            'designation',
            'leave_type',
            'bank',
            'overtime_group',
            'compliance_requirement',
            'document_type'
        ]
        
        export_file = f'master_data_{self.timestamp}.sql'
        
        try:
            with open(export_file, 'w') as f:
                # Write header
                f.write(f"-- Master Data Export\n")
                f.write(f"-- Exported from: Development Database\n")
                f.write(f"-- Date: {datetime.now()}\n")
                f.write(f"-- Tables: {', '.join(master_tables)}\n\n")
                f.write("BEGIN;\n\n")
                
                # Export each table
                for table_name in master_tables:
                    if self._table_exists(self.dev_engine, table_name):
                        print(f"  Exporting: {table_name}...", end=" ")
                        query = f"SELECT * FROM {table_name};"
                        with self.dev_engine.connect() as conn:
                            result = conn.execute(text(query))
                            rows = result.fetchall()
                            
                            if rows:
                                # Get column names
                                columns = result.keys()
                                col_str = ', '.join(columns)
                                
                                # Build INSERT statements
                                for row in rows:
                                    values = ', '.join([
                                        f"'{str(val).replace(chr(39), chr(39)*2)}'" if val is not None else 'NULL'
                                        for val in row
                                    ])
                                    f.write(f"INSERT INTO {table_name} ({col_str}) VALUES ({values});\n")
                                
                                print(f"✅ ({len(rows)} records)")
                            else:
                                print("(empty)")
                
                f.write("\nCOMMIT;\n")
            
            print(f"\n✅ Master data exported to: {export_file}")
            return export_file
            
        except Exception as e:
            print(f"❌ Error exporting master data: {e}")
            return None
    
    def import_master_data(self, export_file):
        """Import master data into production database"""
        print(f"\n📥 Importing master data to production database...")
        
        try:
            with open(export_file, 'r') as f:
                sql_commands = f.read()
            
            with self.prod_engine.connect() as conn:
                # Execute all SQL commands
                conn.execute(text(sql_commands))
                conn.commit()
            
            print("✅ Master data imported successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error importing master data: {e}")
            return False
    
    def verify_migration(self):
        """Verify successful migration"""
        print("\n✅ Verifying migration...")
        
        try:
            dev_inspector = inspect(self.dev_engine)
            prod_inspector = inspect(self.prod_engine)
            
            dev_tables = set(dev_inspector.get_table_names())
            prod_tables = set(prod_inspector.get_table_names())
            
            print(f"Development tables: {len(dev_tables)}")
            print(f"Production tables: {len(prod_tables)}")
            
            # Check table counts
            master_tables = ['organization', 'role', 'designation', 'leave_type']
            for table in master_tables:
                if table in prod_tables:
                    with self.prod_engine.connect() as conn:
                        result = conn.execute(text(f"SELECT COUNT(*) FROM {table};"))
                        count = result.scalar()
                        print(f"  {table}: {count} records")
            
            print("\n✅ Migration verification complete")
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
    
    def _table_exists(self, engine, table_name):
        """Check if table exists"""
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    
    def run_full_migration(self):
        """Execute full migration process"""
        print("=" * 60)
        print("🚀 PRODUCTION DATABASE MIGRATION")
        print("=" * 60)
        
        steps = [
            ("Database Connection", self.connect),
            ("Schema Verification", self.verify_schemas),
            ("Alembic Migrations", self.run_alembic_migrations),
            ("Master Data Export", lambda: self.export_master_data()),
        ]
        
        export_file = None
        
        for step_name, step_func in steps:
            print(f"\n📍 Step: {step_name}")
            result = step_func()
            
            if step_name == "Master Data Export":
                export_file = result
                if not export_file:
                    print(f"❌ {step_name} failed. Stopping migration.")
                    return False
            elif not result:
                print(f"❌ {step_name} failed. Stopping migration.")
                return False
        
        # Import master data
        if export_file:
            if not self.import_master_data(export_file):
                print("❌ Master data import failed. Stopping migration.")
                return False
        
        # Verify migration
        if not self.verify_migration():
            print("⚠️  Verification completed with warnings")
        
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print(f"\n📝 Master data file: {export_file}")
        print("✨ Production database is ready for deployment!")
        
        return True


def main():
    parser = argparse.ArgumentParser(description='HRMS Production Database Migration')
    parser.add_argument('--mode', choices=['full', 'schema-only', 'data-only'], 
                       default='full', help='Migration mode')
    parser.add_argument('--verify-only', action='store_true', 
                       help='Only verify without migrating')
    
    args = parser.parse_args()
    
    migrator = DatabaseMigrator()
    
    if args.verify_only:
        if migrator.connect():
            migrator.verify_schemas()
    elif args.mode == 'full':
        success = migrator.run_full_migration()
        sys.exit(0 if success else 1)
    elif args.mode == 'schema-only':
        if migrator.connect() and migrator.run_alembic_migrations():
            print("✅ Schema migration completed")
        else:
            sys.exit(1)
    elif args.mode == 'data-only':
        if migrator.connect():
            export_file = migrator.export_master_data()
            if export_file and migrator.import_master_data(export_file):
                print("✅ Data migration completed")
            else:
                sys.exit(1)


if __name__ == '__main__':
    main()