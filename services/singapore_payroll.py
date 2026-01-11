from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, date
import calendar

class SingaporePayrollCalculator:
    """
    Singapore payroll calculation engine with CPF, AIS, and compliance features
    """
    
    # CPF Rates (as of 2024)
    CPF_RATES = {
        'citizen_pr': {
            'employee': {
                'below_55': 20.0,
                '55_to_60': 13.0,
                '60_to_65': 7.5,
                'above_65': 5.0
            },
            'employer': {
                'below_55': 17.0,
                '55_to_60': 13.0,
                '60_to_65': 9.0,
                'above_65': 7.5
            }
        },
        'third_country': {
            'employee': {
                'first_year': 5.0,
                'second_year': 15.0,
                'third_year_onwards': 20.0
            },
            'employer': {
                'first_year': 4.0,
                'second_year': 13.0,
                'third_year_onwards': 17.0
            }
        }
    }
    
    # CPF Contribution Caps (monthly)
    CPF_SALARY_CEILING = 6000
    CPF_ORDINARY_WAGE_CEILING = 6000
    
    # AIS Thresholds
    AIS_THRESHOLD = 2200  # Monthly income threshold for AIS
    
    def __init__(self):
        pass
    
    def calculate_age(self, birth_date, reference_date=None):
        """Calculate age on reference date"""
        if reference_date is None:
            reference_date = date.today()
        
        age = reference_date.year - birth_date.year
        if reference_date.month < birth_date.month or \
           (reference_date.month == birth_date.month and reference_date.day < birth_date.day):
            age -= 1
        
        return age
    
    def get_cpf_rate(self, employee, monthly_salary, pay_date=None):
        """Get CPF rates based on employee details"""
        if pay_date is None:
            pay_date = date.today()
        
        age = self.calculate_age(employee.date_of_birth, pay_date)
        
        # Check work permit type for rate determination
        if employee.work_permit_type in ['Citizen', 'PR']:
            category = 'citizen_pr'
            if age < 55:
                age_bracket = 'below_55'
            elif 55 <= age < 60:
                age_bracket = '55_to_60'
            elif 60 <= age < 65:
                age_bracket = '60_to_65'
            else:
                age_bracket = 'above_65'
            
            employee_rate = self.CPF_RATES[category]['employee'][age_bracket]
            employer_rate = self.CPF_RATES[category]['employer'][age_bracket]
        
        else:  # Foreign workers
            category = 'third_country'
            years_in_sg = (pay_date - employee.hire_date).days / 365.25
            
            if years_in_sg < 1:
                period = 'first_year'
            elif years_in_sg < 2:
                period = 'second_year'
            else:
                period = 'third_year_onwards'
            
            employee_rate = self.CPF_RATES[category]['employee'][period]
            employer_rate = self.CPF_RATES[category]['employer'][period]
        
        return employee_rate, employer_rate
    
    def calculate_cpf_contribution(self, employee, gross_salary, pay_date=None):
        """Calculate CPF contributions"""
        if gross_salary <= 0:
            return 0, 0
        
        # Apply salary ceiling
        cpf_salary = min(gross_salary, self.CPF_SALARY_CEILING)
        
        employee_rate, employer_rate = self.get_cpf_rate(employee, cpf_salary, pay_date)
        
        employee_cpf = (cpf_salary * Decimal(employee_rate) / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        employer_cpf = (cpf_salary * Decimal(employer_rate) / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return employee_cpf, employer_cpf
    
    def calculate_overtime_pay(self, employee, overtime_hours):
        """Calculate overtime pay (2x rate for Singapore)"""
        if not employee.hourly_rate or overtime_hours <= 0:
            return Decimal('0')
        
        overtime_rate = employee.hourly_rate * Decimal('2')
        return (overtime_rate * Decimal(str(overtime_hours))).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    
    def is_ais_applicable(self, employee, monthly_income):
        """Check if employee is subject to AIS"""
        # AIS applies to Singapore citizens and PRs earning above threshold
        return (employee.work_permit_type in ['Citizen', 'PR'] and 
                monthly_income >= self.AIS_THRESHOLD)
    
    def calculate_payroll(self, employee, pay_period_start, pay_period_end, 
                         overtime_hours=0, additional_allowances=0, 
                         additional_deductions=0, bonuses=0):
        """Calculate complete payroll for an employee"""
        
        # Calculate basic pay (monthly salary)
        # Use Payroll Configuration as master source of truth
        basic_pay = (employee.payroll_config.basic_salary or Decimal(0)) if employee.payroll_config else Decimal(0)
        
        # Calculate overtime pay
        overtime_pay = self.calculate_overtime_pay(employee, overtime_hours)
        
        # Total allowances
        # Use Payroll Configuration as master source of truth
        config_allowances = employee.payroll_config.get_total_allowances() if employee.payroll_config else Decimal(0)
        total_allowances = config_allowances + additional_allowances
        
        # Calculate gross pay
        gross_pay = basic_pay + overtime_pay + total_allowances + bonuses
        
        # Calculate CPF contributions
        employee_cpf, employer_cpf = self.calculate_cpf_contribution(
            employee, gross_pay, pay_period_end
        )
        
        # Calculate net pay
        net_pay = gross_pay - employee_cpf - additional_deductions
        
        return {
            'basic_pay': basic_pay,
            'overtime_pay': overtime_pay,
            'allowances': total_allowances,
            'bonuses': bonuses,
            'gross_pay': gross_pay,
            'employee_cpf': employee_cpf,
            'employer_cpf': employer_cpf,
            'other_deductions': additional_deductions,
            'net_pay': net_pay,
            'is_ais_applicable': self.is_ais_applicable(employee, gross_pay)
        }
    
    def generate_cpf_file(self, payrolls, month, year):
        """Generate CPF submission file"""
        cpf_data = []
        total_employee_cpf = Decimal('0')
        total_employer_cpf = Decimal('0')
        
        for payroll in payrolls:
            employee = payroll.employee
            
            cpf_record = {
                'employee_id': employee.employee_id,
                'name': f"{employee.first_name} {employee.last_name}",
                'nric': employee.nric,
                'cpf_account': employee.cpf_account,
                'gross_salary': payroll.gross_pay,
                'employee_cpf': payroll.employee_cpf,
                'employer_cpf': payroll.employer_cpf,
                'total_cpf': payroll.employee_cpf + payroll.employer_cpf
            }
            
            cpf_data.append(cpf_record)
            total_employee_cpf += payroll.employee_cpf
            total_employer_cpf += payroll.employer_cpf
        
        return {
            'records': cpf_data,
            'summary': {
                'total_employees': len(cpf_data),
                'total_employee_cpf': total_employee_cpf,
                'total_employer_cpf': total_employer_cpf,
                'total_cpf': total_employee_cpf + total_employer_cpf,
                'month': month,
                'year': year
            }
        }
    
    def generate_ais_file(self, payrolls, year):
        """Generate AIS submission file"""
        ais_data = []
        
        for payroll in payrolls:
            employee = payroll.employee
            
            if self.is_ais_applicable(employee, payroll.gross_pay):
                ais_record = {
                    'employee_id': employee.employee_id,
                    'name': f"{employee.first_name} {employee.last_name}",
                    'nric': employee.nric,
                    'annual_income': payroll.gross_pay * 12,  # Simplified calculation
                    'employment_period': 12  # Assume full year for MVP
                }
                ais_data.append(ais_record)
        
        return {
            'records': ais_data,
            'summary': {
                'total_employees': len(ais_data),
                'year': year
            }
        }
    
    def generate_oed_file(self, payrolls, month, year):
        """Generate OED (Overseas Employee Declaration) file"""
        oed_data = []
        
        for payroll in payrolls:
            employee = payroll.employee
            
            # OED applies to foreign workers
            if employee.work_permit_type not in ['Citizen', 'PR']:
                oed_record = {
                    'employee_id': employee.employee_id,
                    'name': f"{employee.first_name} {employee.last_name}",
                    'passport_number': employee.nric,  # Assuming NRIC field stores passport for foreigners
                    'work_permit_type': employee.work_permit_type,
                    'work_permit_expiry': employee.work_permit_expiry,
                    'gross_salary': payroll.gross_pay,
                    'nationality': employee.nationality,
                    'designation': employee.designation.name if employee.designation else ''
                }
                oed_data.append(oed_record)
        
        return {
            'records': oed_data,
            'summary': {
                'total_employees': len(oed_data),
                'month': month,
                'year': year
            }
        }
    
    def generate_bank_file(self, payrolls, bank_format='GIRO'):
        """Generate bank file for salary transfer"""
        bank_data = []
        total_amount = Decimal('0')
        
        for payroll in payrolls:
            employee = payroll.employee
            
            if employee.bank_account and payroll.net_pay > 0:
                bank_record = {
                    'employee_id': employee.employee_id,
                    'bank_account': employee.bank_account,
                    'bank_name': employee.bank_name,
                    'name': f"{employee.first_name} {employee.last_name}",
                    'amount': payroll.net_pay,
                    'reference': f"SAL{payroll.pay_period_end.strftime('%Y%m')}{employee.employee_id}"
                }
                bank_data.append(bank_record)
                total_amount += payroll.net_pay
        
        return {
            'records': bank_data,
            'summary': {
                'total_employees': len(bank_data),
                'total_amount': total_amount,
                'format': bank_format
            }
        }

