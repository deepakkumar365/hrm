#!/usr/bin/env python3
"""Diagnose the CompanyEmployeeIdConfig table status"""

from app import app, db
from sqlalchemy import text, inspect

def diagnose():
    with app.app_context():
        print("\n" + "="*80)
        print("DIAGNOSTIC REPORT: CompanyEmployeeIdConfig Table")
        print("="*80)
        
        try:
            # Check migration history
            print("\n[1] Checking Migration History...")
            print("-" * 80)
            
            try:
                result = db.session.execute(text(
                    "SELECT version_num FROM alembic_version ORDER BY version_num DESC LIMIT 5"
                ))
                versions = result.fetchall()
                print("✅ Alembic version table exists")
                print(f"   Last 5 applied migrations:")
                for v in versions:
                    status = "✅ (TARGET)" if v[0] == 'add_company_employee_id_config' else ""
                    print(f"   - {v[0]} {status}")
                
                # Check if our migration is applied
                target_applied = any(v[0] == 'add_company_employee_id_config' for v in versions)
                if not target_applied:
                    print("\n❌ PROBLEM: Migration 'add_company_employee_id_config' NOT APPLIED!")
                    print("   The migration file exists but hasn't been executed.")
                else:
                    print("\n✅ Migration 'add_company_employee_id_config' is applied")
                    
            except Exception as e:
                print(f"⚠️  Cannot query alembic_version: {e}")
            
            # Check if table exists
            print("\n[2] Checking Table Existence...")
            print("-" * 80)
            
            inspector = inspect(db.engine)
            all_tables = inspector.get_table_names()
            table_exists = 'hrm_company_employee_id_config' in all_tables
            
            if table_exists:
                print("✅ Table 'hrm_company_employee_id_config' EXISTS in database")
                
                # Get structure
                columns = inspector.get_columns('hrm_company_employee_id_config')
                print(f"\n   Columns ({len(columns)}):")
                for col in columns:
                    print(f"   - {col['name']:25} {str(col['type']):20}")
                
                # Count records
                try:
                    result = db.session.execute(text(
                        "SELECT COUNT(*) FROM hrm_company_employee_id_config"
                    ))
                    count = result.scalar()
                    print(f"\n   Records: {count}")
                except Exception as e:
                    print(f"   Error counting: {e}")
            else:
                print("❌ Table 'hrm_company_employee_id_config' DOES NOT EXIST")
                print("\n   Similar tables in database:")
                for t in sorted(all_tables):
                    if 'employee' in t.lower() or 'company' in t.lower():
                        print(f"   - {t}")
            
            # Check if model is loaded
            print("\n[3] Checking Model Class...")
            print("-" * 80)
            
            try:
                from models import CompanyEmployeeIdConfig
                print("✅ CompanyEmployeeIdConfig model class is importable")
                print(f"   Table name: {CompanyEmployeeIdConfig.__tablename__}")
                print(f"   Columns: {[c.name for c in CompanyEmployeeIdConfig.__table__.columns]}")
            except ImportError as e:
                print(f"❌ Error importing model: {e}")
            
            # Summary
            print("\n" + "="*80)
            print("SUMMARY")
            print("="*80)
            
            if table_exists:
                print("✅ TABLE EXISTS - Everything is OK!")
            else:
                print("❌ TABLE MISSING - Action needed:")
                print("\n   Option 1: Run migration (recommended)")
                print("   $ flask db upgrade")
                print("\n   Option 2: Create table directly")
                print("   $ python create_table_direct.py")
                print("\n   Option 3: Initialize with detection")
                print("   $ python init_company_id_config_now.py")
            
            print("\n" + "="*80 + "\n")
            
            return table_exists
            
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    diagnose()