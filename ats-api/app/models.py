"""
SQLAlchemy database models for the Applicant Tracking System.

This file defines the database schema for the application, including all tables,
columns, and relationships between them.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime, timezone

# --- Enums for status fields ---

class JobStatus(str, enum.Enum):
    """Enum for the possible statuses of a job."""
    draft = "draft"
    open = "open"
    paused = "paused"
    filled = "filled"
    closed = "closed"

class ApplicationStatus(str, enum.Enum):
    """Enum for the possible statuses of an application."""
    applied = "applied"
    screening = "screening"
    interview = "interview"
    offer = "offer"
    hired = "hired"
    rejected = "rejected"

class InterviewType(str, enum.Enum):
    """Enum for the different types of interviews."""
    phone = "phone"
    video = "video"
    onsite = "onsite"

class ResumeStatus(str, enum.Enum):
    """Enum for the status of a resume, e.g., for parsing."""
    valid = "valid"
    invalid = "invalid"
    pending = "pending"

# --- Main Database Models ---

class Company(Base):
    """Represents a client company in the multi-tenant system."""
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    users = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")

class Role(Base):
    """Represents a user role for Role-Based Access Control (RBAC)."""
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    users = relationship("User", back_populates="role")

class User(Base):
    """Represents a user of the ATS (e.g., a recruiter, hiring manager)."""
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    role_id = Column(Integer, ForeignKey("roles.role_id"))

    company = relationship("Company", back_populates="users")
    role = relationship("Role", back_populates="users")

class Job(Base):
    """Represents a job posting."""
    __tablename__ = "jobs"
    job_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    data = Column(JSON)  # Stores detailed job info as a JSON blob

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
    status_history = relationship("JobStatusEvent", back_populates="job")

class Candidate(Base):
    """Represents a job candidate."""
    __tablename__ = "candidates"
    candidate_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    address = Column(Text)
    linkedin_profile = Column(String)
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"))
    job_title = Column(String)

    created_by = relationship("User")
    applications = relationship("Application", back_populates="candidate")
    resumes = relationship("Resume", back_populates="candidate")

class Resume(Base):
    """Represents a candidate's resume, including the file and parsed data."""
    __tablename__ = "resumes"
    resume_id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    file_location = Column(String, nullable=True) # Path to the uploaded file
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    parsed_data = Column(JSON) # Stores parsed resume data as a JSON blob

    candidate = relationship("Candidate", back_populates="resumes")

class Application(Base):
    """Links a Candidate to a Job, representing a job application."""
    __tablename__ = "applications"
    application_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source = Column(String) # e.g., 'LinkedIn', 'Company Website'

    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    status_history = relationship("ApplicationStatusEvent", back_populates="application")

class ApplicationStatusEvent(Base):
    """Tracks the history of status changes for an application."""
    __tablename__ = "application_status_events"
    event_id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.application_id"))
    status = Column(Enum(ApplicationStatus))
    changed_by_user_id = Column(Integer, ForeignKey("users.user_id"))
    reason = Column(String)
    next_action_date = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    application = relationship("Application", back_populates="status_history")

class Interview(Base):
    """Represents a scheduled interview for an application."""
    __tablename__ = "interviews"
    interview_id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.application_id"))
    scheduled_at = Column(DateTime)
    duration_minutes = Column(Integer)
    interview_type = Column(Enum(InterviewType))

    application = relationship("Application")
    interviewers = relationship("Interviewer", back_populates="interview")
    evaluations = relationship("Evaluation", back_populates="interview")

class Interviewer(Base):
    """Associates a User with an Interview."""
    __tablename__ = "interviewers"
    interviewer_id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.interview_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))

    interview = relationship("Interview", back_populates="interviewers")
    user = relationship("User")

class Evaluation(Base):
    """Stores feedback and ratings from an interviewer for an interview."""
    __tablename__ = "evaluations"
    evaluation_id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.interview_id"))
    interviewer_id = Column(Integer, ForeignKey("interviewers.interviewer_id"))
    rating = Column(Integer)
    feedback = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    interview = relationship("Interview", back_populates="evaluations")

class JobStatusEvent(Base):
    """Tracks the history of status changes for a job."""
    __tablename__ = "job_status_events"
    event_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    status = Column(Enum(JobStatus))
    changed_by_user_id = Column(Integer, ForeignKey("users.user_id"))
    reason = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    job = relationship("Job")
