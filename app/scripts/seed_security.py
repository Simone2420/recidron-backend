import argparse
from typing import Dict, List

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Permission, Role, User

PERMISSIONS_SEED: List[Dict[str, str]] = [
    {"code": "user.read", "name": "Read users", "description": "List and read users"},
    {"code": "user.create", "name": "Create users", "description": "Create new users"},
    {"code": "user.update", "name": "Update users", "description": "Update existing users"},
    {"code": "user.delete", "name": "Delete users", "description": "Delete users"},
    {"code": "role.read", "name": "Read roles", "description": "List and read roles"},
    {"code": "role.create", "name": "Create roles", "description": "Create new roles"},
    {"code": "role.update", "name": "Update roles", "description": "Update existing roles"},
    {"code": "role.delete", "name": "Delete roles", "description": "Delete roles"},
    {
        "code": "permission.read",
        "name": "Read permissions",
        "description": "List and read permissions",
    },
    {
        "code": "permission.create",
        "name": "Create permissions",
        "description": "Create new permissions",
    },
    {
        "code": "permission.update",
        "name": "Update permissions",
        "description": "Update existing permissions",
    },
    {
        "code": "permission.delete",
        "name": "Delete permissions",
        "description": "Delete permissions",
    },
]

ROLES_SEED: Dict[str, Dict[str, object]] = {
    "admin": {
        "description": "Full access to security resources",
        "permissions": [perm["code"] for perm in PERMISSIONS_SEED],
    },
    "security_manager": {
        "description": "Can manage users, roles and permissions",
        "permissions": [perm["code"] for perm in PERMISSIONS_SEED],
    },
    "security_viewer": {
        "description": "Read-only access to security resources",
        "permissions": [
            "user.read",
            "role.read",
            "permission.read",
        ],
    },
}


def upsert_permissions(db: Session) -> Dict[str, Permission]:
    permissions_by_code: Dict[str, Permission] = {}

    for permission_data in PERMISSIONS_SEED:
        code = permission_data["code"]
        permission = db.query(Permission).filter(Permission.code == code).first()

        if not permission:
            permission = Permission(
                code=code,
                name=permission_data["name"],
                description=permission_data["description"],
                is_active=True,
            )
            db.add(permission)
        else:
            permission.name = permission_data["name"]
            permission.description = permission_data["description"]
            permission.is_active = True

        permissions_by_code[code] = permission

    db.flush()

    return permissions_by_code


def upsert_roles(db: Session, permissions_by_code: Dict[str, Permission]) -> Dict[str, Role]:
    roles_by_name: Dict[str, Role] = {}

    for role_name, role_data in ROLES_SEED.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=str(role_data["description"]), is_active=True)
            db.add(role)
        else:
            role.description = str(role_data["description"])
            role.is_active = True

        permission_codes = role_data["permissions"]
        role.permissions = [permissions_by_code[code] for code in permission_codes if code in permissions_by_code]
        roles_by_name[role_name] = role

    db.flush()

    return roles_by_name


def assign_admin_role(db: Session, username: str, roles_by_name: Dict[str, Role], make_superuser: bool) -> bool:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False

    admin_role = roles_by_name["admin"]
    if admin_role not in user.roles:
        user.roles.append(admin_role)

    user.is_active = True
    if make_superuser:
        user.is_superuser = True

    db.flush()
    return True


def seed_security(admin_username: str | None = None, make_superuser: bool = False) -> None:
    db: Session = SessionLocal()

    try:
        permissions_by_code = upsert_permissions(db)
        roles_by_name = upsert_roles(db, permissions_by_code)

        assigned_admin = False
        if admin_username:
            assigned_admin = assign_admin_role(db, admin_username, roles_by_name, make_superuser)

        db.commit()

        print(f"Seed completed: {len(permissions_by_code)} permissions, {len(roles_by_name)} roles")
        if admin_username and assigned_admin:
            print(f"Assigned 'admin' role to user '{admin_username}'")
            if make_superuser:
                print(f"User '{admin_username}' marked as superuser")
        elif admin_username:
            print(f"User '{admin_username}' not found. Roles and permissions were still seeded.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed security permissions and roles")
    parser.add_argument(
        "--admin-username",
        dest="admin_username",
        help="Existing username to receive the 'admin' role",
    )
    parser.add_argument(
        "--make-superuser",
        action="store_true",
        help="Also mark the target user as superuser",
    )

    args = parser.parse_args()
    seed_security(admin_username=args.admin_username, make_superuser=args.make_superuser)
