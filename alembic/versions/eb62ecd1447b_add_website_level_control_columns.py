"""add_website_level_control_columns

Revision ID: eb62ecd1447b
Revises: 1f7b937b5b1f
Create Date: 2025-11-26 04:37:20.956364

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "eb62ecd1447b"
down_revision = "1f7b937b5b1f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add missing IPEDS columns that the model expects
    op.add_column(
        "institutions", sa.Column("website", sa.String(length=255), nullable=True)
    )
    op.add_column("institutions", sa.Column("level", sa.SmallInteger(), nullable=True))
    op.add_column(
        "institutions", sa.Column("control", sa.SmallInteger(), nullable=True)
    )

    # Create index for website
    op.create_index(
        "idx_institutions_website", "institutions", ["website"], unique=False
    )


def downgrade() -> None:
    op.drop_index("idx_institutions_website", table_name="institutions")
    op.drop_column("institutions", "control")
    op.drop_column("institutions", "level")
    op.drop_column("institutions", "website")
