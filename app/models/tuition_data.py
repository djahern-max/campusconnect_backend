# app/models/tuition_data.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    TIMESTAMP,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class TuitionData(Base):
    __tablename__ = "tuition_data"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"))
    ipeds_id = Column(Integer, nullable=False, index=True)
    academic_year = Column(String(10), nullable=False, index=True)
    data_source = Column(String(500), nullable=False)

    # Tuition and fees
    tuition_in_state = Column(Float)
    tuition_out_state = Column(Float)
    required_fees_in_state = Column(Float)
    required_fees_out_state = Column(Float)
    room_board_on_campus = Column(Float)

    # Admin override fields
    last_updated_by = Column(Integer, ForeignKey("admin_users.id"))
    is_admin_verified = Column(Boolean, default=False, nullable=False)
    admin_notes = Column(Text)

    # Timestamps
    created_at = Column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    institution = relationship("Institution", back_populates="tuition_data")
    updated_by_user = relationship("AdminUser", foreign_keys=[last_updated_by])
