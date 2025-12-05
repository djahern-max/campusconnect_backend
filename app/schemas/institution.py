# app/schemas/institution.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class InstitutionBase(BaseModel):
    """Base schema with original fields"""

    ipeds_id: int
    name: str
    city: str
    state: str = Field(..., max_length=2, description="Two-letter state code")
    control_type: str
    primary_image_url: Optional[str] = None
    student_faculty_ratio: Optional[float] = None
    size_category: Optional[str] = None
    locale: Optional[str] = None


class InstitutionIPEDSData(BaseModel):
    """IPEDS-specific data fields"""

    # Base IPEDS info
    website: Optional[str] = None
    level: Optional[int] = Field(None, description="1=4-year, 2=2-year, 3=<2-year")
    control: Optional[int] = Field(
        None, description="1=Public, 2=Private NP, 3=Private FP"
    )

    # Data tracking
    data_completeness_score: int = Field(
        0, ge=0, le=100, description="Quality score 0-100"
    )
    data_source: str = Field(
        "manual", description="'manual', 'ipeds', 'admin', or 'mixed'"
    )
    ipeds_year: Optional[str] = Field(
        None, description="Academic year, e.g., '2023-24'"
    )
    is_featured: bool = False

    # Cost data - CHANGED TO FLOAT
    tuition_in_state: Optional[float] = Field(None, description="In-state tuition")
    tuition_out_of_state: Optional[float] = Field(
        None, description="Out-of-state tuition"
    )
    tuition_private: Optional[float] = Field(
        None, description="Private institution tuition"
    )
    tuition_in_district: Optional[float] = Field(
        None, description="In-district tuition"
    )
    room_cost: Optional[float] = Field(None, description="Room cost")
    board_cost: Optional[float] = Field(None, description="Board/meal plan cost")
    room_and_board: Optional[float] = Field(None, description="Combined room and board")
    application_fee_undergrad: Optional[float] = Field(
        None, description="Undergrad application fee"
    )
    application_fee_grad: Optional[float] = Field(
        None, description="Graduate application fee"
    )

    # Admissions data - CHANGED TO FLOAT
    acceptance_rate: Optional[float] = Field(
        None, ge=0, le=100, description="Acceptance rate percentage"
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

    # Add validator to handle Decimal from database
    @field_validator(
        "tuition_in_state",
        "tuition_out_of_state",
        "tuition_private",
        "tuition_in_district",
        "room_cost",
        "board_cost",
        "room_and_board",
        "application_fee_undergrad",
        "application_fee_grad",
        "acceptance_rate",
        mode="before",
    )
    @classmethod
    def convert_decimal_to_float(cls, v):
        """Convert Decimal from database to float for JSON serialization"""
        if v is None:
            return None
        from decimal import Decimal

        if isinstance(v, Decimal):
            return float(v)
        return v


class InstitutionCreate(InstitutionBase):
    """Schema for creating a new institution"""

    pass


class InstitutionUpdate(BaseModel):
    """Schema for updating an institution - all fields optional"""

    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(None, max_length=2)
    control_type: Optional[str] = None
    primary_image_url: Optional[str] = None
    student_faculty_ratio: Optional[float] = None
    size_category: Optional[str] = None
    locale: Optional[str] = None

    # Allow updating IPEDS fields
    website: Optional[str] = None
    level: Optional[int] = None
    control: Optional[int] = None
    data_source: Optional[str] = None
    is_featured: Optional[bool] = None

    # Cost data updates - CHANGED TO FLOAT
    tuition_in_state: Optional[float] = None
    tuition_out_of_state: Optional[float] = None
    tuition_private: Optional[float] = None
    tuition_in_district: Optional[float] = None
    room_cost: Optional[float] = None
    board_cost: Optional[float] = None
    room_and_board: Optional[float] = None
    application_fee_undergrad: Optional[float] = None
    application_fee_grad: Optional[float] = None

    # Admissions data updates - CHANGED TO FLOAT
    acceptance_rate: Optional[float] = Field(None, ge=0, le=100)
    sat_reading_25th: Optional[int] = Field(None, ge=200, le=800)
    sat_reading_75th: Optional[int] = Field(None, ge=200, le=800)
    sat_math_25th: Optional[int] = Field(None, ge=200, le=800)
    sat_math_75th: Optional[int] = Field(None, ge=200, le=800)
    act_composite_25th: Optional[int] = Field(None, ge=1, le=36)
    act_composite_75th: Optional[int] = Field(None, ge=1, le=36)


class InstitutionResponse(InstitutionBase, InstitutionIPEDSData):
    """Complete institution response with all fields"""

    id: int
    created_at: datetime
    updated_at: datetime
    data_last_updated: datetime

    class Config:
        from_attributes = True


class InstitutionSummary(BaseModel):
    """Lightweight summary for list views"""

    id: int
    ipeds_id: int
    name: str
    city: str
    state: str
    data_completeness_score: int
    data_source: str
    is_featured: bool
    primary_image_url: Optional[str] = None

    # Include key cost data for previews - CHANGED TO FLOAT
    tuition_in_state: Optional[float] = None
    tuition_out_of_state: Optional[float] = None
    tuition_private: Optional[float] = None

    # Include key admissions data for previews - CHANGED TO FLOAT
    acceptance_rate: Optional[float] = None

    # Add validator
    @field_validator(
        "tuition_in_state",
        "tuition_out_of_state",
        "tuition_private",
        "acceptance_rate",
        mode="before",
    )
    @classmethod
    def convert_decimal_to_float(cls, v):
        if v is None:
            return None
        from decimal import Decimal

        if isinstance(v, Decimal):
            return float(v)
        return v

    class Config:
        from_attributes = True


class InstitutionWithCompleteness(InstitutionSummary):
    """Institution with completeness details for admin dashboard"""

    website: Optional[str] = None
    level: Optional[int] = None
    ipeds_year: Optional[str] = None
    data_last_updated: datetime

    # Flags for what data exists
    has_cost_data: bool = Field(False, description="Has any cost data")
    has_admissions_data: bool = Field(False, description="Has any admissions data")
    has_images: bool = Field(False, description="Has gallery images")

    class Config:
        from_attributes = True


# NEW: Add response models for API endpoints
class TierStats(BaseModel):
    """Statistics for a completeness tier"""

    tier: str
    count: int
    percentage: float
    avg_score: float


class CompletenessStats(BaseModel):
    """Complete statistics response"""

    total_institutions: int
    tiers: list[TierStats]
    data_sources: dict[str, int]


class StateSummaryInstitution(BaseModel):
    """Lightweight institution data for state summary"""

    id: int
    ipeds_id: int
    name: str
    city: str
    data_completeness_score: int
    tuition_in_state: Optional[float] = None
    tuition_out_of_state: Optional[float] = None
    tuition_private: Optional[float] = None
    acceptance_rate: Optional[float] = None


class StateSummaryResponse(BaseModel):
    """State summary response"""

    state: str
    total_count: int
    avg_completeness_score: Optional[float] = None
    message: Optional[str] = None
    statistics: Optional[dict] = None
    institutions: list[StateSummaryInstitution] = []


class InstitutionFilter(BaseModel):
    """Filter parameters for searching institutions"""

    state: Optional[str] = None
    control_type: Optional[str] = None
    level: Optional[int] = None
    min_completeness: Optional[int] = Field(
        None, ge=0, le=100, description="Minimum completeness score"
    )
    max_completeness: Optional[int] = Field(
        None, ge=0, le=100, description="Maximum completeness score"
    )
    data_source: Optional[str] = Field(None, description="Filter by data source")
    is_featured: Optional[bool] = None
    has_cost_data: Optional[bool] = Field(
        None, description="Filter institutions with cost data"
    )
    has_admissions_data: Optional[bool] = Field(
        None, description="Filter institutions with admissions data"
    )
    search: Optional[str] = Field(None, description="Search by name or city")

    # Pagination
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)

    class Config:
        from_attributes = True


class CompletenessBreakdown(BaseModel):
    """Detailed breakdown of completeness score components"""

    institution_id: int
    institution_name: str
    total_score: int

    # Score components
    core_identity_score: int = Field(..., description="Name, location, website (0-20)")
    cost_data_score: int = Field(..., description="Tuition and room/board (0-40)")
    admissions_score: int = Field(
        ..., description="Acceptance rate and test scores (0-10)"
    )
    image_score: int = Field(..., description="Gallery images (0-30)")
    admin_bonus: int = Field(..., description="Admin verification bonus (0-10)")

    # Missing data flags
    missing_website: bool = False
    missing_tuition: bool = False
    missing_room_board: bool = False
    missing_admissions: bool = False
    missing_images: bool = False

    class Config:
        from_attributes = True


class InstitutionBasicResponse(BaseModel):
    id: int
    ipeds_id: int  # ADD THIS LINE
    name: str

    class Config:
        orm_mode = True
