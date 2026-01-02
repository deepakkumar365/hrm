from datetime import datetime, date, time, timedelta
from app import db
from core.models import Attendance, AttendanceSegment, Employee, WorkingHours
from pytz import timezone, utc
import logging

logger = logging.getLogger(__name__)

class AttendanceService:
    @staticmethod
    def clock_in(employee_id, latitude=None, longitude=None, remarks=None):
        """Handle clock-in logic, creating segments and updating main attendance record."""
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "Employee not found"
            
            # Get company timezone
            company = employee.company
            timezone_str = company.timezone if company else 'UTC'
            tz = timezone(timezone_str)
            
            # Current time in company local
            now_utc = datetime.now(utc)
            current_time = now_utc.astimezone(tz)
            today = current_time.date()
            
            attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
            
            # Auto-close yesterday's forgotten segments if any
            AttendanceService.auto_close_previous_days(employee_id, today)
            
            if not attendance:
                # First clock-in of the day
                attendance = Attendance(
                    employee_id=employee_id,
                    date=today,
                    status='Incomplete',
                    sub_status='Pending Out',
                    timezone=timezone_str,
                    clock_in_time=current_time,
                    clock_in=current_time.time(),
                    location_lat=latitude,
                    location_lng=longitude,
                    remarks=remarks
                )
                db.session.add(attendance)
                db.session.flush()
                
                # Check for lateness
                AttendanceService._check_late_early(attendance, employee, current_time)
            else:
                # Resuming or already clocked in
                # Check if there's an open segment
                open_segment = AttendanceSegment.query.filter_by(
                    attendance_id=attendance.id, 
                    clock_out=None
                ).first()
                
                if open_segment:
                    return False, "Already clocked in"
                
                attendance.status = 'Incomplete'
                attendance.sub_status = 'Pending Out'
                attendance.updated_at = datetime.now()

            # Create new segment
            new_segment = AttendanceSegment(
                attendance_id=attendance.id,
                segment_type='Work',
                clock_in=current_time,
                location_lat=latitude,
                location_lng=longitude,
                remarks=remarks
            )
            db.session.add(new_segment)
            db.session.commit()
            
            return True, "Clocked in successfully"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Clock-in error for employee {employee_id}: {str(e)}")
            return False, f"Server error: {str(e)}"

    @staticmethod
    def start_break(employee_id, remarks=None):
        """Start a break segment."""
        try:
            employee = Employee.query.get(employee_id)
            if not employee: return False, "Employee not found"
            
            company_tz = timezone(employee.company.timezone if employee.company else 'UTC')
            now_local = datetime.now(utc).astimezone(company_tz)
            today = now_local.date()
            
            attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
            if not attendance: return False, "No active attendance for today. Clock in first."
            
            # Ensure work segment is closed or handle overlapping
            open_work = AttendanceSegment.query.filter_by(attendance_id=attendance.id, clock_out=None, segment_type='Work').first()
            if open_work:
                open_work.clock_out = now_local
                duration = (now_local - open_work.clock_in).total_seconds() / 60
                open_work.duration_minutes = int(max(0, duration))
            
            # Start break segment
            new_break = AttendanceSegment(
                attendance_id=attendance.id,
                segment_type='Break',
                clock_in=now_local,
                remarks=remarks
            )
            # Update legacy break field if first break
            if not attendance.break_start:
                attendance.break_start = now_local.time()
                
            db.session.add(new_break)
            db.session.commit()
            return True, "Break started"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def end_break(employee_id, remarks=None):
        """End a break segment and resume work."""
        try:
            employee = Employee.query.get(employee_id)
            if not employee: return False, "Employee not found"
            
            company_tz = timezone(employee.company.timezone if employee.company else 'UTC')
            now_local = datetime.now(utc).astimezone(company_tz)
            today = now_local.date()
            
            attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
            if not attendance: return False, "No attendance record"
            
            open_break = AttendanceSegment.query.filter_by(attendance_id=attendance.id, clock_out=None, segment_type='Break').first()
            if not open_break: return False, "No active break found"
            
            # Close break
            open_break.clock_out = now_local
            duration = (now_local - open_break.clock_in).total_seconds() / 60
            open_break.duration_minutes = int(max(0, duration))
            
            # Update legacy break field
            attendance.break_end = now_local.time()
            
            # Resume work segment
            new_work = AttendanceSegment(
                attendance_id=attendance.id,
                segment_type='Work',
                clock_in=now_local,
                remarks="Resumed after break"
            )
            
            db.session.add(new_work)
            db.session.commit()
            return True, "Break ended and work resumed"
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def clock_out(employee_id, latitude=None, longitude=None, remarks=None):
        """Handle clock-out logic, closing segments and calculating total hours."""
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "Employee not found"
            
            # Get company timezone
            company = employee.company
            timezone_str = company.timezone if company else 'UTC'
            tz = timezone(timezone_str)
            
            # Current time in company local
            now_utc = datetime.now(utc)
            current_time = now_utc.astimezone(tz)
            today = current_time.date()
            
            attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
            
            if not attendance:
                return False, "No active attendance record for today. Please clock in first."
            
            # Find open segment
            open_segment = AttendanceSegment.query.filter_by(
                attendance_id=attendance.id, 
                clock_out=None
            ).first()
            
            if not open_segment:
                return False, "Not currently clocked in"
            
            # Close segment
            open_segment.clock_out = current_time
            duration = (current_time - open_segment.clock_in).total_seconds() / 60
            open_segment.duration_minutes = int(max(0, duration))
            if remarks:
                open_segment.remarks = (open_segment.remarks or "") + f" | Out Note: {remarks}"
            
            # Update main attendance record
            attendance.clock_out_time = current_time
            attendance.clock_out = current_time.time()
            attendance.status = 'Present'
            attendance.sub_status = None
            attendance.updated_at = datetime.now()
            
            # Recalculate total hours
            AttendanceService._calculate_hours(attendance, employee)
            
            # Check for early departure
            AttendanceService._check_late_early(attendance, employee, current_time, is_clock_out=True)
            
            db.session.commit()
            return True, "Clocked out successfully"
        except Exception as e:
            db.session.rollback()
            logger.error(f"Clock-out error for employee {employee_id}: {str(e)}")
            return False, f"Server error: {str(e)}"

    @staticmethod
    def auto_close_previous_days(employee_id, today_date):
        """Handle forgotten clock-outs from previous days."""
        past_incomplete_records = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.status == 'Incomplete',
            Attendance.date < today_date
        ).all()

        for past_record in past_incomplete_records:
            # 1. Close open segments if any
            open_segments = AttendanceSegment.query.filter_by(
                attendance_id=past_record.id,
                clock_out=None
            ).all()
            
            employee = past_record.employee
            # Determine cutoff time (WorkingHours end_time or default 18:00)
            auto_cutoff_time = time(18, 0)
            if employee.working_hours and employee.working_hours.end_time:
                auto_cutoff_time = employee.working_hours.end_time
            
            cutoff_dt = datetime.combine(past_record.date, auto_cutoff_time)
            # Localize cutoff_dt
            tz = timezone(past_record.timezone or 'UTC')
            cutoff_dt = tz.localize(cutoff_dt)
            
            for seg in open_segments:
                seg.clock_out = cutoff_dt
                duration = (cutoff_dt - seg.clock_in).total_seconds() / 60
                seg.duration_minutes = int(max(0, duration))
                seg.remarks = (seg.remarks or "") + " [Auto-closed]"

            # 2. Update main record
            past_record.clock_out = auto_cutoff_time
            past_record.clock_out_time = cutoff_dt
            past_record.status = 'Present'
            past_record.sub_status = 'Auto-closed'
            
            # 3. Calculate hours
            AttendanceService._calculate_hours(past_record, employee)
            
            # 4. Check early departure for the auto-closed record (likely False if closed at EOD)
            AttendanceService._check_late_early(past_record, employee, cutoff_dt, is_clock_out=True)

    @staticmethod
    def _calculate_hours(attendance, employee):
        """Calculate total, regular, and overtime hours from all segments."""
        segments = AttendanceSegment.query.filter_by(attendance_id=attendance.id).all()
        
        total_minutes = sum(s.duration_minutes for s in segments if s.duration_minutes)
        total_hours = total_minutes / 60.0
        
        # Get standard hours
        standard_hours = 8.0
        if employee.working_hours and employee.working_hours.hours_per_day:
            standard_hours = float(employee.working_hours.hours_per_day)
        
        if total_hours > standard_hours:
            attendance.regular_hours = standard_hours
            attendance.overtime_hours = total_hours - standard_hours
            attendance.has_overtime = True
        else:
            attendance.regular_hours = total_hours
            attendance.overtime_hours = 0
            attendance.has_overtime = False
            
        attendance.total_hours = total_hours

    @staticmethod
    def _check_late_early(attendance, employee, current_time, is_clock_out=False):
        """Evaluate lateness or early departure based on WorkingHours."""
        if not employee.working_hours:
            return
            
        wh = employee.working_hours
        grace_period = getattr(wh, 'grace_period', 15)
        tz = current_time.tzinfo
        
        if not is_clock_out:
            # Check Lateness
            if wh.start_time:
                shift_start = tz.localize(datetime.combine(attendance.date, wh.start_time))
                if current_time > (shift_start + timedelta(minutes=grace_period)):
                    attendance.is_late = True
                    late_delta = current_time - shift_start
                    attendance.late_minutes = int(late_delta.total_seconds() / 60)
                else:
                    attendance.is_late = False
                    attendance.late_minutes = 0
        else:
            # Check Early Departure
            if wh.end_time:
                shift_end = tz.localize(datetime.combine(attendance.date, wh.end_time))
                if current_time < shift_end:
                    attendance.is_early_departure = True
                    early_delta = shift_end - current_time
                    attendance.early_departure_minutes = int(early_delta.total_seconds() / 60)
                else:
                    attendance.is_early_departure = False
                    attendance.early_departure_minutes = 0
