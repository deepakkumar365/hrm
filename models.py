from datetime import datetime, date
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(20), default='User')  # Super Admin, Admin, Manager, User
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# OAuth table removed - no longer using Replit Auth

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    nric = db.Column(db.String(20), unique=True, nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    nationality = db.Column(db.String(50))
    address = db.Column(db.Text)
    postal_code = db.Column(db.String(10))
    
    # Employment details
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    hire_date = db.Column(db.Date, nullable=False)
    employment_type = db.Column(db.String(20))  # Full-time, Part-time, Contract
    work_permit_type = db.Column(db.String(30))  # Citizen, PR, Work Permit, S Pass, EP
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
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    termination_date = db.Column(db.Date)
    
    # Foreign key to User for system access
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('employee_profile', uselist=False))
    manager = db.relationship('Employee', remote_side=[id], backref='team_members')

class Payroll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
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
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
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
    
    __table_args__ = (UniqueConstraint('employee_id', 'date'),)

class Leave(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
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
    employee = db.relationship('Employee', backref='leaves')
    requested_by_user = db.relationship('User', foreign_keys=[requested_by])
    approved_by_user = db.relationship('User', foreign_keys=[approved_by])

class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
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
    employee = db.relationship('Employee', backref='claims')
    submitted_by_user = db.relationship('User', foreign_keys=[submitted_by])
    approved_by_user = db.relationship('User', foreign_keys=[approved_by])

class Appraisal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
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
    employee = db.relationship('Employee', backref='appraisals')
    reviewed_by_user = db.relationship('User')

class ComplianceReport(db.Model):
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
