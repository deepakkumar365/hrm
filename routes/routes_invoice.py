"""
Routes for Invoice Management
Handles invoice creation and management by Super Admin and viewing by Tenant Admin / HR Manager
"""
from flask import render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app import app, db
from core.models import Tenant, Invoice, InvoiceItem, User
from datetime import datetime
from functools import wraps
import uuid

def require_login(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(roles):
    """Decorator to check user role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in first', 'warning')
                return redirect(url_for('login'))
            
            user_role = current_user.role.name if current_user.role else None
            if user_role not in roles:
                flash('You do not have permission to access this operation!', 'error')
                return redirect(request.referrer or url_for('dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==================== SUPER ADMIN INVOICE ROUTES ====================

@app.route('/admin/invoices', methods=['GET'])
@require_login
@require_role(['Super Admin'])
def admin_invoices():
    """List all invoices across all tenants (Super Admin only)"""
    try:
        invoices = dict() # We'll group by tenant or just pass a flat list
        invoices_list = Invoice.query.order_by(Invoice.created_at.desc()).all()
        tenants = Tenant.query.all()
        
        return render_template('admin/invoices.html', invoices=invoices_list, tenants=tenants)
    except Exception as e:
        flash(f'Error loading invoices: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/admin/invoices/generate-number', methods=['GET'])
@require_login
@require_role(['Super Admin'])
def admin_invoice_generate_number():
    """Generate an auto-incrementing invoice number based on date"""
    try:
        tenant_id = request.args.get('tenant_id')
        if not tenant_id:
            return jsonify({'success': False, 'message': 'Tenant ID required'}), 400
            
        tenant = Tenant.query.filter_by(id=tenant_id).first()
        if not tenant:
            return jsonify({'success': False, 'message': 'Invalid Tenant'}), 404
            
        # Format: INV-{TenantCode}-{YYYYMMDD}-{Sequence}
        # Example: INV-NEX-20231025-001
        
        date_str = datetime.now().strftime('%Y%m%d')
        prefix = f"INV-{tenant.code}-{date_str}-"
        
        # Find the latest invoice for this tenant with this prefix
        latest_invoice = Invoice.query.filter(
            Invoice.invoice_number.like(f"{prefix}%")
        ).order_by(Invoice.invoice_number.desc()).first()
        
        sequence = 1
        if latest_invoice:
            try:
                # Extract the sequence number part and increment
                last_seq_str = latest_invoice.invoice_number.split('-')[-1]
                sequence = int(last_seq_str) + 1
            except (ValueError, IndexError):
                pass
                
        new_invoice_number = f"{prefix}{sequence:03d}"
        
        return jsonify({
            'success': True, 
            'invoice_number': new_invoice_number
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error generating number: {str(e)}'}), 500


@app.route('/admin/invoices/create', methods=['POST'])
@require_login
@require_role(['Super Admin'])
def admin_invoice_create():
    """Create a new invoice with line items"""
    try:
        # Check if content type is JSON
        if request.is_json:
            data = request.get_json()
            tenant_id = data.get('tenant_id')
            invoice_number = data.get('invoice_number')
            amount = data.get('amount')
            issue_date_str = data.get('issue_date')
            due_date_str = data.get('due_date')
            billing_address = data.get('billing_address')
            subtotal = data.get('subtotal')
            tax_rate = data.get('tax_rate')
            tax_amount = data.get('tax_amount')
            discount_amount = data.get('discount_amount')
            status = data.get('status', 'Pending')
            notes_terms = data.get('notes_terms')
            items_data = data.get('items', [])
        else:
            # Fallback for old FormData submissions (basic)
            tenant_id = request.form.get('tenant_id')
            invoice_number = request.form.get('invoice_number')
            amount = request.form.get('amount')
            issue_date_str = request.form.get('issue_date')
            due_date_str = request.form.get('due_date')
            status = request.form.get('status', 'Pending')
            billing_address = None
            subtotal = amount
            tax_rate = 0
            tax_amount = 0
            discount_amount = 0
            notes_terms = None
            items_data = []

        if not all([tenant_id, invoice_number, amount, issue_date_str, due_date_str]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
            
        issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        
        # Check if invoice_number already exists
        existing = Invoice.query.filter_by(invoice_number=invoice_number).first()
        if existing:
            return jsonify({'success': False, 'message': f'Invoice with number {invoice_number} already exists'}), 400

        invoice = Invoice(
            tenant_id=tenant_id,
            invoice_number=invoice_number,
            amount=amount,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            billing_address=billing_address,
            notes_terms=notes_terms,
            issue_date=issue_date,
            due_date=due_date,
            status=status,
            created_by=current_user.id
        )
        
        db.session.add(invoice)
        db.session.flush() # Get invoice ID
        
        # Add line items
        for item in items_data:
            new_item = InvoiceItem(
                invoice_id=invoice.id,
                description=item.get('description'),
                quantity=item.get('quantity', 1),
                unit_price=item.get('unit_price', 0),
                amount=item.get('amount', 0)
            )
            db.session.add(new_item)
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Invoice created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error creating invoice: {str(e)}'}), 500


@app.route('/admin/invoices/edit/<int:id>', methods=['POST'])
@require_login
@require_role(['Super Admin'])
def admin_invoice_edit(id):
    """Edit an existing invoice"""
    try:
        invoice = Invoice.query.get_or_404(id)
        
        invoice.tenant_id = request.form.get('tenant_id', invoice.tenant_id)
        invoice.invoice_number = request.form.get('invoice_number', invoice.invoice_number)
        invoice.amount = request.form.get('amount', invoice.amount)
        
        issue_date_str = request.form.get('issue_date')
        if issue_date_str:
            invoice.issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
            
        due_date_str = request.form.get('due_date')
        if due_date_str:
            invoice.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
            
        invoice.status = request.form.get('status', invoice.status)
        invoice.description = request.form.get('description', invoice.description)
        invoice.updated_at = datetime.utcnow()
        
        # Check if the new invoice_number conflicts with another existing invoice
        existing = Invoice.query.filter(Invoice.invoice_number == invoice.invoice_number, Invoice.id != id).first()
        if existing:
            return jsonify({'success': False, 'message': f'Invoice with number {invoice.invoice_number} already exists'}), 400
            
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Invoice updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error updating invoice: {str(e)}'}), 500


@app.route('/admin/invoices/delete/<int:id>', methods=['POST'])
@require_login
@require_role(['Super Admin'])
def admin_invoice_delete(id):
    """Delete an invoice"""
    try:
        invoice = Invoice.query.get_or_404(id)
        db.session.delete(invoice)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Invoice deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting invoice: {str(e)}'}), 500


@app.route('/invoices/view/<int:id>', methods=['GET'])
@require_login
def invoice_view(id):
    """View a professional structured invoice"""
    try:
        invoice = Invoice.query.get_or_404(id)
        
        # Check permissions: Super Admin or current tenant match
        if current_user.role != 'Super Admin' and (not current_user.tenant or current_user.tenant.id != invoice.tenant_id):
            flash('You do not have permission to view this invoice', 'error')
            return redirect(url_for('dashboard'))
            
        return render_template('admin/invoice_template.html', invoice=invoice, tenant=invoice.tenant)
    except Exception as e:
        flash(f'Error loading invoice: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


# ==================== TENANT ADMIN / HR MANAGER INVOICE ROUTES ====================

@app.route('/tenant/invoices', methods=['GET'])
@require_login
@require_role(['Tenant Admin', 'HR Manager'])
def tenant_invoices():
    """View invoices for the current tenant"""
    try:
        # Get tenant from current user's organization
        if not current_user.tenant:
            flash('No tenant associated with your account', 'error')
            return redirect(url_for('dashboard'))
            
        tenant_id = current_user.tenant.id
        invoices = Invoice.query.filter_by(tenant_id=tenant_id).order_by(Invoice.created_at.desc()).all()
        
        return render_template('tenant/invoices.html', invoices=invoices, tenant=current_user.tenant)
    except Exception as e:
        flash(f'Error loading invoices: {str(e)}', 'error')
        return redirect(url_for('dashboard'))
