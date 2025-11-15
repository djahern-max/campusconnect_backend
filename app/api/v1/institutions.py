from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
    """Get all institutions with optional state filter"""
    query = select(Institution)

    if state:
        query = query.where(Institution.state == state.upper())

    # Priority states first (NH, MA, VT, NY, FL, CA), then alphabetical
    priority_states = ["NH", "MA", "VT", "NY", "FL", "CA"]
    if not state:
        # Custom sort: priority states first, then alphabetical
        query = query.order_by(Institution.state, Institution.name)
    else:
        query = query.order_by(Institution.name)

    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    institutions = result.scalars().all()

    return institutions


@router.get("/{ipeds_id}", response_model=InstitutionResponse)
async def get_institution(ipeds_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single institution by IPEDS ID"""
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
    """Get a single institution by database ID"""
    query = select(Institution).where(Institution.id == institution_id)
    result = await db.execute(query)
    institution = result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    return institution
