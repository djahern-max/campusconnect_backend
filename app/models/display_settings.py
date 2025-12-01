# app/models/display_settings.pyå
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    TIMESTAMP,
    Text,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from app.core.database import Base


class DisplaySettings(Base):
    __tablename__ = "display_settings"
    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="uq_display_settings_entity"),
    )

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)

    # Section visibility toggles
    show_stats = Column(Boolean, default=True)
    show_financial = Column(Boolean, default=True)
    show_requirements = Column(Boolean, default=True)
    show_image_gallery = Column(Boolean, default=False)
    show_video = Column(Boolean, default=False)
    show_extended_info = Column(Boolean, default=False)

    # Custom content (Premium only)
    custom_tagline = Column(String(200))
    custom_description = Column(Text)
    extended_description = Column(Text)

    # Layout and branding
    layout_style = Column(String(50), default="standard")
    primary_color = Column(String(7))

    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
