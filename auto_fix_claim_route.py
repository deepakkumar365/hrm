#!/usr/bin/env python3
"""
Auto-fix for the incomplete claims_approve function in routes.py
This file fixes the IndentationError by completing the elif block
"""

import os
import sys

def fix_routes_file():
    """Fix the incomplete routes.py file"""
    routes_path = os.path.join(os.path.dirname(__file__), 'routes.py')
    
    try:
        # Read the entire file
        with open(routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the file needs fixing
        if 'elif action == \'reject\':' in content:
            incomplete_part = '        elif action == \'reject\':'
            if content.rstrip().endswith(incomplete_part):
                # File ends with incomplete elif block
                print("Detected incomplete claims_approve function")
                
                # The complete function body
                complete_function = '''@app.route('/claims/<int:claim_id>/approve', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def claims_approve(claim_id):
    """Approve/reject claim"""
    claim = Claim.query.get_or_404(claim_id)

    try:
        action = request.form.get('action')

        if action == 'approve':
            claim.status = 'Approved'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            flash('Claim approved', 'success')
        
        elif action == 'reject':
            claim.status = 'Rejected'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            flash('Claim rejected', 'success')
        
        db.session.commit()
        return redirect(url_for('claims_list'))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')
        return redirect(url_for('claims_list'))
'''
                
                # Find the start of the incomplete function
                incomplete_func_start = content.rfind("@app.route('/claims/<int:claim_id>/approve'")
                
                if incomplete_func_start != -1:
                    # Replace the entire incomplete function with the complete one
                    content = content[:incomplete_func_start] + complete_function
                    
                    # Write back the fixed content
                    with open(routes_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"✅ Successfully fixed routes.py")
                    print(f"   - Completed the claims_approve function")
                    print(f"   - File updated at: {routes_path}")
                    return True
        
        print("No incomplete claims_approve function detected")
        return False
        
    except Exception as e:
        print(f"❌ Error fixing routes.py: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_routes_file()
    sys.exit(0 if success else 1)