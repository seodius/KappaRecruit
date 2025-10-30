"""
API endpoints for managing contacts.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

@router.post("/contacts", response_model=schemas.Contact)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Creates a new contact for the current user's company."""
    return crud.create_contact(db=db, contact=contact, company_id=current_user.company_id)

@router.get("/companies/{company_id}/contacts", response_model=List[schemas.Contact])
def read_contacts_for_company(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Retrieves a list of contacts for a specific company."""
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return crud.get_contacts_by_company(db, company_id=company_id, skip=skip, limit=limit)

@router.get("/contacts/{contact_id}", response_model=schemas.Contact)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Retrieves a single contact by its ID."""
    db_contact = crud.get_contact(db, contact_id=contact_id, company_id=current_user.company_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@router.put("/contacts/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Updates a contact's details."""
    db_contact = crud.update_contact(db, contact_id=contact_id, contact=contact, company_id=current_user.company_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@router.delete("/contacts/{contact_id}", response_model=schemas.Contact)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Deletes a contact."""
    db_contact = crud.delete_contact(db, contact_id=contact_id, company_id=current_user.company_id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact
