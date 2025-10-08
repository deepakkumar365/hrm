"""Reset passwords for default users"""
import sys
sys.path.insert(0, 'E:/Gobi/Pro/HRMS/hrm')

from app import app, db
from models import User

print('\n🔐 Resetting Default User Passwords...')
print('='*60)

with app.app_context():
    # Define default users and their passwords
    default_users = [
        {'username': 'superadmin', 'password': 'admin123'},
        {'username': 'admin', 'password': 'admin123'},
        {'username': 'manager', 'password': 'admin123'},
        {'username': 'user', 'password': 'admin123'}
    ]
    
    updated_count = 0
    for user_data in default_users:
        user = User.query.filter_by(username=user_data['username']).first()
        if user:
            user.set_password(user_data['password'])
            user.must_reset_password = False
            print(f'✅ Reset password for: {user.username} ({user.email})')
            updated_count += 1
        else:
            print(f'⚠️  User not found: {user_data["username"]}')
    
    if updated_count > 0:
        db.session.commit()
        print(f'\n✅ Successfully reset {updated_count} passwords')
        
        # Verify passwords work
        print('\n🔍 Verifying passwords...')
        for user_data in default_users:
            user = User.query.filter_by(username=user_data['username']).first()
            if user and user.check_password(user_data['password']):
                print(f'   ✅ {user.username}: Password verified')
            elif user:
                print(f'   ❌ {user.username}: Password verification failed')
    else:
        print('\n⚠️  No passwords were reset')

print('='*60)
print('\n📝 Default Login Credentials:')
print('   Username: superadmin | Password: admin123')
print('   Username: admin      | Password: admin123')
print('   Username: manager    | Password: admin123')
print('   Username: user       | Password: admin123')
print('\n⚠️  Remember to change these passwords in production!')
print('='*60 + '\n')