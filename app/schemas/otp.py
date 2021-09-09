from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class OTPBase(BaseModel):
    code: int

class OTP(OTPBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
