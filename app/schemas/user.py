from typing import List, Optional
from pydantic import BaseModel

class UserMail(BaseModel):
    email: str

class UserBase(UserMail):
    username: str
    firstname: str
    lastname: str
    phone: int

class User(UserBase):
    id: int
    is_confirmed: bool
    is_admin: bool

    class Config:
        orm_mode = True
