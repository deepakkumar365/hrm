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
    def get_attendance_register_data(tenant_id, company_id=None, start_date=None, end_date=None, include_company_name=False):
        """Get detailed attendance register data as a list of dicts (one row per record). Includes all employees and all days in range."""
        emp_query = Employee.query.filter_by(is_active=True)
        if company_id:
            emp_query = emp_query.filter(Employee.company_id == company_id)
        
        employees = emp_query.order_by(Employee.first_name).all()
        emp_ids = [e.id for e in employees]
        
        # Fetch all existing attendance records in the range
        attendance_records = Attendance.query.filter(
            Attendance.date.between(start_date, end_date),
            Attendance.employee_id.in_(emp_ids)
        ).all()
        
        # Map records by (employee_id, date)
        attendance_map = {(r.employee_id, r.date): r for r in attendance_records}
        
        # Generate date list
        date_list = []
        curr = start_date
        while curr <= end_date:
            date_list.append(curr)
            curr += timedelta(days=1)
        
        report_data = []
        for emp in employees:
            for day in date_list:
                record = attendance_map.get((emp.id, day))
                
                # Build row
                row = {}
                if include_company_name:
                    row['Company'] = emp.company.name if emp.company else 'N/A'
                row['Employee ID'] = emp.employee_id
                row['Employee Name'] = f"{emp.first_name} {emp.last_name}"
                row['Department'] = emp.department or ''
                row['Date'] = day.strftime('%Y-%m-%d')
                
                if record:
                    # Clock In — prefer DateTime, fall back to Time
                    clock_in_val = ''
                    if record.clock_in_time:
                        clock_in_val = record.clock_in_time.strftime('%H:%M:%S')
                    elif record.clock_in:
                        clock_in_val = record.clock_in.strftime('%H:%M')
                    
                    # Clock Out — prefer DateTime, fall back to Time
                    clock_out_val = ''
                    if record.clock_out_time:
                        clock_out_val = record.clock_out_time.strftime('%H:%M:%S')
                    elif record.clock_out:
                        clock_out_val = record.clock_out.strftime('%H:%M')
                    
                    row['Clock In'] = clock_in_val
                    row['Clock Out'] = clock_out_val
                    row['Break Start'] = record.break_start.strftime('%H:%M') if record.break_start else ''
                    row['Break End'] = record.break_end.strftime('%H:%M') if record.break_end else ''
                    row['Regular Hours'] = float(record.regular_hours) if record.regular_hours else 0
                    row['Overtime Hours'] = float(record.overtime_hours) if record.overtime_hours else 0
                    row['Total Hours'] = float(record.total_hours) if record.total_hours else 0
                    row['Status'] = record.status or 'Absent'
                    row['Sub Status'] = record.sub_status or ''
                    row['Late'] = 'Yes' if record.is_late else 'No'
                    row['Late (mins)'] = record.late_minutes or 0
                    row['Early Departure'] = 'Yes' if record.is_early_departure else 'No'
                    row['Early Dept (mins)'] = record.early_departure_minutes or 0
                    row['LOP'] = 'Yes' if record.lop else 'No'
                    row['Remarks'] = record.remarks or ''
                else:
                    # Default row for missing record
                    row['Clock In'] = ''
                    row['Clock Out'] = ''
                    row['Break Start'] = ''
                    row['Break End'] = ''
                    row['Regular Hours'] = 0
                    row['Overtime Hours'] = 0
                    row['Total Hours'] = 0
                    row['Status'] = 'Absent'
                    row['Sub Status'] = ''
                    row['Late'] = 'No'
                    row['Late (mins)'] = 0
                    row['Early Departure'] = 'No'
                    row['Early Dept (mins)'] = 0
                    row['LOP'] = 'No'
                    row['Remarks'] = 'Auto-generated (No record found)'
                
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
    def get_absentee_report_data(tenant_id, company_id=None, target_date=None, include_company_name=False):
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
            row = {}
            if include_company_name:
                row['Company'] = record.employee.company.name if record.employee.company else 'N/A'
            row['Date'] = record.date.strftime('%Y-%m-%d')
            row['Employee ID'] = record.employee.employee_id
            row['Employee Name'] = f"{record.employee.first_name} {record.employee.last_name}"
            row['Department'] = record.employee.department or 'N/A'
            report_data.append(row)
            
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
    def get_overtime_report_data(tenant_id, company_id=None, start_date=None, end_date=None, include_company_name=False):
        """Get overtime report data as a list of dicts"""
        query = OTRequest.query.filter(OTRequest.ot_date.between(start_date, end_date))
        if company_id:
            query = query.filter(OTRequest.company_id == company_id)
            
        records = query.order_by(OTRequest.ot_date.desc()).all()
        
        report_data = []
        for record in records:
            emp_name = f"{record.employee.first_name} {record.employee.last_name}" if record.employee else "Unknown"
            ot_type_name = record.ot_type.name if record.ot_type else "N/A"
            row = {}
            if include_company_name:
                row['Company'] = record.company.name if record.company else 'N/A'
            row['Date'] = record.ot_date.strftime('%Y-%m-%d')
            row['Employee ID'] = record.employee.employee_id if record.employee else ''
            row['Employee Name'] = emp_name
            row['OT Type'] = ot_type_name
            row['Hours'] = record.requested_hours
            row['Amount'] = record.amount
            row['Status'] = record.status
            row['Reason'] = record.reason or ''
            report_data.append(row)
            
        return report_data
