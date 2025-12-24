"""
Script to update organization address and UEN information
Run this script to add/update your organization's details
"""

from app import app, db
from core.models import Organization

def update_organization_info():
    """Update organization address and UEN"""
    with app.app_context():
        # Get the first organization (or you can query by name)
        org = Organization.query.first()
        
        if not org:
            print("❌ No organization found in database!")
            print("Please create an organization first.")
            return
        
        print(f"\n📋 Current Organization: {org.name}")
        print(f"   Current Address: {org.address or 'Not set'}")
        print(f"   Current UEN: {org.uen or 'Not set'}")
        print("\n" + "="*60)
        
        # Get new values
        print("\n📝 Enter new organization details (press Enter to keep current value):\n")
        
        new_address = input(f"Address [{org.address or 'Not set'}]: ").strip()
        new_uen = input(f"UEN Number [{org.uen or 'Not set'}]: ").strip()
        
        # Update if new values provided
        updated = False
        if new_address:
            org.address = new_address
            updated = True
            print(f"✅ Address updated to: {new_address}")
        
        if new_uen:
            org.uen = new_uen
            updated = True
            print(f"✅ UEN updated to: {new_uen}")
        
        if updated:
            try:
                db.session.commit()
                print("\n✅ Organization information updated successfully!")
                print("\n📋 Updated Organization Details:")
                print(f"   Name: {org.name}")
                print(f"   Address: {org.address}")
                print(f"   UEN: {org.uen}")
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Error updating organization: {str(e)}")
        else:
            print("\n⚠️  No changes made.")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("   ORGANIZATION INFORMATION UPDATE TOOL")
    print("="*60)
    update_organization_info()
    print("\n" + "="*60)
