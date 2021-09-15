from typing import List, Optional
from pydantic import BaseModel

class UserMail(BaseModel):
    email: str

class UserBase(UserMail):
    firstname: str
    lastname: str
    phone: str

class User(UserBase):
    id: int
    is_phone_confirmed: bool
    is_admin: bool

    class Config:
        orm_mode = True
