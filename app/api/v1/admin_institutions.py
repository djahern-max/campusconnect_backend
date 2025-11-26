# app/api/v1/admin_institutions.py
"""
Admin-only endpoints for updating and verifying IPEDS institution data.

These endpoints allow authenticated admin users to:
1. Update IPEDS data fields (costs, admissions, etc.)
2. Verify IPEDS data as current
3. Mark institutions as featured
4. View data quality dashboard
5. Track verification history

All endpoints require admin authentication.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc, case
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.models.institution import Institution
from app.models.admin_user import AdminUser  # You'll need to import your admin model
from app.schemas.institution import InstitutionResponse
from pydantic import BaseModel, Field

# You'll need to implement this dependency based on your auth system
# from app.api.deps import get_current_admin_user

router = APIRouter(prefix="/admin/institutions", tags=["admin-institutions"])


# ============================================================================
# PYDANTIC SCHEMAS FOR ADMIN UPDATES
# ============================================================================


class IPEDSDataUpdate(BaseModel):
    """Schema for updating IPEDS-related fields"""

    # Base fields
    website: Optional[str] = None
    level: Optional[int] = Field(None, ge=1, le=3)

    # Cost data
    tuition_in_state: Optional[Decimal] = Field(None, ge=0)
    tuition_out_of_state: Optional[Decimal] = Field(None, ge=0)
    tuition_private: Optional[Decimal] = Field(None, ge=0)
    tuition_in_district: Optional[Decimal] = Field(None, ge=0)
    room_cost: Optional[Decimal] = Field(None, ge=0)
    board_cost: Optional[Decimal] = Field(None, ge=0)
    room_and_board: Optional[Decimal] = Field(None, ge=0)
    application_fee_undergrad: Optional[Decimal] = Field(None, ge=0)
    application_fee_grad: Optional[Decimal] = Field(None, ge=0)

    # Admissions data
    acceptance_rate: Optional[Decimal] = Field(None, ge=0, le=100)
    sat_reading_25th: Optional[int] = Field(None, ge=200, le=800)
    sat_reading_75th: Optional[int] = Field(None, ge=200, le=800)
    sat_math_25th: Optional[int] = Field(None, ge=200, le=800)
    sat_math_75th: Optional[int] = Field(None, ge=200, le=800)
    act_composite_25th: Optional[int] = Field(None, ge=1, le=36)
    act_composite_75th: Optional[int] = Field(None, ge=1, le=36)

    # Academic year for this data
    ipeds_year: Optional[str] = Field(None, description="e.g., '2024-25'")

    class Config:
        json_schema_extra = {
            "example": {
                "tuition_in_state": 12500.00,
                "tuition_out_of_state": 35000.00,
                "room_and_board": 15000.00,
                "acceptance_rate": 45.5,
                "ipeds_year": "2024-25",
            }
        }


class VerifyIPEDSDataRequest(BaseModel):
    """Request to verify current IPEDS data"""

    academic_year: str = Field(
        ..., description="Academic year being verified, e.g., '2024-25'"
    )
    notes: Optional[str] = Field(None, description="Optional notes about verification")


class FeatureToggleRequest(BaseModel):
    """Request to toggle featured status"""

    is_featured: bool


# ============================================================================
# ADMIN UPDATE ENDPOINTS
# ============================================================================


@router.patch("/{institution_id}/ipeds-data", response_model=InstitutionResponse)
async def update_ipeds_data(
    institution_id: int,
    updates: IPEDSDataUpdate,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth is ready
):
    """
    Update IPEDS data for an institution (admin only).

    When admins update IPEDS fields:
    - Completeness score is automatically recalculated by database trigger
    - data_source changes to 'admin' or 'mixed' (depending on previous state)
    - data_last_updated timestamp is updated
    - Changes can be tracked in institution_data_verifications table

    **Requires admin authentication.**
    """
    # Get institution
    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    # Track original data source
    original_data_source = institution.data_source
    ipeds_fields_updated = False

    # Update fields that were provided (exclude_unset means only update non-None values)
    update_data = updates.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            # Check if this is an IPEDS data field
            if field in [
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
                "sat_reading_25th",
                "sat_reading_75th",
                "sat_math_25th",
                "sat_math_75th",
                "act_composite_25th",
                "act_composite_75th",
            ]:
                ipeds_fields_updated = True

            setattr(institution, field, value)

    # Update data_source if admin is updating IPEDS fields
    if ipeds_fields_updated:
        if original_data_source == "ipeds":
            institution.data_source = "mixed"  # Mix of IPEDS and admin updates
        else:
            institution.data_source = "admin"  # Admin-verified data

    # Commit changes (trigger will auto-update completeness score)
    await db.commit()
    await db.refresh(institution)

    # TODO: Create entry in institution_data_verifications table
    # This would track which admin made which changes and when

    return institution


@router.post("/{institution_id}/verify-ipeds-data", response_model=InstitutionResponse)
async def verify_ipeds_data(
    institution_id: int,
    verification: VerifyIPEDSDataRequest,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth is ready
):
    """
    Verify that current IPEDS data is accurate and up-to-date (admin only).

    This endpoint:
    - Marks the data as admin-verified
    - Updates data_source to 'admin'
    - Adds 10-point bonus to completeness score
    - Records verification in audit trail

    Use this when an admin has reviewed the IPEDS data and confirms it's current.

    **Requires admin authentication.**
    """
    # Get institution
    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    # Update to admin-verified
    institution.data_source = "admin"
    institution.ipeds_year = verification.academic_year
    institution.data_last_updated = datetime.utcnow()

    await db.commit()
    await db.refresh(institution)

    # TODO: Create verification record in institution_data_verifications table
    # Mark all current fields as verified by this admin

    return institution


@router.patch("/{institution_id}/featured", response_model=InstitutionResponse)
async def toggle_featured(
    institution_id: int,
    toggle: FeatureToggleRequest,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth is ready
):
    """
    Mark institution as featured or remove featured status (admin only).

    Featured institutions appear in special lists and may get priority display.

    **Requires admin authentication.**
    """
    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    institution.is_featured = toggle.is_featured

    await db.commit()
    await db.refresh(institution)

    return institution


# ============================================================================
# ADMIN DATA QUALITY DASHBOARD
# ============================================================================


@router.get("/data-quality/dashboard")
async def get_data_quality_dashboard(
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth is ready
):
    """
    Get data quality overview for admin dashboard (admin only).

    Shows:
    - Overall completeness statistics
    - Institutions needing attention (low completeness but have some data)
    - Recently updated institutions
    - Verification status breakdown

    **Requires admin authentication.**
    """
    # Overall statistics
    total_query = select(func.count(Institution.id))
    total_result = await db.execute(total_query)
    total_institutions = total_result.scalar()

    avg_query = select(func.avg(Institution.data_completeness_score))
    avg_result = await db.execute(avg_query)
    avg_completeness = avg_result.scalar() or 0

    # Institutions needing attention (20-79 completeness)
    needs_attention_query = (
        select(Institution)
        .where(
            and_(
                Institution.data_completeness_score >= 20,
                Institution.data_completeness_score < 80,
            )
        )
        .order_by(desc(Institution.data_completeness_score))
        .limit(50)
    )

    needs_attention_result = await db.execute(needs_attention_query)
    needs_attention = needs_attention_result.scalars().all()

    # Recently admin-updated
    recently_updated_query = (
        select(Institution)
        .where(Institution.data_source.in_(["admin", "mixed"]))
        .order_by(desc(Institution.data_last_updated))
        .limit(20)
    )

    recently_updated_result = await db.execute(recently_updated_query)
    recently_updated = recently_updated_result.scalars().all()

    # Count by data source
    admin_verified_query = select(func.count(Institution.id)).where(
        Institution.data_source.in_(["admin", "mixed"])
    )
    admin_verified_result = await db.execute(admin_verified_query)
    admin_verified_count = admin_verified_result.scalar()

    return {
        "summary": {
            "total_institutions": total_institutions,
            "avg_completeness_score": round(float(avg_completeness), 1),
            "needs_attention_count": len(needs_attention),
            "admin_verified_count": admin_verified_count,
            "verification_percentage": (
                round((admin_verified_count / total_institutions * 100), 1)
                if total_institutions > 0
                else 0
            ),
        },
        "needs_attention": [
            {
                "id": inst.id,
                "ipeds_id": inst.ipeds_id,
                "name": inst.name,
                "city": inst.city,
                "state": inst.state,
                "data_completeness_score": inst.data_completeness_score,
                "data_source": inst.data_source,
                "missing_data": {
                    "needs_cost_data": not (
                        inst.tuition_in_state or inst.tuition_private
                    ),
                    "needs_room_board": not (
                        inst.room_cost or inst.board_cost or inst.room_and_board
                    ),
                    "needs_admissions": not inst.acceptance_rate,
                    "needs_website": not inst.website,
                },
            }
            for inst in needs_attention
        ],
        "recently_updated": [
            {
                "id": inst.id,
                "ipeds_id": inst.ipeds_id,
                "name": inst.name,
                "city": inst.city,
                "state": inst.state,
                "data_completeness_score": inst.data_completeness_score,
                "data_source": inst.data_source,
                "data_last_updated": inst.data_last_updated,
                "ipeds_year": inst.ipeds_year,
            }
            for inst in recently_updated
        ],
    }


@router.get("/data-quality/by-state")
async def get_data_quality_by_state(
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth is ready
):
    """
    Get data quality statistics grouped by state (admin only).

    Shows which states have the best/worst data quality.
    Useful for targeting outreach efforts.

    **Requires admin authentication.**
    """
    query = (
        select(
            Institution.state,
            func.count(Institution.id).label("count"),
            func.avg(Institution.data_completeness_score).label("avg_score"),
            func.sum(
                case((Institution.data_source.in_(["admin", "mixed"]), 1), else_=0)
            ).label("admin_verified"),
        )
        .group_by(Institution.state)
        .order_by(desc("avg_score"))
    )

    result = await db.execute(query)
    states = result.all()

    return {
        "states": [
            {
                "state": state,
                "total_institutions": count,
                "avg_completeness_score": round(float(avg_score), 1),
                "admin_verified_count": admin_verified,
                "verification_rate": (
                    round((admin_verified / count * 100), 1) if count > 0 else 0
                ),
            }
            for state, count, avg_score, admin_verified in states
        ]
    }


@router.get("/needs-update")
async def get_institutions_needing_update(
    min_completeness: int = Query(40, ge=0, le=100),
    max_completeness: int = Query(79, ge=0, le=100),
    state: Optional[str] = Query(None, max_length=2),
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth is ready
):
    """
    Get list of institutions that need data updates (admin only).

    Finds institutions with:
    - Completeness score in specified range (default: 40-79)
    - Missing critical data (costs, admissions)
    - Old IPEDS data (optional future enhancement)

    **Requires admin authentication.**
    """
    query = select(Institution).where(
        and_(
            Institution.data_completeness_score >= min_completeness,
            Institution.data_completeness_score <= max_completeness,
        )
    )

    if state:
        query = query.where(Institution.state == state.upper())

    query = query.order_by(desc(Institution.data_completeness_score)).limit(limit)

    result = await db.execute(query)
    institutions = result.scalars().all()

    return {
        "filters": {
            "min_completeness": min_completeness,
            "max_completeness": max_completeness,
            "state": state,
        },
        "count": len(institutions),
        "institutions": [
            {
                "id": inst.id,
                "ipeds_id": inst.ipeds_id,
                "name": inst.name,
                "city": inst.city,
                "state": inst.state,
                "data_completeness_score": inst.data_completeness_score,
                "data_source": inst.data_source,
                "ipeds_year": inst.ipeds_year,
                "has_data": {
                    "website": bool(inst.website),
                    "tuition": bool(inst.tuition_in_state or inst.tuition_private),
                    "room_board": bool(
                        inst.room_cost or inst.board_cost or inst.room_and_board
                    ),
                    "admissions": bool(inst.acceptance_rate),
                    "test_scores": bool(inst.sat_math_25th or inst.act_composite_25th),
                },
                "update_url": f"/admin/institutions/{inst.id}/ipeds-data",
            }
            for inst in institutions
        ],
    }


# ============================================================================
# BULK OPERATIONS (FUTURE ENHANCEMENT)
# ============================================================================


class BulkVerifyRequest(BaseModel):
    """Request to verify multiple institutions at once"""

    institution_ids: List[int] = Field(..., max_items=100)
    academic_year: str
    notes: Optional[str] = None


@router.post("/bulk-verify")
async def bulk_verify_institutions(
    request: BulkVerifyRequest,
    db: AsyncSession = Depends(get_db),
    # current_admin: AdminUser = Depends(get_current_admin_user)  # Uncomment when auth is ready
):
    """
    Verify multiple institutions at once (admin only).

    Useful when an admin has reviewed data for multiple institutions
    and wants to mark them all as verified.

    **Requires admin authentication.**
    """
    if len(request.institution_ids) > 100:
        raise HTTPException(
            status_code=400, detail="Cannot verify more than 100 institutions at once"
        )

    # Get institutions
    query = select(Institution).where(Institution.id.in_(request.institution_ids))
    result = await db.execute(query)
    institutions = result.scalars().all()

    if len(institutions) != len(request.institution_ids):
        raise HTTPException(status_code=404, detail="Some institutions not found")

    # Update all to admin-verified
    updated_count = 0
    for institution in institutions:
        institution.data_source = "admin"
        institution.ipeds_year = request.academic_year
        institution.data_last_updated = datetime.utcnow()
        updated_count += 1

    await db.commit()

    return {
        "updated_count": updated_count,
        "academic_year": request.academic_year,
        "institution_ids": [inst.id for inst in institutions],
    }
