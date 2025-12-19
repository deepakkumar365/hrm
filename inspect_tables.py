from app import app, db
from sqlalchemy import text

with app.app_context():
    print("Tables list:")
    res = db.session.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'"))
    for r in res:
        print(f" - {r[0]}")
    
    print("\nhrm_roles count:")
    try:
        count = db.session.execute(text("SELECT count(*) FROM hrm_roles")).scalar()
        print(count)
    except Exception as e:
        print(f"Error hrm_roles: {e}")

    print("\nrole (lowercase) count:")
    try:
        count = db.session.execute(text("SELECT count(*) FROM role")).scalar()
        print(count)
    except Exception as e:
        print(f"Error role: {e}")
