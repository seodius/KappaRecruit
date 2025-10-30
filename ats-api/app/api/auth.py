"""
API endpoints for user authentication (registration and login).
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import crud, schemas, security, models
from ..database import get_db

router = APIRouter()

@router.post("/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Handles new user registration.

    Checks if the user already exists and, if not, creates a new user
    and returns a JWT access token.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    db_user = crud.create_user(db=db, user=user)
    access_token = security.create_access_token(
        data={"sub": user.email}, company_id=db_user.company_id
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/candidate/register", response_model=schemas.Token)
def register_candidate(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Handles new candidate registration.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create the candidate profile first
    candidate = crud.create_candidate(db=db, candidate=schemas.CandidateCreate(email=user.email), user_id=None, company_id=None)

    # Now create the user with the "Candidate" role
    candidate_role = db.query(models.Role).filter(models.Role.name == "Candidate").first()
    if not candidate_role:
        raise HTTPException(status_code=500, detail="Candidate role not found")

    user.role_id = candidate_role.role_id
    user.company_id = None # Candidates are not associated with a company
    db_user = crud.create_user(db=db, user=user)

    # Link the user and candidate
    db_user.candidate_id = candidate.candidate_id
    candidate.user_id = db_user.user_id
    db.commit()

    access_token = security.create_access_token(data={"sub": user.email}, company_id=None)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Handles user login.

    Verifies the user's credentials and, if successful, returns a JWT
    access token.
    """
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # The company_id can be None for candidate users
    access_token = security.create_access_token(
        data={"sub": user.email}, company_id=user.company_id
    )
    return {"access_token": access_token, "token_type": "bearer"}
