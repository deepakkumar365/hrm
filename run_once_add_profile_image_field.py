"""
One-time migration script to add profile_image_path column to hrm_employee.

It uses the app's configured DATABASE_URL (loaded via .env by app.py).
Run once, then delete or keep for record.

Usage (PowerShell):
  Set-Location "E:/Gobi/Pro/hrm-main/hrm-main"; python "E:/Gobi/Pro/hrm-main/hrm-main/run_once_add_profile_image_field.py"
"""
from sqlalchemy import text
from app import app, db

SQL = """
ALTER TABLE public.hrm_employee
  ADD COLUMN IF NOT EXISTS profile_image_path VARCHAR(255);
"""


def main() -> int:
    with app.app_context():
        db.session.execute(text(SQL))
        db.session.commit()
        print("[OK] Column ensured: profile_image_path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())