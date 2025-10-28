#!/usr/bin/env python3
"""Auto-fix routes.py using file read/write"""
import os
import sys

try:
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    routes_file = os.path.join(script_dir, 'routes.py')
    
    # Read the file
    with open(routes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if it has the problem
    if content.endswith('            c'):
        print("[*] Found incomplete routes.py file")
        
        # Remove the stray 'c'
        content = content[:-1]
        
        # Add the complete function ending
        complete_ending = '''claim.status = 'Rejected'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            claim.rejection_reason = request.form.get('reason', '')
            flash('Claim rejected', 'success')
        
        db.session.commit()
        return redirect(url_for('claims_list'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')
        return redirect(url_for('claims_list'))
'''
        
        content += complete_ending
        
        # Write back
        with open(routes_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("[+] Successfully fixed routes.py!")
        sys.exit(0)
    else:
        print("[-] File doesn't end with incomplete marker")
        sys.exit(1)

except Exception as e:
    print(f"[!] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)