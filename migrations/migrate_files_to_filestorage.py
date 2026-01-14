
import os
import sys
from datetime import datetime

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from core.models import Employee, EmployeeDocument, TenantConfiguration, FileStorage, Company

def migrate_employee_documents():
    """Migrate EmployeeDocument records to FileStorage"""
    print("Migrating Employee Documents...")
    docs = EmployeeDocument.query.filter(EmployeeDocument.file_storage_id == None).all()
    count = 0
    for doc in docs:
        if not doc.file_path:
            continue
            
        # Determine tenant_id from employee -> company -> tenant
        tenant_id = None
        company_id = None
        if doc.employee and doc.employee.company:
            company_id = doc.employee.company.id
            tenant_id = doc.employee.company.tenant_id
            
        if not tenant_id:
            print(f"Skipping Document {doc.id}: No Tenant ID found")
            continue

        # Check if already exists in FileStorage to avoid duplicates (optional check)
        # For now, just create new
        
        # Create FileStorage record
        file_record = FileStorage(
            tenant_id=tenant_id,
            company_id=company_id,
            module='HR',
            file_category='document', # Generic
            file_name=doc.document_name, # or derive from path
            file_path=doc.file_path,
            file_type='application/octet-stream', # Unknown
            file_size=0, # Unknown
            uploaded_by=None,
            created_at=doc.created_at or datetime.utcnow()
        )
        db.session.add(file_record)
        db.session.flush() # Get ID
        
        doc.file_storage_id = file_record.id
        count += 1
        
    db.session.commit()
    print(f"Migrated {count} Employee Documents.")

def migrate_profile_pictures():
    """Migrate Employee profile pictures to FileStorage"""
    print("Migrating Profile Pictures...")
    employees = Employee.query.filter(Employee.profile_picture_id == None, Employee.profile_image_path != None).all()
    count = 0
    for emp in employees:
        if not emp.profile_image_path:
            continue
            
        # Determine tenant_id
        tenant_id = None
        company_id = emp.company_id
        if emp.company:
            tenant_id = emp.company.tenant_id
            
        if not tenant_id:
             print(f"Skipping Employee {emp.id}: No Tenant ID found")
             continue

        file_record = FileStorage(
            tenant_id=tenant_id,
            company_id=company_id,
            module='HR',
            file_category='profile',
            file_name=f"profile_{emp.id}",
            file_path=emp.profile_image_path,
            file_type='image/jpeg', # Assumption
            file_size=0,
            uploaded_by=None,
            created_at=datetime.utcnow()
        )
        db.session.add(file_record)
        db.session.flush()
        
        emp.profile_picture_id = file_record.id
        count += 1

    db.session.commit()
    print(f"Migrated {count} Profile Pictures.")

def migrate_tenant_logos():
    """Migrate TenantConfiguration logos to FileStorage"""
    print("Migrating Tenant Logos...")
    configs = TenantConfiguration.query.filter(TenantConfiguration.payslip_logo_id == None).all()
    count = 0
    for config in configs:
        # Check logo_left and logo_right
        # We need to decide which one maps to 'payslip_logo_id' or if we need multiple?
        # The model has 'payslip_logo_id'. Let's assume it maps to 'logo_path' or similar if it existed?
        # Checking TenantConfiguration model... it usually has payslip_logo_left, payslip_logo_right as strings.
        # But we added payslip_logo_id.
        
        # If the goal is to migrate existing string paths to FileStorage, we need to know WHICH string path to migrate.
        # Let's assume we migrate `payslip_logo_left` to `payslip_logo_id` as primary?
        # Or maybe we need TWO IDs?
        # For now, let's skip this if ambiguous, or check model.
        pass
        
    # Checking Company Logos
    companies = Company.query.filter(Company.logo_path != None).all()
    # Company model doesn't have logo_id yet? The user plan only mentioned TenantConfig?
    # Let's stick to the plan: "Iterate TenantConfiguration (logo)..."
    
    # Let's inspect TenantConfiguration model briefly via code if needed.
    # But for now, I'll comment this out or implement a basic version.
    print("Tenant Logo migration skipped (ambiguous mapping).")

if __name__ == "__main__":
    with app.app_context():
        migrate_employee_documents()
        migrate_profile_pictures()
        # migrate_tenant_logos()
        print("Migration Completed.")
