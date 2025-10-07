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

# OAuth table removed - no longer using Replit Auth


# =====================================================
# TENANT & COMPANY MODELS (Multi-tenant Hierarchy)
# =====================================================

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
    
    # Audit fields
    created_by = db.Column(db.String(100), nullable=False, default='system')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified_by = db.Column(db.String(100))
    modified_at = db.Column(db.DateTime)
    
    # Relationships
    companies = db.relationship('Company', back_populates='tenant', cascade='all, delete-orphan')
    organizations = db.relationship('Organization', back_populates='tenant')
    
    def __repr__(self):
        return f'<Tenant {self.name} ({self.code})>'
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'is_active': self.is_active,
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
    
    # Company details
    address = db.Column(db.Text)
    uen = db.Column(db.String(50))  # Unique Entity Number (Singapore)
    registration_number = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    logo_path = db.Column(db.String(255))
    
    # Status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Audit fields
    created_by = db.Column(db.String(100), nullable=False, default='system')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    modified_by = db.Column(db.String(100))
    modified_at = db.Column(db.DateTime)
    
    # Relationships
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


class Employee(db.Model):
    __tablename__ = 'hrm_employee'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    father_name = db.Column(db.String(100))  # NEW: For team info display
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    nric = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    nationality = db.Column(db.String(50))
    address = db.Column(db.Text)
    postal_code = db.Column(db.String(10))
    location = db.Column(db.String(100))  # NEW: Work location for team display
    profile_image_path = db.Column(db.String(255))  # Relative path under static/
    timezone = db.Column(db.String(50), default='UTC')  # NEW: For attendance timezone handling

    # Employment details
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    hire_date = db.Column(db.Date, nullable=False)
    employment_type = db.Column(db.String(20))  # Full-time, Part-time, Contract
    work_permit_type = db.Column(db.String(30))  # Citizen, PR, Work Permit, S Pass, EP
    work_permit_number = db.Column(db.String(50))  # NEW: Work permit number
    work_permit_expiry = db.Column(db.Date)

    # Salary details
    basic_salary = db.Column(db.Numeric(10, 2), nullable=False)
    allowances = db.Column(db.Numeric(10, 2), default=0)
    hourly_rate = db.Column(db.Numeric(8, 2))

    # CPF details
    cpf_account = db.Column(db.String(20))
    employee_cpf_rate = db.Column(db.Numeric(5, 2), default=20.00)
    employer_cpf_rate = db.Column(db.Numeric(5, 2), default=17.00)

    # Bank details
    bank_name = db.Column(db.String(100))
    bank_account = db.Column(db.String(30))
    account_holder_name = db.Column(db.String(100))
    swift_code = db.Column(db.String(11))  # 8 or 11 characters
    ifsc_code = db.Column(db.String(11))   # 11 characters

    # Status
    is_active = db.Column(db.Boolean, default=True)
    termination_date = db.Column(db.Date)

    # Foreign key to User for system access
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organization.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id', ondelete='SET NULL'), nullable=True)
    
    # NEW: Company hierarchy link
    company_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hrm_company.id', ondelete='CASCADE'), nullable=True)

    # Master data relationships
    working_hours_id = db.Column(db.Integer, db.ForeignKey('hrm_working_hours.id'), nullable=True)
    work_schedule_id = db.Column(db.Integer, db.ForeignKey('hrm_work_schedules.id'), nullable=True)

    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.String(100), default='system')
    modified_by = db.Column(db.String(100))

    # Relationships
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
    document_type = db.Column(db.String(50), nullable=False)  # Offer Letter, Appraisal Letter, Salary Slip
    file_path = db.Column(db.String(255), nullable=False)  # Relative path under static/
    issue_date = db.Column(db.Date, nullable=False)
    month = db.Column(db.Integer, nullable=True)  # For salary slips (1-12)
    year = db.Column(db.Integer, nullable=True)   # For salary slips
    description = db.Column(db.Text, nullable=True)
    
    # Audit fields
    uploaded_by = db.Column(db.Integer, db.ForeignKey('hrm_users.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='documents')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f'<EmployeeDocument {self.document_type} for Employee {self.employee_id}>'


class Payroll(db.Model):
    __tablename__ = 'hrm_payroll'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    
    # Earnings
    basic_pay = db.Column(db.Numeric(10, 2), nullable=False)
    overtime_pay = db.Column(db.Numeric(10, 2), default=0)
    allowances = db.Column(db.Numeric(10, 2), default=0)
    bonuses = db.Column(db.Numeric(10, 2), default=0)
    gross_pay = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Deductions
    employee_cpf = db.Column(db.Numeric(10, 2), default=0)
    employer_cpf = db.Column(db.Numeric(10, 2), default=0)
    income_tax = db.Column(db.Numeric(10, 2), default=0)
    other_deductions = db.Column(db.Numeric(10, 2), default=0)
    
    # Net pay
    net_pay = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Work details
    days_worked = db.Column(db.Integer, default=0)
    overtime_hours = db.Column(db.Numeric(5, 2), default=0)
    leave_days = db.Column(db.Integer, default=0)
    
    # Status
    status = db.Column(db.String(20), default='Draft')  # Draft, Approved, Paid
    generated_by = db.Column(db.Integer, db.ForeignKey(User.id))
    generated_at = db.Column(db.DateTime, default=datetime.now)
    
    # Relationships
    employee = db.relationship('Employee', backref='payrolls')
    generated_by_user = db.relationship('User')

class Attendance(db.Model):
    __tablename__ = 'hrm_attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Time tracking
    clock_in = db.Column(db.Time)
    clock_out = db.Column(db.Time)
    break_start = db.Column(db.Time)
    break_end = db.Column(db.Time)
    
    # Hours calculation
    regular_hours = db.Column(db.Numeric(5, 2), default=0)
    overtime_hours = db.Column(db.Numeric(5, 2), default=0)
    total_hours = db.Column(db.Numeric(5, 2), default=0)
    
    # NEW: Overtime tracking
    has_overtime = db.Column(db.Boolean, default=False)
    overtime_approved = db.Column(db.Boolean, nullable=True)
    overtime_approved_by = db.Column(db.Integer, db.ForeignKey('hrm_users.id', ondelete='SET NULL'), nullable=True)
    overtime_approved_at = db.Column(db.DateTime, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='Present')  # Present, Absent, Late, Half-day
    remarks = db.Column(db.Text)
    
    # Location tracking for mobile
    location_lat = db.Column(db.String(20))
    location_lng = db.Column(db.String(20))
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    employee = db.relationship('Employee', backref='attendances')
    overtime_approver = db.relationship('User', foreign_keys=[overtime_approved_by])
    
    __table_args__ = (UniqueConstraint('employee_id', 'date'),)

class Leave(db.Model):
    __tablename__ = 'hrm_leave'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    leave_type = db.Column(db.String(30), nullable=False)  # Annual, Medical, Maternity, etc.
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    days_requested = db.Column(db.Integer, nullable=False)
    
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected
    
    # Approval workflow
    requested_by = db.Column(db.Integer, db.ForeignKey(User.id))
    approved_by = db.Column(db.Integer, db.ForeignKey(User.id))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='leaves')
    requested_by_user = db.relationship('User', foreign_keys=[requested_by])
    approved_by_user = db.relationship('User', foreign_keys=[approved_by])

class Claim(db.Model):
    __tablename__ = 'hrm_claim'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    claim_type = db.Column(db.String(30), nullable=False)  # Medical, Transport, etc.
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    claim_date = db.Column(db.Date, nullable=False)
    
    description = db.Column(db.Text)
    receipt_number = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Pending')  # Pending, Approved, Rejected, Paid
    
    # Approval workflow
    submitted_by = db.Column(db.Integer, db.ForeignKey(User.id))
    approved_by = db.Column(db.Integer, db.ForeignKey(User.id))
    approved_at = db.Column(db.DateTime)
    rejection_reason = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='claims')
    submitted_by_user = db.relationship('User', foreign_keys=[submitted_by])
    approved_by_user = db.relationship('User', foreign_keys=[approved_by])

class Appraisal(db.Model):
    __tablename__ = 'hrm_appraisal'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('hrm_employee.id'), nullable=False)
    review_period_start = db.Column(db.Date, nullable=False)
    review_period_end = db.Column(db.Date, nullable=False)
    
    # Ratings (1-5 scale)
    performance_rating = db.Column(db.Integer)
    goals_achievement = db.Column(db.Integer)
    teamwork_rating = db.Column(db.Integer)
    communication_rating = db.Column(db.Integer)
    overall_rating = db.Column(db.Numeric(3, 2))
    
    # Feedback
    self_review = db.Column(db.Text)
    manager_feedback = db.Column(db.Text)
    development_goals = db.Column(db.Text)
    training_recommendations = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='Draft')  # Draft, Submitted, Completed
    
    # Workflow
    reviewed_by = db.Column(db.Integer, db.ForeignKey(User.id))
    completed_at = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='appraisals')
    reviewed_by_user = db.relationship('User')

class ComplianceReport(db.Model):
    __tablename__ = 'hrm_compliance_report'
    id = db.Column(db.Integer, primary_key=True)
    report_type = db.Column(db.String(20), nullable=False)  # CPF, AIS, OED, IRAS
    period_month = db.Column(db.Integer, nullable=False)
    period_year = db.Column(db.Integer, nullable=False)
    
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(100))
    status = db.Column(db.String(20), default='Generated')  # Generated, Submitted
    
    total_employees = db.Column(db.Integer)
    total_amount = db.Column(db.Numeric(12, 2))
    
    generated_by = db.Column(db.Integer, db.ForeignKey(User.id))
    generated_at = db.Column(db.DateTime, default=datetime.now)
    submitted_at = db.Column(db.DateTime)
    
    # Relationships
    generated_by_user = db.relationship('User')

    def __repr__(self):
        return f'<ComplianceReport {self.report_type} for {self.period_year}-{self.period_month:02d}>'


# Master Data Models
class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=True)
    uen = db.Column(db.String(50), nullable=True)  # Unique Entity Number
    logo_path = db.Column(db.String(255), nullable=True)  # Relative path under static/
    
    # NEW: Tenant hierarchy link
    tenant_id = db.Column(UUID(as_uuid=True), db.ForeignKey('hrm_tenant.id', ondelete='SET NULL'), nullable=True)
    
    # Audit fields
    created_at = db.Column(db.DateTime, default=datetime.now)
    modified_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = db.Column(db.String(100), default='system')
    modified_by = db.Column(db.String(100))

    # Relationships
    tenant = db.relationship('Tenant', back_populates='organizations')
    users = db.relationship('User', back_populates='organization', cascade='all, delete-orphan')
    org_employees = db.relationship('Employee', back_populates='organization', cascade='all, delete-orphan')
    # Renamed from 'employees' to 'org_employees' to avoid backref conflict

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
    
    # Relationship
    manager = db.relationship('Employee', foreign_keys=[manager_id])

    def __repr__(self):
        return f'<Department {self.name}>'


class WorkingHours(db.Model):
    """Master data for working hours configuration"""
    __tablename__ = 'hrm_working_hours'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "Standard 9-6", "Shift A"
    hours_per_day = db.Column(db.Numeric(4, 2), nullable=False)  # e.g., 8.00, 8.50
    hours_per_week = db.Column(db.Numeric(4, 2), nullable=False)  # e.g., 40.00, 44.00
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
    name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., "Standard Hours", "Early Shift"
    start_time = db.Column(db.Time, nullable=False)  # e.g., 09:00:00
    end_time = db.Column(db.Time, nullable=False)    # e.g., 18:00:00
    break_duration = db.Column(db.Integer, default=60)  # break duration in minutes
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f'<WorkSchedule {self.name}: {self.start_time}-{self.end_time}>'
