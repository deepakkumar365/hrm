#!/usr/bin/env python
"""
Quick setup script to create and initialize hrm_company_employee_id_config table
Run this if you already have companies in the database
"""

import sys
from app import app, db
from models import Company, CompanyEmployeeIdConfig, Employee

def setup_company_employee_id_config():
    """Create and populate the company employee ID config table"""
    
    with app.app_context():
        print("=" * 60)
        print("Setting up hrm_company_employee_id_config table...")
        print("=" * 60)
        
        # Step 1: Create table if it doesn't exist
        print("\n1️⃣  Creating table structure...")
        try:
            CompanyEmployeeIdConfig.__table__.create(db.engine, checkfirst=True)
            print("   ✅ Table created (or already exists)")
        except Exception as e:
            print(f"   ❌ Error creating table: {e}")
            return False
        
        # Step 2: Get all companies
        print("\n2️⃣  Fetching all companies...")
        companies = Company.query.all()
        
        if not companies:
            print("   ⚠️  No companies found in database")
            return False
        
        print(f"   Found {len(companies)} company(ies)")
        
        # Step 3: Initialize config for each company
        print("\n3️⃣  Initializing employee ID configs...")
        
        for company in companies:
            # Check if config already exists
            existing_config = CompanyEmployeeIdConfig.query.filter_by(
                company_id=company.id
            ).first()
            
            if existing_config:
                print(f"   ⏭️  {company.code}: Config already exists (seq={existing_config.last_sequence_number})")
                continue
            
            # Get the company code as prefix
            id_prefix = company.code.upper() if company.code else "EMP"
            
            # Count existing employees to determine starting sequence
            employee_count = Employee.query.filter_by(company_id=company.id).count()
            
            # Create config
            config = CompanyEmployeeIdConfig(
                company_id=company.id,
                id_prefix=id_prefix,
                last_sequence_number=employee_count,  # Start from current count
                created_by='system'
            )
            
            try:
                db.session.add(config)
                db.session.commit()
                print(f"   ✅ {company.code}: Initialized with sequence={employee_count}")
            except Exception as e:
                db.session.rollback()
                print(f"   ❌ {company.code}: Failed - {e}")
                return False
        
        # Step 4: Verify setup
        print("\n4️⃣  Verifying setup...")
        all_configs = CompanyEmployeeIdConfig.query.all()
        print(f"   ✅ Found {len(all_configs)} config(s) in database")
        
        for config in all_configs:
            company = Company.query.get(config.company_id)
            print(f"      - {company.code}: prefix='{config.id_prefix}', last_seq={config.last_sequence_number}")
        
        print("\n" + "=" * 60)
        print("✨ Setup complete! The table is ready to use.")
        print("=" * 60)
        return True


if __name__ == '__main__':
    try:
        success = setup_company_employee_id_config()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)