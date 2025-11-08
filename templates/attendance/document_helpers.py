import os
from datetime import datetime
from hrm.models import EmployeeDocument, db
from flask_login import current_user
import logging


def create_document_from_payslip(payroll_record, file_path):
    """
    Creates an EmployeeDocument record for a generated payslip.

    Args:
        payroll_record (Payroll): The payroll record object.
        file_path (str): The absolute path to the generated payslip PDF.
    """
    try:
        # Check if a document for this payslip already exists
        existing_document = EmployeeDocument.query.filter_by(
            employee_id=payroll_record.employee_id,
            document_type='Salary Slip',
            month=payroll_record.pay_period_start.month,
            year=payroll_record.pay_period_start.year
        ).first()

        if existing_document:
            logging.info(f"Payslip document already exists for employee {payroll_record.employee_id} for period {payroll_record.pay_period_start.strftime('%Y-%m')}.")
            return

        new_document = EmployeeDocument(
            employee_id=payroll_record.employee_id,
            document_type='Salary Slip',
            file_path=file_path.replace(os.path.join(os.getcwd(), 'hrm'), '').replace('\\', '/').lstrip('/'),
            issue_date=datetime.utcnow(),
            month=payroll_record.pay_period_start.month,
            year=payroll_record.pay_period_start.year,
            description=f"Salary Slip for {payroll_record.pay_period_start.strftime('%B %Y')}",
            uploaded_by=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(new_document)
        db.session.commit()
        logging.info(f"Successfully created payslip document record for employee {payroll_record.employee_id}.")
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to create payslip document record for employee {payroll_record.employee_id}: {e}")