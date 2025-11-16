"""
Script to set up a Super Admin user and test the invitation/subscription process
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.insert(0, "/Users/ryze.ai/projects/campusconnect-backend")

from app.models.admin_user import AdminUser
from app.models.invitation_code import InvitationCode, InvitationStatus
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.core.security import get_password_hash  # USE THE REAL ONE
import secrets

# Database URL
DATABASE_URL = (
    "postgresql+asyncpg://postgres:your_password@localhost:5432/campusconnect_db"
)


async def create_super_admin(session: AsyncSession, email: str, password: str):
    """Create a Super Admin user"""
    # Check if user already exists
    query = select(AdminUser).where(AdminUser.email == email)
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        print(f"❌ User with email {email} already exists!")
        return existing_user

    # Hash the password using the SAME function as the backend
    hashed_password = get_password_hash(password)

    # Create Super Admin user
    super_admin = AdminUser(
        email=email,
        hashed_password=hashed_password,
        entity_type=None,
        entity_id=None,
        role="super_admin",
        is_active=True,
        created_at=datetime.utcnow(),
    )

    session.add(super_admin)
    await session.commit()
    await session.refresh(super_admin)

    print(f"✅ Super Admin created!")
    print(f"   Email: {email}")
    print(f"   Role: {super_admin.role}")
    print(f"   ID: {super_admin.id}")

    return super_admin


async def generate_invitation_code(
    session: AsyncSession,
    entity_type: str,
    entity_id: int,
    assigned_email: str = None,
    created_by: str = "super_admin",
):
    """Generate an invitation code"""
    # Generate unique code
    code = secrets.token_urlsafe(12)  # Generates a random code

    # Calculate expiration (30 days from now)
    expires_at = datetime.utcnow() + timedelta(days=30)

    # Create invitation
    invitation = InvitationCode(
        code=code,
        entity_type=entity_type,
        entity_id=entity_id,
        assigned_email=assigned_email,
        status=InvitationStatus.PENDING,
        expires_at=expires_at,
        created_by=created_by,
        created_at=datetime.utcnow(),
    )

    session.add(invitation)
    await session.commit()
    await session.refresh(invitation)

    print(f"\n✅ Invitation code generated!")
    print(f"   Code: {invitation.code}")
    print(f"   Entity Type: {entity_type}")
    print(f"   Entity ID: {entity_id}")
    print(f"   Expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
    if assigned_email:
        print(f"   Assigned to: {assigned_email}")

    return invitation


async def get_sample_entities(session: AsyncSession):
    """Get sample institution and scholarship for testing"""
    # Get a sample institution
    inst_query = select(Institution).limit(1)
    inst_result = await session.execute(inst_query)
    institution = inst_result.scalar_one_or_none()

    # Get a sample scholarship
    schol_query = select(Scholarship).limit(1)
    schol_result = await session.execute(schol_query)
    scholarship = schol_result.scalar_one_or_none()

    return institution, scholarship


async def main():
    """Main setup function"""
    print("=" * 60)
    print("CampusConnect - Super Admin Setup & Testing")
    print("=" * 60)

    # Get database URL from user
    db_url = input("\nEnter your database URL (or press Enter for default):\n")
    if not db_url.strip():
        db_url = DATABASE_URL

    # Create async engine
    engine = create_async_engine(db_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Step 1: Create Super Admin
        print("\n" + "=" * 60)
        print("STEP 1: Create Super Admin User")
        print("=" * 60)

        email = input("Enter Super Admin email (default: admin@campusconnect.com): ")
        if not email.strip():
            email = "admin@campusconnect.com"

        password = input("Enter Super Admin password (default: SuperAdmin123!): ")
        if not password.strip():
            password = "SuperAdmin123!"

        super_admin = await create_super_admin(session, email, password)

        # Step 2: Get sample entities
        print("\n" + "=" * 60)
        print("STEP 2: Getting Sample Entities")
        print("=" * 60)

        institution, scholarship = await get_sample_entities(session)

        if institution:
            print(
                f"✅ Found sample institution: {institution.name} (ID: {institution.id})"
            )
        else:
            print("❌ No institutions found in database!")

        if scholarship:
            print(
                f"✅ Found sample scholarship: {scholarship.title} (ID: {scholarship.id})"
            )
        else:
            print("❌ No scholarships found in database!")

        # Step 3: Generate invitation codes
        print("\n" + "=" * 60)
        print("STEP 3: Generate Invitation Codes")
        print("=" * 60)

        invitations = []

        if institution:
            create_inst = input("\nCreate invitation code for institution? (y/n): ")
            if create_inst.lower() == "y":
                inst_email = input("Assign to email (optional, press Enter to skip): ")
                inv = await generate_invitation_code(
                    session,
                    "institution",
                    institution.id,
                    assigned_email=inst_email if inst_email.strip() else None,
                    created_by=email,
                )
                invitations.append(inv)

        if scholarship:
            create_schol = input("\nCreate invitation code for scholarship? (y/n): ")
            if create_schol.lower() == "y":
                schol_email = input("Assign to email (optional, press Enter to skip): ")
                inv = await generate_invitation_code(
                    session,
                    "scholarship",
                    scholarship.id,
                    assigned_email=schol_email if schol_email.strip() else None,
                    created_by=email,
                )
                invitations.append(inv)

        # Step 4: Display test summary
        print("\n" + "=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)

        print(f"\n📧 Super Admin Login:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")

        if invitations:
            print(f"\n🎟️  Invitation Codes Generated:")
            for inv in invitations:
                print(f"   - {inv.code} ({inv.entity_type})")

        print("\n📝 Next Steps:")
        print("1. Start your FastAPI server: uvicorn app.main:app --reload")
        print("2. Login as Super Admin using the credentials above")
        print("3. Test invitation validation:")
        print("   POST /api/v1/admin/auth/validate-invitation")
        print("4. Test admin registration:")
        print("   POST /api/v1/admin/auth/register")
        print("5. Set up Stripe subscription")

        print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
