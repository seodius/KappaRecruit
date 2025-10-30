from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

@router.post("/candidates", response_model=schemas.Candidate)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_candidate = crud.get_candidate_by_email(db, email=candidate.email, company_id=current_user.company_id)
    if db_candidate:
        # If the candidate exists and is accessible, return it to avoid duplicates.
        return db_candidate

    # If the candidate does not exist, create a new one.
    return crud.create_candidate(db=db, candidate=candidate, user_id=current_user.user_id, company_id=current_user.company_id)

@router.get("/candidates", response_model=List[schemas.Candidate])
def read_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    candidates = crud.get_candidates(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return candidates

@router.get("/candidates/{candidate_id}", response_model=schemas.Candidate)
def read_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_candidate = crud.get_candidate(db, candidate_id=candidate_id, company_id=current_user.company_id)
    if db_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return db_candidate

@router.put("/candidates/{candidate_id}", response_model=schemas.Candidate)
def update_candidate(candidate_id: int, candidate: schemas.CandidateCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_candidate = crud.update_candidate(db, candidate_id=candidate_id, candidate=candidate, company_id=current_user.company_id)
    if db_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return db_candidate

@router.delete("/candidates/{candidate_id}", response_model=schemas.Candidate)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_candidate = crud.delete_candidate(db, candidate_id=candidate_id, company_id=current_user.company_id)
    if db_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return db_candidate
