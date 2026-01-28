from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('hrm_payroll')
    print("Columns in hrm_payroll:")
    found_remarks = False
    for column in columns:
        print(f"- {column['name']} ({column['type']})")
        if column['name'] == 'remarks':
            found_remarks = True
    
    if found_remarks:
        print("\nSUCCESS: 'remarks' column FOUND.")
    else:
        print("\nFAILURE: 'remarks' column NOT FOUND.")
