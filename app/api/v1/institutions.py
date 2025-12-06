# app/api/v1/institutions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, func, and_, or_
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import (
    InstitutionResponse,
    InstitutionSummary,
    InstitutionBasicResponse,
)
from app.schemas.institution_data import InstitutionComplete


router = APIRouter(prefix="/institutions", tags=["institutions"])


# ============================================================================
# PAGINATION RESPONSE MODEL
# ============================================================================


class PaginatedInstitutionResponse(BaseModel):
    """Paginated response for institutions list"""

    institutions: List[InstitutionResponse]
    total: int
    page: int
    limit: int
    has_more: bool


# ============================================================================
# MAIN ENDPOINTS
# ============================================================================


@router.get("", response_model=PaginatedInstitutionResponse)
async def get_institutions(
    state: Optional[str] = Query(None, max_length=2),
    page: int = Query(1, ge=1, description="Page number (starts at 1)"),
    limit: int = Query(100, ge=1, le=500, description="Items per page (max 500)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all institutions with optional state filter and pagination.
    Sorted by data completeness score (best schools with best images first).
    PUBLIC endpoint - no authentication required.

    Returns paginated response with metadata for efficient loading.
    """
    # Build base query
    query = select(Institution)
    count_query = select(func.count(Institution.id))

    # Apply state filter to both queries
    if state:
        state_upper = state.upper()
        query = query.where(Institution.state == state_upper)
        count_query = count_query.where(Institution.state == state_upper)

    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Sort by data completeness score (best schools first), then name
    query = query.order_by(Institution.data_completeness_score.desc(), Institution.name)

    # Apply pagination
    offset = (page - 1) * limit
    query = query.limit(limit).offset(offset)

    # Execute query
    result = await db.execute(query)
    institutions = result.scalars().all()

    # Calculate if there are more pages
    has_more = (offset + len(institutions)) < total

    return PaginatedInstitutionResponse(
        institutions=institutions,
        total=total,
        page=page,
        limit=limit,
        has_more=has_more,
    )


# Admin Endpoint


@router.get("/search", response_model=List[InstitutionBasicResponse])
async def search_institutions(
    q: str = Query(..., min_length=1), db: AsyncSession = Depends(get_db)
):
    """
    Quick lookup for institutions by name (for admin UI / invitation creation).
    Returns up to 50 matches.
    """
    query = (
        select(Institution)
        .where(Institution.name.ilike(f"%{q}%"))
        .order_by(Institution.name)
        .limit(50)
    )

    result = await db.execute(query)
    institutions = result.scalars().all()
    return institutions


@router.get("/{ipeds_id}", response_model=InstitutionResponse)
async def get_institution(ipeds_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a single institution by IPEDS ID.
    PUBLIC endpoint - no authentication required.
    """
    query = select(Institution).where(Institution.ipeds_id == ipeds_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution


@router.get("/by-id/{institution_id}", response_model=InstitutionResponse)
async def get_institution_by_id(
    institution_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get a single institution by database ID.
    PUBLIC endpoint - no authentication required.
    """
    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution


# ============================================================================
# ADVANCED SEARCH ENDPOINTS (IPEDS INTEGRATION)
# ============================================================================


@router.get("/search/filtered", response_model=List[InstitutionSummary])
async def search_institutions_filtered(
    # Search filters
    query_text: Optional[str] = Query(
        None, min_length=2, description="Search by name or city"
    ),
    state: Optional[str] = Query(None, max_length=2, description="Filter by state"),
    # IPEDS filters
    min_completeness: Optional[int] = Query(
        60,
        ge=0,
        le=100,
        description="Minimum data completeness score (0-100). Default: 60 for quality data",
    ),
    data_source: Optional[str] = Query(
        None, description="Filter by data source: 'manual', 'ipeds', 'admin', 'mixed'"
    ),
    level: Optional[int] = Query(
        None, ge=1, le=3, description="1=4-year, 2=2-year, 3=<2-year"
    ),
    is_featured: Optional[bool] = Query(
        None, description="Show only featured institutions"
    ),
    # Cost data filters
    has_cost_data: Optional[bool] = Query(
        None, description="Filter institutions with cost data"
    ),
    max_tuition: Optional[float] = Query(None, description="Maximum tuition amount"),
    # Admissions filters
    has_admissions_data: Optional[bool] = Query(
        None, description="Filter institutions with admissions data"
    ),
    max_acceptance_rate: Optional[float] = Query(
        None, ge=0, le=100, description="Maximum acceptance rate"
    ),
    # Pagination
    limit: int = Query(100, le=10000),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Advanced search with IPEDS data filtering.
    Sorted by data completeness score (best schools first).
    PUBLIC endpoint - no authentication required.
    """
    query = select(Institution)

    # Apply filters
    filters = []

    # Text search
    if query_text:
        search_term = f"%{query_text}%"
        filters.append(
            or_(
                Institution.name.ilike(search_term), Institution.city.ilike(search_term)
            )
        )

    # State filter
    if state:
        filters.append(Institution.state == state.upper())

    # Completeness filter (default: 60+)
    if min_completeness is not None:
        filters.append(Institution.data_completeness_score >= min_completeness)

    # Data source filter
    if data_source:
        filters.append(Institution.data_source == data_source)

    # Level filter
    if level:
        filters.append(Institution.level == level)

    # Featured filter
    if is_featured is not None:
        filters.append(Institution.is_featured == is_featured)

    # Cost data filter
    if has_cost_data:
        filters.append(
            or_(
                Institution.tuition_in_state.isnot(None),
                Institution.tuition_out_of_state.isnot(None),
                Institution.tuition_private.isnot(None),
            )
        )

    # Maximum tuition filter
    if max_tuition:
        filters.append(
            or_(
                Institution.tuition_in_state <= max_tuition,
                Institution.tuition_out_of_state <= max_tuition,
                Institution.tuition_private <= max_tuition,
            )
        )

    # Admissions data filter
    if has_admissions_data:
        filters.append(Institution.acceptance_rate.isnot(None))

    # Maximum acceptance rate filter
    if max_acceptance_rate:
        filters.append(Institution.acceptance_rate <= max_acceptance_rate)

    # Apply all filters
    if filters:
        query = query.where(and_(*filters))

    # Order by completeness score (best first), then name
    query = query.order_by(Institution.data_completeness_score.desc(), Institution.name)

    # Pagination
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    institutions = result.scalars().all()

    return institutions


@router.get("/stats/completeness")
async def get_completeness_statistics(db: AsyncSession = Depends(get_db)):
    """
    Get distribution of data completeness scores across all institutions.
    Shows how many institutions fall into each quality tier.
    PUBLIC endpoint - no authentication required.
    """
    # Get tier distribution
    tier_query = select(
        case(
            (Institution.data_completeness_score >= 80, "Excellent (80-100)"),
            (Institution.data_completeness_score >= 60, "Good (60-79)"),
            (Institution.data_completeness_score >= 40, "Fair (40-59)"),
            else_="Poor (0-39)",
        ).label("tier"),
        func.count(Institution.id).label("count"),
        func.avg(Institution.data_completeness_score).label("avg_score"),
    ).group_by("tier")

    result = await db.execute(tier_query)
    tiers = result.all()

    # Get total count
    total_query = select(func.count(Institution.id))
    total_result = await db.execute(total_query)
    total_count = total_result.scalar()

    # Get data source distribution
    source_query = select(
        Institution.data_source, func.count(Institution.id).label("count")
    ).group_by(Institution.data_source)

    source_result = await db.execute(source_query)
    sources = source_result.all()

    # Format response
    tier_data = []
    for tier, count, avg_score in tiers:
        tier_data.append(
            {
                "tier": tier,
                "count": count,
                "percentage": (
                    round((count / total_count * 100), 2) if total_count > 0 else 0
                ),
                "avg_score": round(float(avg_score), 1) if avg_score else 0,
            }
        )

    source_data = {source: count for source, count in sources}

    return {
        "total_institutions": total_count,
        "tiers": tier_data,
        "data_sources": source_data,
    }


@router.get("/featured/list", response_model=List[InstitutionSummary])
async def get_featured_institutions(
    limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)
):
    """
    Get featured institutions (manually curated).
    Only returns institutions with good data quality (70+ completeness).
    PUBLIC endpoint - no authentication required.
    """
    query = (
        select(Institution)
        .where(
            and_(
                Institution.is_featured == True,
                Institution.data_completeness_score >= 70,
            )
        )
        .order_by(Institution.data_completeness_score.desc(), Institution.name)
        .limit(limit)
    )

    result = await db.execute(query)
    institutions = result.scalars().all()

    return institutions


@router.get("/by-state/{state}/summary")
async def get_state_summary(
    state: str,
    min_completeness: int = Query(60, ge=0, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get summary statistics for institutions in a specific state.
    PUBLIC endpoint - no authentication required.
    """
    state = state.upper()

    # Get institutions in state
    query = (
        select(Institution)
        .where(
            and_(
                Institution.state == state,
                Institution.data_completeness_score >= min_completeness,
            )
        )
        .order_by(Institution.data_completeness_score.desc(), Institution.name)
    )

    result = await db.execute(query)
    institutions = result.scalars().all()

    if not institutions:
        return {
            "state": state,
            "total_count": 0,
            "message": "No institutions found matching criteria",
        }

    # Calculate statistics
    total = len(institutions)
    avg_completeness = sum(i.data_completeness_score for i in institutions) / total

    with_cost_data = len(
        [
            i
            for i in institutions
            if i.tuition_in_state or i.tuition_out_of_state or i.tuition_private
        ]
    )

    with_admissions = len([i for i in institutions if i.acceptance_rate])

    # Get level distribution
    four_year = len([i for i in institutions if i.level == 1])
    two_year = len([i for i in institutions if i.level == 2])

    return {
        "state": state,
        "total_count": total,
        "avg_completeness_score": round(avg_completeness, 1),
        "statistics": {
            "with_cost_data": with_cost_data,
            "with_admissions_data": with_admissions,
            "four_year_institutions": four_year,
            "two_year_institutions": two_year,
        },
        "institutions": [
            {
                "id": i.id,
                "ipeds_id": i.ipeds_id,
                "name": i.name,
                "city": i.city,
                "data_completeness_score": i.data_completeness_score,
                "tuition_in_state": (
                    float(i.tuition_in_state) if i.tuition_in_state else None
                ),
                "tuition_out_of_state": (
                    float(i.tuition_out_of_state) if i.tuition_out_of_state else None
                ),
                "tuition_private": (
                    float(i.tuition_private) if i.tuition_private else None
                ),
                "acceptance_rate": (
                    float(i.acceptance_rate) if i.acceptance_rate else None
                ),
            }
            for i in institutions
        ],
    }


@router.get("/complete/{institution_id}", response_model=InstitutionComplete)
async def get_institution_complete(
    institution_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get a single institution by database ID with ALL fields.
    Returns complete data including all IPEDS fields, costs, admissions, timestamps, etc.

    PUBLIC endpoint - no authentication required.
    """
    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution


@router.get("/complete/ipeds/{ipeds_id}", response_model=InstitutionComplete)
async def get_institution_complete_by_ipeds(
    ipeds_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get a single institution by IPEDS ID with ALL fields.
    Returns complete data including all IPEDS fields, costs, admissions, timestamps, etc.

    PUBLIC endpoint - no authentication required.
    """
    query = select(Institution).where(Institution.ipeds_id == ipeds_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution
