"""
Test configuration with proper test isolation
"""

# SET THIS FIRST - before any other imports
import os

# Set testing flag
os.environ["TESTING"] = "true"

# Explicitly load .env.test file before any app imports
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import text

# Get project root (parent of tests directory)
project_root = Path(__file__).parent.parent
env_test_path = project_root / ".env.test"

# Load .env.test file
load_dotenv(env_test_path, override=True)

import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport
from datetime import datetime, timedelta
import secrets
import random

from app.main import app
from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import get_password_hash
from app.models.admin_user import AdminUser
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.models.invitation_code import InvitationCode, InvitationStatus

# Test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    base_url = settings.DATABASE_URL
    if "postgresql://" in base_url and "asyncpg" not in base_url:
        base_url = base_url.replace("postgresql://", "postgresql+asyncpg://")
    TEST_DATABASE_URL = base_url.replace("campusconnect_db", "unified_test")

print(f"\n🔧 Test Database URL: {TEST_DATABASE_URL.split('@')[0]}@...")

# Test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """
    Since unified_test was created from unified_db template,
    it already has all tables. Just verify connection.
    """
    print("\n🔧 Verifying test database connection...")

    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print("✅ Test database connection verified")

    yield

    print("\n🧹 Test session complete")
    await test_engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Fresh database session for each test with automatic rollback.
    Each test gets a clean slate.
    """
    connection = await test_engine.connect()
    transaction = await connection.begin()

    async_session = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session
        await transaction.rollback()

    await connection.close()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Test client with database session override"""

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# === FIXTURES - Use random IDs to avoid conflicts ===


@pytest.fixture
async def super_admin_user(db_session: AsyncSession) -> AdminUser:
    """Create a Super Admin user with unique email"""
    email = f"admin_{random.randint(1000, 9999)}@campusconnect.com"
    super_admin = AdminUser(
        email=email,
        hashed_password=get_password_hash("SuperAdmin123!"),
        entity_type=None,
        entity_id=None,
        role="super_admin",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    db_session.add(super_admin)
    await db_session.flush()
    await db_session.refresh(super_admin)
    return super_admin


@pytest.fixture
async def super_admin_token(client: AsyncClient, super_admin_user: AdminUser) -> str:
    """Get Super Admin JWT token"""
    response = await client.post(
        "/api/v1/admin/auth/login",
        data={"username": super_admin_user.email, "password": "SuperAdmin123!"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def super_admin_headers(super_admin_token: str) -> dict:
    """Authorization headers for Super Admin"""
    return {"Authorization": f"Bearer {super_admin_token}"}


@pytest.fixture
async def test_institution(db_session: AsyncSession) -> Institution:
    """Create a test institution with unique IPEDS ID"""
    ipeds_id = random.randint(100000, 999999)
    institution = Institution(
        ipeds_id=ipeds_id,
        name=f"Test University {ipeds_id}",
        city="Boston",
        state="MA",
        control_type="PUBLIC",
        student_faculty_ratio=15.0,
        size_category="Medium",
        locale="City",
    )
    db_session.add(institution)
    await db_session.flush()
    await db_session.refresh(institution)
    return institution


@pytest.fixture
async def test_scholarship(db_session: AsyncSession) -> Scholarship:
    """Create a test scholarship - use valid enum values"""
    scholarship = Scholarship(
        title=f"Test Scholarship {random.randint(1000, 9999)}",
        organization="Test Organization",
        scholarship_type="ACADEMIC_MERIT",  # Valid enum value
        status="ACTIVE",
        difficulty_level="MODERATE",
        amount_min=1000,
        amount_max=5000,
        is_renewable=True,
        min_gpa=3.0,
    )
    db_session.add(scholarship)
    await db_session.flush()
    await db_session.refresh(scholarship)
    return scholarship


@pytest.fixture
async def invitation_code_institution(
    db_session: AsyncSession, test_institution: Institution, super_admin_user: AdminUser
) -> InvitationCode:
    """Create invitation code for institution"""
    invitation = InvitationCode(
        code=secrets.token_urlsafe(12),
        entity_type="institution",
        entity_id=test_institution.id,
        assigned_email=f"testadmin_{random.randint(1000, 9999)}@institution.com",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=30),
        created_by=super_admin_user.email,
        created_at=datetime.utcnow(),
    )
    db_session.add(invitation)
    await db_session.flush()
    await db_session.refresh(invitation)
    return invitation


@pytest.fixture
async def invitation_code_scholarship(
    db_session: AsyncSession, test_scholarship: Scholarship, super_admin_user: AdminUser
) -> InvitationCode:
    """Create invitation code for scholarship"""
    invitation = InvitationCode(
        code=secrets.token_urlsafe(12),
        entity_type="scholarship",
        entity_id=test_scholarship.id,
        assigned_email=f"testadmin_{random.randint(1000, 9999)}@scholarship.com",
        status=InvitationStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=30),
        created_by=super_admin_user.email,
        created_at=datetime.utcnow(),
    )
    db_session.add(invitation)
    await db_session.flush()
    await db_session.refresh(invitation)
    return invitation


@pytest.fixture
async def registered_admin_user(
    client: AsyncClient, invitation_code_institution: InvitationCode
) -> dict:
    """Register an admin user and return credentials"""
    email = invitation_code_institution.assigned_email
    password = "TestPassword123!"

    response = await client.post(
        "/api/v1/admin/auth/register",
        json={
            "email": email,
            "password": password,
            "invitation_code": invitation_code_institution.code,
        },
    )

    assert response.status_code == 200

    return {"email": email, "password": password, "user_data": response.json()}


@pytest.fixture
async def admin_token(client: AsyncClient, registered_admin_user: dict) -> str:
    """Get admin user JWT token"""
    response = await client.post(
        "/api/v1/admin/auth/login",
        data={
            "username": registered_admin_user["email"],
            "password": registered_admin_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token: str) -> dict:
    """Authorization headers for admin user"""
    return {"Authorization": f"Bearer {admin_token}"}


# === IMAGE TESTING FIXTURES ===


@pytest.fixture
def sample_image_bytes() -> bytes:
    """Create a simple test image in memory"""
    from PIL import Image
    import io

    img = Image.new("RGB", (800, 600), color="#2563eb")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    return img_bytes.read()


@pytest.fixture
def sample_image_path() -> str:
    """Path to test image file"""
    return "tests/test_data/images/test_image.jpg"


# Pytest configuration
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "auth: Authentication tests")
    config.addinivalue_line("markers", "gallery: Gallery management tests")
    config.addinivalue_line("markers", "invitation: Invitation code tests")
    config.addinivalue_line("markers", "super_admin: Super admin only tests")
