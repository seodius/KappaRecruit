"""
API endpoints for managing departments.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

@router.post("/companies/{company_id}/departments", response_model=schemas.Department)
def create_department_for_company(
    company_id: int,
    department: schemas.DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Creates a new department for a specific company."""
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return crud.create_department(db=db, department=department, company_id=company_id)

@router.get("/companies/{company_id}/departments", response_model=List[schemas.Department])
def read_departments_for_company(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Retrieves a list of departments for a specific company."""
    if company_id != current_user.company_id:
        raise HTTPException(status_code=403, detail="Operation not permitted")
    return crud.get_departments_by_company(db, company_id=company_id, skip=skip, limit=limit)

@router.get("/departments/{department_id}", response_model=schemas.Department)
def read_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Retrieves a single department by its ID."""
    db_department = crud.get_department(db, department_id=department_id, company_id=current_user.company_id)
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department

@router.put("/departments/{department_id}", response_model=schemas.Department)
def update_department(
    department_id: int,
    department: schemas.DepartmentUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Updates a department's details."""
    db_department = crud.update_department(db, department_id=department_id, department=department, company_id=current_user.company_id)
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department

@router.delete("/departments/{department_id}", response_model=schemas.Department)
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(security.get_current_user)
):
    """Deletes a department."""
    db_department = crud.delete_department(db, department_id=department_id, company_id=current_user.company_id)
    if db_department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    return db_department
