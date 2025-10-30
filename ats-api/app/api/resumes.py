from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db
import shutil
import os
import uuid

router = APIRouter()

import json
from fastapi import Form

@router.post("/resumes", response_model=schemas.Resume)
def create_resume(
    resume_data: str = Form(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user),
    file: UploadFile = File(...)
):
    resume = schemas.ResumeCreate(**json.loads(resume_data))

    upload_dir = "uploads/"
    os.makedirs(upload_dir, exist_ok=True)

    # Secure filename generation
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{uuid.uuid4()}{file_extension}"
    file_location = os.path.join(upload_dir, safe_filename)

    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db_resume = crud.create_resume(db=db, resume=resume, company_id=current_user.company_id, file_location=file_location)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Candidate not found or access denied.")
    return db_resume

@router.get("/candidates/{candidate_id}/resumes", response_model=List[schemas.Resume])
def read_resumes_for_candidate(candidate_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    resumes = crud.get_resumes_by_candidate(db, candidate_id=candidate_id, company_id=current_user.company_id)
    return resumes

@router.get("/resumes/{resume_id}", response_model=schemas.Resume)
def read_resume(resume_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_resume = crud.get_resume(db, resume_id=resume_id, company_id=current_user.company_id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db_resume

@router.put("/resumes/{resume_id}", response_model=schemas.Resume)
def update_resume(resume_id: int, resume: schemas.ResumeCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_resume = crud.update_resume(db, resume_id=resume_id, resume=resume, company_id=current_user.company_id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db_resume

from fastapi.responses import FileResponse

@router.delete("/resumes/{resume_id}", response_model=schemas.Resume)
def delete_resume(resume_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_resume = crud.delete_resume(db, resume_id=resume_id, company_id=current_user.company_id)
    if db_resume is None:
        raise HTTPException(status_code=404, detail="Resume not found")
    return db_resume

@router.get("/resumes/{resume_id}/download")
def download_resume(resume_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.get_current_user)):
    db_resume = crud.get_resume(db, resume_id=resume_id, company_id=current_user.company_id)
    if db_resume is None or not db_resume.file_location:
        raise HTTPException(status_code=404, detail="Resume file not found")

    upload_dir = os.path.abspath("uploads")
    file_path = os.path.abspath(os.path.join(upload_dir, os.path.basename(db_resume.file_location)))

    if not file_path.startswith(upload_dir):
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Resume file not found on disk")

    return FileResponse(
        path=file_path,
        media_type='application/octet-stream',
        filename=os.path.basename(db_resume.file_location)
    )
