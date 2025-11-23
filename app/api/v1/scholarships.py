# app/api/v1/scholarships.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.models.scholarship import Scholarship
from app.schemas.scholarship import ScholarshipResponse

router = APIRouter(prefix="/scholarships", tags=["scholarships"])


@router.get("", response_model=List[ScholarshipResponse])
async def get_scholarships(
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all scholarships.
    PUBLIC endpoint - no authentication required.
    """
    query = select(Scholarship).order_by(Scholarship.title).limit(limit).offset(offset)

    result = await db.execute(query)
    scholarships = result.scalars().all()

    return scholarships


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
