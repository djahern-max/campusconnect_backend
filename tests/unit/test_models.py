"""
Unit tests for database models
"""
import pytest
from app.models.institution import Institution
from app.models.scholarship import Scholarship
from app.models.admin_user import AdminUser
from app.models.invitation_code import InvitationCode, InvitationStatus
from datetime import datetime, timedelta


@pytest.mark.unit
class TestInstitutionModel:
    """Test Institution model"""
    
    def test_create_institution(self):
        """Test creating an institution instance"""
        institution = Institution(
            ipeds_id=123456,
            name="Harvard University",
            city="Cambridge",
            state="MA",
            control_type="PRIVATE_NONPROFIT"
        )
        
        assert institution.ipeds_id == 123456
        assert institution.name == "Harvard University"
        assert institution.state == "MA"


@pytest.mark.unit
class TestScholarshipModel:
    """Test Scholarship model"""
    
    def test_create_scholarship(self):
        """Test creating a scholarship instance"""
        scholarship = Scholarship(
            title="Gates Millennium Scholars",
            organization="Bill & Melinda Gates Foundation",
            scholarship_type="Merit-based",
            status="Active",
            difficulty_level="High",
            amount_min=10000,
            amount_max=50000,
            is_renewable=True
        )
        
        assert scholarship.title == "Gates Millennium Scholars"
        assert scholarship.amount_min == 10000
        assert scholarship.is_renewable is True


@pytest.mark.unit
class TestAdminUserModel:
    """Test AdminUser model"""
    
    def test_create_super_admin(self):
        """Test creating a Super Admin user"""
        admin = AdminUser(
            email="admin@campusconnect.com",
            hashed_password="hashed_pwd_here",
            entity_type=None,
            entity_id=None,
            role="super_admin",
            is_active=True
        )
        
        assert admin.email == "admin@campusconnect.com"
        assert admin.role == "super_admin"
        assert admin.entity_type is None
        assert admin.is_active is True
    
    def test_create_institution_admin(self):
        """Test creating an institution admin"""
        admin = AdminUser(
            email="admin@harvard.edu",
            hashed_password="hashed_pwd_here",
            entity_type="institution",
            entity_id=1,
            role="admin",
            is_active=True
        )
        
        assert admin.entity_type == "institution"
        assert admin.entity_id == 1
        assert admin.role == "admin"


@pytest.mark.unit
class TestInvitationCodeModel:
    """Test InvitationCode model"""
    
    def test_create_invitation(self):
        """Test creating an invitation code"""
        invitation = InvitationCode(
            code="TEST-CODE-123",
            entity_type="institution",
            entity_id=1,
            status=InvitationStatus.PENDING,
            expires_at=datetime.utcnow() + timedelta(days=30),
            created_by="admin@campusconnect.com"
        )
        
        assert invitation.code == "TEST-CODE-123"
        assert invitation.entity_type == "institution"
        assert invitation.status == InvitationStatus.PENDING
