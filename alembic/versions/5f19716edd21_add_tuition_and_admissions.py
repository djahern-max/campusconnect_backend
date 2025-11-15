"""add tuition and admissions data tables

Revision ID: add_tuition_admissions
Revises: 917197b7ae12
Create Date: 2025-11-15 15:00:00

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_tuition_admissions"
down_revision = "917197b7ae12"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tuition_data table
    op.create_table(
        "tuition_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Integer(), nullable=True),
        sa.Column("ipeds_id", sa.Integer(), nullable=False),
        sa.Column("academic_year", sa.String(length=10), nullable=False),
        sa.Column("data_source", sa.String(length=500), nullable=False),
        sa.Column("tuition_in_state", sa.Float(), nullable=True),
        sa.Column("tuition_out_state", sa.Float(), nullable=True),
        sa.Column("required_fees_in_state", sa.Float(), nullable=True),
        sa.Column("required_fees_out_state", sa.Float(), nullable=True),
        sa.Column("room_board_on_campus", sa.Float(), nullable=True),
        # Admin override fields
        sa.Column("last_updated_by", sa.Integer(), nullable=True),
        sa.Column(
            "is_admin_verified", sa.Boolean(), server_default="false", nullable=False
        ),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["institution_id"], ["institutions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["last_updated_by"],
            ["admin_users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ipeds_id",
            "academic_year",
            "data_source",
            name="uq_tuition_institution_year_source",
        ),
    )
    op.create_index(op.f("ix_tuition_data_id"), "tuition_data", ["id"], unique=False)
    op.create_index(
        op.f("ix_tuition_data_ipeds_id"), "tuition_data", ["ipeds_id"], unique=False
    )
    op.create_index(
        op.f("ix_tuition_data_academic_year"),
        "tuition_data",
        ["academic_year"],
        unique=False,
    )
    op.create_index(
        op.f("ix_tuition_data_institution_id"),
        "tuition_data",
        ["institution_id"],
        unique=False,
    )

    # Create admissions_data table
    op.create_table(
        "admissions_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("institution_id", sa.Integer(), nullable=True),
        sa.Column("ipeds_id", sa.Integer(), nullable=False),
        sa.Column("academic_year", sa.String(length=10), nullable=False),
        sa.Column("applications_total", sa.Integer(), nullable=True),
        sa.Column("admissions_total", sa.Integer(), nullable=True),
        sa.Column("enrolled_total", sa.Integer(), nullable=True),
        sa.Column("acceptance_rate", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("yield_rate", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("sat_reading_25th", sa.Integer(), nullable=True),
        sa.Column("sat_reading_50th", sa.Integer(), nullable=True),
        sa.Column("sat_reading_75th", sa.Integer(), nullable=True),
        sa.Column("sat_math_25th", sa.Integer(), nullable=True),
        sa.Column("sat_math_50th", sa.Integer(), nullable=True),
        sa.Column("sat_math_75th", sa.Integer(), nullable=True),
        sa.Column(
            "percent_submitting_sat", sa.Numeric(precision=5, scale=2), nullable=True
        ),
        # Admin override fields
        sa.Column("last_updated_by", sa.Integer(), nullable=True),
        sa.Column(
            "is_admin_verified", sa.Boolean(), server_default="false", nullable=False
        ),
        sa.Column("admin_notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["institution_id"], ["institutions.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["last_updated_by"],
            ["admin_users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "ipeds_id", "academic_year", name="uq_admissions_institution_year"
        ),
    )
    op.create_index(
        op.f("ix_admissions_data_id"), "admissions_data", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_admissions_data_ipeds_id"),
        "admissions_data",
        ["ipeds_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admissions_data_academic_year"),
        "admissions_data",
        ["academic_year"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admissions_data_institution_id"),
        "admissions_data",
        ["institution_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_admissions_data_acceptance_rate"),
        "admissions_data",
        ["acceptance_rate"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_admissions_data_acceptance_rate"), table_name="admissions_data"
    )
    op.drop_index(
        op.f("ix_admissions_data_institution_id"), table_name="admissions_data"
    )
    op.drop_index(
        op.f("ix_admissions_data_academic_year"), table_name="admissions_data"
    )
    op.drop_index(op.f("ix_admissions_data_ipeds_id"), table_name="admissions_data")
    op.drop_index(op.f("ix_admissions_data_id"), table_name="admissions_data")
    op.drop_table("admissions_data")

    op.drop_index(op.f("ix_tuition_data_institution_id"), table_name="tuition_data")
    op.drop_index(op.f("ix_tuition_data_academic_year"), table_name="tuition_data")
    op.drop_index(op.f("ix_tuition_data_ipeds_id"), table_name="tuition_data")
    op.drop_index(op.f("ix_tuition_data_id"), table_name="tuition_data")
    op.drop_table("tuition_data")
