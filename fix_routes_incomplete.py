#!/usr/bin/env python3
"""Fix incomplete claims_approve function in routes.py"""

import os

def fix_routes_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    routes_path = os.path.join(script_dir, 'routes.py')
    
    # Read the file
    with open(routes_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find and replace the incomplete function
    # Look for the problematic part
    old_pattern = '''        elif action == 'reject':
            c'''
    
    # Complete the function properly
    new_pattern = '''        elif action == 'reject':
            claim.status = 'Rejected'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            claim.rejection_reason = request.form.get('reason', '')
            flash('Claim rejected', 'success')
        
        db.session.commit()
        return redirect(url_for('claims_list'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')
        return redirect(url_for('claims_list'))'''
    
    # Replace
    if old_pattern in content:
        content = content.replace(old_pattern, new_pattern)
        
        # Write back
        with open(routes_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed incomplete claims_approve function in routes.py")
        return True
    else:
        print("❌ Could not find the incomplete pattern to fix")
        return False

if __name__ == '__main__':
    fix_routes_file()