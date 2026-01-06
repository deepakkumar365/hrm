#!/usr/bin/env python3
"""
Pre-Migration Checklist Verification
Ensures all prerequisites are met before database migration
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

# Load environment variables
load_dotenv()

# Add project to path (two levels up from scripts/diagnostics/)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class PreMigrationChecker:
    def __init__(self):
        self.checks = []
        self.critical_issues = []
        self.warnings = []
        
    def check_env_variables(self):
        """Verify all required environment variables are set"""
        print("\n📋 CHECKING ENVIRONMENT VARIABLES")
        print("-" * 60)
        
        required_vars = {
            'DEV_DATABASE_URL': 'Development Database URL',
            'PROD_DATABASE_URL': 'Production Database URL',
            'PROD_SESSION_SECRET': 'Development Session Secret',
            'PROD_SESSION_SECRET': 'Production Session Secret',
        }
        
        env_ok = True
        for var, desc in required_vars.items():
            if os.getenv(var):
                print(f"✅ {desc}: SET")
                self.checks.append(f"{desc}: SET")
            else:
                print(f"❌ {desc}: MISSING")
                self.critical_issues.append(f"{desc} is not set in .env")
                env_ok = False
        
        return env_ok
    
    def check_database_connectivity(self):
        """Test connections to both databases"""
        print("\n🔗 CHECKING DATABASE CONNECTIVITY")
        print("-" * 60)
        
        dev_url = os.getenv('DEV_DATABASE_URL')
        prod_url = os.getenv('PROD_DATABASE_URL')
        
        conn_ok = True
        
        # Test development database
        try:
            dev_engine = create_engine(dev_url, echo=False, connect_args={"timeout": 5})
            with dev_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Development database: CONNECTED")
            self.checks.append("Development database: CONNECTED")
        except Exception as e:
            print(f"❌ Development database: FAILED - {str(e)[:50]}")
            self.critical_issues.append(f"Cannot connect to development database: {e}")
            conn_ok = False
        
        # Test production database
        try:
            prod_engine = create_engine(prod_url, echo=False, connect_args={"timeout": 5})
            with prod_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Production database: CONNECTED")
            self.checks.append("Production database: CONNECTED")
        except Exception as e:
            print(f"❌ Production database: FAILED - {str(e)[:50]}")
            self.critical_issues.append(f"Cannot connect to production database: {e}")
            conn_ok = False
        
        return conn_ok
    
    def check_database_content(self):
        """Verify databases have expected content"""
        print("\n📊 CHECKING DATABASE CONTENT")
        print("-" * 60)
        
        dev_url = os.getenv('DEV_DATABASE_URL')
        prod_url = os.getenv('PROD_DATABASE_URL')
        
        content_ok = True
        
        try:
            dev_engine = create_engine(dev_url, echo=False)
            inspector = inspect(dev_engine)
            dev_tables = inspector.get_table_names()
            
            if dev_tables:
                print(f"✅ Development database: {len(dev_tables)} tables")
                self.checks.append(f"Development database: {len(dev_tables)} tables")
                
                # Show some tables
                for table in sorted(dev_tables)[:5]:
                    print(f"   • {table}")
                if len(dev_tables) > 5:
                    print(f"   ... and {len(dev_tables) - 5} more")
            else:
                print("⚠️  Development database: EMPTY - No tables found")
                self.warnings.append("Development database is empty - no data to migrate")
                content_ok = False
        except Exception as e:
            print(f"❌ Could not inspect development database: {e}")
            self.critical_issues.append(f"Cannot inspect development database: {e}")
            content_ok = False
        
        try:
            prod_engine = create_engine(prod_url, echo=False)
            inspector = inspect(prod_engine)
            prod_tables = inspector.get_table_names()
            
            if prod_tables:
                print(f"⚠️  Production database: {len(prod_tables)} tables (may need backup)")
                self.warnings.append("Production database is not empty - backup recommended")
            else:
                print(f"✅ Production database: EMPTY (ready for migration)")
                self.checks.append("Production database: EMPTY")
        except Exception as e:
            print(f"❌ Could not inspect production database: {e}")
            self.critical_issues.append(f"Cannot inspect production database: {e}")
            content_ok = False
        
        return content_ok
    
    def check_python_environment(self):
        """Verify Python environment and dependencies"""
        print("\n🐍 CHECKING PYTHON ENVIRONMENT")
        print("-" * 60)
        
        env_ok = True
        
        # Check Python version
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        if sys.version_info >= (3, 9):
            print(f"✅ Python version: {py_version}")
            self.checks.append(f"Python: {py_version}")
        else:
            print(f"❌ Python version: {py_version} (requires 3.9+)")
            self.warnings.append(f"Python version {py_version} may be too old")
        
        # Check required packages
        required_packages = {
            'sqlalchemy': 'SQLAlchemy',
            'flask': 'Flask',
            'flask_sqlalchemy': 'Flask-SQLAlchemy',
            'python_dotenv': 'python-dotenv',
            'werkzeug': 'Werkzeug',
        }
        
        for pkg_import, pkg_name in required_packages.items():
            try:
                __import__(pkg_import)
                print(f"✅ {pkg_name}: INSTALLED")
                self.checks.append(f"{pkg_name}: INSTALLED")
            except ImportError:
                print(f"❌ {pkg_name}: MISSING")
                self.critical_issues.append(f"{pkg_name} is not installed")
                env_ok = False
        
        return env_ok
    
    def check_migration_files(self):
        """Verify migration scripts exist"""
        print("\n📁 CHECKING MIGRATION FILES")
        print("-" * 60)
        
        files_ok = True
        base_path = Path(__file__).parent.parent.parent
        
        required_files = {
            'services/db_migration_to_prod.py': 'Main migration script',
            'core/models.py': 'Database models',
            'migrations/alembic.ini': 'Alembic configuration',
            'migrations/env.py': 'Alembic environment',
        }
        
        for file_path, description in required_files.items():
            full_path = base_path / file_path
            if full_path.exists():
                print(f"✅ {description}: FOUND")
                self.checks.append(f"{description}: FOUND")
            else:
                print(f"❌ {description}: MISSING ({file_path})")
                self.warnings.append(f"File not found: {file_path}")
                if 'migration' in file_path.lower() or 'alembic' in file_path.lower():
                    self.critical_issues.append(f"Required file missing: {file_path}")
                    files_ok = False
        
        return files_ok
    
    def check_disk_space(self):
        """Check available disk space"""
        print("\n💾 CHECKING DISK SPACE")
        print("-" * 60)
        
        try:
            import shutil
            base_path = Path(__file__).parent.drive if hasattr(Path(__file__).parent, 'drive') else '/'
            total, used, free = shutil.disk_usage(base_path)
            free_gb = free / (1024**3)
            
            if free_gb > 5:
                print(f"✅ Disk space available: {free_gb:.2f} GB")
                self.checks.append(f"Disk space: {free_gb:.2f} GB")
                return True
            else:
                print(f"⚠️  Disk space low: {free_gb:.2f} GB (recommend 5+ GB)")
                self.warnings.append(f"Low disk space: {free_gb:.2f} GB")
                return False
        except Exception as e:
            print(f"⚠️  Could not check disk space: {e}")
            return True
    
    def check_backup_location(self):
        """Verify backup directory exists and is writable"""
        print("\n🛡️  CHECKING BACKUP LOCATION")
        print("-" * 60)
        
        backup_dir = Path(__file__).parent.parent.parent / 'db_backups'
        
        try:
            backup_dir.mkdir(exist_ok=True)
            
            # Test write permission
            test_file = backup_dir / '.test'
            test_file.write_text('test')
            test_file.unlink()
            
            print(f"✅ Backup directory: READY ({backup_dir})")
            self.checks.append(f"Backup directory: READY")
            return True
        except Exception as e:
            print(f"⚠️  Backup directory issue: {e}")
            self.warnings.append(f"Backup directory may not be writable: {e}")
            return False
    
    def print_summary(self):
        """Print summary of all checks"""
        print("\n" + "="*60)
        print("📋 PRE-MIGRATION CHECKLIST SUMMARY")
        print("="*60)
        
        print(f"\n✅ PASSED CHECKS: {len(self.checks)}")
        for check in self.checks:
            print(f"  • {check}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS: {len(self.warnings)}")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if self.critical_issues:
            print(f"\n❌ CRITICAL ISSUES: {len(self.critical_issues)}")
            for issue in self.critical_issues:
                print(f"  • {issue}")
        
        print("\n" + "-"*60)
        
        if self.critical_issues:
            print("\n🛑 MIGRATION BLOCKED")
            print("Please fix critical issues above before proceeding.\n")
            return False
        elif self.warnings:
            print("\n⚠️  MIGRATION CAN PROCEED WITH CAUTION")
            print("Address warnings if possible.\n")
            return True
        else:
            print("\n✅ ALL CHECKS PASSED - READY FOR MIGRATION\n")
            return True
    
    def run_all_checks(self):
        """Run all pre-migration checks"""
        print("\n" + "="*60)
        print("🚀 PRE-MIGRATION CHECKLIST")
        print("="*60)
        
        self.check_env_variables()
        self.check_database_connectivity()
        self.check_database_content()
        self.check_python_environment()
        self.check_migration_files()
        self.check_disk_space()
        self.check_backup_location()
        
        success = self.print_summary()
        
        return success


def main():
    checker = PreMigrationChecker()
    success = checker.run_all_checks()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
