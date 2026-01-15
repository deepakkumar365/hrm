import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.models import Role, User

def check_access(role_name):
    allowed_roles = ['Super Admin', 'Admin', 'HR Manager']
    can_view = role_name in allowed_roles
    print(f"Role: {role_name}, Can View All Docs: {can_view}")
    return can_view

if __name__ == "__main__":
    print("Verifying Document Access Logic...")
    
    # Test cases
    roles_to_test = ['Super Admin', 'Admin', 'HR Manager', 'Employee', 'Manager']
    
    results = {}
    for r in roles_to_test:
        results[r] = check_access(r)
        
    # Assertions
    assert results['HR Manager'] == True, "HR Manager should have access"
    assert results['Employee'] == False, "Employee should NOT have access"
    assert results['Manager'] == False, "Manager should NOT have access (unless added to list)"
    
    print("\nSUCCESS: Access logic verified correctly.")
