from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal

class AdmissionDataBase(BaseModel):
    ipeds_id: int
    academic_year: str
    applications_total: Optional[int] = None
    admissions_total: Optional[int] = None
    enrolled_total: Optional[int] = None
    acceptance_rate: Optional[Decimal] = None
    yield_rate: Optional[Decimal] = None
    sat_reading_25th: Optional[int] = None
    sat_reading_50th: Optional[int] = None
    sat_reading_75th: Optional[int] = None
    sat_math_25th: Optional[int] = None
    sat_math_50th: Optional[int] = None
    sat_math_75th: Optional[int] = None
    percent_submitting_sat: Optional[Decimal] = None

class AdmissionDataResponse(AdmissionDataBase):
    id: int
    institution_id: int
    is_admin_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class AdmissionDataUpdate(BaseModel):
    """Schema for admins to update/verify their admission data"""
    applications_total: Optional[int] = None
    admissions_total: Optional[int] = None
    enrolled_total: Optional[int] = None
    acceptance_rate: Optional[Decimal] = None
    yield_rate: Optional[Decimal] = None
    sat_reading_25th: Optional[int] = None
    sat_reading_50th: Optional[int] = None
    sat_reading_75th: Optional[int] = None
    sat_math_25th: Optional[int] = None
    sat_math_50th: Optional[int] = None
    sat_math_75th: Optional[int] = None
    percent_submitting_sat: Optional[Decimal] = None
    is_admin_verified: Optional[bool] = None
