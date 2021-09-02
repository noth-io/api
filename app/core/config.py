import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator
import os

class Settings(BaseSettings):
    ENV: str = "DEV"
    API_V1_STR: str = "/v1"
    SECRET_KEY: str = "key" # dev only
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    NOTH_UI_URL = "https://noth-dev.meanite.tk"
    MAIL_SENDER_NAME = "Noth"
    MAIL_SENDER_EMAIL = "admin@noth.io"
    MAIL_API_KEY = "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"
    MAIL_API_URL = "https://api.sendinblue.com/v3/smtp/email"
    MAIL_API_URL = "https://api.sendinblue.com/v3/smtp/email"
    AUTH_MAIL_TOKEN_KEY = "authmailtoken"
    COOKIE_DOMAIN = ".noth-dev.meanite.tk"
    OTP_LIFETIME = 300
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    
    TEST: str = os.getenv('TEST')

    class Config:
        case_sensitive = True

settings = Settings()