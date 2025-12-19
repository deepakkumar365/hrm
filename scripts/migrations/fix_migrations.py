#!/usr/bin/env python
"""Fix migration heads by marking existing migrations as applied"""

from app import app, db
from sqlalchemy import text

def fix_migrations():
    """Mark problematic migrations as applied"""
    with app.app_context():
        # Check which migrations already exist in the database
        result = db.session.execute(text("SELECT version_num FROM alembic_version ORDER BY version_num")).fetchall()
        applied = [r[0] for r in result]
        
        print("Currently applied migrations:")
        for mig in sorted(applied):
            print(f"  ✓ {mig}")
        
        # Check if the problematic migration is already applied
        if 'add_ot_daily_summary_001' not in applied:
            print("\nMarking add_ot_daily_summary_001 as applied...")
            try:
                db.session.execute(text("INSERT INTO alembic_version (version_num) VALUES ('add_ot_daily_summary_001')"))
                db.session.commit()
                print("✓ Migration marked as applied")
            except Exception as e:
                print(f"✗ Error: {e}")
                db.session.rollback()
        else:
            print("\n✓ add_ot_daily_summary_001 is already applied")
        
        # Now try to get current status
        print("\n" + "="*60)
        print("Running: flask db current")
        print("="*60)

if __name__ == '__main__':
    fix_migrations()
