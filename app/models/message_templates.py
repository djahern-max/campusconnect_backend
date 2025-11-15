from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class MessageTemplate(Base):
    __tablename__ = "message_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Template info
    name = Column(String(255), nullable=False)
    template_type = Column(String(50), nullable=False)
    
    # Message content
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    
    # Tracking
    times_used = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100))


class OutreachActivity(Base):
    """Log every outreach activity"""
    __tablename__ = "outreach_activities"
    
    id = Column(Integer, primary_key=True, index=True)
    outreach_tracking_id = Column(Integer, nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False)
    contact_method = Column(String(50), nullable=False)
    
    # Message details
    template_id = Column(Integer, nullable=True)
    subject = Column(String(500))
    message_sent = Column(Text)
    
    # Response
    response_received = Column(Boolean, default=False)
    response_text = Column(Text)
    response_date = Column(TIMESTAMP)
    
    # Metadata
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    created_by = Column(String(100))
