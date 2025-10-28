#!/usr/bin/env python3
"""Add missing claims routes to routes.py"""

claims_routes = '''

# ===== CLAIMS ROUTES =====

@app.route('/claims')
@require_login
def claims_list():
    """List expense claims"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    
    query = Claim.query
    
    # Filter by role/user
    current_role = current_user.role.name if current_user.role else None
    if current_role == 'Employee' and hasattr(current_user, 'employee_profile'):
        query = query.filter(Claim.employee_id == current_user.employee_profile.id)
    elif current_role not in ['Super Admin', 'Admin', 'Manager']:
        flash('Unauthorized', 'error')
        return redirect(url_for('dashboard'))
    
    # Filter by status if provided
    if status_filter:
        query = query.filter(Claim.status == status_filter)
    
    claims = query.paginate(page=page, per_page=20)
    
    return render_template('claims/list.html', 
                         claims=claims, 
                         status_filter=status_filter)


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

if __name__ == '__main__':
    # Read current routes.py
    with open('routes.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if claims_routes already exist
    if '@app.route(\'/claims\')' in content:
        print('✅ Claims routes already exist in routes.py')
    else:
        # Append claims routes
        with open('routes.py', 'a', encoding='utf-8') as f:
            f.write(claims_routes)
        print('✅ Added claims routes to routes.py')