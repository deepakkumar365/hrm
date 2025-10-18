#!/usr/bin/env python3
"""Fix the incomplete claims_approve function in routes.py"""

# Read the file
with open('routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The incomplete function
old_text = """@app.route('/claims/<int:claim_id>/approve', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def claims_approve(claim_id):
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
            c"""

# The complete function
new_text = """@app.route('/claims/<int:claim_id>/approve', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def claims_approve(claim_id):
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
            claim.rejection_reason = request.form.get('rejection_reason')
            flash('Claim rejected', 'success')

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')

    return redirect(url_for('claims_list'))"""

if old_text in content:
    content = content.replace(old_text, new_text)
    print("✓ Found and replaced the incomplete function")
else:
    # Try finding it with just the end part
    if content.endswith("            c"):
        # File ends with incomplete code
        content = content[:-1] + new_text.split("elif action == 'reject':\n            c")[-1]
        print("✓ Fixed by completing the end of the file")
    else:
        print("✗ Could not find the pattern to fix")
        exit(1)

# Write back
with open('routes.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ File has been fixed successfully!")