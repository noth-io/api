from fastapi import APIRouter, Body, Depends, HTTPException
from app.api import deps
from sqlalchemy.orm import Session
from app.crud import user as user_crud
from app import models, schemas
from app.core import security, responses

router = APIRouter()


@router.post("")
def username_auth(user: schemas.UserMail, db: Session = Depends(deps.get_db)):
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    token = security.create_auth_token(user.email, nextstep=4, current_level=1)
    return responses.generate_auth_response(token, "bearer")
