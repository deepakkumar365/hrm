
from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Delete existing version
        db.session.execute(text("DELETE FROM alembic_version"))
        # Insert known valid version
        db.session.execute(text("INSERT INTO alembic_version (version_num) VALUES ('merge_migration_heads')"))
        db.session.commit()
        print("Updated alembic_version to 'merge_migration_heads'")
    except Exception as e:
        print(f"Error updating alembic_version: {e}")
        db.session.rollback()
