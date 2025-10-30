"""
Main application file for the FastAPI ATS API.

This file initializes the FastAPI application, configures the API metadata,
and includes all the API routers from the `app.api` module.
"""

from fastapi import FastAPI
from .api import auth, jobs, candidates, applications, resumes, interviews

# Initialize the FastAPI application
app = FastAPI(
    title="Applicant Tracking System API",
    description="A headless, API-first Applicant Tracking System.",
    version="1.0.0",
)

# Include the API routers for different functionalities
# Each router handles a specific domain of the application (e.g., jobs, candidates).
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(candidates.router, prefix="/api/v1", tags=["candidates"])
app.include_router(applications.router, prefix="/api/v1", tags=["applications"])
app.include_router(resumes.router, prefix="/api/v1", tags=["resumes"])
app.include_router(interviews.router, prefix="/api/v1", tags=["interviews"])

@app.get("/")
def read_root():
    """
    Root endpoint for the API.

    Returns a simple message to indicate that the API is running.
    """
    return {"message": "ATS API is running!"}
