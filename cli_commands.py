"""
Flask CLI Commands for HRMS Database Management
"""
import click
from flask.cli import with_appcontext
from app import app, db
from models import User, Role, Organization
from sqlalchemy import text


@app.cli.command('reset-users')
@click.option('--confirm', is_flag=True, help='Confirm the reset operation')
@with_appcontext
def reset_users(confirm):
    """
    Reset the hrm_users table and create 4 new default users.
    
    WARNING: This will delete ALL existing users!
    
    Usage:
        flask reset-users --confirm
    """
    if not confirm:
        click.echo("⚠️  WARNING: This command will DELETE ALL USERS from the database!")
        click.echo("⚠️  To proceed, run: flask reset-users --confirm")
        return
    
    try:
        click.echo("🔄 Starting user reset process...")
        
        # Step 1: Delete all users (handle foreign key constraints)
        click.echo("📋 Step 1: Deleting all existing users...")
        user_count = User.query.count()
        
        # First, handle foreign key references
        click.echo("  🔗 Handling foreign key constraints...")
        
        # List of all tables and columns that reference hrm_users
        foreign_key_updates = [
            ("hrm_users", "reporting_manager_id"),
            ("hrm_employee", "user_id"),
            ("hrm_payroll", "generated_by"),
            ("hrm_payroll_configuration", "updated_by"),
            ("hrm_attendance", "reviewed_by"),
            ("hrm_leave", "approved_by"),
            ("hrm_leave", "submitted_by"),
            ("hrm_leave", "requested_by"),  # Added this
            ("hrm_claim", "approved_by"),
            ("hrm_claim", "requested_by"),
            ("hrm_claim", "submitted_by"),  # Added this
            ("hrm_compliance_report", "generated_by"),
            ("hrm_employee_documents", "uploaded_by"),
            ("hrm_attendance", "overtime_approved_by"),
        ]
        
        for table, column in foreign_key_updates:
            try:
                db.session.execute(text(f"UPDATE {table} SET {column} = NULL WHERE {column} IS NOT NULL"))
                db.session.commit()  # Commit each update separately
                click.echo(f"    ✓ Cleared {table}.{column}")
            except Exception as e:
                # Table or column might not exist, rollback and skip it
                db.session.rollback()
                click.echo(f"    ⚠ Skipped {table}.{column} (not found or error)")
        
        # Now delete all users
        User.query.delete()
        db.session.commit()
        click.echo(f"✅ Deleted {user_count} users")
        
        # Step 2: Ensure required roles exist
        click.echo("📋 Step 2: Checking required roles...")
        required_roles = {
            'Super Admin': 'Super Administrator with full system access',
            'Admin': 'Administrator with tenant-level access',
            'Manager': 'Manager with team management capabilities',
            'User': 'Regular user with basic access'
        }
        
        roles = {}
        for role_name, role_desc in required_roles.items():
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name, description=role_desc, is_active=True)
                db.session.add(role)
                db.session.flush()
                click.echo(f"  ➕ Created role: {role_name}")
            else:
                click.echo(f"  ✓ Role exists: {role_name}")
            roles[role_name] = role
        
        db.session.commit()
        
        # Step 3: Ensure default organization exists
        click.echo("📋 Step 3: Checking default organization...")
        org = Organization.query.first()
        if not org:
            org = Organization(
                name='Default Organization',
                address='Singapore',
                created_by='system'
            )
            db.session.add(org)
            db.session.flush()
            click.echo("  ➕ Created default organization")
        else:
            click.echo(f"  ✓ Organization exists: {org.name}")
        
        db.session.commit()
        
        # Step 4: Create 4 new users
        click.echo("📋 Step 4: Creating 4 new users...")
        
        users_to_create = [
            {
                'username': 'superadmin',
                'password': 'superadmin123',
                'email': 'superadmin@hrm.com',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'Super Admin'
            },
            {
                'username': 'tenantadmin',
                'password': 'tenantadmin123',
                'email': 'tenantadmin@hrm.com',
                'first_name': 'Tenant',
                'last_name': 'Admin',
                'role': 'Admin'
            },
            {
                'username': 'manager',
                'password': 'manager123',
                'email': 'manager@hrm.com',
                'first_name': 'Team',
                'last_name': 'Manager',
                'role': 'Manager'
            },
            {
                'username': 'employee',
                'password': 'employee123',
                'email': 'employee@hrm.com',
                'first_name': 'Regular',
                'last_name': 'Employee',
                'role': 'User'
            }
        ]
        
        created_users = []
        for user_data in users_to_create:
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                organization_id=org.id,
                role_id=roles[user_data['role']].id,
                is_active=True,
                must_reset_password=False  # Set to False for easy testing
            )
            user.set_password(user_data['password'])
            db.session.add(user)
            created_users.append(user)
            click.echo(f"  ➕ Created user: {user_data['username']} (Role: {user_data['role']})")
        
        db.session.commit()
        
        # Step 5: Display summary
        click.echo("\n" + "="*60)
        click.echo("✅ USER RESET COMPLETED SUCCESSFULLY!")
        click.echo("="*60)
        click.echo("\n📊 Created Users:")
        click.echo("-" * 60)
        for user_data in users_to_create:
            click.echo(f"  Username: {user_data['username']:<20} Password: {user_data['password']}")
            click.echo(f"  Role:     {user_data['role']:<20} Email:    {user_data['email']}")
            click.echo("-" * 60)
        
        click.echo("\n🔐 Login Credentials:")
        click.echo("  All users have been created with the passwords shown above.")
        click.echo("  Password reset is NOT required on first login.")
        click.echo("\n✅ You can now login with any of these accounts!")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"\n❌ ERROR: Failed to reset users!")
        click.echo(f"Error details: {str(e)}")
        import traceback
        click.echo(traceback.format_exc())
        return


@app.cli.command('list-users')
@with_appcontext
def list_users():
    """
    List all users in the system.
    
    Usage:
        flask list-users
    """
    try:
        users = User.query.all()
        
        if not users:
            click.echo("📭 No users found in the database.")
            return
        
        click.echo(f"\n👥 Total Users: {len(users)}")
        click.echo("="*80)
        
        for user in users:
            status = "✅ Active" if user.is_active else "❌ Inactive"
            role_name = user.role.name if user.role else "No Role"
            org_name = user.organization.name if user.organization else "No Organization"
            
            click.echo(f"\nID: {user.id}")
            click.echo(f"  Username:     {user.username}")
            click.echo(f"  Name:         {user.first_name} {user.last_name}")
            click.echo(f"  Email:        {user.email}")
            click.echo(f"  Role:         {role_name}")
            click.echo(f"  Organization: {org_name}")
            click.echo(f"  Status:       {status}")
            click.echo(f"  Created:      {user.created_at}")
            click.echo("-"*80)
        
    except Exception as e:
        click.echo(f"❌ ERROR: {str(e)}")


@app.cli.command('create-user')
@click.option('--username', prompt='Username', help='Username for the new user')
@click.option('--password', prompt='Password', hide_input=True, confirmation_prompt=True, help='Password for the new user')
@click.option('--email', prompt='Email', help='Email address')
@click.option('--first-name', prompt='First Name', help='First name')
@click.option('--last-name', prompt='Last Name', help='Last name')
@click.option('--role', prompt='Role (Super Admin/Admin/Manager/User)', default='User', help='User role')
@with_appcontext
def create_user(username, password, email, first_name, last_name, role):
    """
    Create a new user interactively.
    
    Usage:
        flask create-user
    """
    try:
        # Check if username already exists
        if User.query.filter_by(username=username).first():
            click.echo(f"❌ ERROR: Username '{username}' already exists!")
            return
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            click.echo(f"❌ ERROR: Email '{email}' already exists!")
            return
        
        # Get role
        role_obj = Role.query.filter_by(name=role).first()
        if not role_obj:
            click.echo(f"❌ ERROR: Role '{role}' not found!")
            click.echo("Available roles:")
            for r in Role.query.all():
                click.echo(f"  - {r.name}")
            return
        
        # Get default organization
        org = Organization.query.first()
        if not org:
            click.echo("❌ ERROR: No organization found! Please create an organization first.")
            return
        
        # Create user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            organization_id=org.id,
            role_id=role_obj.id,
            is_active=True,
            must_reset_password=False
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        click.echo(f"\n✅ User created successfully!")
        click.echo(f"  Username: {username}")
        click.echo(f"  Email:    {email}")
        click.echo(f"  Role:     {role}")
        
    except Exception as e:
        db.session.rollback()
        click.echo(f"❌ ERROR: {str(e)}")


# Register CLI commands
def init_cli_commands(app):
    """Initialize CLI commands - called from main.py"""
    # Commands are automatically registered via @app.cli.command decorator
    pass