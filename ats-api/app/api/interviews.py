from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

@router.post("/applications/{application_id}/interviews", response_model=schemas.Interview)
def create_interview_for_application(
    application_id: int,
    interview: schemas.InterviewCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    db_interview = crud.create_interview(db=db, interview=interview, application_id=application_id, company_id=current_user.company_id)
    if db_interview is None:
        raise HTTPException(status_code=404, detail="Application not found or access denied.")
    return db_interview

@router.get("/interviews/{interview_id}", response_model=schemas.Interview)
def read_interview(interview_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_interview = crud.get_interview(db, interview_id=interview_id, company_id=current_user.company_id)
    if db_interview is None:
        raise HTTPException(status_code=404, detail="Interview not found")
    return db_interview

@router.post("/interviews/{interview_id}/evaluations", response_model=schemas.Evaluation)
def create_evaluation_for_interview(
    interview_id: int,
    evaluation: schemas.EvaluationCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    db_evaluation = crud.create_evaluation(db=db, evaluation=evaluation, interview_id=interview_id, company_id=current_user.company_id)
    if db_evaluation is None:
        raise HTTPException(status_code=404, detail="Interview not found or access denied.")
    return db_evaluation
