"""Automatically fix syntax error in routes.py"""

def repair():
    """Repair the incomplete claims_approve function"""
    path = "D:/Projects/HRMS/hrm/routes.py"
    
    # Read all lines
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The incomplete section
    incomplete = """    try:
        action = request.form.get('action')

        if action == 'approve':
            claim.status = 'Approved'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            flash('Claim approved', 'success')
     """
    
    # The complete replacement
    complete = """    try:
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
    
    if incomplete in content:
        content = content.replace(incomplete, complete)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ Fixed syntax error in routes.py")
        return True
    else:
        print("⚠️  Could not find incomplete pattern. Trying alternative...")
        # Try with stripped trailing whitespace
        incomplete2 = """        elif action == 'approve':
            claim.status = 'Approved'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            flash('Claim approved', 'success')"""
        
        if incomplete2 in content:
            replacement = """        if action == 'approve':
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
        return redirect(url_for('claims_list'))"""
            
            content = content.replace(incomplete2, replacement)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Fixed syntax error (alternative method)")
            return True
        
        return False

# Execute immediately when module is imported
repair()