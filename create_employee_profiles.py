"""
Script to create Employee profiles for existing User accounts
"""
from app import app, db
from models import User, Employee, Company, Department, Role
from datetime import date

def create_employee_profiles():
    """Create Employee profiles for users who don't have them"""
    with app.app_context():
        try:
            # Get default company, department, and organization
            company = Company.query.first()
            if not company:
                print("❌ No company found! Please create a company first.")
                return
            
            department = Department.query.first()
            if not department:
                print("❌ No department found! Please create a department first.")
                return
            
            from models import Organization
            organization = Organization.query.first()
            if not organization:
                print("❌ No organization found! Please create an organization first.")
                return
            
            # Get users without employee profiles
            users = User.query.filter(User.employee_profile == None).all()
            
            if not users:
                print("✅ All users already have employee profiles!")
                return
            
            print(f"📋 Found {len(users)} users without employee profiles")
            print(f"📋 Using Company: {company.name}")
            print(f"📋 Using Department: {department.name}")
            print()
            
            created_count = 0
            for user in users:
                # Determine position based on role
                role_name = user.role.name if user.role else "User"
                if role_name == "Super Admin":
                    position = "System Administrator"
                elif role_name == "Admin":
                    position = "HR Administrator"
                elif role_name == "Manager":
                    position = "Team Manager"
                else:
                    position = "Staff Member"
                
                # Create employee profile
                # Generate a dummy NRIC for testing (format: S1234567A)
                dummy_nric = f"S{user.id:07d}A"
                
                employee = Employee(
                    user_id=user.id,
                    company_id=company.id,
                    organization_id=organization.id,  # Required field
                    employee_id=f"EMP{user.id:04d}",
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    phone="+65 9000 0000",
                    nric=dummy_nric,  # Required field
                    position=position,
                    department=department.name,
                    hire_date=date.today(),
                    basic_salary=3000.00,  # Default salary
                    is_active=True
                )
                
                db.session.add(employee)
                created_count += 1
                print(f"  ✅ Created Employee profile for: {user.username} ({role_name})")
            
            db.session.commit()
            
            print()
            print("="*60)
            print(f"✅ Successfully created {created_count} employee profiles!")
            print("="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_employee_profiles()