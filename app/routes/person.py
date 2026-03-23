from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core import get_current_active_user
from app.database import get_db
from app.schemas import PersonCreate, PersonResponse, PersonUpdate
from app.services import PersonService

router = APIRouter(prefix="/persons", tags=["Persons"])


@router.get("/", response_model=List[PersonResponse])
def get_persons(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_active_user),
):
    return PersonService.get_all(db, skip, limit)


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_active_user),
):
    person = PersonService.get_by_id(db, person_id)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.post("/", response_model=PersonResponse, status_code=201)
def create_person(
    payload: PersonCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_active_user),
):
    return PersonService.create(db, payload)


@router.put("/{person_id}", response_model=PersonResponse)
def update_person(
    person_id: int,
    payload: PersonUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_active_user),
):
    person = PersonService.update(db, person_id, payload)
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.delete("/{person_id}", status_code=204)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_active_user),
):
    if not PersonService.delete(db, person_id):
        raise HTTPException(status_code=404, detail="Person not found")
    return None
