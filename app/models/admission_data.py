from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class AdmissionData(Base):
    __tablename__ = "admissions_data"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    ipeds_id = Column(Integer, nullable=False, index=True)
    academic_year = Column(String(10), nullable=False)
    
    # Application metrics
    applications_total = Column(Integer)
    admissions_total = Column(Integer)
    enrolled_total = Column(Integer)
    acceptance_rate = Column(Numeric(5, 2))  # percentage
    yield_rate = Column(Numeric(5, 2))  # percentage
    
    # SAT Reading scores
    sat_reading_25th = Column(Integer)
    sat_reading_50th = Column(Integer)
    sat_reading_75th = Column(Integer)
    
    # SAT Math scores
    sat_math_25th = Column(Integer)
    sat_math_50th = Column(Integer)
    sat_math_75th = Column(Integer)
    
    # Test submission
    percent_submitting_sat = Column(Numeric(5, 2))
    
    # Verification
    is_admin_verified = Column(Boolean, default=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        {'extend_existing': True}
    )
