#!/usr/bin/env python3
"""Fix the truncated routes.py file"""

# Read the file up to the truncation point
with open('D:/Projects/HRMS/hrm/routes.py', 'r') as f:
    content = f.read()

# Find where it's truncated (at the unterminated string)
# The file should end with: request.form.get('r

# Complete the appraisal_create function
completion = """eview_period_start'))
            appraisal.review_period_end = parse_date(
                request.form.get('review_period_end'))
            appraisal.comments = request.form.get('comments')
            
            db.session.add(appraisal)
            db.session.commit()
            flash('Appraisal created successfully!', 'success')
            return redirect(url_for('appraisal_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating appraisal: {str(e)}', 'error')
    
    employees = Employee.query.all()
    return render_template('appraisal/create.html', employees=employees)
"""

# The file ends with: request.form.get('r
# We need to remove 'r and complete it

if content.endswith("request.form.get('r"):
    # Remove the 'r and add the completion
    content = content[:-len("request.form.get('r")] + completion
    
    with open('D:/Projects/HRMS/hrm/routes.py', 'w') as f:
        f.write(content)
    print("✅ routes.py has been fixed!")
    print(f"New file size: {len(content)} characters")
else:
    print("File doesn't end as expected, manual review needed")
    print(f"Last 100 chars: {repr(content[-100:])}")