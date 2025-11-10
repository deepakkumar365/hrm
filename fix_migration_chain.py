#!/usr/bin/env python
"""Diagnose and fix migration chain issues"""

import os
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, r'D:\Projects\HRMS\hrm')

from app import app, db
from alembic import command
from alembic.config import Config

def check_alembic_versions():
    """Check what's in the alembic_version table"""
    try:
        with app.app_context():
            result = db.session.execute(db.text("SELECT * FROM alembic_version;"))
            versions = result.fetchall()
            print("\n📋 Current Alembic Versions in Database:")
            if versions:
                for v in versions:
                    print(f"   - {v[0]}")
            else:
                print("   ❌ No versions found (database not initialized)")
            return versions
    except Exception as e:
        print(f"\n⚠️  Cannot read alembic_version: {e}")
        return None

def list_migration_files():
    """List all migration files and their revision IDs"""
    migrations_dir = Path(r'D:\Projects\HRMS\hrm\migrations\versions')
    print("\n📁 Migration Files Found:")
    
    py_files = sorted([f for f in migrations_dir.glob('*.py') if f.name != '__init__.py'])
    
    for f in py_files:
        content = f.read_text()
        # Extract revision and down_revision
        revision = None
        down_revision = None
        
        for line in content.split('\n'):
            if line.startswith("revision = "):
                revision = line.split("'")[1] if "'" in line else None
            if line.startswith("down_revision = "):
                down_rev_part = line.split('=')[1].strip()
                if down_rev_part == "None":
                    down_revision = "None"
                else:
                    down_revision = down_rev_part.split("'")[1] if "'" in down_rev_part else None
        
        status = "✓" if revision else "✗"
        print(f"   {status} {f.name}")
        print(f"      revision: {revision}")
        print(f"      down_revision: {down_revision}")

def run_migration():
    """Run the migration"""
    print("\n🔄 Running Migration...")
    try:
        with app.app_context():
            alembic_cfg = Config(r'D:\Projects\HRMS\hrm\migrations\alembic.ini')
            alembic_cfg.set_main_option("sqlalchemy.url", app.config['SQLALCHEMY_DATABASE_URI'])
            
            command.upgrade(alembic_cfg, "head")
            print("✅ Migration completed successfully!")
            return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("🔧 Migration Chain Diagnostic Tool")
    print("=" * 60)
    
    # Check current versions
    versions = check_alembic_versions()
    
    # List migrations
    list_migration_files()
    
    # Try to run migration
    print("\n" + "=" * 60)
    if not run_migration():
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
    
    # Verify
    print("\n✅ Verifying migration...")
    versions = check_alembic_versions()
    print("\n✅ Done!")

if __name__ == '__main__':
    main()