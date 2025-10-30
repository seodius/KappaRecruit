"""
API endpoints for managing job applications.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

@router.post("/applications", response_model=schemas.Application)
def create_application(application: schemas.ApplicationCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Creates a new application, linking a candidate to a job."""
    db_application = crud.create_application(db=db, application=application, company_id=current_user.company_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Job not found or access denied.")
    return db_application

@router.get("/applications", response_model=List[schemas.Application])
def read_applications(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Retrieves a list of applications for the current user's company."""
    applications = crud.get_applications(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return applications

@router.get("/applications/{application_id}", response_model=schemas.Application)
def read_application(application_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Retrieves a single application by ID."""
    db_application = crud.get_application(db, application_id=application_id, company_id=current_user.company_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application

@router.put("/applications/{application_id}", response_model=schemas.Application)
def update_application(application_id: int, application: schemas.ApplicationCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Updates an application's details."""
    db_application = crud.update_application(db, application_id=application_id, application=application, company_id=current_user.company_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application

@router.delete("/applications/{application_id}", response_model=schemas.Application)
def delete_application(application_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Deletes an application."""
    db_application = crud.delete_application(db, application_id=application_id, company_id=current_user.company_id)
    if db_application is None:
        raise HTTPException(status_code=404, detail="Application not found")
    return db_application

@router.post("/applications/{application_id}/status", response_model=schemas.ApplicationStatusEvent)
def create_application_status_event(
    application_id: int,
    event: schemas.ApplicationStatusEventCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Creates a new status event for an application (e.g., moving to 'interview' stage)."""
    db_event = crud.create_application_status_event(db=db, event=event, application_id=application_id, company_id=current_user.company_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Application not found or access denied.")
    return db_event
