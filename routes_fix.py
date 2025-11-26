# Complete function replacement for api_attendance_calendar_data
# This should replace lines 2776-2836 in routes.py

@app.route('/api/attendance/calendar-data')
@require_login
def api_attendance_calendar_data():
    """API endpoint to fetch attendance data for the calendar."""
    try:
        employee_id = request.args.get('employee_id', type=int)
        start_str = request.args.get('start')
        end_str = request.args.get('end')

        if not employee_id:
            return jsonify({'error': 'Employee ID is required'}), 400

        # Permission check
        user_role = current_user.role.name if current_user.role else None
        if user_role in ['User', 'Employee']:
            if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile and current_user.employee_profile.id == employee_id):
                return jsonify({'error': 'Permission denied'}), 403
        elif user_role == 'HR Manager':
            employee_to_view = Employee.query.get(employee_id)
            if not (hasattr(current_user, 'employee_profile') and current_user.employee_profile and employee_to_view and employee_to_view.organization_id == current_user.employee_profile.organization_id):
                 return jsonify({'error': 'Permission denied'}), 403

        start_date = datetime.fromisoformat(start_str.split('T')[0]).date()
        end_date = datetime.fromisoformat(end_str.split('T')[0]).date()

        # Fetch attendance and approved leaves for the date range
        attendance_records = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            Attendance.date.between(start_date, end_date)
        ).all()

        leave_records = Leave.query.filter(
            Leave.employee_id == employee_id,
            Leave.status == 'Approved',
            Leave.start_date <= end_date,
            Leave.end_date >= start_date
        ).all()

        # Process data into a dictionary for quick lookup, prioritizing leaves over attendance
        events_dict = {}

        # First, add leave records
        for leave in leave_records:
            current_date = leave.start_date
            while current_date <= leave.end_date:
                if start_date <= current_date <= end_date:
                    events_dict[current_date] = {
                        'date': current_date.isoformat(),
                        'status': 'Leave',
                        'leave_type': leave.leave_type,
                        'remarks': leave.reason or ''
                    }
                current_date += timedelta(days=1)

        # Then, add attendance records, only if a leave is not already on that day
        for record in attendance_records:
            if record.date not in events_dict:
                events_dict[record.date] = {
                    'date': record.date.isoformat(),
                    'status': record.status,
                    'clock_in': record.clock_in.strftime('%H:%M') if record.clock_in else 'N/A',
                    'clock_out': record.clock_out.strftime('%H:%M') if record.clock_out else 'N/A'
                }
        
        # Convert to list and return
        events_list = list(events_dict.values())
        return jsonify(events_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500