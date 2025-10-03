"""
Script to check the current database schema
Useful for debugging schema issues
"""
from app import app, db
from sqlalchemy import inspect
import sys

def check_schema():
    """Display the current database schema for hrm_users table"""
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            print("=" * 80)
            print("DATABASE SCHEMA CHECK")
            print("=" * 80)
            
            # Check if table exists
            tables = inspector.get_table_names()
            print(f"\n📋 Total tables in database: {len(tables)}")
            
            if 'hrm_users' not in tables:
                print("\n❌ ERROR: hrm_users table does not exist!")
                return False
            
            print("\n✅ hrm_users table exists")
            
            # Get columns
            print("\n" + "=" * 80)
            print("COLUMNS IN hrm_users TABLE")
            print("=" * 80)
            
            columns = inspector.get_columns('hrm_users')
            
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col.get('default') else ""
                print(f"  • {col['name']:<30} {str(col['type']):<20} {nullable}{default}")
            
            # Check for the problematic 'role' column
            column_names = [col['name'] for col in columns]
            
            print("\n" + "=" * 80)
            print("SCHEMA VALIDATION")
            print("=" * 80)
            
            issues = []
            
            if 'role' in column_names:
                print("\n❌ ISSUE FOUND: Old 'role' column exists")
                print("   This column should be removed. The model uses 'role_id' instead.")
                issues.append("Old 'role' column exists")
            else:
                print("\n✅ No 'role' column found (correct)")
            
            if 'role_id' in column_names:
                print("✅ 'role_id' column exists (correct)")
            else:
                print("❌ ISSUE FOUND: 'role_id' column is missing")
                issues.append("'role_id' column is missing")
            
            # Get foreign keys
            print("\n" + "=" * 80)
            print("FOREIGN KEYS IN hrm_users TABLE")
            print("=" * 80)
            
            foreign_keys = inspector.get_foreign_keys('hrm_users')
            
            if foreign_keys:
                for fk in foreign_keys:
                    print(f"  • {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
            else:
                print("  No foreign keys found")
            
            # Get indexes
            print("\n" + "=" * 80)
            print("INDEXES IN hrm_users TABLE")
            print("=" * 80)
            
            indexes = inspector.get_indexes('hrm_users')
            
            if indexes:
                for idx in indexes:
                    unique = "UNIQUE" if idx['unique'] else "NON-UNIQUE"
                    print(f"  • {idx['name']:<40} {unique:<12} {idx['column_names']}")
            else:
                print("  No indexes found")
            
            # Summary
            print("\n" + "=" * 80)
            print("SUMMARY")
            print("=" * 80)
            
            if issues:
                print(f"\n❌ Found {len(issues)} issue(s):")
                for i, issue in enumerate(issues, 1):
                    print(f"   {i}. {issue}")
                print("\n💡 Run 'python fix_production_schema.py' to fix these issues")
                return False
            else:
                print("\n✅ Schema looks good! No issues found.")
                return True
                
        except Exception as e:
            print(f"\n❌ Error checking schema: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = check_schema()
    print("\n" + "=" * 80)
    sys.exit(0 if success else 1)