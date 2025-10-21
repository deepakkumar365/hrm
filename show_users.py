"""Display users from hrm_users table and show hashing method"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User
from sqlalchemy import text

print('\n' + '='*80)
print('👥 USERS FROM hrm_users TABLE')
print('='*80)

with app.app_context():
    # Get all users
    users = User.query.all()
    
    print(f'\nTotal Users: {len(users)}\n')
    
    for user in users:
        print(f'ID: {user.id}')
        print(f'Username: {user.username}')
        print(f'Email: {user.email}')
        print(f'First Name: {user.first_name}')
        print(f'Last Name: {user.last_name}')
        print(f'Role ID: {user.role_id}')
        print(f'Organization ID: {user.organization_id}')
        print(f'Is Active: {user.is_active}')
        print(f'Must Reset Password: {user.must_reset_password}')
        print(f'Password Hash: {user.password_hash[:50]}...')  # Show first 50 chars
        print(f'Created At: {user.created_at}')
        print('-' * 80)
    
    print('\n' + '='*80)
    print('🔐 PASSWORD HASHING INFORMATION')
    print('='*80)
    print('\nHash Method: Werkzeug PBKDF2 (SHA-256)')
    print('Library: werkzeug.security')
    print('Functions Used:')
    print('  - generate_password_hash() - for creating hashes')
    print('  - check_password_hash() - for verifying passwords')
    print('\nHash Format: pbkdf2:sha256:salt$hash')
    print('Security: Industry-standard, highly secure')
    print('\nExample hash structure:')
    if users:
        sample_hash = users[0].password_hash
        print(f'  {sample_hash[:80]}...')
        print(f'\nHash length: {len(sample_hash)} characters')
    
    print('\n' + '='*80)
    print('📝 DEFAULT PASSWORDS (for reference)')
    print('='*80)
    print('\nDefault admin/superadmin password is: Admin@123')
    print('Default password for newly created employees is set in constants.py')
    print('\n⚠️  IMPORTANT: Change these passwords in production!')
    print('='*80 + '\n')