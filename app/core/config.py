import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
import os

class Settings(BaseSettings):
    ENV: str = os.getenv("NOTH_API_ENV")
    API_V1_STR: str = "/v1"
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [os.getenv("NOTH_UI_URL")]

    TOKEN_SECRET_KEY: str = os.getenv("NOTH_API_TOKEN_SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("NOTH_API_TOKEN_LIFETIME")
    NOTH_UI_URL: str = os.getenv("NOTH_UI_URL")
    MAIL_SENDER_NAME: str = os.getenv("NOTH_API_MAIL_SENDER_NAME")
    MAIL_SENDER_EMAIL: str = os.getenv("NOTH_API_MAIL_SENDER_EMAIL")
    MAIL_API_KEY: str = os.getenv("NOTH_API_MAIL_API_KEY")
    MAIL_API_URL: str = os.getenv("NOTH_API_MAIL_API_URL")
    AUTH_MAIL_TOKEN_KEY: str = os.getenv("NOTH_API_MAIL_AUTH_TOKEN_KEY")
    COOKIE_DOMAIN: str = os.getenv("NOTH_API_COOKIE_DOMAIN")
    OTP_LIFETIME: int = os.getenv("NOTH_API_OTP_LIFETIME")
    SQLALCHEMY_DATABASE_URL: str = "postgresql://%s:%s@%s/%s" % (os.getenv("NOTH_API_DB_USER"), os.getenv("NOTH_API_DB_PASSWORD"), os.getenv("NOTH_API_DB_URL"), os.getenv("NOTH_API_DB_NAME"))
    
    class Config:
        case_sensitive = True

settings = Settings()