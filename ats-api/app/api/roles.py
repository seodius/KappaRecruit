"""
API endpoints for managing user roles and permissions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

# Dependency to enforce administrator-only access
admin_only = security.RoleChecker(allowed_roles=["Administrator"])

@router.post("/roles", response_model=schemas.Role, dependencies=[Depends(admin_only)])
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    """Creates a new role (Administrator only)."""
    return crud.create_role(db=db, role=role)

@router.get("/roles", response_model=List[schemas.Role], dependencies=[Depends(admin_only)])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retrieves a list of all roles (Administrator only)."""
    return crud.get_roles(db, skip=skip, limit=limit)

@router.get("/roles/{role_id}", response_model=schemas.Role, dependencies=[Depends(admin_only)])
def read_role(role_id: int, db: Session = Depends(get_db)):
    """Retrieves a single role by ID (Administrator only)."""
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.put("/roles/{role_id}", response_model=schemas.Role, dependencies=[Depends(admin_only)])
def update_role(role_id: int, role: schemas.RoleUpdate, db: Session = Depends(get_db)):
    """Updates a role's details (Administrator only)."""
    db_role = crud.update_role(db, role_id=role_id, role=role)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.delete("/roles/{role_id}", response_model=schemas.Role, dependencies=[Depends(admin_only)])
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """Deletes a role (Administrator only)."""
    db_role = crud.delete_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role
