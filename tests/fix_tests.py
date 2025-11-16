#!/usr/bin/env python3
"""
Quick fix script for test_integration.py
Fixes:
1. File paths for sample JSON files
2. Creates test admin user if it doesn't exist
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.admin_user import AdminUser
from app.models.display_settings import DisplaySettings
from app.core.security import get_password_hash
from sqlalchemy import select


async def create_test_admin():
    """Create test admin user if it doesn't exist"""
    
    async with AsyncSessionLocal() as db:
        # Check if admin exists
        query = select(AdminUser).where(AdminUser.email == "admin@snhu.edu")
        result = await db.execute(query)
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            print("✅ Test admin already exists: admin@snhu.edu")
            return
        
        # Create admin user
        admin = AdminUser(
            email="admin@snhu.edu",
            hashed_password=get_password_hash("test123"),
            entity_type="institution",
            entity_id=367,  # Southern New Hampshire University
            role="super_admin",  # Make them super admin for all tests
            is_active=True
        )
        
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        print(f"✅ Created test admin: admin@snhu.edu")
        print(f"   Password: test123")
        print(f"   Entity ID: {admin.entity_id}")
        print(f"   Role: {admin.role}")
        
        # Create display settings if they don't exist
        query = select(DisplaySettings).where(
            DisplaySettings.entity_type == "institution",
            DisplaySettings.entity_id == 367
        )
        result = await db.execute(query)
        existing_settings = result.scalar_one_or_none()
        
        if not existing_settings:
            settings = DisplaySettings(
                entity_type="institution",
                entity_id=367,
                show_stats=True,
                show_financial=True,
                show_requirements=True,
                show_image_gallery=False,
                show_video=False,
                show_extended_info=False,
                layout_style="standard"
            )
            db.add(settings)
            await db.commit()
            print("✅ Created display settings for test admin")


def fix_test_file_paths():
    """Fix file paths in test_integration.py"""
    
    test_file = Path(__file__).parent / "test_integration.py"
    
    if not test_file.exists():
        print("❌ test_integration.py not found!")
        return
    
    content = test_file.read_text()
    
    # Fix the file paths
    fixes = [
        ('with open("tests/sample_institution.json"', 'with open("sample_institution.json"'),
        ('with open("tests/sample_scholarship.json"', 'with open("sample_scholarship.json"'),
        ('with open("tests/sample_display_settings.json"', 'with open("sample_display_settings.json"'),
    ]
    
    changes_made = False
    for old, new in fixes:
        if old in content:
            content = content.replace(old, new)
            changes_made = True
    
    if changes_made:
        test_file.write_text(content)
        print("✅ Fixed file paths in test_integration.py")
    else:
        print("ℹ️  File paths already fixed or not found")


if __name__ == "__main__":
    print("🔧 CampusConnect Test Fix Script")
    print("=" * 50)
    
    # Fix file paths
    fix_test_file_paths()
    
    # Create test admin
    print("\nCreating test admin user...")
    asyncio.run(create_test_admin())
    
    print("\n" + "=" * 50)
    print("✅ Fixes complete!")
    print("\nNow run: pytest test_integration.py -v -s")
