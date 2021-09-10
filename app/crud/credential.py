from sqlalchemy.orm import Session
import models, schemas
from fastapi import Depends, FastAPI
from typing import Any, List

def get_fido2credentials(db: Session, skip: int = 0, limit: int = 100, user_id: int = None) -> List[schemas.Fido2Credential]:
    if not user_id:
        fido2credentials = db.query(models.Fido2Credential).offset(skip).limit(limit).all()
    else:
        fido2credentials = db.query(models.Fido2Credential).filter(models.Fido2Credential.user_id == user_id).offset(skip).limit(limit).all()
    #for fido2credential in fido2credentials:
    #    print(fido2credential.pop('attestation'))
    return fido2credentials

def create_fido2credential(db: Session, user_id: int, attestation):
    db_fido2credential = models.Fido2Credential(attestation=attestation, user_id=user_id)
    db.add(db_fido2credential)
    db.commit()
    db.refresh(db_fido2credential)
    return db_fido2credential

"""
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        return False
    db.delete(db_user)
    db.commit()
    return True
"""