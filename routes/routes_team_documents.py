"""
Routes for Team and Documents modules
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import current_user
from sqlalchemy import and_, or_, extract
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from app import app, db
from core.auth import require_login, require_role
from core.models import Employee, EmployeeDocument, User, Organization, Designation
from core.utils import format_date


# =====================================================
# TEAM MODULE - Show peers with same manager
# =====================================================

@app.route('/team')
@require_login
def team_list():
    """
    Display team members based on user role and is_manager flag:
    - Manager role OR is_manager=True: Shows direct reports (employees who report to this manager)
    - User role (is_manager=False): Shows peers (employees with the same manager)
    """
    # Check if current user has employee profile
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        flash('Employee profile not found. Please contact HR.', 'warning')
        return redirect(url_for('dashboard'))
    
    current_employee = current_user.employee_profile
    user_role_name = current_user.role.name if current_user.role else None
    
    # For Manager role OR employees flagged as is_manager: Show direct reports
    if user_role_name == 'Manager' or current_employee.is_manager:
        # Get all employees who report directly to this manager
        team_members = Employee.query.filter(
            and_(
                Employee.manager_id == current_employee.id,
                Employee.is_active == True
            )
        ).order_by(Employee.first_name, Employee.last_name).all()
        
        if not team_members:
            flash('You do not have any direct reports assigned yet.', 'info')
        
        return render_template('team/team_list.html', 
                             team_members=team_members,
                             manager=None,
                             current_employee=current_employee,
                             is_manager_view=True)
    
    # For User role: Show peers with same manager
    else:
        # Get the manager_id of the current user
        manager_id = current_employee.manager_id
        
        if not manager_id:
            flash('You do not have a reporting manager assigned. Please contact HR.', 'info')
            return render_template('team/team_list.html', team_members=[], is_manager_view=False)
        
        # Get all employees with the same manager (excluding self)
        team_members = Employee.query.filter(
            and_(
                Employee.manager_id == manager_id,
                Employee.id != current_employee.id,
                Employee.is_active == True
            )
        ).order_by(Employee.first_name, Employee.last_name).all()
        
        # Get manager info for display
        manager = Employee.query.get(manager_id)
        
        return render_template('team/team_list.html', 
                             team_members=team_members,
                             manager=manager,
                             current_employee=current_employee,
                             is_manager_view=False)


@app.route('/team/member/<int:member_id>')
@require_login
def get_team_member_profile(member_id):
    """Get team member profile details (JSON response for modal)"""
    # Check if current user has employee profile
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        return jsonify({'error': 'Employee profile not found'}), 403
    
    current_employee = current_user.employee_profile
    
    # Get the team member
    member = Employee.query.get(member_id)
    if not member:
        return jsonify({'error': 'Team member not found'}), 404
    
    # Verify user has access to view this member (must be in their team)
    user_role_name = current_user.role.name if current_user.role else None
    is_manager = user_role_name == 'Manager' or current_employee.is_manager
    
    # Check if member is direct report or peer
    if is_manager:
        # Manager can see direct reports
        if member.manager_id != current_employee.id:
            return jsonify({'error': 'Access denied. Member is not in your team'}), 403
    else:
        # Non-manager can see peers with same manager
        if member.manager_id != current_employee.manager_id or member.id == current_employee.id:
            return jsonify({'error': 'Access denied. Member is not in your team'}), 403
    
    # Build member profile response
    profile_data = {
        'id': member.id,
        'first_name': member.first_name,
        'last_name': member.last_name,
        'employee_id': member.employee_id,
        'email': member.email,
        'phone': member.phone,
        'designation': member.designation.name if member.designation else 'Not Assigned',
        'department': member.department or '-',
        'location': member.location or '-',
        'employment_type': member.employment_type or '-',
        'hire_date': member.hire_date.strftime('%d %B %Y') if member.hire_date else '-',
        'gender': member.gender or '-',
        'date_of_birth': member.date_of_birth.strftime('%d %B %Y') if member.date_of_birth else '-',
        'address': member.address or '-',
        'nationality': member.nationality or '-',
        'phone_display': member.phone or 'Not provided',
        'email_display': member.email or 'Not provided',
        'photo_url': f"static/uploads/photos/{member.profile_image_path}" if member.profile_image_path else None,
        'manager_name': f"{member.manager.first_name} {member.manager.last_name}" if member.manager else 'No Manager',
        'is_active': member.is_active
    }
    
    return jsonify(profile_data)


# =====================================================
# DOCUMENTS MODULE - Employee documents management
# =====================================================

@app.route('/documents')
@require_login
def documents_list():
    """
    Display employee documents (Offer Letter, Appraisal Letter, Salary Slips)
    Only visible to users with 'User' role
    """
    # Check if current user has employee profile
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        flash('Employee profile not found. Please contact HR.', 'warning')
        return redirect(url_for('dashboard'))
    
    current_employee = current_user.employee_profile
    
    # Get all documents for the current employee
    documents = EmployeeDocument.query.filter_by(
        employee_id=current_employee.id
    ).order_by(
        # Sort by year and month for salary slips, then by issue date for all
        db.case(
            (EmployeeDocument.document_type == 'Salary Slip', EmployeeDocument.year),
            else_=None
        ).desc(),
        db.case(
            (EmployeeDocument.document_type == 'Salary Slip', EmployeeDocument.month),
            else_=None
        ).desc(),
        EmployeeDocument.issue_date.desc()
    ).all()

    return render_template('documents/documents_tiles.html',
                         documents=documents,
                         current_employee=current_employee)


@app.route('/documents/download/<int:document_id>')
@require_login
def document_download(document_id):
    """Download a document"""
    from core.models import Payroll
    
    document = EmployeeDocument.query.get_or_404(document_id)
    
    # Security check: ensure user can only download their own documents
    # or if they are admin/HR
    user_role_name = current_user.role.name if current_user.role else None
    is_admin = user_role_name in ['Super Admin', 'Admin', 'HR Manager']
    
    if not is_admin:
        if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
            flash('Access denied.', 'danger')
            return redirect(url_for('dashboard'))
        
        if document.employee_id != current_user.employee_profile.id:
            flash('You can only download your own documents.', 'danger')
            return redirect(url_for('documents_list'))
    
    # Handle Salary Slip documents - redirect to payroll view
    if document.document_type == 'Salary Slip' and document.month and document.year:
        # Find the corresponding payroll record
        payroll = Payroll.query.filter_by(
            employee_id=document.employee_id
        ).filter(
            extract('month', Payroll.pay_period_end) == document.month,
            extract('year', Payroll.pay_period_end) == document.year
        ).first()
        
        if payroll:
            return redirect(url_for('payroll_payslip', payroll_id=payroll.id))
        else:
            flash('Payroll record not found for this salary slip.', 'danger')
            return redirect(url_for('documents_list'))
    
    # Handle other document types - serve from file system
    file_path = os.path.join(app.root_path, 'static', document.file_path)
    
    if not os.path.exists(file_path):
        flash('Document file not found.', 'danger')
        return redirect(url_for('documents_list'))
    
    # Get original filename
    filename = os.path.basename(document.file_path)
    
    return send_file(file_path, as_attachment=True, download_name=filename)


# =====================================================
# ADMIN ROUTES - Document Management (HR/Admin only)
# =====================================================

@app.route('/admin/documents/upload', methods=['GET', 'POST'])
@require_login
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def admin_document_upload():
    """Upload documents for employees (HR/Admin only)"""
    if request.method == 'POST':
        employee_id = request.form.get('employee_id', type=int)
        document_type = request.form.get('document_type')
        issue_date = request.form.get('issue_date')
        month = request.form.get('month', type=int) if request.form.get('month') else None
        year = request.form.get('year', type=int) if request.form.get('year') else None
        description = request.form.get('description', '')
        
        # Validate inputs
        if not employee_id or not document_type or not issue_date:
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('admin_document_upload'))
        
        employee = Employee.query.get(employee_id)
        if not employee:
            flash('Employee not found.', 'danger')
            return redirect(url_for('admin_document_upload'))
        
        # Handle file upload
        if 'document_file' not in request.files:
            flash('No file uploaded.', 'danger')
            return redirect(url_for('admin_document_upload'))
        
        file = request.files['document_file']
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('admin_document_upload'))
        
        # Validate file extension
        allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
        if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
            flash('Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG', 'danger')
            return redirect(url_for('admin_document_upload'))
        
        # Create upload directory if it doesn't exist
        upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'documents')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{employee.employee_id}_{document_type.replace(' ', '_')}_{timestamp}_{filename}"
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
        
        # Store relative path in database
        relative_path = os.path.join('uploads', 'documents', filename)
        
        # Create document record
        document = EmployeeDocument(
            employee_id=employee_id,
            document_type=document_type,
            file_path=relative_path,
            issue_date=datetime.strptime(issue_date, '%Y-%m-%d').date(),
            month=month,
            year=year,
            description=description,
            uploaded_by=current_user.id
        )
        
        db.session.add(document)
        db.session.commit()
        
        flash(f'Document uploaded successfully for {employee.first_name} {employee.last_name}.', 'success')
        return redirect(url_for('admin_document_upload'))
    
    # GET request - show upload form
    employees = Employee.query.filter_by(is_active=True).order_by(Employee.first_name, Employee.last_name).all()
    document_types = ['Offer Letter', 'Appraisal Letter', 'Salary Slip']
    
    return render_template('documents/admin_upload.html',
                         employees=employees,
                         document_types=document_types)


@app.route('/admin/documents/list')
@require_login
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def admin_documents_list():
    """List all employee documents (HR/Admin only)"""
    from core.models import Company
    from uuid import UUID
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    document_type = request.args.get('document_type', '', type=str)
    company_id = request.args.get('company_id', '', type=str)
    year = request.args.get('year', '', type=str)
    user_id = request.args.get('user_id', '', type=str)
    
    # Get accessible companies for the current user (for HR Managers)
    accessible_companies = current_user.get_accessible_companies()
    accessible_company_ids = [c.id for c in accessible_companies]
    
    # Build base query
    query = EmployeeDocument.query.join(Employee)
    
    # Filter by accessible companies - ALWAYS apply this for security
    if accessible_company_ids:
        query = query.filter(Employee.company_id.in_(accessible_company_ids))
    
    # Filter by search (employee name or ID)
    if search:
        query = query.filter(
            or_(
                Employee.first_name.ilike(f'%{search}%'),
                Employee.last_name.ilike(f'%{search}%'),
                Employee.employee_id.ilike(f'%{search}%')
            )
        )
    
    # Filter by document type
    if document_type:
        query = query.filter(EmployeeDocument.document_type == document_type)
    
    # Filter by company (only if explicitly selected and it's in accessible companies)
    if company_id:
        try:
            company_uuid = UUID(company_id) if isinstance(company_id, str) else company_id
            query = query.filter(Employee.company_id == company_uuid)
        except (ValueError, TypeError):
            pass
    
    # Filter by year
    if year:
        try:
            year_int = int(year)
            query = query.filter(EmployeeDocument.year == year_int)
        except (ValueError, TypeError):
            pass
    
    # Filter by user/employee
    if user_id:
        try:
            user_id_int = int(user_id)
            query = query.filter(Employee.id == user_id_int)
        except (ValueError, TypeError):
            pass
    
    documents = query.order_by(EmployeeDocument.issue_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get available options for filters
    document_types = ['Offer Letter', 'Appraisal Letter', 'Salary Slip', 'ID Card', 'Contract', 'Other']
    
    # Get unique years from documents for accessible companies (sorted descending)
    years_query = db.session.query(EmployeeDocument.year.distinct()).join(Employee).filter(
        EmployeeDocument.year.isnot(None),
        Employee.company_id.in_(accessible_company_ids)
    ).order_by(EmployeeDocument.year.desc()).all()
    available_years = sorted([y[0] for y in years_query if y[0]], reverse=True)
    
    # Get employees from accessible companies (for user filter)
    employees_query = Employee.query.filter(
        Employee.company_id.in_(accessible_company_ids),
        Employee.is_active == True
    ).order_by(Employee.first_name, Employee.last_name).all()
    
    return render_template('documents/admin_list.html',
                         documents=documents,
                         document_types=document_types,
                         search=search,
                         selected_document_type=document_type,
                         accessible_companies=accessible_companies,
                         selected_company_id=company_id,
                         available_years=available_years,
                         selected_year=year,
                         employees=employees_query,
                         selected_user_id=user_id)


@app.route('/admin/documents/delete/<int:document_id>', methods=['POST'])
@require_login
@require_role(['Super Admin', 'Admin', 'HR Manager'])
def admin_document_delete(document_id):
    """Delete a document (HR/Admin only)"""
    document = EmployeeDocument.query.get_or_404(document_id)
    
    # Delete file from filesystem
    file_path = os.path.join(app.root_path, 'static', document.file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            app.logger.error(f"Error deleting file {file_path}: {e}")
    
    # Delete database record
    db.session.delete(document)
    db.session.commit()
    
    flash('Document deleted successfully.', 'success')
    return redirect(url_for('admin_documents_list'))
