from fastapi import FastAPI
from .api import auth, jobs, candidates, applications, resumes, interviews

app = FastAPI(
    title="Applicant Tracking System API",
    description="A headless, API-first Applicant Tracking System.",
    version="1.0.0",
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(jobs.router, prefix="/api/v1", tags=["jobs"])
app.include_router(candidates.router, prefix="/api/v1", tags=["candidates"])
app.include_router(applications.router, prefix="/api/v1", tags=["applications"])
app.include_router(resumes.router, prefix="/api/v1", tags=["resumes"])
app.include_router(interviews.router, prefix="/api/v1", tags=["interviews"])

@app.get("/")
def read_root():
    return {"message": "ATS API is running!"}
