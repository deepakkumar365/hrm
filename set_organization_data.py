"""
Direct script to set organization address and UEN
Edit the values below and run this script
"""

from app import app, db
from models import Organization

# ============================================
# EDIT THESE VALUES:
# ============================================
ORGANIZATION_ADDRESS = "123 Business Street, #01-01, Singapore 123456"
ORGANIZATION_UEN = "201234567A"
# ============================================

def set_organization_data():
    """Set organization address and UEN"""
    with app.app_context():
        # Get the first organization
        org = Organization.query.first()
        
        if not org:
            print("❌ No organization found in database!")
            return
        
        print(f"\n{'='*70}")
        print(f"Updating Organization: {org.name}")
        print(f"{'='*70}\n")
        
        print("BEFORE:")
        print(f"  Address: {org.address or '(Not set)'}")
        print(f"  UEN: {org.uen or '(Not set)'}")
        
        # Update the values
        org.address = ORGANIZATION_ADDRESS
        org.uen = ORGANIZATION_UEN
        
        try:
            db.session.commit()
            print("\n✅ UPDATE SUCCESSFUL!\n")
            print("AFTER:")
            print(f"  Address: {org.address}")
            print(f"  UEN: {org.uen}")
            print(f"\n{'='*70}")
            print("Organization data updated successfully!")
            print("The new values will now appear on all payslips.")
            print(f"{'='*70}\n")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error updating organization: {str(e)}")

if __name__ == '__main__':
    set_organization_data()