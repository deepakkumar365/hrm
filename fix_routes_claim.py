#!/usr/bin/env python3
"""Fix incomplete claims_approve function in routes.py"""

import os

# Read the file
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'routes.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the incomplete function
old_code = """        elif action == 'reject':"""

new_code = """        elif action == 'reject':
            claim.status = 'Rejected'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            flash('Claim rejected', 'success')
        
        db.session.commit()
        return redirect(url_for('claims_list'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')
        return redirect(url_for('claims_list'))"""

if old_code in content:
    content = content.replace(old_code, new_code)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Fixed routes.py successfully!")
else:
    print("✗ Could not find the pattern to replace")
    print("Looking for:", repr(old_code))