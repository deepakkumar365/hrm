from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user
from app import app, db
from core.auth import require_role
from core.models import Designation

@app.route('/admin/designations')
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def designation_list():
    """List all designations"""
    designations = Designation.query.filter_by(is_active=True).order_by(Designation.name).all()
    return render_template('designations/list.html', designations=designations)

@app.route('/admin/designations/add', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def designation_add():
    """Add a new designation"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Designation name is required.', 'error')
        elif Designation.query.filter(Designation.name.ilike(name)).first():
            flash('Designation with this name already exists.', 'error')
        else:
            try:
                new_designation = Designation(name=name, created_by=current_user.username)
                db.session.add(new_designation)
                db.session.commit()
                flash('Designation added successfully.', 'success')
                return redirect(url_for('designation_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding designation: {str(e)}', 'error')

    return render_template('designations/form.html', action='Add')

@app.route('/admin/designations/edit/<int:designation_id>', methods=['GET', 'POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def designation_edit(designation_id):
    """Edit a designation"""
    designation = Designation.query.get_or_404(designation_id)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Designation name is required.', 'error')
        elif designation.name != name and Designation.query.filter(Designation.name.ilike(name)).first():
            flash('Designation with this name already exists.', 'error')
        else:
            try:
                designation.name = name
                designation.modified_by = current_user.username
                db.session.commit()
                flash('Designation updated successfully.', 'success')
                return redirect(url_for('designation_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating designation: {str(e)}', 'error')

    return render_template('designations/form.html', designation=designation, action='Edit')

@app.route('/admin/designations/delete/<int:designation_id>', methods=['POST'])
@require_role(['Super Admin', 'Tenant Admin', 'HR Manager'])
def designation_delete(designation_id):
    """Soft delete a designation"""
    designation = Designation.query.get_or_404(designation_id)
    try:
        designation.is_active = False
        designation.modified_by = current_user.username
        db.session.commit()
        flash('Designation deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting designation: {str(e)}', 'error')

    return redirect(url_for('designation_list'))

