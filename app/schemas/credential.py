from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class Fido2CredentialBase(BaseModel):
    user_id: int
    attestation: bytes

class Fido2Credential(Fido2CredentialBase):
    id: int
    is_enabled: bool
    created_at: datetime

    class Config:
        orm_mode = True
