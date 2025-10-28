@echo off
REM Fix for incomplete claims_approve function in routes.py
REM This batch file uses PowerShell with -NoProfile to bypass execution policies

cd /d "D:\Projects\HRMS\hrm"

powershell -NoProfile -Command ^
"$file = 'routes.py'; $content = [System.IO.File]::ReadAllText($file); $fixed = $content.Replace(\"\`\`elif action == 'reject':\`r\`n            c\`\`\", \"\`\`elif action == 'reject':\`r\`n            claim.status = 'Rejected'\`r\`n            claim.approved_by = current_user.id\`r\`n            claim.approved_at = datetime.now()\`r\`n            claim.rejection_reason = request.form.get('rejection_reason')\`r\`n            flash('Claim rejected', 'success')\`r\`n\`r\`n        db.session.commit()\`r\`n\`r\`n    except Exception as e:\`r\`n        db.session.rollback()\`r\`n        flash(f'Error processing claim: {str(e)}', 'error')\`r\`n\`r\`n    return redirect(url_for('claims_list'))\`\`\"); [System.IO.File]::WriteAllText($file, $fixed); Write-Host 'File fixed successfully!'"

echo Done!
pause