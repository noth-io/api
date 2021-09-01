from fastapi import APIRouter, Body, Depends, HTTPException
from app.api import deps
from sqlalchemy.orm import Session
from app.crud import user as user_crud, credential as credential_crud
from app import models, schemas
from app.core import security, responses

router = APIRouter()


@router.post("")
def username_auth(user: schemas.UserMail, db: Session = Depends(deps.get_db)):
    # Check user exists
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if registered Fido2 credentials
    if credential_crud.get_fido2credentials(db, user_id=db_user.id):
        # If yes, request fido2 auth
        authtoken = security.create_auth_token(user.email, nextstep=4, current_level=1)
    else:
        # Else request email auth
        authtoken = security.create_auth_token(user.email, nextstep=20, current_level=1)

    # Return auth token
    return responses.generate_auth_response(authtoken, "bearer")
