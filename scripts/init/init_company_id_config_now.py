#!/usr/bin/env python3
"""
Direct initialization script for CompanyEmployeeIdConfig table.
This script:
1. Creates the table (if it doesn't exist)
2. Initializes configs for all existing companies
3. Detects max sequence per company from existing employees
4. Works with current database connection
"""

import re
from datetime import datetime
from app import app, db
from models import Company, Employee, CompanyEmployeeIdConfig

def extract_sequence_from_employee_id(employee_id, company_code):
    """
    Extract the numeric sequence from employee_id.
    Expected format: COMPANYCODE### (e.g., ACME001, ACME002)
    
    Args:
        employee_id: The full employee ID string
        company_code: The company code prefix
        
    Returns:
        The numeric sequence number or 0 if not found
    """
    if not employee_id:
        return 0
    
    # Remove the company code prefix and extract digits
    prefix_removed = employee_id.replace(company_code, '', 1).lstrip('-_')
    
    # Extract leading digits
    match = re.match(r'^(\d+)', prefix_removed)
    if match:
        try:
            return int(match.group(1))
        except (ValueError, AttributeError):
            return 0
    return 0


def get_max_sequence_for_company(company_id, company_code):
    """
    Get the maximum sequence number from existing employees for a company.
    
    Args:
        company_id: UUID of the company
        company_code: Company code (e.g., 'ACME')
        
    Returns:
        Maximum sequence number found, or 0 if no employees
    """
    employees = Employee.query.filter_by(company_id=company_id).all()
    
    if not employees:
        return 0
    
    max_seq = 0
    for emp in employees:
        seq = extract_sequence_from_employee_id(emp.employee_id, company_code)
        max_seq = max(max_seq, seq)
    
    return max_seq


def initialize_company_id_configs():
    """
    Initialize CompanyEmployeeIdConfig for all existing companies.
    """
    with app.app_context():
        print("\n" + "="*80)
        print("INITIALIZING CompanyEmployeeIdConfig TABLE")
        print("="*80)
        
        try:
            # Step 1: Create the table if it doesn't exist
            print("\n[Step 1] Creating table 'hrm_company_employee_id_config'...")
            CompanyEmployeeIdConfig.__table__.create(db.engine, checkfirst=True)
            print("✅ Table created or already exists")
            
            # Step 2: Get all companies
            print("\n[Step 2] Fetching all companies...")
            companies = Company.query.all()
            print(f"✅ Found {len(companies)} company(ies)")
            
            if not companies:
                print("⚠️  No companies found. Nothing to initialize.")
                return
            
            # Step 3: Initialize configs
            print("\n[Step 3] Initializing configurations...")
            print("-" * 80)
            
            initialized_count = 0
            skipped_count = 0
            
            for company in companies:
                # Check if config already exists
                existing_config = CompanyEmployeeIdConfig.query.filter_by(
                    company_id=company.id
                ).first()
                
                if existing_config:
                    print(f"⏭️  {company.code:15} → SKIPPED (already configured)")
                    skipped_count += 1
                    continue
                
                # Get max sequence from existing employees
                max_seq = get_max_sequence_for_company(company.id, company.code)
                
                # Create config entry
                config = CompanyEmployeeIdConfig(
                    company_id=company.id,
                    last_sequence_number=max_seq,
                    id_prefix=company.code,
                    created_by='system',
                    created_at=datetime.now()
                )
                
                db.session.add(config)
                print(f"✅ {company.code:15} → Initialized (max_seq={max_seq})")
                initialized_count += 1
            
            # Step 4: Commit all changes
            print("-" * 80)
            print("\n[Step 4] Committing changes to database...")
            db.session.commit()
            print("✅ All changes committed successfully!")
            
            # Step 5: Verification
            print("\n[Step 5] Verifying initialization...")
            total_configs = CompanyEmployeeIdConfig.query.count()
            print(f"✅ Total configs in database: {total_configs}")
            
            print("\n[SUMMARY]")
            print(f"  ✅ Initialized: {initialized_count} company(ies)")
            print(f"  ⏭️  Skipped:     {skipped_count} company(ies) (already configured)")
            print(f"  📊 Total:       {total_configs} config(s)")
            
            print("\n" + "="*80)
            print("✅ INITIALIZATION COMPLETE!")
            print("="*80)
            
            # Print all configs
            print("\n📋 CONFIGURED COMPANIES:")
            print("-" * 80)
            configs = CompanyEmployeeIdConfig.query.all()
            for cfg in configs:
                company = Company.query.get(cfg.company_id)
                print(f"  {cfg.id_prefix:15} → Last Seq: {cfg.last_sequence_number:5} | Company: {company.name if company else 'UNKNOWN'}")
            print("-" * 80)
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {str(e)}")
            print("\n" + "="*80)
            import traceback
            traceback.print_exc()
            print("="*80)
            return False


if __name__ == '__main__':
    success = initialize_company_id_configs()
    exit(0 if success else 1)