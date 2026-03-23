from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Person
from app.schemas import PersonCreate, PersonUpdate


class PersonService:
    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Person]:
        return db.query(Person).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, person_id: int) -> Optional[Person]:
        return db.query(Person).filter(Person.id == person_id).first()

    @staticmethod
    def create(db: Session, person: PersonCreate) -> Person:
        db_person = Person(**person.model_dump())
        db.add(db_person)
        db.commit()
        db.refresh(db_person)
        return db_person

    @staticmethod
    def update(db: Session, person_id: int, person: PersonUpdate) -> Optional[Person]:
        db_person = PersonService.get_by_id(db, person_id)
        if not db_person:
            return None

        update_data = person.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_person, key, value)

        db.commit()
        db.refresh(db_person)
        return db_person

    @staticmethod
    def delete(db: Session, person_id: int) -> bool:
        db_person = PersonService.get_by_id(db, person_id)
        if not db_person:
            return False

        db.delete(db_person)
        db.commit()
        return True
