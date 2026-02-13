import io
import csv
import calendar
from datetime import datetime, date, timedelta
from sqlalchemy import func
from core.models import Attendance, Employee, Department, OTRequest, db

class ReportService:
    @staticmethod
    def get_dates_from_filter(filter_type):
        """Convert relative filter type to absolute start and end dates"""
        today = date.today()
        if filter_type == 'today':
            return today, today
        elif filter_type == 'yesterday':
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        elif filter_type == 'last_7_days':
            return today - timedelta(days=7), today
        elif filter_type == 'last_30_days':
            return today - timedelta(days=30), today
        elif filter_type == 'current_month':
            start = date(today.year, today.month, 1)
            _, last_day = calendar.monthrange(today.year, today.month)
            end = date(today.year, today.month, last_day)
            return start, end
        elif filter_type == 'previous_month':
            first_of_current = date(today.year, today.month, 1)
            last_of_prev = first_of_current - timedelta(days=1)
            first_of_prev = date(last_of_prev.year, last_of_prev.month, 1)
            return first_of_prev, last_of_prev
        
        return today, today # Fallback

    @staticmethod
    def generate_attendance_register_csv(tenant_id, company_id=None, start_date=None, end_date=None):
        """Generate monthly attendance register CSV"""
        data = ReportService.get_attendance_register_data(tenant_id, company_id, start_date, end_date)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        if not data:
            return ""

        # Header: Name, Employee ID, Date 1, Date 2, ...
        # Assuming all rows have the same keys, and they are ordered
        header = list(data[0].keys())
        writer.writerow(header)
        
        for row in data:
            writer.writerow(row.values())
            
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def get_attendance_register_data(tenant_id, company_id=None, start_date=None, end_date=None):
        """Get attendance register data as a list of dicts"""
        emp_query = Employee.query.filter_by(is_active=True)
        if company_id:
            emp_query = emp_query.filter(Employee.company_id == company_id)
        
        employees = emp_query.order_by(Employee.first_name).all()
        emp_ids = [e.id for e in employees]
        
        attendance_records = Attendance.query.filter(
            Attendance.date.between(start_date, end_date),
            Attendance.employee_id.in_(emp_ids)
        ).all()
        
        attendance_map = {}
        for record in attendance_records:
            attendance_map[(record.employee_id, record.date)] = record.status

        days = []
        curr = start_date
        while curr <= end_date:
            days.append(curr)
            curr += timedelta(days=1)
            
        report_data = []
        for emp in employees:
            row = {
                'Employee Name': f"{emp.first_name} {emp.last_name}",
                'Employee ID': emp.employee_id
            }
            for d in days:
                row[d.strftime('%Y-%m-%d')] = attendance_map.get((emp.id, d), '-')
            report_data.append(row)
            
        return report_data

    @staticmethod
    def generate_absentee_report_csv(tenant_id, company_id=None, target_date=None):
        """Generate list of absent employees for a target date CSV"""
        data = ReportService.get_absentee_report_data(tenant_id, company_id, target_date)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        if not data:
            writer.writerow(['Date', 'Employee ID', 'Employee Name', 'Department'])
            return output.getvalue()

        header = list(data[0].keys())
        writer.writerow(header)
        
        for row in data:
            writer.writerow(row.values())
            
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def get_absentee_report_data(tenant_id, company_id=None, target_date=None):
        """Get absentee report data as a list of dicts"""
        query = Attendance.query.join(Employee).filter(
            Attendance.date == target_date,
            Attendance.status == 'Absent'
        )
        if company_id:
            query = query.filter(Employee.company_id == company_id)
            
        records = query.order_by(Employee.first_name).all()
        
        report_data = []
        for record in records:
            report_data.append({
                'Date': record.date.strftime('%Y-%m-%d'),
                'Employee ID': record.employee.employee_id,
                'Employee Name': f"{record.employee.first_name} {record.employee.last_name}",
                'Department': record.employee.department or 'N/A'
            })
            
        return report_data

    @staticmethod
    def generate_overtime_report_csv(tenant_id, company_id=None, start_date=None, end_date=None):
        """Generate OT request report CSV"""
        data = ReportService.get_overtime_report_data(tenant_id, company_id, start_date, end_date)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        if not data:
            writer.writerow(['Date', 'Employee ID', 'Employee Name', 'OT Type', 'Hours', 'Amount', 'Status', 'Reason'])
            return output.getvalue()

        header = list(data[0].keys())
        writer.writerow(header)
        
        for row in data:
            writer.writerow(row.values())
            
        output.seek(0)
        return output.getvalue()

    @staticmethod
    def get_overtime_report_data(tenant_id, company_id=None, start_date=None, end_date=None):
        """Get overtime report data as a list of dicts"""
        query = OTRequest.query.filter(OTRequest.ot_date.between(start_date, end_date))
        if company_id:
            query = query.filter(OTRequest.company_id == company_id)
            
        records = query.order_by(OTRequest.ot_date.desc()).all()
        
        report_data = []
        for record in records:
            emp_name = f"{record.employee.first_name} {record.employee.last_name}" if record.employee else "Unknown"
            ot_type_name = record.ot_type.name if record.ot_type else "N/A"
            report_data.append({
                'Date': record.ot_date.strftime('%Y-%m-%d'),
                'Employee ID': record.employee.employee_id if record.employee else '',
                'Employee Name': emp_name,
                'OT Type': ot_type_name,
                'Hours': record.requested_hours,
                'Amount': record.amount,
                'Status': record.status,
                'Reason': record.reason or ''
            })
            
        return report_data
