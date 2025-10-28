#!/usr/bin/env python3
"""
Migration script to set up role management system
- Creates Designation Master table
- Creates UserRoleMapping table  
- Creates RoleAccessControl table
- Adds 'Tenantadmin' role to the system
- Populates default designations
"""

from app import app, db
from models import Role, Designation, UserRoleMapping, RoleAccessControl

def run_migration():
    with app.app_context():
        print("=" * 70)
        print("STARTING ROLE MANAGEMENT MIGRATION")
        print("=" * 70)
        
        # Step 1: Create tables if they don't exist
        print("\n[1/4] Creating new tables...")
        try:
            db.create_all()
            print("✓ Tables created successfully")
        except Exception as e:
            print(f"✗ Error creating tables: {str(e)}")
            return False
        
        # Step 2: Add Tenantadmin role (GEN-EMP-001)
        print("\n[2/4] Adding 'Tenantadmin' role...")
        try:
            # Check if Tenantadmin role already exists
            tenantadmin_role = Role.query.filter_by(name='Tenantadmin').first()
            if not tenantadmin_role:
                tenantadmin_role = Role(
                    name='Tenantadmin',
                    description='Tenant Administrator - manages users and company within assigned tenant',
                    is_active=True
                )
                db.session.add(tenantadmin_role)
                db.session.commit()
                print("✓ 'Tenantadmin' role added successfully")
            else:
                print("✓ 'Tenantadmin' role already exists")
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding Tenantadmin role: {str(e)}")
            return False
        
        # Step 3: Populate default designations (GEN-EMP-004)
        print("\n[3/4] Populating default designations...")
        try:
            default_designations = [
                'Software Engineer',
                'Senior Software Engineer',
                'Team Lead',
                'Project Manager',
                'Product Manager',
                'HR Manager',
                'HR Executive',
                'Finance Manager',
                'Accountant',
                'Sales Manager',
                'Sales Executive',
                'Business Development Manager',
                'Operations Manager',
                'Operations Executive',
                'Marketing Manager',
                'Marketing Specialist',
                'Business Analyst',
                'Data Analyst',
                'Quality Assurance Lead',
                'Quality Assurance Engineer',
                'DevOps Engineer',
                'System Administrator',
                'Network Administrator',
                'Database Administrator',
                'Support Engineer',
            ]
            
            added_count = 0
            for des_name in default_designations:
                if not Designation.query.filter_by(name=des_name).first():
                    designation = Designation(
                        name=des_name,
                        description=f'{des_name} designation',
                        is_active=True,
                        created_by='system'
                    )
                    db.session.add(designation)
                    added_count += 1
            
            db.session.commit()
            print(f"✓ Added {added_count} default designations")
            
        except Exception as e:
            db.session.rollback()
            print(f"✗ Error adding designations: {str(e)}")
            return False
        
        # Step 4: Summary
        print("\n[4/4] Migration complete!")
        print("\n" + "=" * 70)
        print("MIGRATION SUMMARY")
        print("=" * 70)
        print("\n✓ New models created:")
        print("  - Designation (Master data for job positions)")
        print("  - UserRoleMapping (Support for multiple roles per user)")
        print("  - RoleAccessControl (Dynamic access management)")
        
        print("\n✓ System roles updated:")
        super_admin = Role.query.filter_by(name='Super Admin').first() or Role.query.filter_by(name='SUPER_ADMIN').first()
        tenantadmin = Role.query.filter_by(name='Tenantadmin').first()
        hr_manager = Role.query.filter_by(name='HR Manager').first() or Role.query.filter_by(name='HR_MANAGER').first()
        employee = Role.query.filter_by(name='User').first() or Role.query.filter_by(name='Employee').first()
        
        if super_admin:
            print(f"  - Super Admin (ID: {super_admin.id})")
        if tenantadmin:
            print(f"  - Tenantadmin (ID: {tenantadmin.id}) [NEW]")
        if hr_manager:
            print(f"  - HR Manager (ID: {hr_manager.id})")
        if employee:
            print(f"  - User/Employee (ID: {employee.id})")
        
        des_count = Designation.query.count()
        print(f"\n✓ Designations loaded: {des_count} total")
        
        print("\n✓ Next steps:")
        print("  1. Create a 'Designation Master' management screen")
        print("  2. Enable multi-company selection in employee form")
        print("  3. Create 'Access Control Management' UI")
        print("  4. Test employee form with new Designation field")
        
        print("\n" + "=" * 70)
        return True

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)