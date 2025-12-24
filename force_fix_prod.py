
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Delete invalid version
        db.session.execute(text("DELETE FROM alembic_version"))
        # Insert target version
        target = 'e371d5361be6'
        db.session.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{target}')"))
        db.session.commit()
        print(f"Forced alembic_version to '{target}'")
    except Exception as e:
        print(f"Error: {e}")
