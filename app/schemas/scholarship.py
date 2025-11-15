from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class ScholarshipBase(BaseModel):
    title: str
    organization: str
    scholarship_type: str
    status: str
    difficulty_level: str
    amount_min: int
    amount_max: int
    is_renewable: bool
    number_of_awards: Optional[int] = None
    deadline: Optional[date] = None
    application_opens: Optional[date] = None
    for_academic_year: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    min_gpa: Optional[float] = None
    primary_image_url: Optional[str] = None
    verified: bool
    featured: bool

class ScholarshipResponse(ScholarshipBase):
    id: int
    views_count: int
    applications_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
