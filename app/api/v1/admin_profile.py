from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.models.display_settings import DisplaySettings
from app.schemas.display_settings import DisplaySettingsUpdate, DisplaySettingsResponse

router = APIRouter(prefix="/admin/profile", tags=["admin-profile"])

@router.get("/entity")
async def get_my_entity(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the institution or scholarship this admin manages"""
    if current_user.entity_type == "institution":
        query = select(Institution).where(Institution.id == current_user.entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
    else:
        query = select(Scholarship).where(Scholarship.id == current_user.entity_id)
        result = await db.execute(query)
        entity = result.scalar_one_or_none()
    
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return entity

@router.get("/display-settings", response_model=DisplaySettingsResponse)
async def get_display_settings(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get display settings for my entity"""
    query = select(DisplaySettings).where(
        DisplaySettings.entity_type == current_user.entity_type,
        DisplaySettings.entity_id == current_user.entity_id
    )
    result = await db.execute(query)
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Display settings not found")
    
    return settings

@router.put("/display-settings", response_model=DisplaySettingsResponse)
async def update_display_settings(
    updates: DisplaySettingsUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update display settings for my entity"""
    query = select(DisplaySettings).where(
        DisplaySettings.entity_type == current_user.entity_type,
        DisplaySettings.entity_id == current_user.entity_id
    )
    result = await db.execute(query)
    settings = result.scalar_one_or_none()
    
    if not settings:
        raise HTTPException(status_code=404, detail="Display settings not found")
    
    # Update only provided fields
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(settings, field, value)
    
    await db.commit()
    await db.refresh(settings)
    
    return settings
