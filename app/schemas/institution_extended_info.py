from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CustomSection(BaseModel):
    title: str
    content: str
    order: int

class InstitutionExtendedInfoBase(BaseModel):
    # Campus Life
    campus_description: Optional[str] = None
    student_life: Optional[str] = None
    housing_info: Optional[str] = None
    dining_info: Optional[str] = None
    
    # Academics
    programs_overview: Optional[str] = None
    faculty_highlights: Optional[str] = None
    research_opportunities: Optional[str] = None
    study_abroad: Optional[str] = None
    
    # Admissions
    application_tips: Optional[str] = None
    financial_aid_info: Optional[str] = None
    scholarship_opportunities: Optional[str] = None
    
    # Athletics & Activities
    athletics_overview: Optional[str] = None
    clubs_organizations: Optional[str] = None
    
    # Location & Facilities
    location_highlights: Optional[str] = None
    facilities_overview: Optional[str] = None
    
    # Custom Sections
    custom_sections: Optional[List[Dict[str, Any]]] = None

class InstitutionExtendedInfoCreate(InstitutionExtendedInfoBase):
    pass

class InstitutionExtendedInfoUpdate(InstitutionExtendedInfoBase):
    pass

class InstitutionExtendedInfoResponse(InstitutionExtendedInfoBase):
    id: int
    institution_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
