
from app import app
from core.models import User, db

def verify_user():
    with app.app_context():
        u = User.query.filter_by(username='DEVIT057').first()
        if not u:
            print("User DEVIT057 NOT found.")
            return

        print(f"User Found: {u.username}, Role: {u.role.name if u.role else 'None'}")
        
        if u.check_password('Welcome@123'):
            print("Password Correct.")
        else:
            print("Password INCORRECT.")
            # Reset it to match request
            u.set_password('Welcome@123')
            db.session.commit()
            print("Password reset to 'Welcome@123'.")

if __name__ == "__main__":
    verify_user()
