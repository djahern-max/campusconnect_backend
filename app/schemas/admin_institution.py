# app/schemas/admin_institution.py
"""
Schemas for admin institution data updates
Separate from public institution schemas
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


class InstitutionBasicInfoUpdate(BaseModel):
    """Update basic institution information"""

    name: Optional[str] = Field(None, min_length=2, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, min_length=2, max_length=2)
    website: Optional[str] = Field(None, max_length=500)
    control_type: Optional[str] = Field(
        None, description="PUBLIC, PRIVATE_NONPROFIT, PRIVATE_FORPROFIT"
    )
    student_faculty_ratio: Optional[float] = Field(None, ge=0, le=100)
    size_category: Optional[str] = Field(None, max_length=50)
    locale: Optional[str] = Field(None, max_length=50)


class InstitutionCostDataUpdate(BaseModel):
    """Update cost data for institution"""

    tuition_in_state: Optional[float] = Field(
        None, ge=0, description="In-state tuition"
    )
    tuition_out_of_state: Optional[float] = Field(
        None, ge=0, description="Out-of-state tuition"
    )
    tuition_private: Optional[float] = Field(
        None, ge=0, description="Private institution tuition"
    )
    tuition_in_district: Optional[float] = Field(
        None, ge=0, description="In-district tuition"
    )
    room_cost: Optional[float] = Field(None, ge=0, description="Room cost")
    board_cost: Optional[float] = Field(None, ge=0, description="Board/meal plan cost")
    room_and_board: Optional[float] = Field(
        None, ge=0, description="Combined room and board"
    )
    application_fee_undergrad: Optional[float] = Field(
        None, ge=0, description="Undergraduate application fee"
    )
    application_fee_grad: Optional[float] = Field(
        None, ge=0, description="Graduate application fee"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "tuition_in_state": 12500.00,
                "tuition_out_of_state": 28000.00,
                "room_cost": 8500.00,
                "board_cost": 5500.00,
            }
        }


class InstitutionAdmissionsDataUpdate(BaseModel):
    """Update admissions data for institution"""

    acceptance_rate: Optional[float] = Field(
        None, ge=0, le=100, description="Acceptance rate percentage (0-100)"
    )
    sat_reading_25th: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Reading 25th percentile"
    )
    sat_reading_75th: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Reading 75th percentile"
    )
    sat_math_25th: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Math 25th percentile"
    )
    sat_math_75th: Optional[int] = Field(
        None, ge=200, le=800, description="SAT Math 75th percentile"
    )
    act_composite_25th: Optional[int] = Field(
        None, ge=1, le=36, description="ACT Composite 25th percentile"
    )
    act_composite_75th: Optional[int] = Field(
        None, ge=1, le=36, description="ACT Composite 75th percentile"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "acceptance_rate": 65.5,
                "sat_math_25th": 580,
                "sat_math_75th": 680,
                "act_composite_25th": 24,
                "act_composite_75th": 29,
            }
        }


class InstitutionDataVerifyRequest(BaseModel):
    """Request to verify current data is accurate"""

    academic_year: str = Field(
        ..., description="Academic year being verified, e.g., '2025-26'"
    )
    fields: Optional[List[str]] = Field(
        None,
        description="Specific fields to verify. If not provided, verifies all cost/admissions data",
    )
    notes: Optional[str] = Field(
        None, max_length=500, description="Optional notes about verification"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "academic_year": "2025-26",
                "notes": "Verified all costs are current for upcoming academic year",
            }
        }


class InstitutionDataQualityResponse(BaseModel):
    """Response showing data quality metrics"""

    institution_id: int
    institution_name: str
    completeness_score: int = Field(..., ge=0, le=100)
    data_source: str = Field(..., description="'manual', 'ipeds', 'admin', or 'mixed'")
    data_last_updated: datetime
    ipeds_year: Optional[str] = None

    # What's missing
    missing_fields: List[str] = Field(
        ..., description="List of important fields that are empty"
    )

    # What's verified
    verified_fields: List[str] = Field(
        ..., description="List of fields verified by admin"
    )
    verification_count: int = Field(..., description="Total number of verifications")

    # Quick flags
    has_website: bool
    has_tuition_data: bool
    has_room_board: bool
    has_admissions_data: bool

    # 🆕 ADD THESE FIELDS
    image_count: int = Field(0, description="Number of gallery images")
    has_images: bool = Field(False, description="Has at least 1 image")

    # 🆕 ADD DETAILED SCORE BREAKDOWN
    score_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Detailed score breakdown by category"
    )


class VerificationHistoryItem(BaseModel):
    """Single verification history entry"""

    id: int
    field_name: str
    old_value: Optional[str]
    new_value: Optional[str]
    verified_by: str
    verified_at: datetime
    notes: Optional[str]

    class Config:
        from_attributes = True
