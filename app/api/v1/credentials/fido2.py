from fastapi import APIRouter, Body, Depends, HTTPException
from app.api import deps
from sqlalchemy.orm import Session
from app.crud import user as user_crud, credential as credential_crud
from app import models, schemas
from typing import Any, List

router = APIRouter()

@router.get("", response_model=List[schemas.Fido2Credential])
def get_fido2credentials(db: Session = Depends(deps.get_db), current_user: models.User = Depends(deps.get_current_user)):
    # if is admin --> return all for all users
    # else --> return only user credential
    return credential_crud.get_fido2credentials(db, user_id=1)

"""
@router.post("", response_model=schemas.User)
def create_user(user: schemas.UserBase, db: Session = Depends(deps.get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return user_crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    db_user = user_crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.delete("/{user_id}")
def get_user(user_id: int, db: Session = Depends(deps.get_db)):
    db_user = user_crud.delete_user(db, user_id=user_id)
    if db_user is False:
        raise HTTPException(status_code=404, detail="User not found")
    return { "message": "user deleted" }
"""