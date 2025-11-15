# app/models/admission_data.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    TIMESTAMP,
    ForeignKey,
    Numeric,
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime


class AdmissionsData(Base):
    __tablename__ = "admissions_data"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"))
    ipeds_id = Column(Integer, nullable=False, index=True)
    academic_year = Column(String(10), nullable=False, index=True)

    # Application numbers
    applications_total = Column(Integer)
    admissions_total = Column(Integer)
    enrolled_total = Column(Integer)

    # Rates
    acceptance_rate = Column(Numeric(5, 2), index=True)
    yield_rate = Column(Numeric(5, 2))

    # SAT scores
    sat_reading_25th = Column(Integer)
    sat_reading_50th = Column(Integer)
    sat_reading_75th = Column(Integer)
    sat_math_25th = Column(Integer)
    sat_math_50th = Column(Integer)
    sat_math_75th = Column(Integer)
    percent_submitting_sat = Column(Numeric(5, 2))

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
    institution = relationship("Institution", back_populates="admissions_data")
    updated_by_user = relationship("AdminUser", foreign_keys=[last_updated_by])
