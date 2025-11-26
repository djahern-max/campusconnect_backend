# app/models/institution.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    TIMESTAMP,
    Enum,
    Boolean,
    SmallInteger,
    DECIMAL,
)
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class ControlType(str, enum.Enum):
    PUBLIC = "PUBLIC"
    PRIVATE_NONPROFIT = "PRIVATE_NONPROFIT"
    PRIVATE_FOR_PROFIT = "PRIVATE_FOR_PROFIT"


class Institution(Base):
    __tablename__ = "institutions"

    # Original columns
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
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # NEW: Base IPEDS columns
    website = Column(String(255), nullable=True, index=True)
    level = Column(SmallInteger, nullable=True)  # 1=4-year, 2=2-year, 3=<2-year
    control = Column(
        SmallInteger, nullable=True
    )  # 1=Public, 2=Private NP, 3=Private FP (IPEDS format)

    # NEW: Data tracking columns
    data_completeness_score = Column(
        Integer, nullable=False, server_default="0", index=True
    )
    data_last_updated = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    data_source = Column(
        String(50), nullable=False, server_default="manual", index=True
    )
    ipeds_year = Column(String(10), nullable=True)  # e.g., '2023-24'
    is_featured = Column(Boolean, nullable=False, server_default="false", index=True)

    # NEW: Cost data columns
    tuition_in_state = Column(DECIMAL(10, 2), nullable=True)
    tuition_out_of_state = Column(DECIMAL(10, 2), nullable=True)
    tuition_private = Column(DECIMAL(10, 2), nullable=True)
    tuition_in_district = Column(DECIMAL(10, 2), nullable=True)
    room_cost = Column(DECIMAL(10, 2), nullable=True)
    board_cost = Column(DECIMAL(10, 2), nullable=True)
    room_and_board = Column(DECIMAL(10, 2), nullable=True)
    application_fee_undergrad = Column(DECIMAL(10, 2), nullable=True)
    application_fee_grad = Column(DECIMAL(10, 2), nullable=True)

    # NEW: Admissions data columns
    acceptance_rate = Column(DECIMAL(5, 2), nullable=True)
    sat_reading_25th = Column(SmallInteger, nullable=True)
    sat_reading_75th = Column(SmallInteger, nullable=True)
    sat_math_25th = Column(SmallInteger, nullable=True)
    sat_math_75th = Column(SmallInteger, nullable=True)
    act_composite_25th = Column(SmallInteger, nullable=True)
    act_composite_75th = Column(SmallInteger, nullable=True)
