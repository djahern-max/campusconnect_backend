from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class TuitionDataBase(BaseModel):
    ipeds_id: int
    academic_year: str
    data_source: Optional[str] = None
    tuition_in_state: Optional[Decimal] = None
    tuition_out_state: Optional[Decimal] = None
    required_fees_in_state: Optional[Decimal] = None
    required_fees_out_state: Optional[Decimal] = None
    room_board_on_campus: Optional[Decimal] = None

class TuitionDataResponse(TuitionDataBase):
    id: int
    institution_id: int
    is_admin_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TuitionDataUpdate(BaseModel):
    """Schema for admins to update/verify their tuition data"""
    tuition_in_state: Optional[Decimal] = None
    tuition_out_state: Optional[Decimal] = None
    required_fees_in_state: Optional[Decimal] = None
    required_fees_out_state: Optional[Decimal] = None
    room_board_on_campus: Optional[Decimal] = None
    data_source: Optional[str] = None
    is_admin_verified: Optional[bool] = None
