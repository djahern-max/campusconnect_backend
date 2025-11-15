from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.institution_extended_info import InstitutionExtendedInfo
from app.schemas.institution_extended_info import (
    InstitutionExtendedInfoCreate,
    InstitutionExtendedInfoUpdate,
    InstitutionExtendedInfoResponse
)

router = APIRouter(prefix="/admin/extended-info", tags=["admin-extended-info"])

@router.get("", response_model=InstitutionExtendedInfoResponse)
async def get_extended_info(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get extended info for admin's institution"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can have extended info")
    
    query = select(InstitutionExtendedInfo).where(
        InstitutionExtendedInfo.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    extended_info = result.scalar_one_or_none()
    
    if not extended_info:
        # Create empty extended info if it doesn't exist
        extended_info = InstitutionExtendedInfo(
            institution_id=current_user.entity_id
        )
        db.add(extended_info)
        await db.commit()
        await db.refresh(extended_info)
    
    return extended_info

@router.put("", response_model=InstitutionExtendedInfoResponse)
async def update_extended_info(
    updates: InstitutionExtendedInfoUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update extended info for admin's institution"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can have extended info")
    
    query = select(InstitutionExtendedInfo).where(
        InstitutionExtendedInfo.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    extended_info = result.scalar_one_or_none()
    
    if not extended_info:
        # Create new extended info
        extended_info = InstitutionExtendedInfo(
            institution_id=current_user.entity_id,
            **updates.dict(exclude_unset=True)
        )
        db.add(extended_info)
    else:
        # Update existing
        for field, value in updates.dict(exclude_unset=True).items():
            setattr(extended_info, field, value)
    
    await db.commit()
    await db.refresh(extended_info)
    
    return extended_info

@router.delete("")
async def clear_extended_info(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear all extended info (reset to empty)"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can have extended info")
    
    query = select(InstitutionExtendedInfo).where(
        InstitutionExtendedInfo.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    extended_info = result.scalar_one_or_none()
    
    if extended_info:
        await db.delete(extended_info)
        await db.commit()
    
    return {"message": "Extended info cleared successfully"}
