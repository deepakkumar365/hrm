
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        result = db.session.execute(text("SELECT version_num FROM alembic_version"))
        rows = result.fetchall()
        print("--- PROD DB VERSIONS ---")
        for row in rows:
            print(f"Version: {row[0]}")
        print("--- END ---")
    except Exception as e:
        print(f"Error: {e}")
