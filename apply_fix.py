import re
import os

file_path = 'd:/Project/Workouts/hrm/routes/routes.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Pattern to match the IF condition
# if payroll_record and payroll_record.status in ['Draft', 'Generated', 'Approved', 'Paid']:
pattern_if = r"if\s+payroll_record\s+and\s+payroll_record\.status\s+in\s+\['Draft',\s*'Generated',\s*'Approved',\s*'Paid'\]:"
replacement_if = "if payroll_record and payroll_record.status in ['Generated', 'Approved', 'Paid']:"

# Pattern to find the end of the ELSE block to append CPF preservation logic
# We look for the end of the else block which calculates ot values
# ot_allowances = sum(float(s.total_allowances or 0) for s in ot_summaries)
pattern_end_else = r"(ot_allowances\s*=\s*sum\(float\(s\.total_allowances\s*or\s*0\)\s*for\s*s\s*in\s*ot_summaries\))"

replacement_end_else = r"""\1

            # Logic Update: Preservation of CPF overrides for Draft records
            if payroll_record and payroll_record.status == 'Draft':
                 if payroll_record.employee_cpf is not None:
                     cpf_override = float(payroll_record.employee_cpf)
                 if payroll_record.employer_cpf is not None:
                     employer_cpf = float(payroll_record.employer_cpf)"""

# Apply modifications
new_content = content
if re.search(pattern_if, new_content):
    print("Found IF condition, replacing...")
    new_content = re.sub(pattern_if, replacement_if, new_content)
else:
    print("IF condition NOT found!")

if re.search(pattern_end_else, new_content):
    print("Found end of ELSE block, appending logic...")
    new_content = re.sub(pattern_end_else, replacement_end_else, new_content)
else:
    print("End of ELSE block NOT found!")

if new_content != content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("File updated successfully.")
else:
    print("No changes made.")
