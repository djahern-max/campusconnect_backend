# app/schemas/entity_image.py
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class EntityImageBase(BaseModel):
    """Base schema for entity images"""

    caption: Optional[str] = None
    image_type: Optional[str] = None


class EntityImageCreate(EntityImageBase):
    """Schema for creating entity images"""

    entity_type: Literal["institution", "scholarship"]
    entity_id: int
    image_url: str
    cdn_url: str
    filename: str
    display_order: int = 0
    is_featured: bool = False


class EntityImageUpdate(BaseModel):
    """Schema for updating entity images"""

    caption: Optional[str] = None
    image_type: Optional[str] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = None


class EntityImageResponse(EntityImageBase):
    """Schema for entity image responses"""

    id: int
    entity_type: str
    entity_id: int
    image_url: str
    cdn_url: str
    filename: str
    display_order: int
    is_featured: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ImageReorderRequest(BaseModel):
    """Schema for reordering images"""

    image_ids: list[int] = Field(
        ...,
        description="List of image IDs in desired display order (first ID will be display_order 0)",
        min_length=1,
    )

    class Config:
        json_schema_extra = {"example": {"image_ids": [5, 3, 7, 4, 6]}}


class SetFeaturedImageRequest(BaseModel):
    """Schema for setting featured image"""

    image_id: int = Field(..., description="ID of image to set as featured")
