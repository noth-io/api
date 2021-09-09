from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Fido2CredentialBase(BaseModel):
    attestation: bytes
    user_id: int

class Fido2Credential(Fido2CredentialBase):
    id: int
    is_enabled: bool
    created_at: datetime

    class Config:
        orm_mode = True
