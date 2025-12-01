# app/schemas/display_settings.pyå
from pydantic import BaseModel
from typing import Optional


class DisplaySettingsUpdate(BaseModel):
    show_stats: Optional[bool] = None
    show_financial: Optional[bool] = None
    show_requirements: Optional[bool] = None
    show_image_gallery: Optional[bool] = None
    show_video: Optional[bool] = None
    show_extended_info: Optional[bool] = None
    custom_tagline: Optional[str] = None
    custom_description: Optional[str] = None
    extended_description: Optional[str] = None
    layout_style: Optional[str] = None
    primary_color: Optional[str] = None


class DisplaySettingsResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    show_stats: bool
    show_financial: bool
    show_requirements: bool
    show_image_gallery: bool
    show_video: bool
    show_extended_info: bool
    custom_tagline: Optional[str]
    custom_description: Optional[str]
    extended_description: Optional[str]
    layout_style: str
    primary_color: Optional[str]

    class Config:
        from_attributes = True
