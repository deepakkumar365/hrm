
from app import app, db
from core.models import FileStorage

def init_db():
    with app.app_context():
        print("Creating tables...")
        # specific creation if possible, or generic
        # db.create_all() checks existence, so safe usually
        try:
            db.metadata.create_all(bind=db.engine)
            print("Tables created.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    init_db()
