from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InstitutionImageBase(BaseModel):
    caption: Optional[str] = None
    display_order: int = 0
    is_featured: bool = False
    image_type: Optional[str] = None  # 'campus', 'students', 'facilities', 'events'

class InstitutionImageCreate(InstitutionImageBase):
    image_url: str
    cdn_url: str
    filename: str

class InstitutionImageUpdate(BaseModel):
    caption: Optional[str] = None
    display_order: Optional[int] = None
    is_featured: Optional[bool] = None
    image_type: Optional[str] = None

class InstitutionImageResponse(InstitutionImageBase):
    id: int
    institution_id: int
    image_url: str
    cdn_url: str
    filename: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ImageReorderRequest(BaseModel):
    image_ids: list[int]  # Ordered list of image IDs
