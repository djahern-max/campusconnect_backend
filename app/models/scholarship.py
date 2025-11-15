from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, Boolean, Date, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ScholarshipType(str, enum.Enum):
    ACADEMIC_MERIT = "ACADEMIC_MERIT"
    NEED_BASED = "NEED_BASED"
    STEM = "STEM"
    ARTS = "ARTS"
    DIVERSITY = "DIVERSITY"
    ATHLETIC = "ATHLETIC"
    LEADERSHIP = "LEADERSHIP"
    MILITARY = "MILITARY"
    CAREER_SPECIFIC = "CAREER_SPECIFIC"

class ScholarshipStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    EXPIRED = "EXPIRED"

class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MODERATE = "MODERATE"
    HARD = "HARD"
    VERY_HARD = "VERY_HARD"

class Scholarship(Base):
    __tablename__ = "scholarships"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    organization = Column(String(255), nullable=False, index=True)
    scholarship_type = Column(Enum(ScholarshipType), nullable=False)
    status = Column(Enum(ScholarshipStatus), nullable=False, default=ScholarshipStatus.ACTIVE)
    difficulty_level = Column(Enum(DifficultyLevel), nullable=False, default=DifficultyLevel.MODERATE)
    amount_min = Column(Integer, nullable=False)
    amount_max = Column(Integer, nullable=False)
    is_renewable = Column(Boolean, nullable=False, default=False)
    number_of_awards = Column(Integer)
    deadline = Column(Date)
    application_opens = Column(Date)
    for_academic_year = Column(String(20))
    description = Column(String(500))
    website_url = Column(String(500))
    min_gpa = Column(Numeric(3, 2))
    primary_image_url = Column(String(500))
    verified = Column(Boolean, nullable=False, default=False)
    featured = Column(Boolean, nullable=False, default=False)
    views_count = Column(Integer, nullable=False, default=0)
    applications_count = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP)
