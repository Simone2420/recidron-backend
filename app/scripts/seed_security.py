import argparse

from sqlalchemy.orm import joinedload

from app.database import SessionLocal
from app.models import Role, User
from app.schemas.security import PersonCreate, UserCreate
from app.services.security import SecurityService


def seed_security(
    admin_username: str | None = None,
    admin_password: str | None = None,
    admin_email: str | None = None,
    make_superuser: bool = False,
) -> None:
    """
    Seed the database with predefined security roles and permissions.

    Creates:
    - 2 roles (admin, user) and 12 permissions if they don't already exist
    - Optionally creates a new superuser if credentials are provided
    - Or promotes an existing user to superuser

    Args:
        admin_username: Username for the superuser (create new or promote existing).
        admin_password: Password for the new superuser (required if creating new).
        admin_email: Email for the new superuser (required if creating new).
        make_superuser: If True, create new or promote existing user to superuser.
    """
    db = SessionLocal()
    try:
        # Seed roles and permissions (idempotent)
        SecurityService.seed_security_catalog(db)
        print("✓ Security catalog seeded: 2 roles (admin, user) and 12 permissions")

        # Create or promote superuser
        if admin_username and make_superuser:
            user = (
                db.query(User)
                .options(joinedload(User.roles))
                .filter(User.username == admin_username)
                .first()
            )

            if user:
                # Promote existing user to superuser and admin role
                user.is_superuser = True
                admin_role = db.query(Role).filter(Role.name == "admin").first()
                if admin_role and admin_role not in user.roles:
                    # Remove user role if present
                    user_role = db.query(Role).filter(Role.name == "user").first()
                    if user_role and user_role in user.roles:
                        user.roles.remove(user_role)
                    user.roles.append(admin_role)
                db.commit()
                print(f"✓ User '{admin_username}' promoted to superuser with admin role")
            elif admin_password and admin_email:
                # Create new superuser
                person_create = PersonCreate(
                    first_name="Admin",
                    last_name="User",
                    email=admin_email,
                    phone=None,
                )
                user_create = UserCreate(
                    username=admin_username,
                    password=admin_password,
                    person=person_create,
                )
                user = SecurityService.register_user(db, user_create)
                user.is_superuser = True

                # Assign admin role and remove user role
                admin_role = db.query(Role).filter(Role.name == "admin").first()
                user_role = db.query(Role).filter(Role.name == "user").first()
                if user_role and user_role in user.roles:
                    user.roles.remove(user_role)
                if admin_role and admin_role not in user.roles:
                    user.roles.append(admin_role)

                db.commit()
                print(f"✓ Superuser '{admin_username}' created with admin role")
            else:
                print(f"⚠ User '{admin_username}' not found")
                print("  To create new superuser, provide --admin-password and --admin-email")
                print("  Example: seed_security --admin-username admin --admin-password mypass123")
                print("           --admin-email admin@example.com --make-superuser")

        print("✓ Security seed completed successfully")
    finally:
        db.close()


def main() -> None:
    """CLI entry point for seeding security data."""
    parser = argparse.ArgumentParser(
        description="Seed predefined security roles, permissions, and optionally create/promote a superuser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Only seed roles and permissions
  python -m app.scripts.seed_security

  # Promote existing user to superuser
  python -m app.scripts.seed_security --admin-username admin --make-superuser

  # Create new superuser
  python -m app.scripts.seed_security --admin-username admin --admin-password mypass123 \\
    --admin-email admin@example.com --make-superuser
        """,
    )
    parser.add_argument("--admin-username", dest="admin_username", default=None, help="Username for superuser")
    parser.add_argument("--admin-password", dest="admin_password", default=None, help="Password for new superuser")
    parser.add_argument("--admin-email", dest="admin_email", default=None, help="Email for new superuser")
    parser.add_argument("--make-superuser", action="store_true", help="Create or promote user to superuser")
    args = parser.parse_args()

    seed_security(
        admin_username=args.admin_username,
        admin_password=args.admin_password,
        admin_email=args.admin_email,
        make_superuser=args.make_superuser,
    )


if __name__ == "__main__":
    main()
