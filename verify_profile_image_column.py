from app import app, db
from sqlalchemy import text
from models import Employee


def main() -> int:
    with app.app_context():
        rows = db.session.execute(text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema='public' AND table_name='hrm_employee'
            ORDER BY ordinal_position
            """
        )).fetchall()
        cols = [r[0] for r in rows]
        print("[COLUMNS]", cols)
        print("[HAS profile_image_path]", 'profile_image_path' in cols)
        sample = db.session.query(Employee.id, Employee.profile_image_path).limit(5).all()
        print("[SAMPLE]", sample)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())