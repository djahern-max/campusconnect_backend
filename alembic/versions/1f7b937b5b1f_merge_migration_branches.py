"""merge_migration_branches

Revision ID: 1f7b937b5b1f
Revises: 1fcaca15316, 9bde3ba3d4a1
Create Date: 2025-11-26 04:37:15.704268

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f7b937b5b1f'
down_revision = ('1fcaca15316', '9bde3ba3d4a1')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
