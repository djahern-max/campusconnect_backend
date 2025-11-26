# app/api/v1/admin_institution_data.py
"""
Admin endpoints for updating institution data
Allows institution admins to update their own data through the UI
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Optional
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.institution import Institution
from app.models.institution_data_verifications import InstitutionDataVerification
from app.schemas.institution import (
    InstitutionResponse,
    InstitutionUpdate,
)
from app.schemas.admin_institution import (
    InstitutionBasicInfoUpdate,
    InstitutionCostDataUpdate,
    InstitutionAdmissionsDataUpdate,
    InstitutionDataVerifyRequest,
    InstitutionDataQualityResponse,
)

router = APIRouter(prefix="/institution-data", tags=["admin-institution-data"])


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


async def verify_admin_owns_institution(
    admin_user: AdminUser, institution_id: int
) -> None:
    """Verify admin has permission to update this institution"""
    if admin_user.role == "super_admin":
        return  # Super admins can update any institution

    if admin_user.entity_type != "institution":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only institution admins can update institution data",
        )

    if admin_user.entity_id != institution_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own institution's data",
        )


async def create_verification_record(
    db: AsyncSession,
    institution_id: int,
    field_name: str,
    old_value: Optional[str],
    new_value: Optional[str],
    verified_by: str,
    notes: Optional[str] = None,
):
    """Create a verification record for a field update"""
    verification = InstitutionDataVerification(
        institution_id=institution_id,
        field_name=field_name,
        old_value=str(old_value) if old_value is not None else None,
        new_value=str(new_value) if new_value is not None else None,
        verified_by=verified_by,
        verified_at=datetime.utcnow(),
        notes=notes,
    )
    db.add(verification)


async def update_data_source(
    db: AsyncSession, institution: Institution, fields_updated: list[str]
):
    """Update data_source field based on what was changed"""
    # Get all verifications for this institution
    query = select(InstitutionDataVerification).where(
        InstitutionDataVerification.institution_id == institution.id
    )
    result = await db.execute(query)
    verifications = result.scalars().all()

    verified_fields = {v.field_name for v in verifications}

    # Determine new data source
    if institution.data_source == "manual":
        # Was manual, now has admin updates
        new_source = "admin"
    elif institution.data_source == "ipeds":
        # Was IPEDS, now has some admin updates
        new_source = "mixed" if len(verified_fields) > 0 else "ipeds"
    elif institution.data_source == "mixed":
        # Already mixed, check if ALL fields are now verified
        # For now, keep as mixed
        new_source = "mixed"
    else:
        new_source = "mixed"

    institution.data_source = new_source
    institution.data_last_updated = datetime.utcnow()


async def recalculate_completeness_score(
    db: AsyncSession, institution: Institution
) -> int:
    """Recalculate and update completeness score"""
    score = 0

    # Core identity (20 points)
    if institution.name and institution.city and institution.state:
        score += 10
    if institution.website:
        score += 10

    # Cost data (40 points)
    has_tuition = (
        institution.tuition_in_state
        or institution.tuition_out_of_state
        or institution.tuition_private
    )
    if has_tuition:
        score += 20

    has_room_board = institution.room_cost or institution.board_cost
    if has_room_board:
        score += 20

    # Admissions (10 points)
    if institution.acceptance_rate:
        score += 5
    if institution.sat_math_25th or institution.act_composite_25th:
        score += 5

    # Images (30 points) - would need to query entity_images table
    # For now, skip or implement if needed

    # Admin verification bonus (10 points)
    if institution.data_source in ["admin", "mixed"]:
        score += 10

    institution.data_completeness_score = min(score, 100)
    return institution.data_completeness_score


# ============================================================================
# GET CURRENT DATA & QUALITY
# ============================================================================


@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution_data(
    institution_id: int,
    current_admin: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current institution data
    Admins can only see their own institution (unless super_admin)
    """
    await verify_admin_owns_institution(current_admin, institution_id)

    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    return institution


@router.get("/{institution_id}/quality", response_model=InstitutionDataQualityResponse)
async def get_data_quality(
    institution_id: int,
    current_admin: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get data quality report for institution
    Shows what's missing, what's verified, completeness score breakdown
    """
    await verify_admin_owns_institution(current_admin, institution_id)

    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    # Get verification history
    verify_query = select(InstitutionDataVerification).where(
        InstitutionDataVerification.institution_id == institution_id
    )
    verify_result = await db.execute(verify_query)
    verifications = verify_result.scalars().all()

    verified_fields = {v.field_name for v in verifications}

    # Analyze what's missing
    missing_fields = []
    if not institution.website:
        missing_fields.append("website")
    if not (
        institution.tuition_in_state
        or institution.tuition_out_of_state
        or institution.tuition_private
    ):
        missing_fields.append("tuition")
    if not (institution.room_cost or institution.board_cost):
        missing_fields.append("room_and_board")
    if not institution.acceptance_rate:
        missing_fields.append("acceptance_rate")

    # Calculate score breakdown
    return InstitutionDataQualityResponse(
        institution_id=institution.id,
        institution_name=institution.name,
        completeness_score=institution.data_completeness_score,
        data_source=institution.data_source,
        data_last_updated=institution.data_last_updated,
        ipeds_year=institution.ipeds_year,
        missing_fields=missing_fields,
        verified_fields=list(verified_fields),
        verification_count=len(verifications),
        has_website=bool(institution.website),
        has_tuition_data=bool(
            institution.tuition_in_state
            or institution.tuition_out_of_state
            or institution.tuition_private
        ),
        has_room_board=bool(institution.room_cost or institution.board_cost),
        has_admissions_data=bool(institution.acceptance_rate),
    )


# ============================================================================
# UPDATE ENDPOINTS - SECTION BY SECTION
# ============================================================================


@router.put("/{institution_id}/basic-info", response_model=InstitutionResponse)
async def update_basic_info(
    institution_id: int,
    updates: InstitutionBasicInfoUpdate,
    current_admin: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update basic institution information (name, location, website, etc.)
    """
    await verify_admin_owns_institution(current_admin, institution_id)

    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    # Track what changed for verification records
    fields_updated = []

    # Update fields and create verification records
    update_data = updates.model_dump(exclude_unset=True)
    for field_name, new_value in update_data.items():
        if hasattr(institution, field_name):
            old_value = getattr(institution, field_name)
            if old_value != new_value:
                setattr(institution, field_name, new_value)
                fields_updated.append(
                    field_name
                )  # TODO: Uncomment when InstitutionDataVerification model exists
                #
                await create_verification_record(
                    db=db,
                    institution_id=institution_id,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    verified_by=current_admin.email,
                    notes=f"Updated via admin UI by {current_admin.email}",
                )

    # Update data source if changes were made
    if fields_updated:
        await update_data_source(db, institution, fields_updated)
        await recalculate_completeness_score(db, institution)

    await db.commit()
    await db.refresh(institution)

    return institution


@router.put("/{institution_id}/cost-data", response_model=InstitutionResponse)
async def update_cost_data(
    institution_id: int,
    updates: InstitutionCostDataUpdate,
    current_admin: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update cost data (tuition, room, board, fees)
    """
    await verify_admin_owns_institution(current_admin, institution_id)

    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    fields_updated = []
    update_data = updates.model_dump(exclude_unset=True)

    for field_name, new_value in update_data.items():
        if hasattr(institution, field_name):
            old_value = getattr(institution, field_name)
            # Convert to Decimal if it's a float
            if isinstance(new_value, float):
                new_value = Decimal(str(new_value))
            if old_value != new_value:
                setattr(institution, field_name, new_value)
                fields_updated.append(
                    field_name
                )  # TODO: Uncomment when InstitutionDataVerification model exists
                #
                await create_verification_record(
                    db=db,
                    institution_id=institution_id,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    verified_by=current_admin.email,
                    notes=f"Cost data updated for {institution.ipeds_year or 'current'} academic year",
                )

    if fields_updated:
        await update_data_source(db, institution, fields_updated)
        await recalculate_completeness_score(db, institution)

    await db.commit()
    await db.refresh(institution)

    return institution


@router.put("/{institution_id}/admissions-data", response_model=InstitutionResponse)
async def update_admissions_data(
    institution_id: int,
    updates: InstitutionAdmissionsDataUpdate,
    current_admin: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update admissions data (acceptance rate, test scores)
    """
    await verify_admin_owns_institution(current_admin, institution_id)

    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    fields_updated = []
    update_data = updates.model_dump(exclude_unset=True)

    for field_name, new_value in update_data.items():
        if hasattr(institution, field_name):
            old_value = getattr(institution, field_name)
            # Convert to Decimal for acceptance_rate
            if field_name == "acceptance_rate" and isinstance(new_value, float):
                new_value = Decimal(str(new_value))
            if old_value != new_value:
                setattr(institution, field_name, new_value)
                fields_updated.append(
                    field_name
                )  # TODO: Uncomment when InstitutionDataVerification model exists
                #
                await create_verification_record(
                    db=db,
                    institution_id=institution_id,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    verified_by=current_admin.email,
                    notes=f"Admissions data updated for {institution.ipeds_year or 'current'} academic year",
                )

    if fields_updated:
        await update_data_source(db, institution, fields_updated)
        await recalculate_completeness_score(db, institution)

    await db.commit()
    await db.refresh(institution)

    return institution


# ============================================================================
# VERIFY CURRENT DATA
# ============================================================================


@router.post("/{institution_id}/verify-current")
async def verify_current_data(
    institution_id: int,
    verify_request: InstitutionDataVerifyRequest,
    current_admin: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify that current IPEDS or existing data is still accurate
    Quick action button: "Verify data is current for 2025-26"
    """
    await verify_admin_owns_institution(current_admin, institution_id)

    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    # Create verification records for specified fields
    fields_verified = verify_request.fields or [
        "tuition_in_state",
        "tuition_out_of_state",
        "tuition_private",
        "room_cost",
        "board_cost",
        "acceptance_rate",
    ]

    verified_count = 0
    for field_name in fields_verified:
        if hasattr(institution, field_name):
            current_value = getattr(institution, field_name)
            if (
                current_value is not None
            ):  # Only verify fields that have data    # TODO: Uncomment when InstitutionDataVerification model exists
                #
                await create_verification_record(
                    db=db,
                    institution_id=institution_id,
                    field_name=field_name,
                    old_value=current_value,
                    new_value=current_value,  # Same value = verified as current
                    verified_by=current_admin.email,
                    notes=verify_request.notes
                    or f"Verified as current for {verify_request.academic_year}",
                )
                verified_count += 1

    # Update metadata
    institution.data_source = "admin"  # Now admin-verified
    institution.data_last_updated = datetime.utcnow()
    institution.ipeds_year = verify_request.academic_year
    await recalculate_completeness_score(db, institution)

    await db.commit()

    return {
        "message": "Data verified successfully",
        "fields_verified": verified_count,
        "academic_year": verify_request.academic_year,
        "completeness_score": institution.data_completeness_score,
        "data_source": institution.data_source,
    }


# ============================================================================
# VERIFICATION HISTORY
# ============================================================================


@router.get("/{institution_id}/verification-history")
async def get_verification_history(
    institution_id: int,
    limit: int = 50,
    current_admin: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get history of all data verifications/updates
    Audit trail for transparency
    """
    await verify_admin_owns_institution(current_admin, institution_id)

    query = (
        select(InstitutionDataVerification)
        .where(InstitutionDataVerification.institution_id == institution_id)
        .order_by(InstitutionDataVerification.verified_at.desc())
        .limit(limit)
    )

    result = await db.execute(query)
    verifications = result.scalars().all()

    return [
        {
            "id": v.id,
            "field_name": v.field_name,
            "old_value": v.old_value,
            "new_value": v.new_value,
            "verified_by": v.verified_by,
            "verified_at": v.verified_at,
            "notes": v.notes,
        }
        for v in verifications
    ]
