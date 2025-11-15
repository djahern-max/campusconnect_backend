from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.institution_image import InstitutionImage
from app.schemas.institution_image import (
    InstitutionImageCreate,
    InstitutionImageUpdate,
    InstitutionImageResponse,
    ImageReorderRequest
)
from app.services.image_service import image_service

router = APIRouter(prefix="/admin/gallery", tags=["admin-gallery"])

@router.get("", response_model=List[InstitutionImageResponse])
async def get_gallery_images(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all gallery images for admin's institution"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can have galleries")
    
    query = select(InstitutionImage).where(
        InstitutionImage.institution_id == current_user.entity_id
    ).order_by(InstitutionImage.display_order, InstitutionImage.created_at)
    
    result = await db.execute(query)
    images = result.scalars().all()
    
    return images

@router.post("", response_model=InstitutionImageResponse)
async def add_gallery_image(
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    image_type: Optional[str] = Form(None),
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload and add image to gallery"""
    if current_user.entity_type != "institution":
        raise HTTPException(status_code=400, detail="Only institutions can have galleries")
    
    # Upload image to DigitalOcean Spaces
    folder_path = f"campusconnect/institution_{current_user.entity_id}/gallery"
    upload_result = await image_service.upload_to_spaces(file, folder_path)
    
    # Get next display order
    query = select(InstitutionImage).where(
        InstitutionImage.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    existing_count = len(result.scalars().all())
    
    # Create gallery image record
    new_image = InstitutionImage(
        institution_id=current_user.entity_id,
        image_url=upload_result['url'],
        cdn_url=upload_result['cdn_url'],
        filename=upload_result['filename'],
        caption=caption,
        image_type=image_type,
        display_order=existing_count
    )
    
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    
    return new_image

@router.put("/{image_id}", response_model=InstitutionImageResponse)
async def update_gallery_image(
    image_id: int,
    updates: InstitutionImageUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update gallery image caption, order, etc."""
    query = select(InstitutionImage).where(
        InstitutionImage.id == image_id,
        InstitutionImage.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Update fields
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(image, field, value)
    
    await db.commit()
    await db.refresh(image)
    
    return image

@router.delete("/{image_id}")
async def delete_gallery_image(
    image_id: int,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete image from gallery and DigitalOcean Spaces"""
    query = select(InstitutionImage).where(
        InstitutionImage.id == image_id,
        InstitutionImage.institution_id == current_user.entity_id
    )
    result = await db.execute(query)
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Delete from DigitalOcean Spaces using full path
    try:
        # Build the full path: campusconnect/institution_X/gallery/filename.png
        full_path = f"campusconnect/institution_{current_user.entity_id}/gallery/{image.filename}"
        await image_service.delete_from_spaces(full_path)
    except Exception as e:
        # Log the error but continue with database deletion
        print(f"Warning: Failed to delete image from storage: {e}")
    
    # Delete from database
    await db.delete(image)
    await db.commit()
    
    return {"message": "Image deleted successfully"}

@router.put("/reorder")
async def reorder_gallery_images(
    reorder: ImageReorderRequest,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reorder gallery images"""
    # Update display order for each image
    for index, image_id in enumerate(reorder.image_ids):
        stmt = update(InstitutionImage).where(
            InstitutionImage.id == image_id,
            InstitutionImage.institution_id == current_user.entity_id
        ).values(display_order=index)
        
        await db.execute(stmt)
    
    await db.commit()
    
    return {"message": "Images reordered successfully"}
