
original_block = """            employer_cpf = 0.0 # Track Employer CPF
            
            if payroll_record and payroll_record.status in ['Draft', 'Generated', 'Approved', 'Paid']:
                # SOURCE 1: Use persisted overrides from Payroll table
                total_ot_hours = float(payroll_record.overtime_hours or 0)
                ot_amount = float(payroll_record.overtime_pay or 0)
                
                # Use persisted CPF if available
                if payroll_record.employee_cpf is not None:
                     cpf_override = float(payroll_record.employee_cpf)
                
                # Use persisted Employer CPF if available
                if payroll_record.employer_cpf is not None:
                    employer_cpf = float(payroll_record.employer_cpf)

            else:
                # SOURCE 2: Calculate from Daily Summaries (Live Data)
                ot_summaries = OTDailySummary.query.filter_by(
                    employee_id=emp.id,
                    status='Approved'
                ).filter(
                    extract('month', OTDailySummary.ot_date) == month,
                    extract('year', OTDailySummary.ot_date) == year
                ).all()

                # Aggregate Approved OT Data
                total_ot_hours = sum(float(s.ot_hours or 0) for s in ot_summaries)
                ot_amount = sum(float(s.ot_amount or 0) for s in ot_summaries)
                ot_allowances = sum(float(s.total_allowances or 0) for s in ot_summaries)"""

new_block = """            employer_cpf = 0.0 # Track Employer CPF
            
            # Logic Update: For 'Draft' records, ALWAYS recalculate OT from daily summaries
            # to ensure late approvals are reflected. Only use stored values for finalized records.
            if payroll_record and payroll_record.status in ['Generated', 'Approved', 'Paid']:
                # SOURCE 1: Use persisted overrides from Payroll table (Finalized Data)
                total_ot_hours = float(payroll_record.overtime_hours or 0)
                ot_amount = float(payroll_record.overtime_pay or 0)
                
                # Use persisted CPF if available
                if payroll_record.employee_cpf is not None:
                     cpf_override = float(payroll_record.employee_cpf)
                
                # Use persisted Employer CPF if available
                if payroll_record.employer_cpf is not None:
                    employer_cpf = float(payroll_record.employer_cpf)

            else:
                # SOURCE 2: Calculate from Daily Summaries (Live Data)
                # Applies to: No Record OR 'Draft' Record
                ot_summaries = OTDailySummary.query.filter_by(
                    employee_id=emp.id,
                    status='Approved'
                ).filter(
                    extract('month', OTDailySummary.ot_date) == month,
                    extract('year', OTDailySummary.ot_date) == year
                ).all()

                # Aggregate Approved OT Data
                total_ot_hours = sum(float(s.ot_hours or 0) for s in ot_summaries)
                ot_amount = sum(float(s.ot_amount or 0) for s in ot_summaries)
                ot_allowances = sum(float(s.total_allowances or 0) for s in ot_summaries)
                
                # If we have a Draft record, we might still want to preserve CPF overrides
                if payroll_record and payroll_record.status == 'Draft':
                     if payroll_record.employee_cpf is not None:
                         cpf_override = float(payroll_record.employee_cpf)
                     if payroll_record.employer_cpf is not None:
                         employer_cpf = float(payroll_record.employer_cpf)"""

with open('d:/Project/Workouts/hrm/routes/routes.py', 'r', encoding='utf-8') as f:
    content = f.read()

if original_block.strip() in content:
    print("Found exact block, replacing...")
    new_content = content.replace(original_block.strip(), new_block.strip())
    with open('d:/Project/Workouts/hrm/routes/routes.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Success")
else:
    print("Block not found. Trying stricter or looser match.")
    # Fallback: line by line match?
    # Simple check for the unique if statement
    target_line = "if payroll_record and payroll_record.status in ['Draft', 'Generated', 'Approved', 'Paid']:"
    if target_line in content:
        print("Found target line, attempting partial replacement...")
        new_line = "if payroll_record and payroll_record.status in ['Generated', 'Approved', 'Paid']:"
        new_content = content.replace(target_line, new_line)
        
        # We also need to add the preserve logic at the end of the ELSE block.
        # This is harder to do safely with simple replace.
        print("...Actually, a simple replace of the IF condition handles the MAIN part (forcing calculation for Draft).")
        print("But we need to preserve CPF overrides.")
        print("Manual patch recommended if strict block fails.")
