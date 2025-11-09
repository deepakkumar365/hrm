@echo off
cd /d "D:/Projects/HRMS/hrm"
python -c "import sys; sys.path.insert(0, '.'); from app import app, db; ctx = app.app_context(); ctx.push(); inspector = db.inspect(db.engine); tables = inspector.get_table_names(); exists = 'hrm_company_employee_id_config' in tables; print('Table hrm_company_employee_id_config EXISTS:', exists); [print(f'All tables: {t}') for t in sorted(tables) if 'company' in t.lower() or 'employee' in t.lower()]"
pause