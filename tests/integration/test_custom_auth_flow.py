"""
Integration tests for CampusConnect's custom authentication flow
"""
import pytest
from httpx import AsyncClient
from app.models.invitation_code import InvitationStatus


@pytest.mark.integration
@pytest.mark.auth
class TestSuperAdminFlow:
    """Test Super Admin authentication and permissions"""
    
    @pytest.mark.asyncio
    async def test_super_admin_login(self, client: AsyncClient, super_admin_user):
        """Test Super Admin can login"""
        response = await client.post(
            "/api/v1/admin/auth/login",
            data={
                "username": super_admin_user.email,  # Use dynamic email from fixture
                "password": "SuperAdmin123!"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_super_admin_get_info(
        self,
        client: AsyncClient,
        super_admin_headers: dict,
        super_admin_user
    ):
        """Test Super Admin can access /auth/me"""
        response = await client.get(
            "/api/v1/admin/auth/me",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == super_admin_user.email  # Use dynamic email
        assert data["role"] == "super_admin"
        assert data["entity_type"] is None
        assert data["entity_id"] is None


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.invitation
class TestInvitationFlow:
    """Test complete invitation code flow"""
    
    @pytest.mark.asyncio
    async def test_create_invitation_code(
        self,
        client: AsyncClient,
        super_admin_headers: dict,
        test_institution
    ):
        """Test Super Admin can create invitation codes"""
        response = await client.post(
            "/api/v1/admin/auth/invitations",
            headers=super_admin_headers,
            json={
                "entity_type": "institution",
                "entity_id": test_institution.id,
                "assigned_email": "newinvite@test.com",
                "expires_in_days": 30
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "code" in data
        assert data["entity_type"] == "institution"
        assert data["entity_id"] == test_institution.id
        # API returns lowercase status
        assert data["status"].lower() == "pending"
        assert "expires_at" in data
    
    @pytest.mark.asyncio
    async def test_list_invitations(
        self,
        client: AsyncClient,
        super_admin_headers: dict,
        invitation_code_institution
    ):
        """Test Super Admin can list all invitations"""
        response = await client.get(
            "/api/v1/admin/auth/invitations",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
    
    @pytest.mark.asyncio
    async def test_validate_invitation_code(
        self,
        client: AsyncClient,
        invitation_code_institution
    ):
        """Test public invitation validation (no auth required)"""
        response = await client.post(
            "/api/v1/admin/auth/validate-invitation",
            json={"code": invitation_code_institution.code}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["entity_type"] == "institution"
        assert "entity_name" in data
    
    @pytest.mark.asyncio
    async def test_validate_invalid_code(self, client: AsyncClient):
        """Test validation with invalid code"""
        response = await client.post(
            "/api/v1/admin/auth/validate-invitation",
            json={"code": "INVALID-CODE-123"}
        )
        
        # API returns 200 with valid=False instead of error code
        assert response.status_code == 200
        data = response.json()
        assert data.get("valid") is False


@pytest.mark.integration
@pytest.mark.auth
class TestAdminRegistrationAndLogin:
    """Test admin user registration and authentication"""
    
    @pytest.mark.asyncio
    async def test_complete_registration_flow(
        self,
        client: AsyncClient,
        invitation_code_institution,
        db_session
    ):
        """Test complete registration flow with invitation code"""
        email = invitation_code_institution.assigned_email
        password = "TestPassword123!"
        
        # 1. Register with invitation code
        register_response = await client.post(
            "/api/v1/admin/auth/register",
            json={
                "email": email,
                "password": password,
                "invitation_code": invitation_code_institution.code
            }
        )
        
        assert register_response.status_code == 200
        user_data = register_response.json()
        assert user_data["email"] == email
        assert user_data["role"] == "admin"
        assert user_data["entity_type"] == "institution"
        assert user_data["is_active"] is True
        
        # 2. Login with credentials
        login_response = await client.post(
            "/api/v1/admin/auth/login",
            data={"username": email, "password": password}
        )
        
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        
        # 3. Access protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_response = await client.get("/api/v1/admin/auth/me", headers=headers)
        
        assert me_response.status_code == 200
        me_data = me_response.json()
        assert me_data["email"] == email
        
        # 4. Verify invitation code is now CLAIMED
        await db_session.refresh(invitation_code_institution)
        assert invitation_code_institution.status == InvitationStatus.CLAIMED
    
    @pytest.mark.asyncio
    async def test_cannot_reuse_claimed_invitation(
        self,
        client: AsyncClient,
        registered_admin_user,
        invitation_code_institution
    ):
        """Test that claimed invitation codes cannot be reused"""
        response = await client.post(
            "/api/v1/admin/auth/register",
            json={
                "email": "another@test.com",
                "password": "TestPassword123!",
                "invitation_code": invitation_code_institution.code
            }
        )
        
        # Should fail because code is already claimed
        assert response.status_code in [400, 404]
    
    @pytest.mark.asyncio
    async def test_login_with_wrong_password(
        self,
        client: AsyncClient,
        registered_admin_user
    ):
        """Test login fails with incorrect password"""
        response = await client.post(
            "/api/v1/admin/auth/login",
            data={
                "username": registered_admin_user["email"],
                "password": "WrongPassword123!"
            }
        )
        
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.auth
class TestAdminEntityAccess:
    """Test admin users can access their entities"""
    
    @pytest.mark.asyncio
    async def test_admin_can_access_entity(
        self,
        client: AsyncClient,
        admin_headers: dict,
        test_institution
    ):
        """Test admin user can access their institution/scholarship"""
        response = await client.get(
            "/api/v1/admin/profile/entity",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data  # Institution/Scholarship name
    
    @pytest.mark.asyncio
    async def test_admin_can_get_display_settings(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test admin can access display settings"""
        response = await client.get(
            "/api/v1/admin/profile/display-settings",
            headers=admin_headers
        )
        
        # May return 200 or 404 depending on if settings exist
        assert response.status_code in [200, 404]
