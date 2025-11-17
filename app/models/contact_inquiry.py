from sqlalchemy import Column, Integer, String, Text, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class InquiryType(str, enum.Enum):
    HIGHER_EDUCATION = "HIGHER_EDUCATION"
    SCHOLARSHIP_ORGANIZATION = "SCHOLARSHIP_ORGANIZATION"
    OTHER = "OTHER"


class ContactInquiry(Base):
    __tablename__ = "contact_inquiries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    institution_name = Column(String(255), nullable=False)
    phone_number = Column(String(50), nullable=True)
    inquiry_type = Column(Enum(InquiryType), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
