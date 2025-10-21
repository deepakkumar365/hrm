from datetime import datetime, date, time
from uuid import uuid4

from app import db
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint, Index
from sqlalchemy.orm import validates
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model, UserMixin):
    __tablename__ = 'hrm_users'
    __table_args__ = (
        Index('ix_hrm_users_role_id', 'role_id'),
        Index('ix_hrm_users_organization_id', 'organization_id'),
        Index('ix_hrm_users_reporting_manager_id', 'reporting_manager_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    must_reset_password = db.Column(db.Boolean, default=True, nullable=False)

    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    reporting_manager_id = db.Column(db.Integer, db.ForeignKey('hrm_users.id', ondelete='SET NULL'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    organization = db.relationship('Organization', back_populates='users')
    role = db.relationship('Role', back_populates='users')
    reporting_manager = db.relationship('User', remote_side=[id], backref=db.backref('direct_reports', lazy='dynamic'))
    employee_profile = db.relationship('Employee', back_populates='user', uselist=False)

    def set_password(self, password):
        # Use Werkzeug's password hashing utilities for secure storage
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def role_name(self):
        return self.role.name if self.role else None


class Tenant(db.Model):
    """Top-level tenant entity for multi-tenant HRMS"""
    __tablename__ = 'hrm_tenant'
    __table_args__ = (
        Index('idx_hrm_tenant_code', 'code'),
        Index('idx_hrm_tenant_is_active', 'is_active'),
        Index('idx_hrm_tenant_created_at', 'created_at'),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = db.Column(db.String(255), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    country_code = db.Column(db.String(10), nullable=True)
    currency_code = db.Column(db.String(10), nullable=True)

    created_by = db.Column(db.String(100), nullable=False, default='system')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified_by = db.Column(db.String(100))
    modified_at = db.Column(db.DateTime)

    companies = db.relationship('Company', back_populates='tenant', cascade='all, delete-orphan')
    organizations = db.relationship('Organization', back_populates='tenant')
    payment_configs = db.relationship('TenantPaymentConfig', back_populates='tenant', cascade='all, delete-orphan')
    documents = db.relationship('TenantDocument', back_populates='tenant', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Tenant {self.name} ({self.code})>'

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'is_active': self.is_active,
            'country_code': self.country_code,
            'currency_code': self.currency_code,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_by': self.modified_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
        }


class Company(db.Model):
    """Company entities belonging to a tenant"""
    __tablename__ = 'hrm_company'
    __table_args__ = (
        Index('idx_hrm_company_tenant_id', 'tenant_id'),
        Index('idx_hrm_company_code', 'code'),
        Index('idx_hrm_company_is_active', 'is_active'),
        Index('idx_hrm_company_created_at', 'created_at'),
        UniqueConstraint('tenant_id', 'code', name='uq_company_tenant_code'),
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hrm_tenant.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    address = db.Column(db.Text)
    uen = db.Column(db.String(50))
    registration_number = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    logo_path = db.Column(db.String(255))

    is_active = db.Column(db.Boolean, default=True, nullable=False)

    created_by = db.Column(db.String(100), nullable=False, default='system')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified_by = db.Column(db.String(100))
    modified_at = db.Column(db.DateTime)

    tenant = db.relationship('Tenant', back_populates='companies')
    employees = db.relationship('Employee', back_populates='company')

    def __repr__(self):
        return f'<Company {self.name} ({self.code})>'

    def to_dict(self):
        return {
            'id': str(self.id),
            'tenant_id': str(self.tenant_id),
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'address': self.address,
            'uen': self.uen,
            'registration_number': self.registration_number,
            'tax_id': self.tax_id,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'logo_path': self.logo_path,
            'is_active': self.is_active,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_by': self.modified_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
        }


class TenantPaymentConfig(db.Model):
    """Tenant Payment Configuration for billing management"""
    __tablename__ = 'hrm_tenant_payment_config'
    __table_args__ = (
        Index('idx_hrm_tenant_payment_tenant_id', 'tenant_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hrm_tenant.id', ondelete='CASCADE'), nullable=False)

    payment_type = db.Column(db.String(20), nullable=False, default='Fixed')

    implementation_charges = db.Column(db.Numeric(10, 2), nullable=True, default=0)
    monthly_charges = db.Column(db.Numeric(10, 2), nullable=True, default=0)
    other_charges = db.Column(db.Numeric(10, 2), nullable=True, default=0)

    frequency = db.Column(db.String(20), nullable=False, default='Monthly')

    created_by = db.Column(db.String(100), nullable=False, default='system')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified_by = db.Column(db.String(100))
    modified_at = db.Column(db.DateTime)

    tenant = db.relationship('Tenant', back_populates='payment_configs')

    def __repr__(self):
        return f'<TenantPaymentConfig {self.tenant_id} - {self.payment_type}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': str(self.tenant_id),
            'payment_type': self.payment_type,
            'implementation_charges': float(self.implementation_charges) if self.implementation_charges else 0,
            'monthly_charges': float(self.monthly_charges) if self.monthly_charges else 0,
            'other_charges': float(self.other_charges) if self.other_charges else 0,
            'frequency': self.frequency,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'modified_by': self.modified_by,
            'modified_at': self.modified_at.isoformat() if self.modified_at else None,
        }


class TenantDocument(db.Model):
    """Tenant document attachments"""
    __tablename__ = 'hrm_tenant_documents'
    __table_args__ = (
        Index('idx_hrm_tenant_documents_tenant_id', 'tenant_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hrm_tenant.id', ondelete='CASCADE'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(50), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)

    uploaded_by = db.Column(db.String(100), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.now)

    tenant = db.relationship('Tenant', back_populates='documents')

    def __repr__(self):
        return f'<TenantDocument {self.file_name} for Tenant {self.tenant_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'tenant_id': str(self.tenant_id),
            'file_name': self.file_name,
            'file_path': self.file_path,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'uploaded_by': self.uploaded_by,
            'upload_date': self.upload_date.isoformat() if self.upload_date else None,
        }


class Employee(db.Model):
    __tablename__ = 'hrm_employee'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    father_name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    nric = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    nationality = db.Column(db.String(50))
    address = db.Column(db.Text)
    postal_code = db.Column(db.String(10))
    location = db.Column(db.String(100))
    profile_image_path = db.Column(db.String(255))
    timezone = db.Column(db.String(50), default='UTC')

    position = db.Column(db.String(100), nullable=False)
    designation_id = db.Column(db.Integer, db.ForeignKey('hrm_designation.id'), nullable=True)
    department = db.Column(db.String(100))
    hire_date = db.Column(db.Date, nullable=False)
    employment_type = db.Column(db.String(20))
    work_permit_type = db.Column(db.String(30))
    work_permit_number = db.Column(db.String(50))
    work_permit_expiry = db.Column(db.Date)

    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)
    allowances = db.Column(db.Numeric(10, 2), default=0)
    hourly_rate = db.Column(db.Numeric(8, 2))

    cpf_account = db.Column(db.String(20))
    employee_cpf_rate = db.Column(db.Numeric(5, 2), default=20.00)
    employer_cpf_rate = db.Column(db.Numeric(5, 2), default=17.00)

    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(30))
    account_holder_name = db.Column(db.String(100))
    swift_code = db.Column(db.String(11))
    ifsc_code = db.Column(db.String(11))

    is_active = db.Column(db.Boolean, default=True)
    termination_date = db.Column(db.Date)

    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id', ondelete='SET NULL'), nullable=True)

    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hrm_company.id', ondelete='CASCADE'), nullable=True)

    working_hours_id = db.Column(db.Integer, db.ForeignKey('hrm_working_hours.id'), nullable=True)
    work_schedule_id = db.Column(db.Integer, db.ForeignKey('hrm_work_schedules.id'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.String(100), default='system')
    modified_by = db.Column(db.String(100))

    user = db.relationship('User', back_populates='employee_profile')
    organization = db.relationship('Organization', back_populates='org_employees')
    company = db.relationship('Company', back_populates='employees')
    manager = db.relationship(
        'Employee',
        remote_side=[id],
        backref=db.backref('direct_reports', lazy='dynamic'),
        foreign_keys=[manager_id],
        post_update=True,
    )
    working_hours = db.relationship('WorkingHours', backref='employees')
    work_schedule = db.relationship('WorkSchedule', backref='employees')
    designation = db.relationship('Designation', backref='employees')
    leaves = db.relationship('Leave', back_populates='employee')
    claims = db.relationship('Claim', back_populates='employee')
    appraisals = db.relationship('Appraisal', back_populates='employee')
    documents = db.relationship('EmployeeDocument', back_populates='employee', cascade='all, delete-orphan')

    @validates('manager_id')
    def validate_manager(self, key, manager_id):
        if manager_id is None:
            return manager_id

        manager = Employee.query.get(manager_id)
        if manager is None:
            raise ValueError('Reporting manager must exist.')
        if manager.organization_id != self.organization_id:
            raise ValueError('Manager must belong to the same organization as the employee.')
        return manager_id


class EmployeeDocument(db.Model):
    """Employee documents like Offer Letter, Appraisal Letter, Salary Slip"""
    __tablename__ = 'hrm_employee_documents'
    __table_args__ = (
        Index('ix_hrm_employee_documents_employee_id', 'employee_id'),
        Index('ix_hrm_employee_documents_document_type', 'document_type'),
        Index('ix_hrm_employee_documents_year_month', 'year', 'month'),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id', ondelete='CASCADE'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    issue_date = db.Column(db.Date, nullable=False)
    month = db.Column(db.Integer, nullable=True)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)

    uploaded_by = db.Column(db.Integer, db.ForeignKey('hrm_users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    employee = db.relationship('Employee', back_populates='documents')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])

    def __repr__(self):
        return f'<EmployeeDocument {self.document_type} for Employee {self.employee_id}>'


class EmployeeBankInfo(db.Model):
    """Employee bank information for payroll processing"""
    __tablename__ = 'hrm_employee_bank_info'
    __table_args__ = (
        Index('ix_hrm_employee_bank_info_employee_id', 'employee_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id', ondelete='CASCADE'), nullable=False, unique=True)
    bank_account_name = db.Column(db.String(100), nullable=True)
    bank_account_number = db.Column(db.String(30), nullable=True)
    bank_code = db.Column(db.String(20), nullable=True)
    paynow_no = db.Column(db.String(20), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    employee = db.relationship('Employee', backref=db.backref('bank_info', uselist=False))

    def __repr__(self):
        return f'<EmployeeBankInfo for Employee {self.employee_id}>'


class PayrollConfiguration(db.Model):
    """Employee-specific payroll configuration for allowances and OT rates"""
    __tablename__ = 'hrm_payroll_configuration'
    __table_args__ = (
        Index('ix_hrm_payroll_config_employee_id', 'employee_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False, unique=True)

    allowance_1_name = db.Column(db.String(100), default='Transport Allowance')
    allowance_1_amount = db.Column(db.Numeric(10, 2), default=0)

    allowance_2_name = db.Column(db.String(100), default='Housing Allowance')
    allowance_2_amount = db.Column(db.Numeric(10, 2), default=0)

    allowance_3_name = db.Column(db.String(100), default='Meal Allowance')
    allowance_3_amount = db.Column(db.Numeric(10, 2), default=0)

    allowance_4_name = db.Column(db.String(100), default='Other Allowance')
    allowance_4_amount = db.Column(db.Numeric(10, 2), default=0)

    ot_rate_per_hour = db.Column(db.Numeric(8, 2), nullable=True)

    employer_cpf = db.Column(db.Numeric(10, 2), default=0)
    employee_cpf = db.Column(db.Numeric(10, 2), default=0)
    net_salary = db.Column(db.Numeric(10, 2), default=0)
    remarks = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)

    employee = db.relationship('Employee', backref=db.backref('payroll_config', uselist=False))
    updated_by_user = db.relationship('User')

    def get_total_allowances(self):
        return (self.allowance_1_amount or 0) + (self.allowance_2_amount or 0) + \
               (self.allowance_3_amount or 0) + (self.allowance_4_amount or 0)

    def get_effective_ot_rate(self):
        return self.ot_rate_per_hour or self.employee.hourly_rate or 0


class Payroll(db.Model):
    __tablename__ = 'hrm_payroll'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)

    basic_pay = db.Column(db.Numeric(10, 2), nullable=False)
    overtime_pay = db.Column(db.Numeric(10, 2), default=0)
    allowances = db.Column(db.Numeric(10, 2), default=0)
    bonuses = db.Column(db.Numeric(10, 2), default=0)
    gross_pay = db.Column(db.Numeric(10, 2), nullable=False)

    employee_cpf = db.Column(db.Numeric(10, 2), default=0)
    employer_cpf = db.Column(db.Numeric(10, 2), default=0)
    income_tax = db.Column(db.Numeric(10, 2), default=0)
    other_deductions = db.Column(db.Numeric(10, 2), default=0)

    net_pay = db.Column(db.Numeric(10, 2), nullable=False)

    days_worked = db.Column(db.Integer, default=0)
    overtime_hours = db.Column(db.Numeric(5, 2), default=0)
    leave_days = db.Column(db.Integer, default=0)

    status = db.Column(db.String(20), default='Draft')
    generated_by = db.Column(db.Integer, db.ForeignKey(User.id))
    generated_at = db.Column(db.DateTime, default=datetime.now)

    employee = db.relationship('Employee', backref='payrolls')
    generated_by_user = db.relationship('User')

class Attendance(db.Model):
    __tablename__ = 'hrm_attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    clock_in = db.Column(db.Time)
    clock_out = db.Column(db.Time)
    break_start = db.Column(db.Time)
    break_end = db.Column(db.Time)

    regular_hours = db.Column(db.Numeric(5, 2), default=0)
    overtime_hours = db.Column(db.Numeric(5, 2), default=0)
    total_hours = db.Column(db.Numeric(5, 2), default=0)

    has_overtime = db.Column(db.Boolean, default=False)
    overtime_approved = db.Column(db.Boolean, nullable=True)
    overtime_approved_by = db.Column(db.Integer, db.ForeignKey('hrm_users.id', ondelete='SET NULL'), nullable=True)
    overtime_approved_at = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(20), default='Present')
    remarks = db.Column(db.Text)

    location_lat = db.Column(db.String(20))
    location_lng = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    employee = db.relationship('Employee', backref='attendances')
    overtime_approver = db.relationship('User', foreign_keys=[overtime_approved_by])

    __table_args__ = (UniqueConstraint('employee_id', 'date'),)

class Leave(db.Model):
    __tablename__ = 'hrm_leave'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    leave_type = db.Column(db.String(30), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)

    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')

    requested_by = db.Column(db.Integer, db.ForeignKey(User.id))
    approved_by = db.Column(db.Integer, db.ForeignKey(User.id))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    employee = db.relationship('Employee', back_populates='leaves')
    requested_by_user = db.relationship('User', foreign_keys=[requested_by])
    approved_by_user = db.relationship('User', foreign_keys=[approved_by])

class Claim(db.Model):
    __tablename__ = 'hrm_claim'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    claim_type = db.Column(db.String(30), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    claim_date = db.Column(db.Date, nullable=False)

    description = db.Column(db.Text)
    receipt_number = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')

    submitted_by = db.Column(db.Integer, db.ForeignKey(User.id))
    approved_by = db.Column(db.Integer, db.ForeignKey(User.id))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    employee = db.relationship('Employee', back_populates='claims')
    submitted_by_user = db.relationship('User', foreign_keys=[submitted_by])
    approved_by_user = db.relationship('User', foreign_keys=[approved_by])

class Appraisal(db.Model):
    __tablename__ = 'hrm_appraisal'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)

    performance_rating = db.Column(db.Integer)
    goals_achievement = db.Column(db.Integer)
    teamwork_rating = db.Column(db.Integer)
    communication_rating = db.Column(db.Integer)
    overall_rating = db.Column(db.Numeric(3, 2))

    self_review = db.Column(db.Text)
    manager_feedback = db.Column(db.Text)
    development_goals = db.Column(db.Text)
    training_recommendations = db.Column(db.Text)

    status = db.Column(db.String(20), default='Draft')

    reviewed_by = db.Column(db.Integer, db.ForeignKey(User.id))
    completed_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    employee = db.relationship('Employee', back_populates='appraisals')
    reviewed_by_user = db.relationship('User')

class ComplianceReport(db.Model):
    __tablename__ = 'hrm_compliance_report'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(20), nullable=False)
    period_month = db.Column(db.Integer, nullable=False)
    period_year = db.Column(db.Integer, nullable=False)

    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Generated')

    total_employees = db.Column(db.Integer)
    total_amount = db.Column(db.Numeric(12, 2))

    generated_by = db.Column(db.Integer, db.ForeignKey(User.id))
    generated_at = db.Column(db.DateTime, default=datetime.now)
    submitted_at = db.Column(db.DateTime)

    generated_by_user = db.relationship('User')

    def __repr__(self):
        return f'<ComplianceReport {self.report_type} for {self.period_year}-{self.period_month:02d}>'


class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=True)
    uen = db.Column(db.String(50), nullable=True)
    logo_path = db.Column(db.String(255), nullable=True)

    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hrm_tenant.id', ondelete='SET NULL'), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.String(100), default='system')
    modified_by = db.Column(db.String(100))

    tenant = db.relationship('Tenant', back_populates='organizations')
    users = db.relationship('User', back_populates='organization', cascade='all, delete-orphan')
    org_employees = db.relationship('Employee', back_populates='organization', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Organization {self.name}>'


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    users = db.relationship('User', back_populates='role', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Role {self.name}>'


class Department(db.Model):
    """Master data for departments"""
    __tablename__ = 'hrm_departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    manager = db.relationship('Employee', foreign_keys=[manager_id])

    def __repr__(self):
        return f'<Department {self.name}>'


class WorkingHours(db.Model):
    """Master data for working hours configuration"""
    __tablename__ = 'hrm_working_hours'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    hours_per_day = db.Column(db.Numeric(4, 2), nullable=False)
    hours_per_week = db.Column(db.Numeric(4, 2), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<WorkingHours {self.name}: {self.hours_per_day}h/day>'


class WorkSchedule(db.Model):
    """Master data for work start/end times"""
    __tablename__ = 'hrm_work_schedules'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    break_duration = db.Column(db.Integer, default=60)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<WorkSchedule {self.name}: {self.start_time}-{self.end_time}>'


class Designation(db.Model):
    """Master data for job designations/positions"""
    __tablename__ = 'hrm_designation'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.String(100), default='system')
    modified_by = db.Column(db.String(100))

    def __repr__(self):
        return f'<Designation {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class UserRoleMapping(db.Model):
    """Maps users to multiple roles and companies for flexible access control"""
    __tablename__ = 'hrm_user_role_mapping'
    __table_args__ = (
        Index('idx_user_role_mapping_user_id', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('hrm_users.id', ondelete='CASCADE'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False)
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hrm_company.id', ondelete='CASCADE'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.String(100), default='system')

    user = db.relationship('User', backref='role_mappings')
    role = db.relationship('Role')
    company = db.relationship('Company')

    def __repr__(self):
        return f'<UserRoleMapping user_id={self.user_id} role_id={self.role_id}>'


class RoleAccessControl(db.Model):
    """Controls which roles have access to which modules, menus, and sub-menus"""
    __tablename__ = 'hrm_role_access_control'
    __table_args__ = (
        Index('idx_role_access_module_menu', 'module_name', 'menu_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    module_name = db.Column(db.String(100), nullable=False)
    menu_name = db.Column(db.String(100), nullable=False)
    sub_menu_name = db.Column(db.String(100), nullable=True)

    super_admin_access = db.Column(db.String(20), default='Editable')
    tenant_admin_access = db.Column(db.String(20), default='Hidden')
    hr_manager_access = db.Column(db.String(20), default='Hidden')
    employee_access = db.Column(db.String(20), default='Hidden')

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.String(100), default='system')
    updated_by = db.Column(db.String(100))

    def __repr__(self):
        return f'<RoleAccessControl {self.module_name}.{self.menu_name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'module_name': self.module_name,
            'menu_name': self.menu_name,
            'sub_menu_name': self.sub_menu_name,
            'super_admin_access': self.super_admin_access,
            'tenant_admin_access': self.tenant_admin_access,
            'hr_manager_access': self.hr_manager_access,
            'employee_access': self.employee_access,
        }


class AuditLog(db.Model):
    """Audit log for tracking all access control and system changes"""
    __tablename__ = 'hrm_audit_log'
    __table_args__ = (
        Index('idx_audit_log_user_id', 'user_id'),
        Index('idx_audit_log_action', 'action'),
        Index('idx_audit_log_created_at', 'created_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('hrm_users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(100), nullable=False)
    resource_id = db.Column(db.String(100), nullable=False)
    changes = db.Column(db.Text)
    status = db.Column(db.String(20), default='Success')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    user = db.relationship('User', backref='audit_logs')

    def __repr__(self):
        return f'<AuditLog {self.action} on {self.resource_type}:{self.resource_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'changes': self.changes,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
