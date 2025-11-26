# app/api/v1/admin_scholarships.py
"""
Admin-only endpoints for managing scholarships.

These endpoints allow authenticated admin users to:
1. Create new scholarships
2. Update existing scholarships
3. Delete scholarships
4. Mark scholarships as verified/featured
5. View scholarship statistics
6. Manage scholarship status

All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, or_
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.models.scholarship import Scholarship, ScholarshipStatus
from app.schemas.scholarship import ScholarshipResponse
from pydantic import BaseModel, Field

# You'll need to implement this dependency based on your auth system
# from app.api.deps import get_current_admin_user

router = APIRouter(prefix="/admin/scholarships", tags=["admin-scholarships"])


# ============================================================================
# PYDANTIC SCHEMAS FOR ADMIN OPERATIONS
# ============================================================================


class ScholarshipCreate(BaseModel):
    """Schema for creating a new scholarship"""

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
    """Schema for updating a scholarship - all fields optional"""

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


class VerifyScholarshipRequest(BaseModel):
    """Request to verify a scholarship"""

    verified: bool
    notes: Optional[str] = Field(None, description="Optional notes about verification")


class FeatureScholarshipRequest(BaseModel):
    """Request to feature/unfeature a scholarship"""

    featured: bool


# ============================================================================
# CRUD ENDPOINTS
# ============================================================================


@router.post(
    "", response_model=ScholarshipResponse, status_code=status.HTTP_201_CREATED
)
async def create_scholarship(
    scholarship: ScholarshipCreate,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Create a new scholarship (admin only).

    **Requires admin authentication.**
    """
    # Validate amount_max >= amount_min
    if scholarship.amount_max < scholarship.amount_min:
        raise HTTPException(
            status_code=400,
            detail="amount_max must be greater than or equal to amount_min",
        )

    # Create scholarship
    new_scholarship = Scholarship(**scholarship.model_dump())

    db.add(new_scholarship)
    await db.commit()
    await db.refresh(new_scholarship)

    return new_scholarship


@router.patch("/{scholarship_id}", response_model=ScholarshipResponse)
async def update_scholarship(
    scholarship_id: int,
    updates: ScholarshipUpdate,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Update a scholarship (admin only).

    Only provided fields will be updated. All fields are optional.

    **Requires admin authentication.**
    """
    # Get scholarship
    query = select(Scholarship).where(Scholarship.id == scholarship_id)
    result = await db.execute(query)
    scholarship = result.scalar_one_or_none()

    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    # Update fields that were provided
    update_data = updates.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(scholarship, field, value)

    # Validate amounts if either was updated
    if "amount_min" in update_data or "amount_max" in update_data:
        if scholarship.amount_max < scholarship.amount_min:
            raise HTTPException(
                status_code=400,
                detail="amount_max must be greater than or equal to amount_min",
            )

    # Update timestamp
    scholarship.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(scholarship)

    return scholarship


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scholarship(
    scholarship_id: int,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Delete a scholarship (admin only).

    **Requires admin authentication.**
    """
    query = select(Scholarship).where(Scholarship.id == scholarship_id)
    result = await db.execute(query)
    scholarship = result.scalar_one_or_none()

    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    await db.delete(scholarship)
    await db.commit()

    return None


# ============================================================================
# VERIFICATION & FEATURING
# ============================================================================


@router.patch("/{scholarship_id}/verify", response_model=ScholarshipResponse)
async def verify_scholarship(
    scholarship_id: int,
    verification: VerifyScholarshipRequest,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Mark scholarship as verified or unverified (admin only).

    Verified scholarships show a badge and are trusted by users.

    **Requires admin authentication.**
    """
    query = select(Scholarship).where(Scholarship.id == scholarship_id)
    result = await db.execute(query)
    scholarship = result.scalar_one_or_none()

    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    scholarship.verified = verification.verified
    scholarship.updated_at = datetime.utcnow()

    # TODO: Log verification in audit trail with notes

    await db.commit()
    await db.refresh(scholarship)

    return scholarship


@router.patch("/{scholarship_id}/feature", response_model=ScholarshipResponse)
async def feature_scholarship(
    scholarship_id: int,
    feature_request: FeatureScholarshipRequest,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Mark scholarship as featured or remove featured status (admin only).

    Featured scholarships appear in special lists and get priority display.

    **Requires admin authentication.**
    """
    query = select(Scholarship).where(Scholarship.id == scholarship_id)
    result = await db.execute(query)
    scholarship = result.scalar_one_or_none()

    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    scholarship.featured = feature_request.featured
    scholarship.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(scholarship)

    return scholarship


# ============================================================================
# BATCH OPERATIONS
# ============================================================================


class BulkStatusUpdateRequest(BaseModel):
    """Request to update status for multiple scholarships"""

    scholarship_ids: List[int] = Field(..., max_items=100)
    status: str

    class Config:
        json_schema_extra = {
            "example": {"scholarship_ids": [1, 2, 3], "status": "EXPIRED"}
        }


@router.post("/bulk-status-update")
async def bulk_update_status(
    request: BulkStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Update status for multiple scholarships at once (admin only).

    Useful for:
    - Marking expired scholarships as EXPIRED
    - Deactivating old scholarships
    - Reactivating scholarships for new year

    **Requires admin authentication.**
    """
    if len(request.scholarship_ids) > 100:
        raise HTTPException(
            status_code=400, detail="Cannot update more than 100 scholarships at once"
        )

    # Validate status
    valid_statuses = ["ACTIVE", "INACTIVE", "EXPIRED"]
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Status must be one of: {', '.join(valid_statuses)}",
        )

    # Get scholarships
    query = select(Scholarship).where(Scholarship.id.in_(request.scholarship_ids))
    result = await db.execute(query)
    scholarships = result.scalars().all()

    if len(scholarships) != len(request.scholarship_ids):
        raise HTTPException(status_code=404, detail="Some scholarships not found")

    # Update all
    updated_count = 0
    for scholarship in scholarships:
        scholarship.status = ScholarshipStatus[request.status]
        scholarship.updated_at = datetime.utcnow()
        updated_count += 1

    await db.commit()

    return {
        "updated_count": updated_count,
        "new_status": request.status,
        "scholarship_ids": [s.id for s in scholarships],
    }


# ============================================================================
# ADMIN DASHBOARD & STATISTICS
# ============================================================================


@router.get("/stats/overview")
async def get_scholarship_stats(
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Get scholarship statistics for admin dashboard (admin only).

    **Requires admin authentication.**
    """
    # Total counts
    total_query = select(func.count(Scholarship.id))
    total_result = await db.execute(total_query)
    total_scholarships = total_result.scalar()

    # By status
    active_query = select(func.count(Scholarship.id)).where(
        Scholarship.status == ScholarshipStatus.ACTIVE
    )
    active_result = await db.execute(active_query)
    active_count = active_result.scalar()

    # Verified count
    verified_query = select(func.count(Scholarship.id)).where(
        Scholarship.verified == True
    )
    verified_result = await db.execute(verified_query)
    verified_count = verified_result.scalar()

    # Featured count
    featured_query = select(func.count(Scholarship.id)).where(
        Scholarship.featured == True
    )
    featured_result = await db.execute(featured_query)
    featured_count = featured_result.scalar()

    # Total amount available (sum of max amounts for active scholarships)
    amount_query = select(func.sum(Scholarship.amount_max)).where(
        Scholarship.status == ScholarshipStatus.ACTIVE
    )
    amount_result = await db.execute(amount_query)
    total_amount = amount_result.scalar() or 0

    # By type
    type_query = (
        select(Scholarship.scholarship_type, func.count(Scholarship.id).label("count"))
        .where(Scholarship.status == ScholarshipStatus.ACTIVE)
        .group_by(Scholarship.scholarship_type)
    )

    type_result = await db.execute(type_query)
    types = type_result.all()

    return {
        "summary": {
            "total_scholarships": total_scholarships,
            "active_scholarships": active_count,
            "verified_scholarships": verified_count,
            "featured_scholarships": featured_count,
            "total_amount_available": float(total_amount),
            "verification_rate": (
                round((verified_count / total_scholarships * 100), 1)
                if total_scholarships > 0
                else 0
            ),
        },
        "by_type": [
            {"type": str(type_name), "count": count} for type_name, count in types
        ],
    }


@router.get("/needs-review")
async def get_scholarships_needing_review(
    verified: Optional[bool] = Query(None, description="Filter by verification status"),
    expired: Optional[bool] = Query(None, description="Show only expired scholarships"),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Get scholarships that need admin review (admin only).

    Useful for:
    - Finding unverified scholarships
    - Identifying expired scholarships
    - Reviewing recently added scholarships

    **Requires admin authentication.**
    """
    query = select(Scholarship)

    filters = []

    # Verification filter
    if verified is not None:
        filters.append(Scholarship.verified == verified)

    # Expired filter (deadline passed)
    if expired:
        filters.append(
            and_(Scholarship.deadline.isnot(None), Scholarship.deadline < date.today())
        )

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(desc(Scholarship.created_at)).limit(limit)

    result = await db.execute(query)
    scholarships = result.scalars().all()

    return {
        "filters": {"verified": verified, "expired": expired},
        "count": len(scholarships),
        "scholarships": [
            {
                "id": s.id,
                "title": s.title,
                "organization": s.organization,
                "status": str(s.status),
                "verified": s.verified,
                "featured": s.featured,
                "deadline": s.deadline,
                "amount_max": s.amount_max,
                "is_expired": s.deadline < date.today() if s.deadline else False,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
            }
            for s in scholarships
        ],
    }


@router.get("/recent")
async def get_recent_scholarships(
    days: int = Query(7, ge=1, le=90, description="Look back this many days"),
    limit: int = Query(20, le=100),
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Get recently created or updated scholarships (admin only).

    **Requires admin authentication.**
    """
    from datetime import timedelta

    cutoff_date = datetime.utcnow() - timedelta(days=days)

    query = (
        select(Scholarship)
        .where(
            or_(
                Scholarship.created_at >= cutoff_date,
                Scholarship.updated_at >= cutoff_date,
            )
        )
        .order_by(desc(Scholarship.updated_at))
        .limit(limit)
    )

    result = await db.execute(query)
    scholarships = result.scalars().all()

    return {
        "lookback_days": days,
        "count": len(scholarships),
        "scholarships": scholarships,
    }


# ============================================================================
# SEARCH & FILTER (ADMIN VIEW)
# ============================================================================


@router.get("/search", response_model=List[ScholarshipResponse])
async def search_scholarships_admin(
    query_text: Optional[str] = Query(None, min_length=2),
    scholarship_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    verified: Optional[bool] = Query(None),
    featured: Optional[bool] = Query(None),
    min_amount: Optional[int] = Query(None, ge=0),
    max_amount: Optional[int] = Query(None, ge=0),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth ready
):
    """
    Advanced search for scholarships with admin filters (admin only).

    Includes all scholarships regardless of status, unlike public endpoint.

    **Requires admin authentication.**
    """
    query = select(Scholarship)

    filters = []

    # Text search
    if query_text:
        search_term = f"%{query_text}%"
        filters.append(
            or_(
                Scholarship.title.ilike(search_term),
                Scholarship.organization.ilike(search_term),
                Scholarship.description.ilike(search_term),
            )
        )

    # Type filter
    if scholarship_type:
        filters.append(Scholarship.scholarship_type == scholarship_type)

    # Status filter
    if status:
        filters.append(Scholarship.status == status)

    # Verified filter
    if verified is not None:
        filters.append(Scholarship.verified == verified)

    # Featured filter
    if featured is not None:
        filters.append(Scholarship.featured == featured)

    # Amount filters
    if min_amount is not None:
        filters.append(Scholarship.amount_max >= min_amount)

    if max_amount is not None:
        filters.append(Scholarship.amount_min <= max_amount)

    if filters:
        query = query.where(and_(*filters))

    query = query.order_by(Scholarship.title).limit(limit).offset(offset)

    result = await db.execute(query)
    scholarships = result.scalars().all()

    return scholarships
