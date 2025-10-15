"""
Routes for Team and Documents modules
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import current_user
from sqlalchemy import and_, or_
from datetime import datetime
import os
from werkzeug.utils import secure_filename

from app import app, db
from auth import require_login, require_role
from models import Employee, EmployeeDocument, User, Organization
from utils import format_date


# =====================================================
# TEAM MODULE - Show peers with same manager
# =====================================================

@app.route('/team')
@require_login
def team_list():
    """
    Display team members based on user role:
    - User role: Shows peers (employees with the same manager)
    - Manager role: Shows direct reports (employees who report to this manager)
    """
    # Check if current user has employee profile
    if not hasattr(current_user, 'employee_profile') or not current_user.employee_profile:
        flash('Employee profile not found. Please contact HR.', 'warning')
        return redirect(url_for('dashboard'))
    
    current_employee = current_user.employee_profile
    user_role_name = current_user.role.name if current_user.role else None
    
    # For Manager role: Show direct reports
    if user_role_name == 'Manager':
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
    ).order_by(EmployeeDocument.issue_date.desc()).all()
    
    # Separate documents by type
    offer_letters = [doc for doc in documents if doc.document_type == 'Offer Letter']
    appraisal_letters = [doc for doc in documents if doc.document_type == 'Appraisal Letter']
    salary_slips = [doc for doc in documents if doc.document_type == 'Salary Slip']
    
    # Sort salary slips by year and month (most recent first)
    salary_slips.sort(key=lambda x: (x.year or 0, x.month or 0), reverse=True)
    
    return render_template('documents/documents_list.html',
                         offer_letters=offer_letters,
                         appraisal_letters=appraisal_letters,
                         salary_slips=salary_slips,
                         current_employee=current_employee)


@app.route('/documents/download/<int:document_id>')
@require_login
def document_download(document_id):
    """Download a document"""
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
    
    # Build file path
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
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    document_type = request.args.get('document_type', '', type=str)
    
    query = EmployeeDocument.query.join(Employee)
    
    if search:
        query = query.filter(
            or_(
                Employee.first_name.ilike(f'%{search}%'),
                Employee.last_name.ilike(f'%{search}%'),
                Employee.employee_id.ilike(f'%{search}%')
            )
        )
    
    if document_type:
        query = query.filter(EmployeeDocument.document_type == document_type)
    
    documents = query.order_by(EmployeeDocument.issue_date.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    document_types = ['Offer Letter', 'Appraisal Letter', 'Salary Slip']
    
    return render_template('documents/admin_list.html',
                         documents=documents,
                         document_types=document_types,
                         search=search,
                         selected_document_type=document_type)


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