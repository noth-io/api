from sqlalchemy.orm import Session
import models, schemas
from fastapi import Depends, FastAPI

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_fido2credentials(db: Session, skip: int = 0, limit: int = 100, user_id: int = None):
    if not user_id:
        fido2credentials = db.query(models.Fido2Credential).offset(skip).limit(limit).all()
    else:
        fido2credentials = db.query(models.Fido2Credential).filter(models.Fido2Credential.user_id == user_id).offset(skip).limit(limit).all()
    return fido2credentials

def create_user(db: Session, user: schemas.UserBase):
    db_user = models.User(username=user.username, email=user.email, firstname=user.firstname, lastname=user.lastname, phone=user.phone)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return False
    db.delete(db_user)
    db.commit()
    return True