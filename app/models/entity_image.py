# app/models/entity_image.py
from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class EntityImage(Base):
    """
    Gallery images for both institutions and scholarships.
    This polymorphic model supports multiple entity types.
    """
    __tablename__ = "entity_images"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(20), nullable=False)  # 'institution' or 'scholarship'
    entity_id = Column(Integer, nullable=False)
    image_url = Column(String(500), nullable=False)
    cdn_url = Column(String(500), nullable=False)
    filename = Column(String(255), nullable=False)
    caption = Column(Text, nullable=True)
    display_order = Column(Integer, nullable=False, default=0)
    is_featured = Column(Boolean, nullable=False, default=False)
    image_type = Column(String(50), nullable=True)  # 'campus', 'students', 'facilities', 'events'
    created_at = Column(DateTime(timezone=False), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())

    __table_args__ = (
        CheckConstraint(
            "entity_type IN ('institution', 'scholarship')",
            name="check_entity_type"
        ),
    )

    def __repr__(self):
        return f"<EntityImage(id={self.id}, entity_type={self.entity_type}, entity_id={self.entity_id}, filename={self.filename})>"
