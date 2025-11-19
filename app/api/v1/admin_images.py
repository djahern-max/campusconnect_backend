from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.admin_auth import get_current_user
from app.models.admin_user import AdminUser
from app.services.image_service import image_service
import os
from datetime import datetime

router = APIRouter(prefix="/admin/images", tags=["admin-images"])

# Allowed image types
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: AdminUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload an image to DigitalOcean Spaces"""

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content and check size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE / (1024*1024):.0f}MB",
        )

    # Reset file pointer for re-reading
    await file.seek(0)

    # Upload to DigitalOcean Spaces using the correct method
    folder_path = f"campusconnect/{current_user.entity_type}_{current_user.entity_id}"

    try:
        result = await image_service.upload_to_spaces(
            file=file, folder_path=folder_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")

    return {
        "success": True,
        "filename": result["filename"],
        "url": result["url"],
        "cdn_url": result["cdn_url"],
        "s3_key": result["path"],
        "size_bytes": len(file_content),
        "message": "Image uploaded successfully to DigitalOcean Spaces",
    }


@router.get("/list")
async def list_images(current_user: AdminUser = Depends(get_current_user)):
    """List all images for this entity from DigitalOcean Spaces"""

    # Get all campusconnect images
    all_images = await image_service.list_images()

    # Filter for this entity
    prefix = f"campusconnect/{current_user.entity_type}_{current_user.entity_id}_"
    entity_images = [img for img in all_images if img["path"].startswith(prefix)]

    # Sort by last modified (newest first)
    entity_images.sort(key=lambda x: x["last_modified"], reverse=True)

    return {"count": len(entity_images), "images": entity_images}


@router.delete("/{filename}")
async def delete_image(
    filename: str, current_user: AdminUser = Depends(get_current_user)
):
    """Delete an image from DigitalOcean Spaces"""

    # Verify the file belongs to this entity
    prefix = f"{current_user.entity_type}_{current_user.entity_id}_"
    if not filename.startswith(prefix):
        raise HTTPException(
            status_code=403, detail="You don't have permission to delete this file"
        )

    # Full S3 key
    s3_key = f"campusconnect/{filename}"

    # Delete from Spaces
    image_service.delete_image(s3_key)

    return {
        "success": True,
        "message": f"Image {filename} deleted successfully from DigitalOcean Spaces",
    }
