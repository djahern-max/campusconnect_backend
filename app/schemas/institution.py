from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InstitutionBase(BaseModel):
    ipeds_id: int
    name: str
    city: str
    state: str
    control_type: str
    primary_image_url: Optional[str] = None
    student_faculty_ratio: Optional[float] = None
    size_category: Optional[str] = None
    locale: Optional[str] = None

class InstitutionResponse(InstitutionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
