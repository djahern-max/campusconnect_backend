from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.admission_data import AdmissionData
from app.models.tuition_data import TuitionData
from app.schemas.admission import AdmissionDataResponse, AdmissionDataUpdate
from app.schemas.tuition import TuitionDataResponse, TuitionDataUpdate

router = APIRouter(prefix="/admin/data", tags=["admin-data"])

# ============= ADMISSIONS DATA =============

@router.get("/admissions", response_model=List[AdmissionDataResponse])
async def get_my_admissions_data(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all admissions data for admin's institution"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions have admissions data")
    
    query = select(AdmissionData).where(
        AdmissionData.institution_id == current_user.entity_id
    ).order_by(AdmissionData.academic_year.desc())
    
    result = await db.execute(query)
    admissions = result.scalars().all()
    
    return admissions


@router.put("/admissions/{admission_id}", response_model=AdmissionDataResponse)
async def update_admissions_data(
    admission_id: int,
    updates: AdmissionDataUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update admissions data for a specific year"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can update admissions data")
    
    # Verify ownership
    query = select(AdmissionData).where(
        AdmissionData.id == admission_id,
        AdmissionData.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    admission = result.scalar_one_or_none()
    
    if not admission:
        raise HTTPException(status_code=404, detail="Admissions data not found")
    
    # Update fields
    update_data = updates.dict(exclude_unset=True)
    
    await db.execute(
        update(AdmissionData)
        .where(AdmissionData.id == admission_id)
        .values(**update_data)
    )
    
    await db.commit()
    await db.refresh(admission)
    
    return admission


# ============= TUITION DATA =============

@router.get("/tuition", response_model=List[TuitionDataResponse])
async def get_my_tuition_data(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all tuition data for admin's institution"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions have tuition data")
    
    query = select(TuitionData).where(
        TuitionData.institution_id == current_user.entity_id
    ).order_by(TuitionData.academic_year.desc())
    
    result = await db.execute(query)
    tuition = result.scalars().all()
    
    return tuition


@router.put("/tuition/{tuition_id}", response_model=TuitionDataResponse)
async def update_tuition_data(
    tuition_id: int,
    updates: TuitionDataUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update tuition data for a specific year"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can update tuition data")
    
    # Verify ownership
    query = select(TuitionData).where(
        TuitionData.id == tuition_id,
        TuitionData.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    tuition = result.scalar_one_or_none()
    
    if not tuition:
        raise HTTPException(status_code=404, detail="Tuition data not found")
    
    # Update fields
    update_data = updates.dict(exclude_unset=True)
    
    await db.execute(
        update(TuitionData)
        .where(TuitionData.id == tuition_id)
        .values(**update_data)
    )
    
    await db.commit()
    await db.refresh(tuition)
    
    return tuition


@router.post("/admissions/{admission_id}/verify")
async def verify_admissions_data(
    admission_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark admissions data as verified by the institution"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can verify data")
    
    query = select(AdmissionData).where(
        AdmissionData.id == admission_id,
        AdmissionData.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    admission = result.scalar_one_or_none()
    
    if not admission:
        raise HTTPException(status_code=404, detail="Admissions data not found")
    
    await db.execute(
        update(AdmissionData)
        .where(AdmissionData.id == admission_id)
        .values(is_admin_verified=True)
    )
    
    await db.commit()
    
    return {"message": "Admissions data verified successfully"}


@router.post("/tuition/{tuition_id}/verify")
async def verify_tuition_data(
    tuition_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark tuition data as verified by the institution"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can verify data")
    
    query = select(TuitionData).where(
        TuitionData.id == tuition_id,
        TuitionData.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    tuition = result.scalar_one_or_none()
    
    if not tuition:
        raise HTTPException(status_code=404, detail="Tuition data not found")
    
    await db.execute(
        update(TuitionData)
        .where(TuitionData.id == tuition_id)
        .values(is_admin_verified=True)
    )
    
    await db.commit()
    
    return {"message": "Tuition data verified successfully"}
