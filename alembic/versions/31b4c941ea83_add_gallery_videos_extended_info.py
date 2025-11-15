"""add_gallery_videos_extended_info

Revision ID: 31b4c941ea83
Revises: d4e6bce4ebdf
Create Date: 2025-11-15 04:03:10.484568

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "gallery_videos_001"
down_revision = "d4e6bce4ebdf"
branch_labels = None
depends_on = None


def upgrade():
    # Create institution_images table
    op.create_table(
        "institution_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=False),
        sa.Column("cdn_url", sa.String(500), nullable=False),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "image_type", sa.String(50), nullable=True
        ),  # 'campus', 'students', 'facilities', 'events'
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["institution_id"], ["institutions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_institution_images_institution_id", "institution_images", ["institution_id"]
    )
    op.create_index(
        "ix_institution_images_display_order", "institution_images", ["display_order"]
    )

    # Create institution_videos table
    op.create_table(
        "institution_videos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Integer(), nullable=False),
        sa.Column("video_url", sa.String(500), nullable=False),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("thumbnail_url", sa.String(500), nullable=True),
        sa.Column(
            "video_type", sa.String(50), nullable=True
        ),  # 'tour', 'testimonial', 'overview', 'custom'
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["institution_id"], ["institutions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_institution_videos_institution_id", "institution_videos", ["institution_id"]
    )
    op.create_index(
        "ix_institution_videos_display_order", "institution_videos", ["display_order"]
    )

    # Create institution_extended_info table
    op.create_table(
        "institution_extended_info",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Integer(), nullable=False),
        # Campus Life
        sa.Column("campus_description", sa.Text(), nullable=True),
        sa.Column("student_life", sa.Text(), nullable=True),
        sa.Column("housing_info", sa.Text(), nullable=True),
        sa.Column("dining_info", sa.Text(), nullable=True),
        # Academics
        sa.Column("programs_overview", sa.Text(), nullable=True),
        sa.Column("faculty_highlights", sa.Text(), nullable=True),
        sa.Column("research_opportunities", sa.Text(), nullable=True),
        sa.Column("study_abroad", sa.Text(), nullable=True),
        # Admissions
        sa.Column("application_tips", sa.Text(), nullable=True),
        sa.Column("financial_aid_info", sa.Text(), nullable=True),
        sa.Column("scholarship_opportunities", sa.Text(), nullable=True),
        # Athletics & Activities
        sa.Column("athletics_overview", sa.Text(), nullable=True),
        sa.Column("clubs_organizations", sa.Text(), nullable=True),
        # Location & Facilities
        sa.Column("location_highlights", sa.Text(), nullable=True),
        sa.Column("facilities_overview", sa.Text(), nullable=True),
        # Custom Sections (flexible)
        sa.Column(
            "custom_sections", postgresql.JSONB(astext_type=sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")
        ),
        sa.ForeignKeyConstraint(
            ["institution_id"], ["institutions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("institution_id"),
    )
    op.create_index(
        "ix_institution_extended_info_institution_id",
        "institution_extended_info",
        ["institution_id"],
    )


def downgrade():
    op.drop_index(
        "ix_institution_extended_info_institution_id",
        table_name="institution_extended_info",
    )
    op.drop_table("institution_extended_info")

    op.drop_index(
        "ix_institution_videos_display_order", table_name="institution_videos"
    )
    op.drop_index(
        "ix_institution_videos_institution_id", table_name="institution_videos"
    )
    op.drop_table("institution_videos")

    op.drop_index(
        "ix_institution_images_display_order", table_name="institution_images"
    )
    op.drop_index(
        "ix_institution_images_institution_id", table_name="institution_images"
    )
    op.drop_table("institution_images")
