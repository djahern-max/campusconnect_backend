# app/models/institution_data_verifications.py
"""
Model for tracking institution data verifications and updates.
Creates an audit trail of all changes made by admins.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class InstitutionDataVerification(Base):
    """
    Tracks verification and updates to institution data.

    Creates an audit trail showing:
    - Which admin made the change
    - What field was changed
    - Old value vs new value
    - When it was changed
    - Any notes about the change
    """

    __tablename__ = "institution_data_verifications"

    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(
        Integer, ForeignKey("institutions.id"), nullable=False, index=True
    )

    # What was changed
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)

    # Who and when
    verified_by = Column(String(255), nullable=False)  # Admin email
    verified_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Optional notes
    notes = Column(Text, nullable=True)

    # Relationship back to institution
    institution = relationship("Institution", backref="data_verifications")

    def __repr__(self):
        return f"<InstitutionDataVerification(institution_id={self.institution_id}, field={self.field_name}, by={self.verified_by})>"
