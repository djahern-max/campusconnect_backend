# app/api/v1/institutions.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, case
from typing import List, Optional
from app.core.database import get_db
from app.models.institution import Institution
from app.schemas.institution import InstitutionResponse

router = APIRouter(prefix="/institutions", tags=["institutions"])


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
