#!/usr/bin/env python3
"""
Initialize Company Employee ID Configuration

This script creates CompanyEmployeeIdConfig entries for all existing companies.
It should be run once after deploying the updated models.

Usage: python init_company_employee_id_config.py
"""

import sys
from app import app, db
from models import Company, Employee, CompanyEmployeeIdConfig


def init_company_id_configs():
    """Initialize CompanyEmployeeIdConfig for all companies"""
    with app.app_context():
        try:
            # Get all companies
            companies = Company.query.all()
            
            if not companies:
                print("❌ No companies found in the database")
                return False
            
            print(f"📋 Found {len(companies)} companies")
            
            created_count = 0
            skipped_count = 0
            
            for company in companies:
                # Check if config already exists
                existing_config = CompanyEmployeeIdConfig.query.filter_by(company_id=company.id).first()
                
                if existing_config:
                    print(f"⏭️  Skipping {company.code}: Config already exists (last_seq={existing_config.last_sequence_number})")
                    skipped_count += 1
                    continue
                
                # Get the highest employee number for this company from existing employees
                max_employee = Employee.query.filter_by(company_id=company.id).all()
                
                # Extract numeric part from employee_id to determine starting sequence
                max_sequence = 0
                for emp in max_employee:
                    if emp.employee_id and emp.employee_id.startswith(company.code):
                        # Extract the numeric part
                        numeric_part = emp.employee_id[len(company.code):]
                        if numeric_part.isdigit():
                            seq_num = int(numeric_part)
                            max_sequence = max(max_sequence, seq_num)
                
                # Create config with existing max sequence
                config = CompanyEmployeeIdConfig(
                    company_id=company.id,
                    id_prefix=company.code,
                    last_sequence_number=max_sequence,
                    created_by='system'
                )
                
                db.session.add(config)
                print(f"✅ Created config for {company.code} (existing employees: {len(max_employee)}, last_seq={max_sequence})")
                created_count += 1
            
            # Commit all changes
            db.session.commit()
            
            print(f"\n✨ Configuration Initialization Complete!")
            print(f"   Created: {created_count} configs")
            print(f"   Skipped: {skipped_count} configs (already exist)")
            print(f"   Total:   {len(companies)} companies")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during initialization: {str(e)}")
            db.session.rollback()
            return False


def verify_configs():
    """Verify that all configs were created correctly"""
    with app.app_context():
        try:
            print("\n🔍 Verifying Configuration...")
            
            configs = CompanyEmployeeIdConfig.query.all()
            companies = Company.query.all()
            
            if len(configs) != len(companies):
                print(f"⚠️  Warning: {len(configs)} configs for {len(companies)} companies")
            
            for config in configs:
                company = Company.query.get(config.company_id)
                employees = Employee.query.filter_by(company_id=config.company_id).count()
                print(f"   {config.id_prefix}: last_seq={config.last_sequence_number}, employees={employees}")
            
            print(f"\n✅ All configurations verified!")
            return True
            
        except Exception as e:
            print(f"❌ Error during verification: {str(e)}")
            return False


if __name__ == '__main__':
    print("=" * 60)
    print("Company Employee ID Configuration Initialization")
    print("=" * 60)
    
    success = init_company_id_configs()
    
    if success:
        verify_configs()
        sys.exit(0)
    else:
        sys.exit(1)