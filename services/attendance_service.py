from datetime import datetime, date, time, timedelta
from app import db
from core.models import Attendance, AttendanceSegment, Employee, WorkingHours
from pytz import timezone, utc
import logging
from core.timezone_utils import get_employee_timezone

logger = logging.getLogger(__name__)

class AttendanceService:
    @staticmethod
    def clock_in(employee_id, latitude=None, longitude=None, remarks=None):
        """Handle clock-in logic, creating segments and updating main attendance record."""
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "Employee not found", None
            
            # Get employee timezone (falls back to company)
            timezone_str = get_employee_timezone(employee)
            tz = timezone(timezone_str)
            
            # Current time in company local for date logic
            now_utc = datetime.now(utc)
            local_now = now_utc.astimezone(tz)
            today = local_now.date()
            
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
                    clock_in_time=now_utc, # Store UTC
                    clock_in=local_now.time(), # Local time for legacy display
                    location_lat=latitude,
                    location_lng=longitude,
                    remarks=remarks
                )
                db.session.add(attendance)
                db.session.flush()
                
                # Check for lateness (logic uses local time)
                AttendanceService._check_late_early(attendance, employee, local_now)
            else:
                # Resuming or already clocked in
                # Check if there's an open segment
                open_segment = AttendanceSegment.query.filter_by(
                    attendance_id=attendance.id, 
                    clock_out=None
                ).first()
                
                if open_segment:
                    return False, "Already clocked in", attendance
                
                attendance.status = 'Incomplete'
                attendance.sub_status = 'Pending Out'
                attendance.updated_at = datetime.utcnow()

            # Create new segment
            new_segment = AttendanceSegment(
                attendance_id=attendance.id,
                segment_type='Work',
                clock_in=now_utc, # Store UTC
                location_lat=latitude,
                location_lng=longitude,
                remarks=remarks
            )
            db.session.add(new_segment)
            db.session.commit()
            
            return True, "Clocked in successfully", attendance
        except Exception as e:
            db.session.rollback()
            logger.error(f"Clock-in error for employee {employee_id}: {str(e)}")
            return False, f"Server error: {str(e)}", None

    @staticmethod
    def start_break(employee_id, remarks=None):
        """Start a break segment."""
        try:
            employee = Employee.query.get(employee_id)
            if not employee: return False, "Employee not found", None
            
            timezone_str = get_employee_timezone(employee)
            company_tz = timezone(timezone_str)
            now_utc = datetime.now(utc)
            now_local = now_utc.astimezone(company_tz)
            today = now_local.date()
            
            attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
            if not attendance: return False, "No active attendance for today. Clock in first.", None
            
            # Ensure work segment is closed or handle overlapping
            open_work = AttendanceSegment.query.filter_by(attendance_id=attendance.id, clock_out=None, segment_type='Work').first()
            if open_work:
                open_work.clock_out = now_utc # Store UTC
                # Duration calculation remains correct with aware datetimes or consistent naive UTC
                # but since seg.clock_in is now UTC (standardized), we use now_utc
                duration = (now_utc - open_work.clock_in.replace(tzinfo=utc)).total_seconds() / 60
                open_work.duration_minutes = int(round(max(0, duration)))
            
            # Start break segment
            new_break = AttendanceSegment(
                attendance_id=attendance.id,
                segment_type='Break',
                clock_in=now_utc, # Store UTC
                remarks=remarks
            )
            # Update legacy break field if first break
            if not attendance.break_start:
                attendance.break_start = now_local.time()
                
            db.session.add(new_break)
            db.session.commit()
            return True, "Break started", attendance
        except Exception as e:
            db.session.rollback()
            return False, str(e), None

    @staticmethod
    def end_break(employee_id, remarks=None):
        """End a break segment and resume work."""
        try:
            employee = Employee.query.get(employee_id)
            if not employee: return False, "Employee not found", None
            
            timezone_str = get_employee_timezone(employee)
            company_tz = timezone(timezone_str)
            now_utc = datetime.now(utc)
            now_local = now_utc.astimezone(company_tz)
            today = now_local.date()
            
            attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
            if not attendance: return False, "No attendance record", None
            
            open_break = AttendanceSegment.query.filter_by(attendance_id=attendance.id, clock_out=None, segment_type='Break').first()
            if not open_break: return False, "No active break found", attendance
            
            # Close break
            open_break.clock_out = now_utc # Store UTC
            duration = (now_utc - open_break.clock_in.replace(tzinfo=utc)).total_seconds() / 60
            open_break.duration_minutes = int(round(max(0, duration)))
            
            # Update legacy break field
            attendance.break_end = now_local.time()
            
            # Resume work segment
            new_work = AttendanceSegment(
                attendance_id=attendance.id,
                segment_type='Work',
                clock_in=now_utc, # Store UTC
                remarks="Resumed after break"
            )
            
            db.session.add(new_work)
            db.session.commit()
            return True, "Break ended and work resumed", attendance
        except Exception as e:
            db.session.rollback()
            return False, str(e), None

    @staticmethod
    def clock_out(employee_id, latitude=None, longitude=None, remarks=None):
        """Handle clock-out logic, closing segments and calculating total hours."""
        try:
            employee = Employee.query.get(employee_id)
            if not employee:
                return False, "Employee not found", None
            
            # Get employee timezone
            timezone_str = get_employee_timezone(employee)
            tz = timezone(timezone_str)
            
            # Current time in company local for date logic
            now_utc = datetime.now(utc)
            local_now = now_utc.astimezone(tz)
            today = local_now.date()
            
            # Night Shift Support: Find the most recent incomplete attendance record
            # instead of strictly filtering by today's date.
            attendance = Attendance.query.filter_by(
                employee_id=employee_id, 
                status='Incomplete',
                sub_status='Pending Out'
            ).order_by(Attendance.date.desc()).first()
            
            # Fallback to today's record if no incomplete record found
            if not attendance:
                attendance = Attendance.query.filter_by(employee_id=employee_id, date=today).first()
            
            if not attendance:
                return False, "No active attendance record found. Please clock in first.", None
            
            # Find open segment
            open_segment = AttendanceSegment.query.filter_by(
                attendance_id=attendance.id, 
                clock_out=None
            ).first()
            
            if not open_segment:
                return False, "Not currently clocked in", attendance
            
            # Close segment
            open_segment.clock_out = now_utc # Store UTC
            duration = (now_utc - open_segment.clock_in.replace(tzinfo=utc)).total_seconds() / 60
            open_segment.duration_minutes = int(round(max(0, duration)))
            if remarks:
                open_segment.remarks = (open_segment.remarks or "") + f" | Out Note: {remarks}"
            
            # Update main attendance record
            attendance.clock_out_time = now_utc # Store UTC
            attendance.clock_out = local_now.time() # Local time for legacy display
            attendance.status = 'Present'
            attendance.sub_status = None
            attendance.updated_at = datetime.utcnow()
            
            # Recalculate total hours
            AttendanceService._calculate_hours(attendance, employee)
            
            # Check for early departure (logic uses local time)
            AttendanceService._check_late_early(attendance, employee, local_now, is_clock_out=True)
            
            db.session.commit()
            return True, "Clocked out successfully", attendance
        except Exception as e:
            db.session.rollback()
            logger.error(f"Clock-out error for employee {employee_id}: {str(e)}")
            return False, f"Server error: {str(e)}", None

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
            
            cutoff_local = datetime.combine(past_record.date, auto_cutoff_time)
            # Localize cutoff_dt
            tz = timezone(past_record.timezone or 'UTC')
            cutoff_local = tz.localize(cutoff_local)
            cutoff_utc = cutoff_local.astimezone(utc).replace(tzinfo=None) # Store as naive UTC
            
            for seg in open_segments:
                seg.clock_out = cutoff_utc
                # seg.clock_in is stored in UTC, so we can subtract directly if both naive or both aware
                seg_clock_in = seg.clock_in.replace(tzinfo=utc) if seg.clock_in.tzinfo is None else seg.clock_in
                duration = (cutoff_local.astimezone(utc) - seg_clock_in).total_seconds() / 60
                seg.duration_minutes = int(round(max(0, duration)))
                seg.remarks = (seg.remarks or "") + " [Auto-closed]"

            # 2. Update main record
            past_record.clock_out = auto_cutoff_time
            past_record.clock_out_time = cutoff_utc
            past_record.status = 'Present'
            past_record.sub_status = 'Auto-closed'
            
            # 3. Calculate hours
            AttendanceService._calculate_hours(past_record, employee)
            
            # 4. Check early departure (logic uses local time)
            AttendanceService._check_late_early(past_record, employee, cutoff_local, is_clock_out=True)

    @staticmethod
    def _calculate_hours(attendance, employee):
        """Calculate total, regular, and overtime hours from all segments."""
        segments = AttendanceSegment.query.filter_by(attendance_id=attendance.id).all()
        
        total_minutes = 0
        for s in segments:
            if s.clock_in and s.clock_out:
                # Ensure we have aware datetimes for calculation if they were stored naive
                c_in = s.clock_in.replace(tzinfo=utc) if s.clock_in.tzinfo is None else s.clock_in
                c_out = s.clock_out.replace(tzinfo=utc) if s.clock_out.tzinfo is None else s.clock_out
                duration = (c_out - c_in).total_seconds() / 60
                s.duration_minutes = int(round(max(0, duration)))
                total_minutes += s.duration_minutes
        
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
