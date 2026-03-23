from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import Permission, Role
from app.schemas import RoleCreate, RoleUpdate


class RoleService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
        return (
            db.query(Role)
            .options(joinedload(Role.permissions))
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_id(db: Session, role_id: int) -> Optional[Role]:
        return (
            db.query(Role)
            .options(joinedload(Role.permissions))
            .filter(Role.id == role_id)
            .first()
        )

    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def create(db: Session, role: RoleCreate) -> Role:
        db_role = Role(
            name=role.name,
            description=role.description,
            is_active=role.is_active,
        )

        if role.permission_ids:
            permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all()
            db_role.permissions = permissions

        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role

    @staticmethod
    def update(db: Session, role_id: int, role: RoleUpdate) -> Optional[Role]:
        db_role = RoleService.get_by_id(db, role_id)
        if not db_role:
            return None

        update_data = role.model_dump(exclude_unset=True, exclude={"permission_ids"})
        for key, value in update_data.items():
            setattr(db_role, key, value)

        if role.permission_ids is not None:
            permissions = db.query(Permission).filter(Permission.id.in_(role.permission_ids)).all()
            db_role.permissions = permissions

        db.commit()
        db.refresh(db_role)
        return db_role

    @staticmethod
    def delete(db: Session, role_id: int) -> bool:
        db_role = RoleService.get_by_id(db, role_id)
        if not db_role:
            return False

        db.delete(db_role)
        db.commit()
        return True
