from app import app
from core.models import Employee, FileStorage
import routes.routes
print("Imports successful!")
print("Employee model fields check:")
e = Employee()
print(f"Has hazmat_file_url: {hasattr(Employee, 'hazmat_file_url')}")
print(f"Has airport_pass_file_url: {hasattr(Employee, 'airport_pass_file_url')}")
print(f"Has psa_pass_file_url: {hasattr(Employee, 'psa_pass_file_url')}")
print(f"Has hazmat_file_id: {hasattr(Employee, 'hazmat_file_id')}")
