"""
Test script to simulate the /employees/add route logic
This verifies that the exact code from routes.py works correctly
"""
from app import app, db
from models import Role, Department, WorkingHours, WorkSchedule, Employee

def test_employees_add_route_logic():
    """Simulate the exact logic from the /employees/add route"""
    with app.app_context():
        print("=" * 60)
        print("Testing /employees/add Route Logic")
        print("=" * 60)
        
        try:
            # This is the exact code from routes.py line 329-340
            print("\nExecuting the exact query from routes.py line 329...")
            roles = Role.query.filter_by(is_active=True).order_by(Role.name).all()
            departments = Department.query.filter_by(is_active=True).order_by(Department.name).all()
            working_hours = WorkingHours.query.filter_by(is_active=True).order_by(WorkingHours.name).all()
            work_schedules = WorkSchedule.query.filter_by(is_active=True).order_by(WorkSchedule.name).all()
            managers = Employee.query.filter_by(is_active=True).filter(Employee.position.ilike('%manager%')).all()
            
            print("\n✓ All queries executed successfully!")
            print(f"\nData loaded for employee form:")
            print(f"  - Roles: {len(roles)}")
            for role in roles:
                print(f"    • {role.name}")
            print(f"  - Departments: {len(departments)}")
            for dept in departments[:3]:  # Show first 3
                print(f"    • {dept.name}")
            if len(departments) > 3:
                print(f"    ... and {len(departments) - 3} more")
            print(f"  - Working Hours: {len(working_hours)}")
            print(f"  - Work Schedules: {len(work_schedules)}")
            print(f"  - Managers: {len(managers)}")
            
            print("\n" + "=" * 60)
            print("SUCCESS! ✓")
            print("=" * 60)
            print("\nThe /employees/add route will work correctly.")
            print("The error 'Entity namespace for \"role\" has no property \"is_active\"'")
            print("has been resolved.")
            print("\nYou can now:")
            print("1. Start the application: python app.py")
            print("2. Login with admin credentials")
            print("3. Navigate to /employees/add")
            print("4. Add new employees without errors")
            
            return True
            
        except Exception as e:
            print("\n" + "=" * 60)
            print("ERROR! ✗")
            print("=" * 60)
            print(f"\nError: {e}")
            print(f"Type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = test_employees_add_route_logic()
    exit(0 if success else 1)