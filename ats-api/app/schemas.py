from pydantic import BaseModel, model_validator
from typing import List, Optional
from datetime import datetime
from .models import JobStatus, ApplicationStatus, InterviewType
from .models import JobStatus as JobStatusEnum
from .database import Base

class UserBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str
    company_id: int
    role_id: int

from pydantic import ConfigDict

class User(UserBase):
    user_id: int
    company_id: int
    role_id: int

    model_config = ConfigDict(from_attributes=True)

class JobStatusEventBase(BaseModel):
    status: JobStatusEnum
    reason: Optional[str] = None

class JobStatusEventCreate(JobStatusEventBase):
    changed_by_user_id: int

class JobStatusEvent(JobStatusEventBase):
    event_id: int
    job_id: int
    changed_by_user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EvaluationBase(BaseModel):
    rating: int
    feedback: str

class EvaluationCreate(EvaluationBase):
    interviewer_id: int

class Evaluation(EvaluationBase):
    evaluation_id: int
    interview_id: int
    interviewer_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterviewerBase(BaseModel):
    user_id: int

class InterviewerCreate(InterviewerBase):
    pass

class Interviewer(InterviewerBase):
    interviewer_id: int
    interview_id: int

    model_config = ConfigDict(from_attributes=True)

class InterviewBase(BaseModel):
    scheduled_at: datetime
    duration_minutes: int
    interview_type: InterviewType

class InterviewCreate(InterviewBase):
    interviewers: List[InterviewerCreate]

class Interview(InterviewBase):
    interview_id: int
    application_id: int
    interviewers: List[Interviewer] = []
    evaluations: List[Evaluation] = []

    model_config = ConfigDict(from_attributes=True)

from uuid import UUID
from .models import JobStatus as JobStatusEnum
from .models import JobStatus as JobStatusEnum

class Requirement(BaseModel):
    description: str
    weight: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class CompanyInfo(BaseModel):
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
    type: str
    address: Optional[dict] = None
    remotePolicy: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class Compensation(BaseModel):
    type: str
    currency: str
    minAmount: Optional[float] = None
    maxAmount: Optional[float] = None
    summary: Optional[str] = None
    benefits: Optional[List[dict]] = None

    model_config = ConfigDict(from_attributes=True)

class InterviewStep(BaseModel):
    step: int
    type: str
    description: str

    model_config = ConfigDict(from_attributes=True)

class HiringManager(BaseModel):
    userId: UUID
    name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class JobBase(BaseModel):
    jobId: str
    description: str
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
    company_id: int

class Job(JobBase):
    job_id: int
    company_id: int
    company: CompanyInfo
    status_history: List[JobStatusEvent] = []

    @model_validator(mode='before')
    def flatten_orm_data(cls, v):
        if hasattr(v, '_sa_instance_state'):
            # It's an ORM model. Let's build the dict for Pydantic.
            flat_dict = v.data.copy() if v.data else {}
            flat_dict['job_id'] = v.job_id
            flat_dict['company_id'] = v.company_id
            flat_dict['status_history'] = v.status_history
            # The company info is now sourced from the relationship, not the JSON blob
            if v.company:
                flat_dict['company'] = v.company
            return flat_dict
        return v

    model_config = ConfigDict(from_attributes=True)

class CandidateBase(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin_profile: Optional[str] = None
    job_title: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    candidate_id: int

    model_config = ConfigDict(from_attributes=True)

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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    company_id: Optional[int] = None

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

from .models import ResumeStatus

class UnifiedResume(BaseModel):
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
    candidate_id: int

from pydantic import model_validator

class Resume(UnifiedResume):
    resume_id: int
    candidate_id: int
    date_created: datetime
    file_location: Optional[str] = None

    @model_validator(mode='before')
    def flatten_orm_data(cls, v):
        if hasattr(v, '_sa_instance_state'):
            # It's an ORM model. Let's build the dict for Pydantic.
            flat_dict = v.parsed_data.copy() if v.parsed_data else {}
            flat_dict['resume_id'] = v.resume_id
            flat_dict['candidate_id'] = v.candidate_id
            flat_dict['date_created'] = v.date_created
            flat_dict['file_location'] = v.file_location
            return flat_dict
        return v

    model_config = ConfigDict(from_attributes=True)
