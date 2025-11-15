from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.institution_video import InstitutionVideo
from app.schemas.institution_video import (
    InstitutionVideoCreate,
    InstitutionVideoUpdate,
    InstitutionVideoResponse,
    VideoReorderRequest
)

router = APIRouter(prefix="/admin/videos", tags=["admin-videos"])

@router.get("", response_model=List[InstitutionVideoResponse])
async def get_videos(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all videos for admin's institution"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can have videos")
    
    query = select(InstitutionVideo).where(
        InstitutionVideo.institution_id == current_user.entity_id
    ).order_by(InstitutionVideo.display_order, InstitutionVideo.created_at)
    
    result = await db.execute(query)
    videos = result.scalars().all()
    
    return videos

@router.post("", response_model=InstitutionVideoResponse)
async def add_video(
    video_data: InstitutionVideoCreate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add video (YouTube/Vimeo URL)"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can have videos")
    
    # Get next display order
    query = select(InstitutionVideo).where(
        InstitutionVideo.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    existing_count = len(result.scalars().all())
    
    new_video = InstitutionVideo(
        institution_id=current_user.entity_id,
        video_url=video_data.video_url,
        title=video_data.title,
        description=video_data.description,
        thumbnail_url=video_data.thumbnail_url,
        video_type=video_data.video_type,
        display_order=existing_count,
        is_featured=video_data.is_featured
    )
    
    db.add(new_video)
    await db.commit()
    await db.refresh(new_video)
    
    return new_video

@router.put("/{video_id}", response_model=InstitutionVideoResponse)
async def update_video(
    video_id: int,
    updates: InstitutionVideoUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update video details"""
    query = select(InstitutionVideo).where(
        InstitutionVideo.id == video_id,
        InstitutionVideo.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(video, field, value)
    
    await db.commit()
    await db.refresh(video)
    
    return video

@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete video"""
    query = select(InstitutionVideo).where(
        InstitutionVideo.id == video_id,
        InstitutionVideo.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    await db.delete(video)
    await db.commit()
    
    return {"message": "Video deleted successfully"}

@router.put("/reorder")
async def reorder_videos(
    reorder: VideoReorderRequest,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reorder videos"""
    for index, video_id in enumerate(reorder.video_ids):
        stmt = update(InstitutionVideo).where(
            InstitutionVideo.id == video_id,
            InstitutionVideo.institution_id == current_user.entity_id
        ).values(display_order=index)
        
        await db.execute(stmt)
    
    await db.commit()
    
    return {"message": "Videos reordered successfully"}
