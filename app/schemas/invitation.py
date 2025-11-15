from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class InvitationCodeCreate(BaseModel):
    entity_type: str
    entity_id: int
    assigned_email: Optional[EmailStr] = None
    expires_in_days: int = 30

class InvitationCodeResponse(BaseModel):
    id: int
    code: str
    entity_type: str
    entity_id: int
    assigned_email: Optional[str]
    status: str
    expires_at: datetime
    created_at: datetime
    claimed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class InvitationValidateRequest(BaseModel):
    code: str

class InvitationValidateResponse(BaseModel):
    valid: bool
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    entity_name: Optional[str] = None
    message: str
