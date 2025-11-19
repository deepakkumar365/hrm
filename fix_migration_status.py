#!/usr/bin/env python
"""Fix migration history by marking completed migrations"""

from app import db
from sqlalchemy import text

def mark_migration_as_applied(revision_id):
    """Mark a migration as applied in alembic_version table"""
    try:
        # Check if migration is already marked as applied
        result = db.session.execute(
            text("SELECT 1 FROM alembic_version WHERE version_num = :version"),
            {"version": revision_id}
        ).fetchone()
        
        if not result:
            # Insert the migration as applied
            db.session.execute(
                text("INSERT INTO alembic_version (version_num) VALUES (:version)"),
                {"version": revision_id}
            )
            db.session.commit()
            print(f"✓ Marked '{revision_id}' as applied")
        else:
            print(f"✓ '{revision_id}' already marked as applied")
            
    except Exception as e:
        print(f"✗ Error marking '{revision_id}': {e}")
        db.session.rollback()

if __name__ == '__main__':
    with db.app.app_context():
        # Mark problematic migrations as already applied
        migrations_to_mark = [
            'add_payroll_config',  # This table already exists
            '010_add_ot_tables',
            'add_company_currency_code',
            'add_enhancements_fields',
            'leave_allocation_001'
        ]
        
        print("Marking completed migrations in database...")
        for migration in migrations_to_mark:
            mark_migration_as_applied(migration)
        
        print("\n✅ Migration status updated!")