from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class InstitutionImage(Base):
    __tablename__ = "institution_images"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    cdn_url = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    caption = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0, index=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    image_type = Column(String(50), nullable=True)  # 'campus', 'students', 'facilities', 'events'
    created_at = Column(DateTime, nullable=False, server_default=func.now())
