# app/schemas/institution_data.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from decimal import Decimal


class InstitutionComplete(BaseModel):
    """Complete institution data with ALL fields from database"""

    # Primary fields
    id: int
    ipeds_id: int
    name: str
    city: str
    state: str
    control_type: str
    primary_image_url: Optional[str] = None
    website: Optional[str] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime
    data_last_updated: datetime

    # Institutional characteristics
    level: Optional[int] = None
    control: Optional[int] = None
    student_faculty_ratio: Optional[Decimal] = None
    size_category: Optional[str] = None
    locale: Optional[str] = None

    # Data tracking
    data_completeness_score: int
    data_source: str
    ipeds_year: Optional[str] = None
    is_featured: bool

    # Cost data
    tuition_in_state: Optional[Decimal] = None
    tuition_out_of_state: Optional[Decimal] = None
    tuition_private: Optional[Decimal] = None
    tuition_in_district: Optional[Decimal] = None
    room_cost: Optional[Decimal] = None
    board_cost: Optional[Decimal] = None
    room_and_board: Optional[Decimal] = None
    application_fee_undergrad: Optional[Decimal] = None
    application_fee_grad: Optional[Decimal] = None

    # Admissions data
    acceptance_rate: Optional[Decimal] = None
    sat_reading_25th: Optional[int] = None
    sat_reading_75th: Optional[int] = None
    sat_math_25th: Optional[int] = None
    sat_math_75th: Optional[int] = None
    act_composite_25th: Optional[int] = None
    act_composite_75th: Optional[int] = None

    class Config:
        from_attributes = True
