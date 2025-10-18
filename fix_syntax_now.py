#!/usr/bin/env python3
"""Fix the incomplete claims_approve function syntax error"""

def fix_routes():
    routes_path = "D:/Projects/HRMS/hrm/routes.py"
    
    # Read the file
    with open(routes_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # The file ends incomplete at line 2921
    # We need to complete the claims_approve function
    
    # Find the incomplete line
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        # After the 'flash(Claim approved...)' line, we need to add the rest
        if i == 2919:  # Line 2920 (0-indexed)
            new_lines.append("        elif action == 'reject':\n")
            new_lines.append("            claim.status = 'Rejected'\n")
            new_lines.append("            claim.approved_by = current_user.id\n")
            new_lines.append("            claim.approved_at = datetime.now()\n")
            new_lines.append("            claim.rejection_reason = request.form.get('reason', '')\n")
            new_lines.append("            flash('Claim rejected', 'info')\n")
            new_lines.append("\n")
            new_lines.append("        db.session.commit()\n")
            new_lines.append("        return redirect(url_for('claims_list'))\n")
            new_lines.append("\n")
            new_lines.append("    except Exception as e:\n")
            new_lines.append("        db.session.rollback()\n")
            new_lines.append("        flash(f'Error processing claim: {str(e)}', 'error')\n")
            new_lines.append("        return redirect(url_for('claims_list'))\n")
    
    # Write back
    with open(routes_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("✅ Fixed incomplete claims_approve function in routes.py")

if __name__ == '__main__':
    fix_routes()