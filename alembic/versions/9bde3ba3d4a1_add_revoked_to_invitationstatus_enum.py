"""add_revoked_to_invitationstatus_enum

Revision ID: 9bde3ba3d4a1
Revises: c7627ac90d7f
Create Date: 2025-11-24 04:22:37.124465

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9bde3ba3d4a1"
down_revision = "c7627ac90d7f"
branch_labels = None
depends_on = None


def upgrade():
    # Add REVOKED to invitationstatus enum
    op.execute("ALTER TYPE invitationstatus ADD VALUE IF NOT EXISTS 'REVOKED'")


def downgrade():
    # Can't easily remove enum values in PostgreSQL
    # Document that downgrade is not supported
    pass
