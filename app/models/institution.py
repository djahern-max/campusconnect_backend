from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, Enum
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ControlType(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE_NONPROFIT = "PRIVATE_NONPROFIT"
    PRIVATE_FOR_PROFIT = "PRIVATE_FOR_PROFIT"  # Correct: with underscores

class Institution(Base):
    __tablename__ = "institutions"
    
    id = Column(Integer, primary_key=True, index=True)
    ipeds_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    city = Column(String(100), nullable=False, index=True)
    state = Column(String(2), nullable=False, index=True)
    control_type = Column(Enum(ControlType), nullable=False)
    primary_image_url = Column(String(500))
    student_faculty_ratio = Column(Numeric(5, 2))
    size_category = Column(String(50))
    locale = Column(String(50))
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
