# python
# File: seed.py
import click
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import SQLAlchemyError
from app import db  # your app must export the SQLAlchemy instance named `db`

# Import models inside functions to avoid circular import issues
# from models import Organization, Role, User


def seed_roles():
    from models import Role
    roles = [
        {"name": "SUPER_ADMIN", "description": "Super administrator with all permissions."},
        {"name": "ADMIN", "description": "Administrator with organization-wide permissions."},
        {"name": "HR_MANAGER", "description": "HR manager with employee management permissions."},
        {"name": "EMPLOYEE", "description": "Regular employee with limited permissions."},
    ]

    created = []
    try:
        with db.session.begin():
            for r in roles:
                existing = db.session.query(Role).filter_by(name=r["name"]).first()
                if not existing:
                    db.session.add(Role(name=r["name"], description=r["description"]))
                    created.append(r["name"])
        for name in created:
            click.echo(f"✅ Created role: {name}")
        for r in roles:
            if r["name"] not in created:
                click.echo(f"✅ Role \"{r['name']}\" already exists")
    except SQLAlchemyError as e:
        db.session.rollback()
        click.echo(f"❌ Error seeding roles: {e}")
        raise


def seed_organization():
    from models import Organization
    org_name = "AKS Logistics"
    try:
        with db.session.begin():
            org = db.session.query(Organization).filter_by(name=org_name).first()
            if not org:
                org = Organization(name=org_name)
                db.session.add(org)
                created = True
            else:
                created = False
        # ensure id is populated when newly created
        if created:
            db.session.refresh(org)
            click.echo(f"✅ Created organization: \"{org_name}\"")
        else:
            click.echo(f"✅ Organization \"{org_name}\" already exists")
        return org
    except SQLAlchemyError as e:
        db.session.rollback()
        click.echo(f"❌ Error seeding organization: {e}")
        raise


def seed_super_admin(org):
    from models import User, Role
    email = "superadmin@akslogistics.com"
    try:
        existing = db.session.query(User).filter_by(email=email).first()
        if existing:
            click.echo("✅ Super Admin user already exists")
            return
        role = db.session.query(Role).filter_by(name="SUPER_ADMIN").first()
        if not role:
            click.echo("❌ SUPER_ADMIN role not found. Please run role seeding first.")
            return
        password_hash = generate_password_hash("Admin@123")
        user = User(
            username="superadmin",
            email=email,
            password_hash=password_hash,
            organization_id=org.id,
            role_id=role.id,
            must_reset_password=False,
        )
        # set optional fields if present on the model
        if hasattr(user, "first_name"):
            setattr(user, "first_name", "Super")
        if hasattr(user, "last_name"):
            setattr(user, "last_name", "Admin")
        if hasattr(user, "is_active"):
            setattr(user, "is_active", True)
        db.session.add(user)
        db.session.commit()
        click.echo("✅ Super Admin user created")
    except SQLAlchemyError as e:
        db.session.rollback()
        click.echo(f"❌ Error seeding Super Admin user: {e}")
        raise


@click.group()
def seed():
    """Seed the database with default roles, organization, and Super Admin user."""
    pass


@seed.command("run")
@with_appcontext
def run():
    try:
        seed_roles()
        org = seed_organization()
        seed_super_admin(org)
    except Exception as e:
        try:
            db.session.rollback()
        except Exception:
            pass
        click.echo(f"❌ Error during seeding: {e}")
        raise
    finally:
        try:
            db.session.close()
        except Exception:
            pass


def register_seed(flask_app):
    """Register the seed CLI group on the provided Flask app."""
    flask_app.cli.add_command(seed)


# Note: Auto-registration removed to avoid circular imports
# The seed command is registered in app.py after models are imported