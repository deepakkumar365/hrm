#!/usr/bin/env python3
"""Fix the incomplete routes.py file"""

# Read the file
with open('routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove the incomplete last line if it's just "claim.approved_at"
if lines and lines[-1].strip() == 'claim.approved_at':
    lines = lines[:-1]

# Add the complete function ending
complete_ending = """            claim.approved_at = datetime.now()
            flash('Claim rejected', 'success')
        
        db.session.commit()
        return redirect(url_for('claims_list'))

    except Exception as e:
        db.session.rollback()
        flash(f'Error processing claim: {str(e)}', 'error')
        return redirect(url_for('claims_list'))
"""

lines.append(complete_ending)

# Write back
with open('routes.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('✅ Fixed incomplete claims_approve function in routes.py')