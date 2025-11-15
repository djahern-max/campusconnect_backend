from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime

class InstitutionVideoBase(BaseModel):
    video_url: str
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_type: Optional[str] = None  # 'tour', 'testimonial', 'overview', 'custom'
    display_order: int = 0
    is_featured: bool = False

class InstitutionVideoCreate(InstitutionVideoBase):
    pass

class InstitutionVideoUpdate(BaseModel):
    video_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_type: Optional[str] = None
    display_order: Optional[int] = None
    is_featured: Optional[bool] = None

class InstitutionVideoResponse(InstitutionVideoBase):
    id: int
    institution_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class VideoReorderRequest(BaseModel):
    video_ids: list[int]  # Ordered list of video IDs
