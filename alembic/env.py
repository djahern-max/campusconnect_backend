# alembic/env.py for CampusConnect
# This tells Alembic to IGNORE MagicScholar tables (not drop them)
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import Base
from app.core.database import Base

# Import ALL CampusConnect models (including shared models)
# Based on actual files in app/models/
from app.models.admin_user import AdminUser
from app.models.admission_data import AdmissionData
from app.models.contact_inquiry import ContactInquiry
from app.models.display_settings import DisplaySettings
from app.models.entity_image import EntityImage
from app.models.institution_extended_info import InstitutionExtendedInfo
from app.models.institution_image import InstitutionImage
from app.models.institution_video import InstitutionVideo
from app.models.institution import Institution
from app.models.invitation_code import InvitationCode
from app.models.message_templates import MessageTemplate, OutreachActivity
from app.models.outreach_tracking import OutreachTracking
from app.models.scholarship import Scholarship
from app.models.subscription import Subscription
from app.models.tuition_data import TuitionData

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def include_object(object, name, type_, reflected, compare_to):
    """
    Control which database objects Alembic should manage.

    - Exclude alembic_version tables (both magicscholar and campusconnect)
    - IGNORE MagicScholar-specific tables
    - IGNORE modifications to shared tables (they're managed by MagicScholar)
    """
    # Always exclude alembic_version tables
    if type_ == "table" and name in (
        "alembic_version",
        "alembic_version_magicscholar",
        "alembic_version_campusconnect",
    ):
        return False

    # MagicScholar tables that CampusConnect should IGNORE
    magicscholar_tables = {
        "users",
        "user_profiles",
        "oauth_accounts",
        "oauth_states",
        "college_applications",
        "scholarship_applications",
        "enrollment_data",
        "graduation_data",
    }

    # Shared tables that already exist (managed by MagicScholar)
    # CampusConnect should NOT modify these
    shared_tables = {
        "institutions",
        "scholarships",
        "admissions_data",
        "tuition_data",
        "entity_images",
    }

    if type_ == "table":
        # Ignore MagicScholar tables completely
        if name in magicscholar_tables:
            return False

        # For shared tables: only ignore if they already exist in DB
        # (compare_to is None means table exists in DB but not being created by this migration)
        if name in shared_tables:
            # If compare_to is not None, the table is being created/modified
            # We want to prevent modifications, so always return False for shared tables
            return False

    # For indexes, constraints, and foreign keys
    if type_ in ("index", "unique_constraint", "foreign_key", "column"):
        table_name = None
        if hasattr(object, "table"):
            table_name = object.table.name
        elif hasattr(object, "parent"):
            table_name = object.parent.name

        # Ignore operations on MagicScholar or shared tables
        if table_name in magicscholar_tables or table_name in shared_tables:
            return False

    return True


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
        compare_type=True,
        version_table="alembic_version_campusconnect",  # ADD THIS LINE
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # Try environment variable first (production), fall back to alembic.ini (local)
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        # Production: use DATABASE_URL environment variable
        from sqlalchemy import create_engine

        connectable = create_engine(database_url, poolclass=pool.NullPool)
    else:
        # Local development: use alembic.ini
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
            compare_type=True,
            version_table="alembic_version_campusconnect",
        )

        with context.begin_transaction():
            context.run_migrations()
