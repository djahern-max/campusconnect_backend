# app/api/v1/admin_gallery.py
"""
Gallery management endpoints for both institutions and scholarships.
Uses the entity_images table to support multiple entity types.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from typing import List, Optional, Dict
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.models.entity_image import EntityImage
import os
from app.schemas.entity_image import (
    EntityImageResponse,
    EntityImageUpdate,
    ImageReorderRequest,
    SetFeaturedImageRequest,
)
from app.services.image_service import image_service

router = APIRouter(prefix="/admin/gallery", tags=["admin-gallery"])


@router.put("/reorder")
async def reorder_gallery_images(
    reorder: ImageReorderRequest,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reorder gallery images"""
    # Update display order for each image
    for index, image_id in enumerate(reorder.image_ids):
        stmt = (
            update(EntityImage)
            .where(
                and_(
                    EntityImage.id == image_id,
                    EntityImage.entity_type == current_user.entity_type,
                    EntityImage.entity_id == current_user.entity_id,
                )
            )
            .values(display_order=index)
        )

        await db.execute(stmt)

    await db.commit()

    return {"message": "Images reordered successfully"}


@router.post("/set-featured")
async def set_featured_image(
    request: SetFeaturedImageRequest,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set an image as the featured/primary image"""
    # First, unset all featured images for this entity
    await db.execute(
        update(EntityImage)
        .where(
            and_(
                EntityImage.entity_type == current_user.entity_type,
                EntityImage.entity_id == current_user.entity_id,
            )
        )
        .values(is_featured=False)
    )

    # Set the requested image as featured
    result = await db.execute(
        select(EntityImage).where(
            and_(
                EntityImage.id == request.image_id,
                EntityImage.entity_type == current_user.entity_type,
                EntityImage.entity_id == current_user.entity_id,
            )
        )
    )
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    image.is_featured = True

    # Also update the primary_image_url in institutions/scholarships table
    if current_user.entity_type == "institution":
        from app.models.institution import Institution

        inst_result = await db.execute(
            select(Institution).where(Institution.id == current_user.entity_id)
        )
        institution = inst_result.scalar_one_or_none()
        if institution:
            institution.primary_image_url = image.cdn_url
    elif current_user.entity_type == "scholarship":
        from app.models.scholarship import Scholarship

        schol_result = await db.execute(
            select(Scholarship).where(Scholarship.id == current_user.entity_id)
        )
        scholarship = schol_result.scalar_one_or_none()
        if scholarship:
            scholarship.primary_image_url = image.cdn_url

    await db.commit()
    await db.refresh(image)

    return {"message": "Featured image updated successfully", "image": image}


@router.get("/featured", response_model=Optional[EntityImageResponse])
async def get_featured_image(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get the featured/primary image for this entity"""
    query = select(EntityImage).where(
        and_(
            EntityImage.entity_type == current_user.entity_type,
            EntityImage.entity_id == current_user.entity_id,
            EntityImage.is_featured == True,
        )
    )
    result = await db.execute(query)
    image = result.scalar_one_or_none()

    return image


@router.get("", response_model=List[EntityImageResponse])
async def get_gallery_images(
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all gallery images for admin's institution or scholarship"""
    query = (
        select(EntityImage)
        .where(
            and_(
                EntityImage.entity_type == current_user.entity_type,
                EntityImage.entity_id == current_user.entity_id,
            )
        )
        .order_by(EntityImage.display_order, EntityImage.created_at)
    )

    result = await db.execute(query)
    images = result.scalars().all()

    return images


@router.post("", response_model=EntityImageResponse)
async def add_gallery_image(
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    image_type: Optional[str] = Form(None),
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload and add image to gallery"""

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate file extension
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Optional: Validate file size (10MB max)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB",
        )

    # Reset file pointer after reading
    await file.seek(0)

    # Upload image to DigitalOcean Spaces
    folder_path = (
        f"campusconnect/{current_user.entity_type}_{current_user.entity_id}/gallery"
    )
    upload_result = await image_service.upload_to_spaces(file, folder_path)

    # Get next display order
    query = select(func.count(EntityImage.id)).where(
        and_(
            EntityImage.entity_type == current_user.entity_type,
            EntityImage.entity_id == current_user.entity_id,
        )
    )
    result = await db.execute(query)
    existing_count = result.scalar() or 0

    # Create gallery image record
    new_image = EntityImage(
        entity_type=current_user.entity_type,
        entity_id=current_user.entity_id,
        image_url=upload_result["url"],
        cdn_url=upload_result["cdn_url"],
        filename=upload_result["filename"],
        caption=caption,
        image_type=image_type,
        display_order=existing_count,
    )

    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)

    return new_image


@router.put("/{image_id}", response_model=EntityImageResponse)
async def update_gallery_image(
    image_id: int,
    updates: EntityImageUpdate,
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update gallery image caption, type, etc."""
    query = select(EntityImage).where(
        and_(
            EntityImage.id == image_id,
            EntityImage.entity_type == current_user.entity_type,
            EntityImage.entity_id == current_user.entity_id,
        )
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
    db: AsyncSession = Depends(get_db),
):
    """Delete image from gallery and DigitalOcean Spaces"""
    query = select(EntityImage).where(
        and_(
            EntityImage.id == image_id,
            EntityImage.entity_type == current_user.entity_type,
            EntityImage.entity_id == current_user.entity_id,
        )
    )
    result = await db.execute(query)
    image = result.scalar_one_or_none()

    if not image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete from DigitalOcean Spaces
    try:
        full_path = f"campusconnect/{current_user.entity_type}_{current_user.entity_id}/gallery/{image.filename}"
        await image_service.delete_from_spaces(full_path)
    except Exception as e:
        print(f"Warning: Failed to delete image from storage: {e}")

    # Delete from database
    await db.delete(image)
    await db.commit()

    return {"message": "Image deleted successfully"}
