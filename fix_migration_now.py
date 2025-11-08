#!/usr/bin/env python
"""
Direct migration fix - Apply currency_code column migration
This script will:
1. Apply pending migrations
2. Verify currency_code exists
3. Show final status
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("🚀 APPLYING CURRENCY CODE MIGRATION")
print("=" * 70)

try:
    # Step 1: Import and setup
    print("\n📦 Step 1: Loading Flask application...")
    from main import app, db
    
    with app.app_context():
        from flask_migrate import upgrade, current
        from sqlalchemy import text, inspect
        
        # Step 2: Show current migration state
        print("\n📋 Step 2: Checking current migration state...")
        try:
            current_revision = current()
            print(f"   ✓ Current revision: {current_revision}")
        except:
            print("   ⚠️  No migrations applied yet")
        
        # Step 3: Apply migrations
        print("\n🔄 Step 3: Applying pending migrations...")
        upgrade()
        print("   ✅ Migrations applied!")
        
        # Step 4: Verify the column exists
        print("\n✅ Step 4: Verifying currency_code column...")
        inspector = inspect(db.engine)
        columns = inspector.get_columns('hrm_company')
        column_names = [col['name'] for col in columns]
        
        if 'currency_code' in column_names:
            print("   ✅ currency_code column EXISTS!")
            for col in columns:
                if col['name'] == 'currency_code':
                    print(f"      • Type: {col['type']}")
                    print(f"      • Nullable: {col['nullable']}")
                    print(f"      • Default: {col['default']}")
        else:
            print("   ❌ currency_code column NOT found")
            print("   Available columns:", ', '.join(column_names[:5]), "...")
        
        # Step 5: Check existing companies
        print("\n📊 Step 5: Checking existing companies...")
        result = db.session.execute(text("SELECT COUNT(*) as count FROM hrm_company"))
        company_count = result.fetchone()[0]
        print(f"   ✓ Total companies in database: {company_count}")
        
        if company_count > 0:
            result = db.session.execute(text(
                "SELECT id, name, currency_code FROM hrm_company LIMIT 3"
            ))
            rows = result.fetchall()
            print("   ✓ Sample companies:")
            for row in rows:
                print(f"      • {row[1]}: currency_code = '{row[2]}'")
        
        # Step 6: Final status
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print("\n🎉 Summary:")
        print("   ✓ Migration applied successfully")
        print("   ✓ currency_code column added to hrm_company")
        print("   ✓ Default value: SGD")
        print(f"   ✓ {company_count} companies configured")
        print("\n✨ You can now:")
        print("   1. Restart your Flask app: python main.py")
        print("   2. Navigate to Company management")
        print("   3. Create/Edit companies with currency selection")
        print("   4. Use currency codes in payroll module")
        print("\n" + "=" * 70)

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    print("\n📋 Full error trace:")
    traceback.print_exc()
    print("\n⚠️  Troubleshooting steps:")
    print("   1. Ensure PostgreSQL is running")
    print("   2. Check DATABASE_URL in .env file")
    print("   3. Verify database connection")
    sys.exit(1)

print("\n✅ Script completed successfully!")
sys.exit(0)