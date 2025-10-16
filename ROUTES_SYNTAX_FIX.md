# Routes.py Syntax Error Fix

## Issue Found
The `routes.py` file had an incomplete/truncated function at the end:
- **Line 2892**: `claim.approved_at` - incomplete statement
- Missing except/finally block to close the try block in `claims_approve()` function

## Error Message
```
SyntaxError: expected 'except' or 'finally' block
```

## Fix Applied
Completed the `claims_approve()` function (lines 2874-2901):

### Before (Broken)
```python
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
            claim.approved_at  # <-- INCOMPLETE!
```

### After (Fixed)
```python
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
```

## Changes Made
1. ✅ Completed line 2892: Added `= datetime.now()`
2. ✅ Added missing `elif action == 'reject':` block (lines 2889-2893)
3. ✅ Added database commit and redirect (lines 2895-2896)
4. ✅ Added proper exception handling (lines 2898-2901)

## Testing
Run this command in PyCharm Terminal to verify syntax:
```bash
python verify_syntax.py
```

Or use PyCharm's built-in syntax checker: Right-click on `routes.py` → "Run" → "Run Python"

## Next Steps
Your app should now start without the syntax error! 

**Note**: The app will still need the database connection from your `.env` file to run properly.

---

**Status**: ✅ Fixed - Syntax error resolved, app should now load properly