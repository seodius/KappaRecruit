"""
API endpoints for managing candidates.

These endpoints handle the creation, retrieval, updating, and deletion of
candidates, with multi-tenancy enforced to ensure data privacy.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

@router.post("/candidates", response_model=schemas.Candidate)
def create_candidate(candidate: schemas.CandidateCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """
    Creates a new candidate or retrieves an existing one with the same email.

    This prevents duplicate candidate profiles and associates the new candidate
    with the user and company that created them.
    """
    db_candidate = crud.get_candidate_by_email(db, email=candidate.email, company_id=current_user.company_id)
    if db_candidate:
        return db_candidate

    return crud.create_candidate(db=db, candidate=candidate, user_id=current_user.user_id, company_id=current_user.company_id)

@router.get("/candidates", response_model=List[schemas.Candidate])
def read_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Retrieves a list of candidates accessible to the current user's company."""
    candidates = crud.get_candidates(db, company_id=current_user.company_id, skip=skip, limit=limit)
    return candidates

@router.get("/candidates/{candidate_id}", response_model=schemas.Candidate)
def read_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Retrieves a single candidate by ID, ensuring they are accessible to the company."""
    db_candidate = crud.get_candidate(db, candidate_id=candidate_id, company_id=current_user.company_id)
    if db_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return db_candidate

@router.put("/candidates/{candidate_id}", response_model=schemas.Candidate)
def update_candidate(candidate_id: int, candidate: schemas.CandidateCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Updates a candidate's details, ensuring they are accessible to the company."""
    db_candidate = crud.update_candidate(db, candidate_id=candidate_id, candidate=candidate, company_id=current_user.company_id)
    if db_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return db_candidate

@router.delete("/candidates/{candidate_id}", response_model=schemas.Candidate)
def delete_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    """Deletes a candidate, ensuring they are accessible to the company."""
    db_candidate = crud.delete_candidate(db, candidate_id=candidate_id, company_id=current_user.company_id)
    if db_candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return db_candidate
