from typing import Optional

from pydantic import BaseModel

"""
class Token(BaseModel):
    access_token: str
    token_type: str
"""

class TokenPayload(BaseModel):
    sub: str
    type: str

class AuthTokenPayload(TokenPayload):
    current_level: int
    nextstep: int

class RegisterTokenPayload(TokenPayload):
    step: int
