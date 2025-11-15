from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminRegister(BaseModel):
    email: EmailStr
    password: str
    invitation_code: str  # REQUIRED for registration

class AdminLogin(BaseModel):
    email: EmailStr
    password: str

class AdminResponse(BaseModel):
    id: int
    email: str
    entity_type: str
    entity_id: int
    role: str
    is_active: bool
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
