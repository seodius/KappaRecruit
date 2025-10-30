from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas
from ..database import get_db

router = APIRouter()

from typing import List

from .. import security

@router.post("/jobs", response_model=schemas.Job)
def create_job(job: schemas.JobCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_job = crud.create_job(db=db, job=job, company_id=current_user.company_id)
    if db_job is None:
        raise HTTPException(status_code=400, detail="Job could not be created for this company.")
    return db_job

@router.get("/jobs", response_model=List[schemas.Job])
def read_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    jobs = crud.get_jobs(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return jobs

@router.get("/jobs/{job_id}", response_model=schemas.Job)
def read_job(job_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_job = crud.get_job(db, job_id=job_id, company_id=current_user.company_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@router.post("/jobs/{job_id}/status", response_model=schemas.JobStatusEvent)
def create_job_status_event(
    job_id: int,
    event: schemas.JobStatusEventCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    db_event = crud.create_job_status_event(db=db, event=event, job_id=job_id, company_id=current_user.company_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Job not found or access denied.")
    return db_event

@router.put("/jobs/{job_id}", response_model=schemas.Job)
def update_job(job_id: int, job: schemas.JobCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_job = crud.update_job(db, job_id=job_id, job=job, company_id=current_user.company_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@router.delete("/jobs/{job_id}", response_model=schemas.Job)
def delete_job(job_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_job = crud.delete_job(db, job_id=job_id, company_id=current_user.company_id)
    if db_job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job
