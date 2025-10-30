"""
API endpoints for candidates to manage their own data.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

@router.get("/me/profile", response_model=schemas.Candidate)
def read_my_profile(db: Session = Depends(get_db), current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Candidate"]))):
    """Retrieves the current candidate's profile."""
    if not current_user.candidate_id:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return crud.get_candidate(db, candidate_id=current_user.candidate_id, user_id=current_user.user_id)

@router.put("/me/profile", response_model=schemas.Candidate)
def update_my_profile(
    candidate: schemas.CandidateCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Candidate"]))
):
    """Updates the current candidate's profile."""
    if not current_user.candidate_id:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return crud.update_candidate(db, candidate_id=current_user.candidate_id, candidate=candidate, company_id=None)

@router.get("/me/resumes", response_model=List[schemas.Resume])
def read_my_resumes(db: Session = Depends(get_db), current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Candidate"]))):
    """Retrieves the current candidate's resumes."""
    if not current_user.candidate_id:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    return crud.get_resumes_by_candidate(db, candidate_id=current_user.candidate_id, company_id=None)

@router.get("/me/interviews", response_model=List[schemas.Interview])
def read_my_interviews(db: Session = Depends(get_db), current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Candidate"]))):
    """Retrieves the current candidate's scheduled interviews."""
    if not current_user.candidate_id:
        raise HTTPException(status_code=404, detail="Candidate profile not found")
    # This is a simplified implementation. A real implementation would need a new CRUD function
    # to get interviews by candidate_id.
    applications = crud.get_applications_by_candidate(db, candidate_id=current_user.candidate_id)
    interviews = []
    for app in applications:
        interviews.extend(app.interviews)
    return interviews
