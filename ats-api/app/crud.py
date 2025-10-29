from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash

# Helper function to check company access for a candidate
def _is_candidate_in_company(db: Session, candidate_id: int, company_id: int):
    """
    Checks if a candidate is associated with a given company, either through
    an application or by having been created by a user from that company.
    """
    # Check for association through an application
    is_via_app = db.query(models.Candidate).join(models.Application).join(models.Job).filter(
        models.Candidate.candidate_id == candidate_id,
        models.Job.company_id == company_id
    ).first() is not None
    if is_via_app:
        return True

    # Check if the candidate was created by a user from the company
    candidate = db.query(models.Candidate).filter(models.Candidate.candidate_id == candidate_id).first()
    if candidate and candidate.created_by:
        try:
            created_by_info = json.loads(candidate.created_by)
            if created_by_info.get("company_id") == company_id:
                return True
        except json.JSONDecodeError:
            # Handle cases where created_by is not a valid JSON string
            return False

    return False

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        company_id=user.company_id,
        role_id=user.role_id,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Job CRUD
def get_job(db: Session, job_id: int, company_id: int):
    return db.query(models.Job).filter(models.Job.job_id == job_id, models.Job.company_id == company_id).first()

def get_jobs(db: Session, company_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Job).filter(models.Job.company_id == company_id).offset(skip).limit(limit).all()

def create_job(db: Session, job: schemas.JobCreate, company_id: int):
    job_data = job.model_dump()

    # Ensure the job is being created for the correct company
    if job.company_id != company_id:
        return None

    company = db.query(models.Company).filter_by(company_id=company_id).first()
    if not company:
        return None

    # The 'company' field is not part of the JobCreate schema anymore, so no need to remove it
    db_job = models.Job(
        company_id=company_id,
        data=job_data
    )
    db_job.company = company

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job(db: Session, job_id: int, job: schemas.JobCreate, company_id: int):
    db_job = get_job(db, job_id=job_id, company_id=company_id)
    if db_job:
        job_data = job.model_dump()
        db_job.data = job_data
        db.commit()
        db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: int, company_id: int):
    db_job = get_job(db, job_id=job_id, company_id=company_id)
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job

# Candidate CRUD
def get_candidate(db: Session, candidate_id: int, company_id: int):
    # First, try to find the candidate through an application, which is the most secure way.
    candidate = db.query(models.Candidate).join(models.Application).join(models.Job).filter(
        models.Candidate.candidate_id == candidate_id,
        models.Job.company_id == company_id
    ).first()

    # If no application exists, allow access if the candidate was created by a user from this company.
    if not candidate:
        candidate = db.query(models.Candidate).filter(
            models.Candidate.candidate_id == candidate_id,
            models.Candidate.created_by.contains(f'"company_id": {company_id}') # This is a simplification; direct relation is better
        ).first()

    return candidate

def get_candidates(db: Session, company_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Candidate).distinct(models.Candidate.candidate_id).join(models.Application).join(models.Job).filter(
        models.Job.company_id == company_id
    ).offset(skip).limit(limit).all()

import json

def get_candidate_by_email(db: Session, email: str, company_id: int):
    # This check is simplified. A more robust implementation would check
    # if a candidate with this email is accessible to the company,
    # either through an application or by being created by a user from that company.
    return db.query(models.Candidate).filter(models.Candidate.email == email).first()

def create_candidate(db: Session, candidate: schemas.CandidateCreate, user_id: int, company_id: int):
    created_by_info = {"user_id": user_id, "company_id": company_id}
    db_candidate = models.Candidate(
        **candidate.model_dump(),
        created_by=json.dumps(created_by_info)
    )
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate

def update_candidate(db: Session, candidate_id: int, candidate: schemas.CandidateCreate, company_id: int):
    if not _is_candidate_in_company(db, candidate_id, company_id):
        return None
    db_candidate = db.query(models.Candidate).filter(models.Candidate.candidate_id == candidate_id).first()
    if db_candidate:
        update_data = candidate.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_candidate, key, value)
        db.commit()
        db.refresh(db_candidate)
    return db_candidate

def delete_candidate(db: Session, candidate_id: int, company_id: int):
    if not _is_candidate_in_company(db, candidate_id, company_id):
        return None
    db_candidate = db.query(models.Candidate).filter(models.Candidate.candidate_id == candidate_id).first()
    if db_candidate:
        db.delete(db_candidate)
        db.commit()
    return db_candidate

# Application CRUD
def get_application(db: Session, application_id: int, company_id: int):
    return db.query(models.Application).join(models.Job).filter(
        models.Application.application_id == application_id,
        models.Job.company_id == company_id
    ).first()

def get_applications(db: Session, company_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Application).join(models.Job).filter(
        models.Job.company_id == company_id
    ).offset(skip).limit(limit).all()

def create_application(db: Session, application: schemas.ApplicationCreate, company_id: int):
    # Verify the job exists and belongs to the company
    db_job = get_job(db, job_id=application.job_id, company_id=company_id)
    if not db_job:
        return None
    db_application = models.Application(**application.model_dump())
    db.add(db_application)
    db.commit()
    db.refresh(db_application)
    return db_application

def update_application(db: Session, application_id: int, application: schemas.ApplicationCreate, company_id: int):
    db_application = get_application(db, application_id=application_id, company_id=company_id)
    if db_application:
        # Ensure the new job_id also belongs to the company
        if application.job_id != db_application.job_id:
            if not get_job(db, job_id=application.job_id, company_id=company_id):
                return None
        update_data = application.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_application, key, value)
        db.commit()
        db.refresh(db_application)
    return db_application

def delete_application(db: Session, application_id: int, company_id: int):
    db_application = get_application(db, application_id=application_id, company_id=company_id)
    if db_application:
        db.delete(db_application)
        db.commit()
    return db_application

# Resume CRUD
def create_resume(db: Session, resume: schemas.ResumeCreate, company_id: int, file_location: str):
    if not _is_candidate_in_company(db, resume.candidate_id, company_id):
        return None

    resume_data_dict = resume.model_dump()

    db_resume = models.Resume(
        candidate_id=resume.candidate_id,
        parsed_data=resume_data_dict,
        file_location=file_location
    )
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    return db_resume

def get_resumes_by_candidate(db: Session, candidate_id: int, company_id: int):
    if not _is_candidate_in_company(db, candidate_id, company_id):
        return []
    return db.query(models.Resume).filter(models.Resume.candidate_id == candidate_id).all()

def get_resume(db: Session, resume_id: int, company_id: int):
    resume = db.query(models.Resume).filter(models.Resume.resume_id == resume_id).first()
    if resume and _is_candidate_in_company(db, resume.candidate_id, company_id):
        return resume
    return None

def update_resume(db: Session, resume_id: int, resume: schemas.ResumeCreate, company_id: int):
    db_resume = get_resume(db, resume_id, company_id)
    if db_resume:
        update_data = resume.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_resume, key, value)
        db.commit()
        db.refresh(db_resume)
    return db_resume

def delete_resume(db: Session, resume_id: int, company_id: int):
    db_resume = get_resume(db, resume_id, company_id)
    if db_resume:
        db.delete(db_resume)
        db.commit()
    return db_resume

# Job Status Event CRUD
def create_job_status_event(db: Session, event: schemas.JobStatusEventCreate, job_id: int, company_id: int):
    db_job = get_job(db, job_id=job_id, company_id=company_id)
    if not db_job:
        return None
    db_event = models.JobStatusEvent(**event.model_dump(), job_id=job_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# Application Status Event CRUD
def create_application_status_event(db: Session, event: schemas.ApplicationStatusEventCreate, application_id: int, company_id: int):
    db_application = get_application(db, application_id=application_id, company_id=company_id)
    if not db_application:
        return None
    db_event = models.ApplicationStatusEvent(**event.model_dump(), application_id=application_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# Interview CRUD
def create_interview(db: Session, interview: schemas.InterviewCreate, application_id: int, company_id: int):
    db_application = get_application(db, application_id=application_id, company_id=company_id)
    if not db_application:
        return None
    db_interview = models.Interview(
        application_id=application_id,
        scheduled_at=interview.scheduled_at,
        duration_minutes=interview.duration_minutes,
        interview_type=interview.interview_type,
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    for interviewer in interview.interviewers:
        db_interviewer = models.Interviewer(
            interview_id=db_interview.interview_id,
            user_id=interviewer.user_id,
        )
        db.add(db_interviewer)
    db.commit()
    db.refresh(db_interview)
    return db_interview

def get_interview(db: Session, interview_id: int, company_id: int):
    return db.query(models.Interview).join(models.Application).join(models.Job).filter(
        models.Interview.interview_id == interview_id,
        models.Job.company_id == company_id
    ).first()

def create_evaluation(db: Session, evaluation: schemas.EvaluationCreate, interview_id: int, company_id: int):
    db_interview = get_interview(db, interview_id=interview_id, company_id=company_id)
    if not db_interview:
        return None
    db_evaluation = models.Evaluation(**evaluation.model_dump(), interview_id=interview_id)
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation
