#!/usr/bin/env python3
"""Execute the syntax fix"""
import sys
import os

# Get the project directory where this script is located
project_dir = os.path.dirname(os.path.abspath(__file__))
# Change to the project directory
sys.path.insert(0, project_dir)

try:
    # Import and execute the fix
    from auto_syntax_fix import repair
    result = repair()
    if result:
        print("\n✅ Syntax fix completed successfully!")
        print("You can now run: python main.py")
    else:
        print("⚠️ Fix did not complete. Trying alternative approach...")
        
        # Alternative: directly fix using string replacement with smarter matching
        path = os.path.join(project_dir, "routes.py")
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Search for the incomplete pattern more flexibly
        if "flash('Claim approved', 'success')" in content and content.rstrip().endswith("flash('Claim approved', 'success')") or content.rstrip().endswith("success')"):
            # Find the start of claims_approve function
            idx = content.rfind("def claims_approve(claim_id):")
            if idx != -1:
                # Replace from function start onwards
                before = content[:idx]
                
                fixed_function = """def claims_approve(claim_id):
    \"\"\"Approve/reject claim\"\"\"
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
            claim.rejection_reason = request.form.get('reason', '')
            flash('Claim rejected', 'info')

        db.session.commit()
        return redirect(url_for('claims_list'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')
        return redirect(url_for('claims_list'))
"""
                
                content = before + fixed_function
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ Alternative fix applied!")
        
except Exception as e:
    print(f"❌ Error during fix: {e}")
    import traceback
    traceback.print_exc()