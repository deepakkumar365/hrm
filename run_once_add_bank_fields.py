"""
One-time migration script to add new banking columns to hrm_employee.

It uses the app's configured DATABASE_URL (loaded via .env by app.py).
Run once, then delete or keep for record.

Usage (PowerShell):
  Set-Location "E:/Gobi/Pro/hrm-main/hrm-main"; python "E:/Gobi/Pro/hrm-main/hrm-main/run_once_add_bank_fields.py"
"""
from sqlalchemy import text
from app import app, db

SQL = """
ALTER TABLE public.hrm_employee
  ADD COLUMN IF NOT EXISTS account_holder_name VARCHAR(100),
  ADD COLUMN IF NOT EXISTS swift_code VARCHAR(11),
  ADD COLUMN IF NOT EXISTS ifsc_code VARCHAR(11);
"""


def main() -> int:
    with app.app_context():
        db.session.execute(text(SQL))
        db.session.commit()
        print("[OK] Columns ensured: account_holder_name, swift_code, ifsc_code")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())