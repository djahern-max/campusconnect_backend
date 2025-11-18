"""Add entity_images table

Revision ID: abc123def456
Revises: 917197b7ae12
Create Date: 2025-11-17 19:15:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "abc123def456"
down_revision = "03ca36b7af8b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create entity_images table
    op.create_table(
        "entity_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("entity_type", sa.String(length=20), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("cdn_url", sa.String(length=500), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("image_type", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "entity_type IN ('institution', 'scholarship')", name="check_entity_type"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entity_images_id"), "entity_images", ["id"], unique=False)
    op.create_index(
        "idx_entity_images_entity",
        "entity_images",
        ["entity_type", "entity_id"],
        unique=False,
    )
    op.create_index(
        "idx_entity_images_display_order",
        "entity_images",
        ["display_order"],
        unique=False,
    )
    op.create_index(
        "idx_entity_images_featured", "entity_images", ["is_featured"], unique=False
    )

    # Unique index to ensure only one featured image per entity
    op.execute(
        """
        CREATE UNIQUE INDEX idx_entity_images_one_featured 
        ON entity_images(entity_type, entity_id) 
        WHERE is_featured = true
    """
    )


def downgrade() -> None:
    op.drop_index("idx_entity_images_one_featured", table_name="entity_images")
    op.drop_index("idx_entity_images_featured", table_name="entity_images")
    op.drop_index("idx_entity_images_display_order", table_name="entity_images")
    op.drop_index("idx_entity_images_entity", table_name="entity_images")
    op.drop_index(op.f("ix_entity_images_id"), table_name="entity_images")
    op.drop_table("entity_images")
