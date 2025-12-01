# app/api/v1/scholarships.py
# app/api/v1/scholarships.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models.scholarship import Scholarship
from app.schemas.scholarship import ScholarshipResponse

router = APIRouter(prefix="/scholarships", tags=["scholarships"])


# ============================================================================
# PAGINATION RESPONSE MODEL
# ============================================================================


class PaginatedScholarshipResponse(BaseModel):
    """Paginated response for scholarships list"""

    scholarships: List[ScholarshipResponse]
    total: int
    page: int
    limit: int
    has_more: bool


# ============================================================================
# MAIN ENDPOINTS
# ============================================================================


@router.get("", response_model=PaginatedScholarshipResponse)
async def get_scholarships(
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(100, ge=1, le=500, description="Items per page (max 500)"),
    scholarship_type: Optional[str] = Query(
        None, description="Filter by scholarship type"
    ),
    status: Optional[str] = Query(
        None, description="Filter by status (default: ACTIVE only)"
    ),
    featured: Optional[bool] = Query(None, description="Filter featured scholarships"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all scholarships with pagination.
    Sorted by featured first, then by deadline (soonest first), then by title.
    PUBLIC endpoint - no authentication required.

    By default, only returns ACTIVE scholarships.
    """
    # Build base query
    query = select(Scholarship)
    count_query = select(func.count(Scholarship.id))

    # Default to ACTIVE scholarships only unless status is explicitly provided
    if status:
        query = query.where(Scholarship.status == status.upper())
        count_query = count_query.where(Scholarship.status == status.upper())
    else:
        query = query.where(Scholarship.status == "ACTIVE")
        count_query = count_query.where(Scholarship.status == "ACTIVE")

    # Apply filters
    if scholarship_type:
        query = query.where(Scholarship.scholarship_type == scholarship_type.upper())
        count_query = count_query.where(
            Scholarship.scholarship_type == scholarship_type.upper()
        )

    if featured is not None:
        query = query.where(Scholarship.featured == featured)
        count_query = count_query.where(Scholarship.featured == featured)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Sort: Featured first, then by deadline (soonest first, nulls last), then by title
    query = query.order_by(
        Scholarship.featured.desc(),
        Scholarship.deadline.asc().nullslast(),
        Scholarship.title,
    )

    # Apply pagination
    offset = (page - 1) * limit
    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    scholarships = result.scalars().all()

    # Calculate if there are more pages
    has_more = (offset + len(scholarships)) < total

    return PaginatedScholarshipResponse(
        scholarships=scholarships,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more,
    )


@router.get("/{scholarship_id}", response_model=ScholarshipResponse)
async def get_scholarship(scholarship_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single scholarship by ID.
    PUBLIC endpoint - no authentication required.
    """
    query = select(Scholarship).where(Scholarship.id == scholarship_id)
    result = await db.execute(query)
    scholarship = result.scalar_one_or_none()

    if not scholarship:
        raise HTTPException(status_code=404, detail="Scholarship not found")

    return scholarship
