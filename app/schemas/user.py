from typing import List, Optional
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    firstname: str
    lastname: str
    phone: int

class User(UserBase):
    id: int
    is_confirmed: bool
    is_admin: bool

    class Config:
        orm_mode = True
