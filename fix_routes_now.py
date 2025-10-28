#!/usr/bin/env python3
"""Fix routes.py incomplete function"""
import os

# Read the file
file_path = os.path.join(os.path.dirname(__file__), 'routes.py')
with open(file_path, 'rb') as f:
    content_bytes = f.read()

# Convert to string
content = content_bytes.decode('utf-8', errors='replace')

# Find and replace
if "elif action == 'reject':" in content and content.rstrip().endswith("c"):
    # Find the position of the incomplete elif
    pos = content.rfind("elif action == 'reject':")
    if pos != -1:
        # Get everything up to and including "elif action == 'reject':"
        before = content[:pos + len("elif action == 'reject':")]
        
        # Add the complete function body
        replacement = before + """
            claim.status = 'Rejected'
            claim.approved_by = current_user.id
            claim.approved_at = datetime.now()
            claim.rejection_reason = request.form.get('rejection_reason')
            flash('Claim rejected', 'success')

        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')

    return redirect(url_for('claims_list'))
"""
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(replacement)
        print("✅ Fixed!")
        exit(0)

print("❌ Could not find pattern to fix")
exit(1)