from flask import Blueprint, redirect, url_for, flash, current_app
import os
from core.dev_utils import clean_database_hrm

dev_bp = Blueprint('dev', __name__)

@dev_bp.route('/clean-db', methods=['POST'])
def clean_db():
    if os.environ.get('ENVIRONMENT') != 'development':
        flash('Action not allowed in this environment.', 'error')
        return redirect(url_for('login'))
    
    success, message = clean_database_hrm()
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    
    return redirect(url_for('login'))
