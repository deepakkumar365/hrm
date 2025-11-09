#!/usr/bin/env python
"""Verify hrm_company_employee_id_config table exists and has data"""

import sys
from app import app, db
from models import CompanyEmployeeIdConfig, Company

def verify():
    with app.app_context():
        print("=" * 60)
        print("VERIFICATION REPORT: hrm_company_employee_id_config")
        print("=" * 60)
        
        try:
            # Check if table exists
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'hrm_company_employee_id_config' not in tables:
                print("\n❌ TABLE NOT FOUND!")
                print("Available tables:", sorted(tables))
                return False
            
            print("\n✅ Table EXISTS in database")
            
            # Check columns
            columns = inspector.get_columns('hrm_company_employee_id_config')
            print("\n📋 Columns:")
            for col in columns:
                col_type = col['type']
                nullable = "nullable" if col['nullable'] else "NOT NULL"
                print(f"   - {col['name']:30} {str(col_type):20} {nullable}")
            
            # Query data
            configs = CompanyEmployeeIdConfig.query.all()
            print(f"\n📊 Data: {len(configs)} configuration(s)")
            
            if configs:
                for config in configs:
                    company = Company.query.get(config.company_id)
                    print(f"   ✅ {company.code:15} | Prefix: {config.id_prefix:10} | Last Seq: {config.last_sequence_number}")
            else:
                print("   ⚠️  No configurations found - Run setup_company_employee_id_config.py")
            
            print("\n" + "=" * 60)
            print("✨ Verification complete!")
            print("=" * 60)
            return len(configs) > 0
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = verify()
    sys.exit(0 if success else 1)