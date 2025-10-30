"""
Database configuration and session management for the ATS API.

This file sets up the SQLAlchemy engine, session factory, and a dependency
for providing database sessions to API endpoints.
"""

import json
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DATABASE_URL

def uuid_serializer(obj):
    """
    Custom JSON serializer to handle UUID objects, which are not
    natively serializable by the default JSON library.
    """
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError("Object of type UUID is not JSON serializable")

# Create the SQLAlchemy engine with the custom JSON serializer
engine = create_engine(DATABASE_URL, json_serializer=uuid_serializer)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative database models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency to provide a database session to API endpoints.
    This ensures that the database session is created and closed correctly
    for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
