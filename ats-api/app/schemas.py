"""
Pydantic schemas for the Applicant Tracking System API.

This file defines the data structures used for API requests and responses,
providing data validation, serialization, and documentation.
"""

from pydantic import BaseModel, model_validator, ConfigDict
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from .models import JobStatus, ApplicationStatus, InterviewType
from .models import JobStatus as JobStatusEnum

# --- User Schemas ---

class UserBase(BaseModel):
    """Base schema for user data."""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str
    company_id: int
    role_id: int

class User(UserBase):
    """Schema for representing a user in API responses."""
    user_id: int
    company_id: int
    role_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Role Schemas ---

class RoleBase(BaseModel):
    """Base schema for a role."""
    name: str
    permissions: Optional[List[str]] = []

class RoleCreate(RoleBase):
    """Schema for creating a new role."""
    pass

class RoleUpdate(RoleBase):
    """Schema for updating an existing role."""
    pass

class Role(RoleBase):
    """Schema for representing a role in API responses."""
    role_id: int

    model_config = ConfigDict(from_attributes=True)

# --- Department and Contact Schemas ---

class ContactBase(BaseModel):
    """Base schema for a contact."""
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None

class ContactCreate(ContactBase):
    """Schema for creating a new contact."""
    company_id: Optional[int] = None
    department_id: Optional[int] = None

class ContactUpdate(ContactBase):
    """Schema for updating a contact."""
    pass

class Contact(ContactBase):
    """Schema for representing a contact in API responses."""
    contact_id: int
    company_id: Optional[int] = None
    department_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class DepartmentBase(BaseModel):
    """Base schema for a department."""
    name: str
    parent_department_id: Optional[int] = None

class DepartmentCreate(DepartmentBase):
    """Schema for creating a new department."""
    company_id: int

class DepartmentUpdate(DepartmentBase):
    """Schema for updating a department."""
    pass

class Department(DepartmentBase):
    """Schema for representing a department in API responses."""
    department_id: int
    company_id: int
    contacts: List[Contact] = []
    children: List['Department'] = []
    model_config = ConfigDict(from_attributes=True)

# --- Event Schemas (for status histories) ---

class JobStatusEventBase(BaseModel):
    """Base schema for a job status event."""
    status: JobStatusEnum
    reason: Optional[str] = None

class JobStatusEventCreate(JobStatusEventBase):
    """Schema for creating a new job status event."""
    changed_by_user_id: int

class JobStatusEvent(JobStatusEventBase):
    """Schema for representing a job status event in API responses."""
    event_id: int
    job_id: int
    changed_by_user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Interview & Evaluation Schemas ---

class EvaluationBase(BaseModel):
    """Base schema for an interview evaluation."""
    rating: int
    feedback: str

class EvaluationCreate(EvaluationBase):
    """Schema for creating a new evaluation."""
    interviewer_id: int

class Evaluation(EvaluationBase):
    """Schema for representing an evaluation in API responses."""
    evaluation_id: int
    interview_id: int
    interviewer_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterviewerBase(BaseModel):
    """Base schema for an interviewer."""
    user_id: int

class InterviewerCreate(InterviewerBase):
    """Schema for creating a new interviewer."""
    pass

class Interviewer(InterviewerBase):
    """Schema for representing an interviewer in API responses."""
    interviewer_id: int
    interview_id: int

    model_config = ConfigDict(from_attributes=True)

class InterviewBase(BaseModel):
    """Base schema for an interview."""
    scheduled_at: datetime
    duration_minutes: int
    interview_type: InterviewType

class InterviewCreate(InterviewBase):
    """Schema for creating a new interview."""
    interviewers: List[InterviewerCreate]

class Interview(InterviewBase):
    """Schema for representing an interview in API responses."""
    interview_id: int
    application_id: int
    interviewers: List[Interviewer] = []
    evaluations: List[Evaluation] = []

    model_config = ConfigDict(from_attributes=True)

# --- Job Schemas (based on a detailed, nested structure) ---

class Requirement(BaseModel):
    """Schema for a job requirement."""
    description: str
    weight: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class CompanyInfo(BaseModel):
    """Schema for detailed company information within a job posting."""
    name: str
    description: Optional[str] = None
    websiteUrl: Optional[str] = None
    logoUrl: Optional[str] = None
    industry: Optional[str] = None
    mission: Optional[str] = None
    cultureSummary: Optional[str] = None
    values: Optional[List[str]] = None
    diversityStatement: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class LocationInfo(BaseModel):
    """Schema for job location details."""
    type: str
    address: Optional[dict] = None
    remotePolicy: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class Compensation(BaseModel):
    """Schema for job compensation details."""
    type: str
    currency: str
    minAmount: Optional[float] = None
    maxAmount: Optional[float] = None
    summary: Optional[str] = None
    benefits: Optional[List[dict]] = None
    model_config = ConfigDict(from_attributes=True)

class InterviewStep(BaseModel):
    """Schema for a step in the interview process."""
    step: int
    type: str
    description: str
    model_config = ConfigDict(from_attributes=True)

class HiringManager(BaseModel):
    """Schema for the hiring manager associated with a job."""
    userId: UUID
    name: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class JobDescription(BaseModel):
    """Schema for a single, detailed job description."""
    text: str
    goal: Optional[str] = None
    target_platform: Optional[str] = None
    language: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    """Base schema for a job posting, containing the detailed, nested structure."""
    jobId: str
    descriptions: List[JobDescription]
    location: LocationInfo
    employmentType: str
    responsibilities: List[str]
    requirements: Optional[List[Requirement]] = None
    niceToHaves: Optional[List[Requirement]] = None
    department: Optional[str] = None
    experienceLevel: Optional[str] = None
    compensation: Optional[Compensation] = None
    postedDate: Optional[datetime] = None
    closingDate: Optional[datetime] = None
    applyUrl: Optional[str] = None
    interviewProcess: Optional[List[InterviewStep]] = None
    hiringManager: Optional[HiringManager] = None
    openings: Optional[int] = 1
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

class JobCreate(JobBase):
    """Schema for creating a new job posting."""
    company_id: int

class Job(JobBase):
    """Schema for representing a job in API responses."""
    job_id: int
    company_id: int
    company: CompanyInfo
    status_history: List[JobStatusEvent] = []

    @model_validator(mode='before')
    def flatten_orm_data(cls, v):
        """
        Pydantic validator to map data from the SQLAlchemy ORM model to this schema.
        It unnests the JSON data from the `data` column and populates the `company`
        field from the ORM relationship.
        """
        if hasattr(v, '_sa_instance_state'):
            flat_dict = v.data.copy() if v.data else {}
            flat_dict['job_id'] = v.job_id
            flat_dict['company_id'] = v.company_id
            flat_dict['status_history'] = v.status_history
            if v.company:
                flat_dict['company'] = v.company
            return flat_dict
        return v

    model_config = ConfigDict(from_attributes=True)

# --- Candidate Schemas ---

class CandidateBase(BaseModel):
    """Base schema for candidate data."""
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin_profile: Optional[str] = None
    job_title: Optional[str] = None

class CandidateCreate(CandidateBase):
    """Schema for creating a new candidate."""
    pass

class Candidate(CandidateBase):
    """Schema for representing a candidate in API responses."""
    candidate_id: int
    model_config = ConfigDict(from_attributes=True)

# --- Application Schemas ---

class ApplicationStatusEventBase(BaseModel):
    status: ApplicationStatus
    reason: Optional[str] = None
    next_action_date: Optional[datetime] = None

class ApplicationStatusEventCreate(ApplicationStatusEventBase):
    changed_by_user_id: int

class ApplicationStatusEvent(ApplicationStatusEventBase):
    event_id: int
    application_id: int
    changed_by_user_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ApplicationBase(BaseModel):
    source: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    job_id: int
    candidate_id: int

class Application(ApplicationBase):
    application_id: int
    job_id: int
    candidate_id: int
    applied_at: datetime
    status_history: List[ApplicationStatusEvent] = []
    model_config = ConfigDict(from_attributes=True)

# --- Auth Schemas ---

class Token(BaseModel):
    """Schema for the JWT access token."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Schema for the data encoded within a JWT."""
    email: Optional[str] = None
    company_id: Optional[int] = None

# --- Unified Resume Schemas ---

class Meta(BaseModel):
    schemaVersion: Optional[str] = "1.0.0"
    source: Optional[str] = None
    createdAt: Optional[datetime] = None
    lastModified: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class Location(BaseModel):
    address: Optional[str] = None
    postalCode: Optional[str] = None
    city: Optional[str] = None
    countryCode: Optional[str] = None
    region: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class Profile(BaseModel):
    network: str
    username: Optional[str] = None
    url: str
    model_config = ConfigDict(from_attributes=True)

class Basics(BaseModel):
    name: str
    label: Optional[str] = None
    image: Optional[str] = None
    email: str
    phone: Optional[str] = None
    summary: Optional[str] = None
    location: Optional[Location] = None
    profiles: Optional[List[Profile]] = None
    model_config = ConfigDict(from_attributes=True)

class Work(BaseModel):
    company: str
    position: str
    location: Optional[str] = None
    url: Optional[str] = None
    startDate: str
    endDate: Optional[str] = None
    isCurrent: Optional[bool] = False
    summary: Optional[str] = None
    highlights: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)

class Education(BaseModel):
    institution: str
    area: str
    studyType: str
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    gpa: Optional[str] = None
    courses: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)

class Skill(BaseModel):
    category: str
    name: str
    level: Optional[str] = None
    keywords: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)

class Project(BaseModel):
    name: str
    description: str
    role: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None
    url: Optional[str] = None
    repositoryUrl: Optional[str] = None
    technologiesUsed: Optional[List[str]] = None
    model_config = ConfigDict(from_attributes=True)

class Publication(BaseModel):
    name: Optional[str] = None
    publisher: Optional[str] = None
    releaseDate: Optional[str] = None
    url: Optional[str] = None
    summary: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class Certificate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    url: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class Language(BaseModel):
    language: Optional[str] = None
    fluency: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class Reference(BaseModel):
    name: Optional[str] = None
    reference: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class CustomSection(BaseModel):
    title: str
    content: str
    model_config = ConfigDict(from_attributes=True)

class UnifiedResume(BaseModel):
    """The main, comprehensive schema for resume data."""
    meta: Optional[Meta] = None
    basics: Basics
    work: List[Work]
    education: List[Education]
    skills: Optional[List[Skill]] = None
    projects: Optional[List[Project]] = None
    publications: Optional[List[Publication]] = None
    certificates: Optional[List[Certificate]] = None
    languages: Optional[List[Language]] = None
    references: Optional[List[Reference]] = None
    customSections: Optional[List[CustomSection]] = None

class ResumeCreate(UnifiedResume):
    """Schema for creating a new resume."""
    candidate_id: int

class Resume(UnifiedResume):
    """Schema for representing a resume in API responses."""
    resume_id: int
    candidate_id: int
    date_created: datetime
    file_location: Optional[str] = None

    @model_validator(mode='before')
    def flatten_orm_data(cls, v):
        """
        Pydantic validator to map data from the SQLAlchemy ORM model to this schema.
        It unnests the JSON data from the `parsed_data` column.
        """
        if hasattr(v, '_sa_instance_state'):
            flat_dict = v.parsed_data.copy() if v.parsed_data else {}
            flat_dict['resume_id'] = v.resume_id
            flat_dict['candidate_id'] = v.candidate_id
            flat_dict['date_created'] = v.date_created
            flat_dict['file_location'] = v.file_location
            return flat_dict
        return v

    model_config = ConfigDict(from_attributes=True)
