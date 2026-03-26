from datetime import datetime

from sqlalchemy.orm import Session, joinedload

from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from app.models import Permission, Person, Role, User
from app.schemas.security import UserCreate


PREDEFINED_PERMISSIONS: list[dict[str, str]] = [
    {"code": "users.read", "name": "View users", "description": "Can view users", "module": "users", "action": "read"},
    {"code": "users.create", "name": "Create users", "description": "Can create users", "module": "users", "action": "create"},
    {"code": "users.update", "name": "Update users", "description": "Can update users", "module": "users", "action": "update"},
    {"code": "users.assign_role", "name": "Assign roles", "description": "Can assign roles to users", "module": "users", "action": "assign_role"},
    {"code": "roles.read", "name": "View roles", "description": "Can view roles", "module": "roles", "action": "read"},
    {"code": "roles.create", "name": "Create roles", "description": "Can create roles", "module": "roles", "action": "create"},
    {"code": "roles.update", "name": "Update roles", "description": "Can update roles", "module": "roles", "action": "update"},
    {"code": "permissions.read", "name": "View permissions", "description": "Can view permissions", "module": "permissions", "action": "read"},
    {"code": "auth.read_me", "name": "Read own profile", "description": "Can access own profile endpoint", "module": "auth", "action": "read_me"},
    {"code": "auth.register", "name": "Register users", "description": "Can register users", "module": "auth", "action": "register"},
    {"code": "audit.read", "name": "View audit", "description": "Can view audit information", "module": "audit", "action": "read"},
    {"code": "security.seed", "name": "Seed security", "description": "Can execute security seeding", "module": "security", "action": "seed"},
]

PREDEFINED_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "admin": [p["code"] for p in PREDEFINED_PERMISSIONS],
    "user": ["users.read", "roles.read", "permissions.read", "auth.read_me", "audit.read"],
}

PREDEFINED_ROLE_DESCRIPTIONS: dict[str, str] = {
    "admin": "Full system access",
    "user": "Regular user with read-only access",
}


class SecurityService:
    @staticmethod
    def seed_security_catalog(db: Session) -> None:
        """
        Idempotent seeding of predefined security roles and permissions.

        Creates:
        - 12 permissions across modules: users, roles, permissions, auth, audit, security
        - 2 roles: 
          * admin: Full system access (all permissions)
          * user: Regular user with read-only access
        """
        permissions_by_code: dict[str, Permission] = {}

        for permission_data in PREDEFINED_PERMISSIONS:
            permission = db.query(Permission).filter(Permission.code == permission_data["code"]).first()
            if permission is None:
                permission = Permission(**permission_data)
                db.add(permission)
                db.flush()
            permissions_by_code[permission.code] = permission

        for role_name, permission_codes in PREDEFINED_ROLE_PERMISSIONS.items():
            role = db.query(Role).filter(Role.name == role_name).first()
            if role is None:
                role = Role(name=role_name, description=PREDEFINED_ROLE_DESCRIPTIONS.get(role_name), is_system=True)
                db.add(role)
                db.flush()

            role.permissions = [permissions_by_code[code] for code in permission_codes if code in permissions_by_code]

        db.commit()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> User | None:
        return (
            db.query(User)
            .options(
                joinedload(User.person),
                joinedload(User.roles).joinedload(Role.permissions),
            )
            .filter(User.username == username)
            .first()
        )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> User | None:
        user = SecurityService.get_user_by_username(db, username)
        if user is None:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None

        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def register_user(db: Session, payload: UserCreate) -> User:
        username_exists = db.query(User).filter(User.username == payload.username).first()
        if username_exists:
            raise ValueError("Username already exists")

        email_exists = db.query(Person).filter(Person.email == payload.person.email).first()
        if email_exists:
            raise ValueError("Email already exists")

        person = Person(
            first_name=payload.person.first_name,
            last_name=payload.person.last_name,
            email=payload.person.email,
            phone=payload.person.phone,
        )
        db.add(person)
        db.flush()

        user = User(
            person_id=person.id,
            username=payload.username,
            password_hash=get_password_hash(payload.password),
            is_active=True,
            is_superuser=False,
        )

        default_role = db.query(Role).filter(Role.name == "user").first()
        if default_role is not None:
            user.roles.append(default_role)

        db.add(user)
        db.commit()
        db.refresh(user)
        return SecurityService.get_user_by_username(db, user.username) or user

    @staticmethod
    def create_token_for_user(user: User) -> str:
        permission_codes = sorted({permission.code for role in user.roles for permission in role.permissions})
        role_names = sorted({role.name for role in user.roles})
        return create_access_token(
            subject=user.username,
            extra_claims={
                "uid": user.id,
                "roles": role_names,
                "permissions": permission_codes,
            },
        )

    @staticmethod
    def get_user_from_token(db: Session, token: str) -> User | None:
        payload = decode_access_token(token)
        if not payload:
            return None

        username = payload.get("sub")
        if not username:
            return None

        return SecurityService.get_user_by_username(db, username)

    @staticmethod
    def list_roles(db: Session) -> list[Role]:
        return db.query(Role).options(joinedload(Role.permissions)).order_by(Role.name.asc()).all()

    @staticmethod
    def list_permissions(db: Session) -> list[Permission]:
        return db.query(Permission).order_by(Permission.code.asc()).all()

    @staticmethod
    def assign_role_to_user(db: Session, user_id: int, role_name: str) -> User | None:
        user = (
            db.query(User)
            .options(joinedload(User.person), joinedload(User.roles).joinedload(Role.permissions))
            .filter(User.id == user_id)
            .first()
        )
        if user is None:
            return None

        role = db.query(Role).filter(Role.name == role_name).first()
        if role is None:
            raise ValueError("Role not found")

        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)

        return user

    @staticmethod
    def promote_user_to_admin(db: Session, user_id: int) -> User | None:
        user = (
            db.query(User)
            .options(joinedload(User.person), joinedload(User.roles).joinedload(Role.permissions))
            .filter(User.id == user_id)
            .first()
        )
        if user is None:
            return None

        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if admin_role is None:
            raise ValueError("Admin role not found")

        if admin_role not in user.roles:
            user.roles.append(admin_role)

        user_role = db.query(Role).filter(Role.name == "user").first()
        if user_role and user_role in user.roles:
            user.roles.remove(user_role)

        db.commit()
        db.refresh(user)
        return user
