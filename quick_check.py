#!/usr/bin/env python3
import sys
sys.path.insert(0, 'D:/Projects/HRMS/hrm')

from app import app, db
from sqlalchemy import text, inspect

with app.app_context():
    print("\n" + "="*80)
    print("QUICK TABLE CHECK")
    print("="*80)
    
    try:
        inspector = inspect(db.engine)
        all_tables = inspector.get_table_names()
        
        print(f"\n📊 Total tables: {len(all_tables)}")
        
        target = 'hrm_company_employee_id_config'
        if target in all_tables:
            print(f"\n✅ TABLE '{target}' EXISTS!")
            
            # Get columns
            cols = inspector.get_columns(target)
            print(f"\nColumns ({len(cols)}):")
            for col in cols:
                print(f"  - {col['name']}")
            
            # Count records
            result = db.session.execute(text(f"SELECT COUNT(*) FROM {target}"))
            count = result.scalar()
            print(f"\nRecords: {count}")
            
        else:
            print(f"\n❌ TABLE '{target}' DOES NOT EXIST")
            print(f"\nTables found ({len(all_tables)}):")
            for t in sorted(all_tables):
                if 'company' in t.lower() or 'employee' in t.lower():
                    print(f"  • {t}")
        
        print("\n" + "="*80)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()