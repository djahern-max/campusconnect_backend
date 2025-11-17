from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class ContactInquiryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    institution_name: str = Field(..., min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=50)
    inquiry_type: str
    message: str = Field(..., min_length=1)


class ContactInquiryResponse(BaseModel):
    id: int
    name: str
    email: str
    institution_name: str
    phone_number: Optional[str]
    inquiry_type: str
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True
