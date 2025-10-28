#!/usr/bin/env python
"""Fix syntax error in routes.py - incomplete try block in claims_submit function"""

import sys

def fix_routes():
    file_path = 'routes.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The incomplete section at the end
    incomplete = """@app.route('/claims/submit', methods=['GET', 'POST'])
@require_login
def claims_submit():
    \"\"\"Submit new claim\"\"\"
    if request.method == 'POST':
        try:
            if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
                flash('Employee profile required for submitting claims', 'error')"""
    
    # The complete section
    complete = """@app.route('/claims/submit', methods=['GET', 'POST'])
@require_login
def claims_submit():
    \"\"\"Submit new claim\"\"\"
    if request.method == 'POST':
        try:
            if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
                flash('Employee profile required for submitting claims', 'error')
                return redirect(url_for('claims_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting claim: {str(e)}', 'error')
            return redirect(url_for('claims_list'))"""
    
    if incomplete in content:
        content = content.replace(incomplete, complete)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed syntax error in routes.py")
        return True
    else:
        print("❌ Could not find the incomplete section to fix")
        return False

if __name__ == '__main__':
    fix_routes()