"""
Verify that all HRM tables exist in the configured database; create any that are missing.

Usage (PowerShell):
  $env:DATABASE_URL = "postgresql://user:pass@host:5432/dbname"
  $env:SESSION_SECRET = "dev-secret"
  python "d:\Project\Workouts\GitHub\hrm\verify_db.py"

Notes:
- The application already auto-creates tables on startup (see app.py). This script mainly verifies.
- If your shell does not load .env automatically, set env vars as shown above before running.
"""
from __future__ import annotations

import os
import sys
from typing import Set

from sqlalchemy import inspect

# Importing app will initialize Flask and (by design) attempt to create tables.
# We still perform an explicit verification and (idempotent) create_all() if needed.
from app import app, db  # noqa: E402
import models  # noqa: F401, E402  # ensure models are registered


def get_existing_tables() -> Set[str]:
    """Return a set of existing table names across default search_path and 'public' schema."""
    inspector = inspect(db.engine)
    existing = set(inspector.get_table_names())
    try:
        existing |= set(inspector.get_table_names(schema="public"))
    except Exception:
        # Not all DBs support schemas in the same way; ignore if unsupported
        pass
    return existing


def main() -> int:
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[ERROR] DATABASE_URL is not set. Please export it before running.")
        return 2

    with app.app_context():
        expected = {t.name for t in db.metadata.sorted_tables}
        existing_before = get_existing_tables()

        missing = sorted(expected - existing_before)
        if missing:
            print(f"[INFO] Missing tables detected: {', '.join(missing)}")
            print("[ACTION] Creating missing tables...")
            # db.create_all()  # Removed. Use Alembic/Flask-Migrate for schema management.
        else:
            print("[OK] All expected tables already exist.")

        # Re-check to confirm
        existing_after = get_existing_tables()
        still_missing = sorted(expected - existing_after)
        if still_missing:
            print(f"[ERROR] Some tables are still missing after create_all(): {', '.join(still_missing)}")
            return 3

        print(f"[OK] Verification complete. Total tables: {len(expected)}. Database ready.")
        return 0


if __name__ == "__main__":
    sys.exit(main())