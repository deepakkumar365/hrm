"""
Flask Routes for Tenant and Company Management
Multi-tenant hierarchy CRUD operations
"""

from flask import jsonify, request, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlalchemy import func
from app import app, db
from models import Tenant, Company, Employee
from auth import require_role
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_current_user_email():
    """Get current user's email for audit fields"""
    if current_user and current_user.is_authenticated:
        return current_user.email
    return 'system'


# =====================================================
# TENANT ROUTES - UI
# =====================================================

@app.route('/tenants')
@require_role(['Super Admin', 'Admin', 'Manager'])
def tenant_list():
    """Display tenant list page with optimized queries"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        
        # Subquery to count companies per tenant (prevents N+1 queries)
        company_count_subquery = (
            db.session.query(
                Company.tenant_id,
                func.count(Company.id).label('company_count')
            )
            .group_by(Company.tenant_id)
            .subquery()
        )
        
        # Main query with eager loading
        query = db.session.query(
            Tenant,
            func.coalesce(company_count_subquery.c.company_count, 0).label('company_count')
        ).outerjoin(
            company_count_subquery,
            Tenant.id == company_count_subquery.c.tenant_id
        )
        
        if search:
            query = query.filter(
                db.or_(
                    Tenant.name.ilike(f'%{search}%'),
                    Tenant.code.ilike(f'%{search}%')
                )
            )
        
        # Execute query and get results
        results = query.order_by(Tenant.created_at.desc()).all()
        
        # Create list of tuples (tenant, company_count)
        tenants_with_counts = [(tenant, count) for tenant, count in results]
        
        return render_template('masters/tenants.html', 
                             tenants_with_counts=tenants_with_counts,
                             search=search)
    except Exception as e:
        logger.error(f"Error displaying tenant list: {str(e)}")
        flash(f'Error loading tenants: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


# =====================================================
# TENANT ROUTES - API
# =====================================================

@app.route('/api/tenants', methods=['GET'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def list_tenants():
    """List all tenants"""
    try:
        tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [tenant.to_dict() for tenant in tenants],
            'count': len(tenants)
        }), 200
    except Exception as e:
        logger.error(f"Error listing tenants: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tenants/<uuid:tenant_id>', methods=['GET'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def get_tenant(tenant_id):
    """Get a specific tenant by ID"""
    try:
        tenant = Tenant.query.get_or_404(tenant_id)
        return jsonify({
            'success': True,
            'data': tenant.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting tenant {tenant_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404


@app.route('/api/tenants', methods=['POST'])
@require_role(['Super Admin', 'Admin'])
def create_tenant():
    """Create a new tenant"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name') or not data.get('code'):
            return jsonify({
                'success': False,
                'error': 'Name and code are required'
            }), 400
        
        # Create new tenant
        tenant = Tenant(
            name=data['name'],
            code=data['code'].upper(),
            description=data.get('description'),
            is_active=data.get('is_active', True),
            created_by=get_current_user_email()
        )
        
        db.session.add(tenant)
        db.session.commit()
        
        logger.info(f"Tenant created: {tenant.name} by {get_current_user_email()}")
        
        return jsonify({
            'success': True,
            'message': 'Tenant created successfully',
            'data': tenant.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error creating tenant: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Tenant with this name or code already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating tenant: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tenants/<uuid:tenant_id>', methods=['PUT'])
@require_role(['Super Admin', 'Admin'])
def update_tenant(tenant_id):
    """Update an existing tenant"""
    try:
        tenant = Tenant.query.get_or_404(tenant_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            tenant.name = data['name']
        if 'code' in data:
            tenant.code = data['code'].upper()
        if 'description' in data:
            tenant.description = data['description']
        if 'is_active' in data:
            tenant.is_active = data['is_active']
        
        tenant.modified_by = get_current_user_email()
        tenant.modified_at = datetime.now()
        
        db.session.commit()
        
        logger.info(f"Tenant updated: {tenant.name} by {get_current_user_email()}")
        
        return jsonify({
            'success': True,
            'message': 'Tenant updated successfully',
            'data': tenant.to_dict()
        }), 200
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error updating tenant: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Tenant with this name or code already exists'
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating tenant: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/tenants/<uuid:tenant_id>', methods=['DELETE'])
@require_role(['Super Admin', 'Admin'])
def delete_tenant(tenant_id):
    """Delete a tenant (cascades to companies and employees)"""
    try:
        tenant = Tenant.query.get_or_404(tenant_id)
        tenant_name = tenant.name
        
        # Check if tenant has companies
        company_count = Company.query.filter_by(tenant_id=tenant_id).count()
        
        db.session.delete(tenant)
        db.session.commit()
        
        logger.warning(f"Tenant deleted: {tenant_name} (had {company_count} companies) by {get_current_user_email()}")
        
        return jsonify({
            'success': True,
            'message': f'Tenant deleted successfully (cascaded to {company_count} companies)'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting tenant: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# COMPANY ROUTES - UI
# =====================================================

@app.route('/companies')
@require_role(['Super Admin', 'Admin', 'Manager'])
def company_list():
    """Display company list page with optimized queries"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '', type=str)
        tenant_id = request.args.get('tenant_id', '', type=str)
        
        # Subquery to count employees per company (prevents N+1 queries)
        employee_count_subquery = (
            db.session.query(
                Employee.company_id,
                func.count(Employee.id).label('employee_count')
            )
            .group_by(Employee.company_id)
            .subquery()
        )
        
        # Main query with eager loading of tenant relationship
        query = db.session.query(
            Company,
            func.coalesce(employee_count_subquery.c.employee_count, 0).label('employee_count')
        ).outerjoin(
            employee_count_subquery,
            Company.id == employee_count_subquery.c.company_id
        ).options(
            selectinload(Company.tenant)  # Eager load tenant to avoid N+1
        )
        
        if search:
            query = query.filter(
                db.or_(
                    Company.name.ilike(f'%{search}%'),
                    Company.code.ilike(f'%{search}%'),
                    Company.uen.ilike(f'%{search}%')
                )
            )
        
        if tenant_id:
            query = query.filter(Company.tenant_id == tenant_id)
        
        # Execute query and get results
        results = query.order_by(Company.created_at.desc()).all()
        
        # Create list of tuples (company, employee_count)
        companies_with_counts = [(company, count) for company, count in results]
        
        # Get all tenants for filter dropdown and modal
        tenants = Tenant.query.filter_by(is_active=True).order_by(Tenant.name).all()
        
        return render_template('masters/companies.html', 
                             companies_with_counts=companies_with_counts,
                             tenants=tenants,
                             search=search,
                             selected_tenant_id=tenant_id)
    except Exception as e:
        logger.error(f"Error displaying company list: {str(e)}")
        flash(f'Error loading companies: {str(e)}', 'error')
        return redirect(url_for('dashboard'))


# =====================================================
# COMPANY ROUTES - API
# =====================================================

@app.route('/api/companies', methods=['GET'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def list_companies():
    """List all companies (optionally filter by tenant)"""
    try:
        tenant_id = request.args.get('tenant_id')
        
        query = Company.query
        if tenant_id:
            query = query.filter_by(tenant_id=tenant_id)
        
        companies = query.order_by(Company.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [company.to_dict() for company in companies],
            'count': len(companies)
        }), 200
    except Exception as e:
        logger.error(f"Error listing companies: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/companies/<uuid:company_id>', methods=['GET'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def get_company(company_id):
    """Get a specific company by ID"""
    try:
        company = Company.query.get_or_404(company_id)
        return jsonify({
            'success': True,
            'data': company.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error getting company {company_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404


@app.route('/api/companies', methods=['POST'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def create_company():
    """Create a new company"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('tenant_id') or not data.get('name') or not data.get('code'):
            return jsonify({
                'success': False,
                'error': 'Tenant ID, name, and code are required'
            }), 400
        
        # Verify tenant exists
        tenant = Tenant.query.get(data['tenant_id'])
        if not tenant:
            return jsonify({
                'success': False,
                'error': 'Tenant not found'
            }), 404
        
        # Create new company
        company = Company(
            tenant_id=data['tenant_id'],
            name=data['name'],
            code=data['code'].upper(),
            description=data.get('description'),
            address=data.get('address'),
            uen=data.get('uen'),
            registration_number=data.get('registration_number'),
            tax_id=data.get('tax_id'),
            phone=data.get('phone'),
            email=data.get('email'),
            website=data.get('website'),
            logo_path=data.get('logo_path'),
            is_active=data.get('is_active', True),
            created_by=get_current_user_email()
        )
        
        db.session.add(company)
        db.session.commit()
        
        logger.info(f"Company created: {company.name} under tenant {tenant.name} by {get_current_user_email()}")
        
        return jsonify({
            'success': True,
            'message': 'Company created successfully',
            'data': company.to_dict()
        }), 201
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error creating company: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Company with this code already exists for this tenant'
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating company: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/companies/<uuid:company_id>', methods=['PUT'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def update_company(company_id):
    """Update an existing company"""
    try:
        company = Company.query.get_or_404(company_id)
        data = request.get_json()
        
        # Update fields
        updatable_fields = [
            'name', 'code', 'description', 'address', 'uen',
            'registration_number', 'tax_id', 'phone', 'email',
            'website', 'logo_path', 'is_active'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'code':
                    setattr(company, field, data[field].upper())
                else:
                    setattr(company, field, data[field])
        
        company.modified_by = get_current_user_email()
        company.modified_at = datetime.now()
        
        db.session.commit()
        
        logger.info(f"Company updated: {company.name} by {get_current_user_email()}")
        
        return jsonify({
            'success': True,
            'message': 'Company updated successfully',
            'data': company.to_dict()
        }), 200
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Integrity error updating company: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Company with this code already exists for this tenant'
        }), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating company: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/companies/<uuid:company_id>', methods=['DELETE'])
@require_role(['Super Admin', 'Admin'])
def delete_company(company_id):
    """Delete a company (cascades to employees)"""
    try:
        company = Company.query.get_or_404(company_id)
        company_name = company.name
        
        # Check if company has employees
        employee_count = Employee.query.filter_by(company_id=company_id).count()
        
        db.session.delete(company)
        db.session.commit()
        
        logger.warning(f"Company deleted: {company_name} (had {employee_count} employees) by {get_current_user_email()}")
        
        return jsonify({
            'success': True,
            'message': f'Company deleted successfully (cascaded to {employee_count} employees)'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting company: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# EMPLOYEE-COMPANY LINKING ROUTES
# =====================================================

@app.route('/api/employees/<int:employee_id>/link-company', methods=['PUT'])
@require_role(['Super Admin', 'Admin', 'Manager'])
def link_employee_to_company(employee_id):
    """Link an employee to a company"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        company_id = data.get('company_id')
        if not company_id:
            return jsonify({
                'success': False,
                'error': 'Company ID is required'
            }), 400
        
        # Verify company exists
        company = Company.query.get(company_id)
        if not company:
            return jsonify({
                'success': False,
                'error': 'Company not found'
            }), 404
        
        employee.company_id = company_id
        employee.modified_by = get_current_user_email()
        
        db.session.commit()
        
        logger.info(f"Employee {employee.employee_id} linked to company {company.name} by {get_current_user_email()}")
        
        return jsonify({
            'success': True,
            'message': f'Employee linked to {company.name} successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error linking employee to company: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/companies/<uuid:company_id>/employees', methods=['GET'])
@require_role(['Super Admin', 'Admin', 'Manager', 'User'])
def get_company_employees(company_id):
    """Get all employees for a specific company"""
    try:
        company = Company.query.get_or_404(company_id)
        employees = Employee.query.filter_by(company_id=company_id, is_active=True).all()
        
        employee_list = [{
            'id': emp.id,
            'employee_id': emp.employee_id,
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'email': emp.email,
            'position': emp.position,
            'department': emp.department,
            'hire_date': emp.hire_date.isoformat() if emp.hire_date else None,
        } for emp in employees]
        
        return jsonify({
            'success': True,
            'company': company.to_dict(),
            'employees': employee_list,
            'count': len(employee_list)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting company employees: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================================
# WEB UI ROUTES (Optional - for HTML pages)
# =====================================================

@app.route('/tenants')
@require_role(['Super Admin', 'Admin', 'Manager'])
def tenants_page():
    """Render tenants management page"""
    tenants = Tenant.query.order_by(Tenant.created_at.desc()).all()
    return render_template('masters/tenants.html', tenants=tenants)


@app.route('/companies')
@require_role(['Super Admin', 'Admin', 'Manager'])
def companies_page():
    """Render companies management page"""
    companies = Company.query.order_by(Company.created_at.desc()).all()
    tenants = Tenant.query.filter_by(is_active=True).all()
    return render_template('masters/companies.html', companies=companies, tenants=tenants)