from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Permission
from app.schemas import PermissionCreate, PermissionUpdate


class PermissionService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Permission]:
        return db.query(Permission).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, permission_id: int) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.id == permission_id).first()

    @staticmethod
    def get_by_code(db: Session, code: str) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.code == code).first()

    @staticmethod
    def create(db: Session, permission: PermissionCreate) -> Permission:
        db_permission = Permission(**permission.model_dump())
        db.add(db_permission)
        db.commit()
        db.refresh(db_permission)
        return db_permission

    @staticmethod
    def update(db: Session, permission_id: int, permission: PermissionUpdate) -> Optional[Permission]:
        db_permission = PermissionService.get_by_id(db, permission_id)
        if not db_permission:
            return None

        update_data = permission.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_permission, key, value)

        db.commit()
        db.refresh(db_permission)
        return db_permission

    @staticmethod
    def delete(db: Session, permission_id: int) -> bool:
        db_permission = PermissionService.get_by_id(db, permission_id)
        if not db_permission:
            return False

        db.delete(db_permission)
        db.commit()
        return True
