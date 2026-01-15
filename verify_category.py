from app import app
from core.models import EmployeeDocument
print("Checking EmployeeDocument model...")
if hasattr(EmployeeDocument, 'category'):
    print("SUCCESS: 'category' field found in EmployeeDocument model.")
    # Check default value? Not easy without instance inspection, but migration ran.
    doc = EmployeeDocument()
    if doc.category == 'Official':
       print("SUCCESS: Default value is 'Official'.")
    else:
       print(f"WARNING: Default value is {doc.category}")
else:
    print("FAILURE: 'category' field NOT found.")
