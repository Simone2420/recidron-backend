from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.core.security import get_password_hash
from app.models import Permission, Role, User
from app.schemas import UserCreate, UserUpdate


class UserService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return (
            db.query(User)
            .options(
                joinedload(User.person),
                joinedload(User.roles).joinedload(Role.permissions),
                joinedload(User.permissions),
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return (
            db.query(User)
            .options(
                joinedload(User.person),
                joinedload(User.roles).joinedload(Role.permissions),
                joinedload(User.permissions),
            )
            .filter(User.id == user_id)
            .first()
        )

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create(db: Session, user: UserCreate) -> User:
        db_user = User(
            username=user.username,
            email=user.email,
            password_hash=get_password_hash(user.password),
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            person_id=user.person_id,
        )

        if user.role_ids:
            roles = db.query(Role).filter(Role.id.in_(user.role_ids)).all()
            db_user.roles = roles

        if user.permission_ids:
            permissions = db.query(Permission).filter(Permission.id.in_(user.permission_ids)).all()
            db_user.permissions = permissions

        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def update(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
        db_user = UserService.get_by_id(db, user_id)
        if not db_user:
            return None

        update_data = user.model_dump(exclude_unset=True, exclude={"password", "role_ids", "permission_ids"})
        for key, value in update_data.items():
            setattr(db_user, key, value)

        if user.password:
            db_user.password_hash = get_password_hash(user.password)

        if user.role_ids is not None:
            roles = db.query(Role).filter(Role.id.in_(user.role_ids)).all()
            db_user.roles = roles

        if user.permission_ids is not None:
            permissions = db.query(Permission).filter(Permission.id.in_(user.permission_ids)).all()
            db_user.permissions = permissions

        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        db_user = UserService.get_by_id(db, user_id)
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True

    @staticmethod
    def get_effective_permission_codes(user: User) -> List[str]:
        permission_codes = {permission.code for permission in user.permissions if permission.is_active}

        for role in user.roles:
            if not role.is_active:
                continue
            for permission in role.permissions:
                if permission.is_active:
                    permission_codes.add(permission.code)

        return sorted(permission_codes)
