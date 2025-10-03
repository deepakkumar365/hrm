"""
Quick script to check current organization data in the database
"""

from app import app, db
from models import Organization

def check_organization():
    """Check organization data"""
    with app.app_context():
        orgs = Organization.query.all()
        
        if not orgs:
            print("❌ No organizations found in database!")
            return
        
        print(f"\n{'='*70}")
        print(f"Found {len(orgs)} organization(s) in database:")
        print(f"{'='*70}\n")
        
        for org in orgs:
            print(f"ID: {org.id}")
            print(f"Name: {org.name}")
            print(f"Address: {org.address if org.address else '❌ NOT SET (NULL)'}")
            print(f"UEN: {org.uen if org.uen else '❌ NOT SET (NULL)'}")
            print(f"Logo Path: {org.logo_path if org.logo_path else 'Not set'}")
            print(f"Created: {org.created_at}")
            print(f"Updated: {org.updated_at}")
            print(f"{'-'*70}\n")

if __name__ == '__main__':
    check_organization()