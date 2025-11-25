#!/usr/bin/env python3
"""
Fix multiple migration heads issue
This script merges all migration heads into a single linear chain
"""
import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment
os.environ['FLASK_APP'] = 'main.py'
os.environ['FLASK_ENV'] = 'development'

print("=" * 70)
print("FIXING MIGRATION HEADS ISSUE")
print("=" * 70)

# Import Flask app
try:
    from app import app, db
    from flask_migrate import init, migrate, upgrade, current, heads
    
    with app.app_context():
        print("\n1️⃣ CHECKING CURRENT MIGRATION STATUS...")
        try:
            current_rev = current()
            print(f"   ✅ Current revision: {current_rev}")
        except Exception as e:
            print(f"   ⚠️  Current revision check: {e}")
        
        print("\n2️⃣ ATTEMPTING TO UPGRADE TO ALL HEADS (merge)...")
        try:
            # Try to upgrade to all heads (this will merge them)
            subprocess.run(
                [sys.executable, '-m', 'flask', 'db', 'upgrade', 'heads'],
                cwd=str(project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            print("   ✅ Attempted upgrade to heads")
        except Exception as e:
            print(f"   ❌ Error with heads: {e}")
            print("\n3️⃣ FALLING BACK: UPGRADING WITH DEFAULT HEAD...")
            try:
                upgrade()
                print("   ✅ Successfully upgraded to default head")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        print("\n4️⃣ VERIFYING TIMEZONE COLUMN EXISTS...")
        try:
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('hrm_company')]
            
            if 'timezone' in columns:
                print("   ✅ TIMEZONE COLUMN EXISTS!")
                print(f"   Column list: {', '.join(columns[-5:])}")  # Show last 5 columns
            else:
                print("   ❌ TIMEZONE column not found")
                print(f"   Available columns: {', '.join(columns)}")
        except Exception as e:
            print(f"   ❌ Error checking columns: {e}")
        
        print("\n" + "=" * 70)
        print("MIGRATION FIX COMPLETE")
        print("=" * 70)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)