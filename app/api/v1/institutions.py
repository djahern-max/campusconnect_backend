# app/api/v1/institutions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case, func, and_, or_
from typing import List, Optional
from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionResponse, InstitutionSummary


router = APIRouter(prefix="/institutions", tags=["institutions"])


# ============================================================================
# EXISTING ENDPOINTS (UNCHANGED - 100% BACKWARD COMPATIBLE)
# ============================================================================


@router.get("", response_model=List[InstitutionResponse])
async def get_institutions(
    state: Optional[str] = Query(None, max_length=2),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all institutions with optional state filter.
    Priority states (NH, MA, CA) are shown first when no filter is applied.
    PUBLIC endpoint - no authentication required.

    BACKWARD COMPATIBLE: Returns all institutions regardless of completeness score.
    Use /institutions/search for filtered results.
    """
    query = select(Institution)

    if state:
        query = query.where(Institution.state == state.upper())
        # When filtering by state, just sort by name
        query = query.order_by(Institution.name)
    else:
        # No filter - prioritize NH, MA, CA first, then alphabetical
        priority_order = case(
            (Institution.state == "NH", 1),
            (Institution.state == "MA", 2),
            (Institution.state == "CA", 3),
            else_=4,
        )
        query = query.order_by(priority_order, Institution.state, Institution.name)

    query = query.limit(limit).offset(offset)

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
# NEW ENDPOINTS (IPEDS INTEGRATION)
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
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Advanced search with IPEDS data filtering.

    This endpoint filters by data quality and returns only institutions
    that meet your criteria. For backward compatibility, use the main
    /institutions endpoint which returns all institutions.

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


# ============================================================================
# HELPER ENDPOINT FOR TESTING
# ============================================================================


@router.get("/test/fields/{ipeds_id}")
async def test_ipeds_fields(ipeds_id: int, db: AsyncSession = Depends(get_db)):
    """
    Test endpoint to verify IPEDS fields are populated correctly.
    Shows all IPEDS fields for a specific institution.

    Use this to verify migration worked and data import was successful.
    """
    query = select(Institution).where(Institution.ipeds_id == ipeds_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return {
        "basic_info": {
            "id": institution.id,
            "ipeds_id": institution.ipeds_id,
            "name": institution.name,
            "city": institution.city,
            "state": institution.state,
            "website": institution.website,
            "level": institution.level,
            "control": institution.control,
        },
        "data_tracking": {
            "data_completeness_score": institution.data_completeness_score,
            "data_source": institution.data_source,
            "ipeds_year": institution.ipeds_year,
            "is_featured": institution.is_featured,
            "data_last_updated": institution.data_last_updated,
        },
        "cost_data": {
            "tuition_in_state": (
                float(institution.tuition_in_state)
                if institution.tuition_in_state
                else None
            ),
            "tuition_out_of_state": (
                float(institution.tuition_out_of_state)
                if institution.tuition_out_of_state
                else None
            ),
            "tuition_private": (
                float(institution.tuition_private)
                if institution.tuition_private
                else None
            ),
            "room_cost": (
                float(institution.room_cost) if institution.room_cost else None
            ),
            "board_cost": (
                float(institution.board_cost) if institution.board_cost else None
            ),
            "room_and_board": (
                float(institution.room_and_board)
                if institution.room_and_board
                else None
            ),
        },
        "admissions_data": {
            "acceptance_rate": (
                float(institution.acceptance_rate)
                if institution.acceptance_rate
                else None
            ),
            "sat_reading_25th": institution.sat_reading_25th,
            "sat_reading_75th": institution.sat_reading_75th,
            "sat_math_25th": institution.sat_math_25th,
            "sat_math_75th": institution.sat_math_75th,
            "act_composite_25th": institution.act_composite_25th,
            "act_composite_75th": institution.act_composite_75th,
        },
    }
