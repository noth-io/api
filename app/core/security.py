from datetime import datetime, timedelta
from typing import Any, Union
import schemas
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

def create_register_token(
    subject: Union[str, Any], step: int, expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "register", "step": step}
    encoded_jwt = jwt.encode(
        to_encode, settings.TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_auth_token(
    subject: Union[str, Any], nextstep: int, current_level: int, expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "authentication", "nextstep": nextstep, "current_level": current_level}
    encoded_jwt = jwt.encode(
        to_encode, settings.TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_session_token(
    subject: Union[str, Any], loa: int, expires_delta: timedelta = None
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "session", "loa": loa}
    encoded_jwt = jwt.encode(
        to_encode, settings.TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

"""
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
"""

def validate_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.TOKEN_SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except:
        raise HTTPException(
            status_code=403,
            detail="Could not validate credentials",
        )
    if token_data.type == "authentication":
        token_data = schemas.AuthTokenPayload(**payload)
    if token_data.type == "register":
        token_data = schemas.RegisterTokenPayload(**payload)
    return token_data