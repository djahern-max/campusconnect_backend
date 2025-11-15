from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base

class InstitutionExtendedInfo(Base):
    __tablename__ = "institution_extended_info"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Campus Life
    campus_description = Column(Text, nullable=True)
    student_life = Column(Text, nullable=True)
    housing_info = Column(Text, nullable=True)
    dining_info = Column(Text, nullable=True)
    
    # Academics
    programs_overview = Column(Text, nullable=True)
    faculty_highlights = Column(Text, nullable=True)
    research_opportunities = Column(Text, nullable=True)
    study_abroad = Column(Text, nullable=True)
    
    # Admissions
    application_tips = Column(Text, nullable=True)
    financial_aid_info = Column(Text, nullable=True)
    scholarship_opportunities = Column(Text, nullable=True)
    
    # Athletics & Activities
    athletics_overview = Column(Text, nullable=True)
    clubs_organizations = Column(Text, nullable=True)
    
    # Location & Facilities
    location_highlights = Column(Text, nullable=True)
    facilities_overview = Column(Text, nullable=True)
    
    # Custom Sections (flexible)
    custom_sections = Column(JSONB, nullable=True)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
