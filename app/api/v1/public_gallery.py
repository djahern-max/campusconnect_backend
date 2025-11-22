# app/api/v1/public_gallery.py
"""
Public endpoints for gallery images.
Used by MagicScholar App to display institution/scholarship galleries.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from app.core.database import get_db
from app.models.entity_image import EntityImage
from app.schemas.entity_image import EntityImageResponse

router = APIRouter(tags=["public-gallery"])


@router.get(
    "/institutions/{institution_id}/gallery", response_model=List[EntityImageResponse]
)
async def get_institution_gallery(
    institution_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get gallery images for a specific institution.
    PUBLIC endpoint - no authentication required.
    Used by MagicScholar App to display institution galleries.
    """
    query = (
        select(EntityImage)
        .where(
            and_(
                EntityImage.entity_type == "institution",
                EntityImage.entity_id == institution_id,
            )
        )
        .order_by(EntityImage.display_order, EntityImage.created_at)
    )

    result = await db.execute(query)
    images = result.scalars().all()

    return images


@router.get(
    "/institutions/{institution_id}/featured-image",
    response_model=Optional[EntityImageResponse],
)
async def get_institution_featured_image(
    institution_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get the featured/primary image for an institution.
    PUBLIC endpoint.
    """
    query = select(EntityImage).where(
        and_(
            EntityImage.entity_type == "institution",
            EntityImage.entity_id == institution_id,
            EntityImage.is_featured == True,
        )
    )

    result = await db.execute(query)
    image = result.scalar_one_or_none()

    return image


@router.get(
    "/scholarships/{scholarship_id}/gallery", response_model=List[EntityImageResponse]
)
async def get_scholarship_gallery(
    scholarship_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get gallery images for a specific scholarship.
    PUBLIC endpoint - no authentication required.
    Used by MagicScholar App to display scholarship galleries.
    """
    query = (
        select(EntityImage)
        .where(
            and_(
                EntityImage.entity_type == "scholarship",
                EntityImage.entity_id == scholarship_id,
            )
        )
        .order_by(EntityImage.display_order, EntityImage.created_at)
    )

    result = await db.execute(query)
    images = result.scalars().all()

    return images


@router.get(
    "/scholarships/{scholarship_id}/featured-image",
    response_model=Optional[EntityImageResponse],
)
async def get_scholarship_featured_image(
    scholarship_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get the featured/primary image for a scholarship.
    PUBLIC endpoint.
    """
    query = select(EntityImage).where(
        and_(
            EntityImage.entity_type == "scholarship",
            EntityImage.entity_id == scholarship_id,
            EntityImage.is_featured == True,
        )
    )

    result = await db.execute(query)
    image = result.scalar_one_or_none()

    return image


# Optional: Get images by IPEDS ID instead of internal ID
@router.get(
    "/institutions/ipeds/{ipeds_id}/gallery", response_model=List[EntityImageResponse]
)
async def get_institution_gallery_by_ipeds(
    ipeds_id: int, db: AsyncSession = Depends(get_db)
):
    """
    Get gallery images for an institution by IPEDS ID.
    More convenient for MagicScholar App since it uses IPEDS IDs.
    """
    from app.models.institution import Institution

    # First get the institution
    inst_result = await db.execute(
        select(Institution).where(Institution.ipeds_id == ipeds_id)
    )
    institution = inst_result.scalar_one_or_none()

    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    # Then get its gallery
    query = (
        select(EntityImage)
        .where(
            and_(
                EntityImage.entity_type == "institution",
                EntityImage.entity_id == institution.id,
            )
        )
        .order_by(EntityImage.display_order, EntityImage.created_at)
    )

    result = await db.execute(query)
    images = result.scalars().all()

    return images


@router.get("/featured-images")
async def get_all_featured_images(db: AsyncSession = Depends(get_db)):
    """
    Get all featured images for homepage carousel.
    PUBLIC endpoint - no authentication required.
    """
    from app.models.institution import Institution

    # Get all featured images
    query = (
        select(EntityImage)
        .where(EntityImage.is_featured == True)
        .order_by(EntityImage.created_at.desc())
    )

    result = await db.execute(query)
    featured_images = result.scalars().all()

    enriched_results = []

    for image in featured_images:
        if image.entity_type == "institution":
            # Get institution details
            inst_query = select(Institution).where(Institution.id == image.entity_id)
            inst_result = await db.execute(inst_query)
            institution = inst_result.scalar_one_or_none()

            if institution:
                enriched_results.append(
                    {
                        "id": image.id,
                        "image_url": image.image_url,
                        "cdn_url": image.cdn_url,
                        "caption": image.caption,
                        "entity_type": "institution",
                        "entity_id": institution.id,
                        "entity_name": institution.name,
                        "entity_city": institution.city,
                        "entity_state": institution.state,
                        "entity_ipeds_id": institution.ipeds_id,
                    }
                )

    return enriched_results
