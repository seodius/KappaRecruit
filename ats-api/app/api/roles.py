"""
API endpoints for managing user roles and permissions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import crud, schemas, security
from ..database import get_db

router = APIRouter()

@router.post("/roles", response_model=schemas.Role)
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Administrator"]))):
    """Creates a new role (Administrator only)."""
    return crud.create_role(db=db, role=role)

@router.get("/roles", response_model=List[schemas.Role])
def read_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Administrator"]))):
    """Retrieves a list of all roles (Administrator only)."""
    return crud.get_roles(db, skip=skip, limit=limit)

@router.get("/roles/{role_id}", response_model=schemas.Role)
def read_role(role_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Administrator"]))):
    """Retrieves a single role by ID (Administrator only)."""
    db_role = crud.get_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.put("/roles/{role_id}", response_model=schemas.Role)
def update_role(role_id: int, role: schemas.RoleUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Administrator"]))):
    """Updates a role's details (Administrator only)."""
    db_role = crud.update_role(db, role_id=role_id, role=role)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role

@router.delete("/roles/{role_id}", response_model=schemas.Role)
def delete_role(role_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(security.RoleChecker(allowed_roles=["Administrator"]))):
    """Deletes a role (Administrator only)."""
    db_role = crud.delete_role(db, role_id=role_id)
    if db_role is None:
        raise HTTPException(status_code=404, detail="Role not found")
    return db_role
