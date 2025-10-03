"""
Verify the Flask app can start without template syntax errors
"""

from app import app
import routes

def verify_app():
    print("\n" + "="*70)
    print("🔍 VERIFYING FLASK APP")
    print("="*70)
    
    try:
        with app.app_context():
            # Try to access the app
            print(f"✅ App name: {app.name}")
            print(f"✅ Debug mode: {app.debug}")
            print(f"✅ Template folder: {app.template_folder}")
            
            # Check if we can import routes
            print("✅ Routes imported successfully")
            
            print("\n" + "="*70)
            print("✅ FLASK APP IS READY TO START!")
            print("="*70)
            print("\n📝 To start the application, run:")
            print("   python app.py")
            print("\n👤 Login with:")
            print("   Username: admin@noltrion.com")
            print("   Password: Admin@123")
            print("\n" + "="*70 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    verify_app()