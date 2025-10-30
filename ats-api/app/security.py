"""
Security-related functions for the ATS API.

This file includes password hashing, JWT creation and decoding, and the main
FastAPI dependency for authenticating users and enforcing multi-tenancy.
"""

import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import crud, schemas
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .database import get_db

# Define the OAuth2 password bearer scheme, which specifies the token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    """Verifies a plain-text password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    """Hashes a plain-text password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict, company_id: int):
    """
    Creates a new JWT access token.

    The token includes the user's identity (`sub`), an expiration time (`exp`),
    and the `company_id` for multi-tenancy enforcement.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "company_id": company_id})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    FastAPI dependency to get the current authenticated user from a JWT.

    This function decodes the JWT, validates its signature and expiration,
    and retrieves the user from the database. It also enforces multi-tenancy
    by ensuring the user belongs to the `company_id` encoded in the token.
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        company_id: int = payload.get("company_id")
        if email is None or company_id is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email, company_id=company_id)
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_email(db, email=token_data.email)

    # Security check: Ensure the user exists and belongs to the company specified in the token.
    if user is None or user.company_id != token_data.company_id:
        raise credentials_exception

    return user
