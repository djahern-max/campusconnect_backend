from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from app.core.database import get_db
from app.models.admission_data import AdmissionData
from app.models.tuition_data import TuitionData
from app.schemas.admission import AdmissionDataResponse
from app.schemas.tuition import TuitionDataResponse

router = APIRouter(prefix="/institutions", tags=["institutions-data"])

@router.get("/{ipeds_id}/admissions", response_model=List[AdmissionDataResponse])
async def get_institution_admissions(
    ipeds_id: int,
    academic_year: Optional[str] = Query(None, description="Filter by academic year (e.g., '2023-24')"),
    db: AsyncSession = Depends(get_db)
):
    """Get admission statistics for an institution"""
    query = select(AdmissionData).where(AdmissionData.ipeds_id == ipeds_id)
    
    if academic_year:
        query = query.where(AdmissionData.academic_year == academic_year)
    
    query = query.order_by(AdmissionData.academic_year.desc())
    
    result = await db.execute(query)
    admissions = result.scalars().all()
    
    if not admissions:
        raise HTTPException(status_code=404, detail="No admissions data found for this institution")
    
    return admissions


@router.get("/{ipeds_id}/tuition", response_model=List[TuitionDataResponse])
async def get_institution_tuition(
    ipeds_id: int,
    academic_year: Optional[str] = Query(None, description="Filter by academic year (e.g., '2023-24')"),
    db: AsyncSession = Depends(get_db)
):
    """Get tuition and cost information for an institution"""
    query = select(TuitionData).where(TuitionData.ipeds_id == ipeds_id)
    
    if academic_year:
        query = query.where(TuitionData.academic_year == academic_year)
    
    query = query.order_by(TuitionData.academic_year.desc())
    
    result = await db.execute(query)
    tuition = result.scalars().all()
    
    if not tuition:
        raise HTTPException(status_code=404, detail="No tuition data found for this institution")
    
    return tuition


@router.get("/{ipeds_id}/financial-overview")
async def get_financial_overview(
    ipeds_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a combined overview of the most recent tuition and admissions data"""
    # Get most recent tuition data
    tuition_query = select(TuitionData).where(
        TuitionData.ipeds_id == ipeds_id
    ).order_by(TuitionData.academic_year.desc()).limit(1)
    
    tuition_result = await db.execute(tuition_query)
    tuition = tuition_result.scalar_one_or_none()
    
    # Get most recent admissions data
    admissions_query = select(AdmissionData).where(
        AdmissionData.ipeds_id == ipeds_id
    ).order_by(AdmissionData.academic_year.desc()).limit(1)
    
    admissions_result = await db.execute(admissions_query)
    admissions = admissions_result.scalar_one_or_none()
    
    if not tuition and not admissions:
        raise HTTPException(status_code=404, detail="No financial or admissions data found")
    
    return {
        "ipeds_id": ipeds_id,
        "tuition": TuitionDataResponse.from_orm(tuition) if tuition else None,
        "admissions": AdmissionDataResponse.from_orm(admissions) if admissions else None
    }
