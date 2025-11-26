# app/schemas/scholarship.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date


# ============================================================================
# BASE SCHEMAS
# ============================================================================


class ScholarshipBase(BaseModel):
    """Base scholarship fields"""

    title: str
    organization: str
    scholarship_type: str
    status: str
    difficulty_level: str
    amount_min: int
    amount_max: int
    is_renewable: bool
    number_of_awards: Optional[int] = None
    deadline: Optional[date] = None
    application_opens: Optional[date] = None
    for_academic_year: Optional[str] = None
    description: Optional[str] = None
    website_url: Optional[str] = None
    min_gpa: Optional[float] = None
    primary_image_url: Optional[str] = None
    verified: bool
    featured: bool


# ============================================================================
# PUBLIC SCHEMAS (for students)
# ============================================================================


class ScholarshipResponse(ScholarshipBase):
    """Standard response for public endpoints"""

    id: int
    views_count: int
    applications_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ScholarshipSummary(BaseModel):
    """Lightweight summary for list views"""

    id: int
    title: str
    organization: str
    scholarship_type: str
    amount_min: int
    amount_max: int
    deadline: Optional[date] = None
    verified: bool
    featured: bool
    difficulty_level: str
    primary_image_url: Optional[str] = None

    class Config:
        from_attributes = True


class ScholarshipDetail(ScholarshipResponse):
    """Extended detail view with all information"""

    # Inherits all fields from ScholarshipResponse
    # Can add computed fields here

    @property
    def is_expired(self) -> bool:
        """Check if scholarship deadline has passed"""
        if self.deadline:
            return self.deadline < date.today()
        return False

    @property
    def days_until_deadline(self) -> Optional[int]:
        """Calculate days until deadline"""
        if self.deadline:
            delta = self.deadline - date.today()
            return delta.days
        return None

    class Config:
        from_attributes = True


# ============================================================================
# ADMIN SCHEMAS
# ============================================================================


class ScholarshipCreate(BaseModel):
    """Schema for creating a new scholarship (admin only)"""

    title: str = Field(..., min_length=1, max_length=255)
    organization: str = Field(..., min_length=1, max_length=255)
    scholarship_type: str
    status: str = "ACTIVE"
    difficulty_level: str = "MODERATE"
    amount_min: int = Field(..., ge=0)
    amount_max: int = Field(..., ge=0)
    is_renewable: bool = False
    number_of_awards: Optional[int] = Field(None, ge=1)
    deadline: Optional[date] = None
    application_opens: Optional[date] = None
    for_academic_year: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = Field(None, max_length=500)
    min_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    primary_image_url: Optional[str] = Field(None, max_length=500)
    verified: bool = False
    featured: bool = False

    class Config:
        json_schema_extra = {
            "example": {
                "title": "STEM Excellence Scholarship",
                "organization": "Tech Foundation",
                "scholarship_type": "STEM",
                "amount_min": 5000,
                "amount_max": 10000,
                "deadline": "2025-03-15",
                "description": "For outstanding STEM students",
                "website_url": "https://example.com/scholarship",
                "min_gpa": 3.5,
            }
        }


class ScholarshipUpdate(BaseModel):
    """Schema for updating a scholarship (admin only) - all fields optional"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    organization: Optional[str] = Field(None, min_length=1, max_length=255)
    scholarship_type: Optional[str] = None
    status: Optional[str] = None
    difficulty_level: Optional[str] = None
    amount_min: Optional[int] = Field(None, ge=0)
    amount_max: Optional[int] = Field(None, ge=0)
    is_renewable: Optional[bool] = None
    number_of_awards: Optional[int] = Field(None, ge=1)
    deadline: Optional[date] = None
    application_opens: Optional[date] = None
    for_academic_year: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = Field(None, max_length=500)
    website_url: Optional[str] = Field(None, max_length=500)
    min_gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    primary_image_url: Optional[str] = Field(None, max_length=500)
    verified: Optional[bool] = None
    featured: Optional[bool] = None


class ScholarshipAdminView(ScholarshipResponse):
    """Admin view with additional management fields"""

    # Includes all public fields plus admin-specific info

    # Computed fields for admin dashboard
    is_expired: bool = Field(default=False, description="Whether deadline has passed")
    needs_review: bool = Field(
        default=False, description="Whether scholarship needs admin review"
    )
    days_until_deadline: Optional[int] = Field(
        None, description="Days remaining until deadline"
    )

    class Config:
        from_attributes = True


class ScholarshipFilter(BaseModel):
    """Filter parameters for searching scholarships"""

    query_text: Optional[str] = Field(
        None, min_length=2, description="Search in title, organization, description"
    )
    scholarship_type: Optional[str] = Field(None, description="Filter by type")
    status: Optional[str] = Field(None, description="Filter by status")
    verified: Optional[bool] = Field(None, description="Filter by verification status")
    featured: Optional[bool] = Field(None, description="Filter by featured status")
    difficulty_level: Optional[str] = Field(None, description="Filter by difficulty")
    min_amount: Optional[int] = Field(None, ge=0, description="Minimum award amount")
    max_amount: Optional[int] = Field(None, ge=0, description="Maximum award amount")
    min_gpa: Optional[float] = Field(
        None, ge=0.0, le=4.0, description="Minimum GPA requirement"
    )
    is_renewable: Optional[bool] = Field(
        None, description="Filter renewable scholarships"
    )
    has_deadline: Optional[bool] = Field(
        None, description="Filter scholarships with deadline set"
    )

    # Pagination
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=500)

    class Config:
        from_attributes = True


# ============================================================================
# STATISTICS & DASHBOARD SCHEMAS
# ============================================================================


class ScholarshipStats(BaseModel):
    """Statistics for admin dashboard"""

    total_scholarships: int
    active_scholarships: int
    verified_scholarships: int
    featured_scholarships: int
    expired_scholarships: int
    total_amount_available: float
    avg_award_amount: float

    # By type
    by_type: dict

    # By difficulty
    by_difficulty: dict


class ScholarshipTypeBreakdown(BaseModel):
    """Breakdown of scholarships by type"""

    scholarship_type: str
    count: int
    total_amount: float
    avg_amount: float


# ============================================================================
# BULK OPERATION SCHEMAS
# ============================================================================


class BulkUpdateRequest(BaseModel):
    """Request for bulk updates"""

    scholarship_ids: list[int] = Field(..., max_items=100)
    updates: ScholarshipUpdate


class BulkStatusUpdateRequest(BaseModel):
    """Request to update status for multiple scholarships"""

    scholarship_ids: list[int] = Field(..., max_items=100)
    status: str


class BulkVerifyRequest(BaseModel):
    """Request to verify multiple scholarships"""

    scholarship_ids: list[int] = Field(..., max_items=100)
    verified: bool
    notes: Optional[str] = None
