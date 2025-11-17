#!/usr/bin/env python3
"""Fix incomplete routes.py file"""

# Read the file
with open('routes.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

print(f"File has {len(lines)} lines")
print(f"Last line: {repr(lines[-1][:100])}")

# Keep everything up to line 2833 (before incomplete claims_submit)
kept_lines = lines[:2833]

# Complete claims routes
complete_routes = '''
@app.route('/claims/submit', methods=['GET', 'POST'])
@require_login
def claims_submit():
    """Submit new claim"""
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        flash('Employee profile required for submitting claims', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            claim = Claim()
            claim.employee_id = current_user.employee_profile.id
            claim.organization_id = current_user.organization_id
            claim.claim_type = request.form.get('claim_type')
            claim.amount = float(request.form.get('amount', 0))
            claim.description = request.form.get('description')
            claim.claim_date = datetime.now()
            claim.status = 'Pending'
            
            db.session.add(claim)
            db.session.commit()
            
            flash('Claim submitted successfully', 'success')
            return redirect(url_for('claims_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error submitting claim: {str(e)}', 'error')
    
    return render_template('claims/form.html')


@app.route('/claims/<int:claim_id>/approve', methods=['POST'])
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

# Write the fixed file
with open('routes.py', 'w', encoding='utf-8') as f:
    f.writelines(kept_lines)
    f.write(complete_routes)
    f.write('\n')

print("✅ Fixed routes.py - replaced incomplete claims routes")
print(f"New file size: {len(open('routes.py', 'r', encoding='utf-8', errors='replace').readlines())} lines")