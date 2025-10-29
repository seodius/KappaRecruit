from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from .database import Base
import enum
from datetime import datetime, timezone

class JobStatus(str, enum.Enum):
    draft = "draft"
    open = "open"
    paused = "paused"
    filled = "filled"
    closed = "closed"

class ApplicationStatus(str, enum.Enum):
    applied = "applied"
    screening = "screening"
    interview = "interview"
    offer = "offer"
    hired = "hired"
    rejected = "rejected"

class InterviewType(str, enum.Enum):
    phone = "phone"
    video = "video"
    onsite = "onsite"

class ResumeStatus(str, enum.Enum):
    valid = "valid"
    invalid = "invalid"
    pending = "pending"

class Company(Base):
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    users = relationship("User", back_populates="company")
    jobs = relationship("Job", back_populates="company")

class Role(Base):
    __tablename__ = "roles"
    role_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="role")

class User(Base):
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
    __tablename__ = "jobs"
    job_id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    data = Column(JSON)
    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")
    status_history = relationship("JobStatusEvent", back_populates="job")

from sqlalchemy import Boolean

class Candidate(Base):
    __tablename__ = "candidates"
    candidate_id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String)
    address = Column(Text)
    linkedin_profile = Column(String)
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = Column(String)
    job_title = Column(String)
    applications = relationship("Application", back_populates="candidate")
    resumes = relationship("Resume", back_populates="candidate")

class Resume(Base):
    __tablename__ = "resumes"
    resume_id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    file_location = Column(String, nullable=True)
    date_created = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    parsed_data = Column(JSON)
    candidate = relationship("Candidate", back_populates="resumes")

class Application(Base):
    __tablename__ = "applications"
    application_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    candidate_id = Column(Integer, ForeignKey("candidates.candidate_id"))
    applied_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source = Column(String)
    job = relationship("Job", back_populates="applications")
    candidate = relationship("Candidate", back_populates="applications")
    status_history = relationship("ApplicationStatusEvent", back_populates="application")

class ApplicationStatusEvent(Base):
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
    __tablename__ = "interviewers"
    interviewer_id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.interview_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    interview = relationship("Interview", back_populates="interviewers")
    user = relationship("User")

class Evaluation(Base):
    __tablename__ = "evaluations"
    evaluation_id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.interview_id"))
    interviewer_id = Column(Integer, ForeignKey("interviewers.interviewer_id"))
    rating = Column(Integer)
    feedback = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    interview = relationship("Interview", back_populates="evaluations")

class JobStatusEvent(Base):
    __tablename__ = "job_status_events"
    event_id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id"))
    status = Column(Enum(JobStatus))
    changed_by_user_id = Column(Integer, ForeignKey("users.user_id"))
    reason = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    job = relationship("Job")
