#!/usr/bin/env python3
"""
Fix the syntax error in routes.py by completing the incomplete claims_submit function.
The try block at line 2932 is missing its except clause.
"""

# Read the file
with open('routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Check if the incomplete section exists
if "flash('Employee profile required for submitting claims', 'error')" in content and \
   "def claims_submit():" in content:
    
    # Replace the incomplete try block with a complete one
    old_code = """            if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
                flash('Employee profile required for submitting claims', 'error')"""
    
    new_code = """            if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
                flash('Employee profile required for submitting claims', 'error')
                return redirect(url_for('claims_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting claim: {str(e)}', 'error')
            return redirect(url_for('claims_list'))"""
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        with open('routes.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed syntax error in routes.py - added except clause to claims_submit")
    else:
        print("⚠️ Could not find the exact old_code section")
        # Try with repr to debug
        print(f"Length of content: {len(content)}")
        print(f"File ends with: {repr(content[-200:])}")
else:
    print("❌ Could not find the incomplete section")