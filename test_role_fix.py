"""
Test script to verify the Role is_active fix
"""
from app import app, db
from models import Role, Department, WorkingHours, WorkSchedule, Employee

def test_role_queries():
    """Test that Role queries with is_active filter work correctly"""
    with app.app_context():
        print("=" * 60)
        print("Testing Role is_active Fix")
        print("=" * 60)
        
        # Test 1: Query all active roles
        print("\n1. Testing Role.query.filter_by(is_active=True)...")
        try:
            roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
            print(f"   ✓ Found {len(roles)} active roles:")
            for role in roles:
                print(f"     - {role.name} (is_active={role.is_active})")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        # Test 2: Query other master data (should still work)
        print("\n2. Testing other master data queries...")
        try:
            departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
            print(f"   ✓ Found {len(departments)} active departments")
            
            working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
            print(f"   ✓ Found {len(working_hours)} active working hours")
            
            work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
            print(f"   ✓ Found {len(work_schedules)} active work schedules")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        # Test 3: Verify Role model has is_active attribute
        print("\n3. Testing Role model attributes...")
        try:
            test_role = Role.query.first()
            if test_role:
                assert hasattr(test_role, 'is_active'), "Role model missing is_active attribute"
                print(f"   ✓ Role model has is_active attribute")
                print(f"   ✓ Sample role '{test_role.name}' is_active={test_role.is_active}")
            else:
                print("   ⚠ No roles found in database")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            return False
        
        # Test 4: Test creating a role with is_active
        print("\n4. Testing role creation with is_active...")
        try:
            # Check if test role exists
            test_role = Role.query.filter_by(name='Test Role').first()
            if test_role:
                db.session.delete(test_role)
                db.session.commit()
            
            # Create new role
            new_role = Role(name='Test Role', description='Test', is_active=False)
            db.session.add(new_role)
            db.session.commit()
            print(f"   ✓ Created test role with is_active=False")
            
            # Query inactive roles
            inactive_roles = Role.query.filter_by(is_active=False).all()
            print(f"   ✓ Found {len(inactive_roles)} inactive roles")
            
            # Clean up
            db.session.delete(new_role)
            db.session.commit()
            print(f"   ✓ Cleaned up test role")
        except Exception as e:
            print(f"   ✗ Error: {e}")
            db.session.rollback()
            return False
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        print("\nThe /employees/add route should now work correctly.")
        print("You can start the application with: python app.py")
        return True

if __name__ == '__main__':
    success = test_role_queries()
    exit(0 if success else 1)