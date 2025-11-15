from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Enum as SQLEnum, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class ContactStatus(str, enum.Enum):
    NOT_CONTACTED = "not_contacted"
    CONTACTED = "contacted"
    FOLLOW_UP_SENT = "follow_up_sent"
    REGISTERED = "registered"
    DECLINED = "declined"
    NO_RESPONSE = "no_response"

class ContactMethod(str, enum.Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    TEXT = "text"
    OTHER = "other"

class OutreachTracking(Base):
    __tablename__ = "outreach_tracking"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Entity being contacted
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(Integer, nullable=False, index=True)
    
    # Contact information
    contact_name = Column(String(255))
    contact_title = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    linkedin_url = Column(String(500))
    
    # Tracking
    status = Column(SQLEnum(ContactStatus), nullable=False, default=ContactStatus.NOT_CONTACTED, index=True)
    last_contact_date = Column(TIMESTAMP)
    last_contact_method = Column(SQLEnum(ContactMethod))
    contact_attempt_count = Column(Integer, default=0)
    
    # Invitation
    invitation_code_id = Column(Integer, ForeignKey("invitation_codes.id"), nullable=True)
    invitation_sent_date = Column(TIMESTAMP)
    
    # Follow-up tracking
    next_follow_up_date = Column(TIMESTAMP)
    follow_up_count = Column(Integer, default=0)
    
    # Notes and feedback
    notes = Column(Text)
    response_feedback = Column(Text)
    
    # Conversion tracking
    registered_date = Column(TIMESTAMP)
    registered_admin_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    
    # Priority and tags
    priority = Column(String(20), default='normal')
    tags = Column(Text)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(String(100))
