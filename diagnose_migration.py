#!/usr/bin/env python
"""Diagnose migration and database state"""
from app import db, create_app

app = create_app()
with app.app_context():
    print("\n" + "="*60)
    print("🔍 MIGRATION DIAGNOSTIC")
    print("="*60)
    
    # Check alembic_version table
    try:
        result = db.session.execute(db.text('SELECT version_num FROM alembic_version'))
        versions = [row[0] for row in result]
        print(f"\n✅ Alembic versions applied: {len(versions)} migration(s)")
        for v in versions:
            print(f"   - {v}")
    except Exception as e:
        print(f"\n❌ Could not read alembic_version: {e}")
    
    # Check if designation_id column exists
    try:
        result = db.session.execute(db.text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='hrm_employee' AND column_name='designation_id'"
        ))
        if result.fetchone():
            print("\n✅ Column designation_id EXISTS in database")
        else:
            print("\n❌ Column designation_id MISSING from database")
    except Exception as e:
        print(f"\n❌ Could not check column: {e}")
    
    # Check all columns in hrm_employee
    try:
        result = db.session.execute(db.text(
            "SELECT column_name FROM information_schema.columns WHERE table_name='hrm_employee' ORDER BY ordinal_position"
        ))
        columns = [row[0] for row in result]
        print(f"\n📊 Current hrm_employee columns ({len(columns)} total):")
        for col in columns:
            print(f"   - {col}")
    except Exception as e:
        print(f"\n❌ Could not list columns: {e}")
    
    print("\n" + "="*60)