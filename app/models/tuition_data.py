from sqlalchemy import Column, Integer, String, Numeric, TIMESTAMP, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class TuitionData(Base):
    __tablename__ = "tuition_data"
    
    id = Column(Integer, primary_key=True, index=True)
    institution_id = Column(Integer, ForeignKey("institutions.id", ondelete="CASCADE"), nullable=False, index=True)
    ipeds_id = Column(Integer, nullable=False, index=True)
    academic_year = Column(String(10), nullable=False)
    data_source = Column(String(500))
    
    # Tuition costs
    tuition_in_state = Column(Numeric(10, 2))
    tuition_out_state = Column(Numeric(10, 2))
    
    # Required fees
    required_fees_in_state = Column(Numeric(10, 2))
    required_fees_out_state = Column(Numeric(10, 2))
    
    # Room and board
    room_board_on_campus = Column(Numeric(10, 2))
    
    # Verification
    is_admin_verified = Column(Boolean, default=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        {'extend_existing': True}
    )
