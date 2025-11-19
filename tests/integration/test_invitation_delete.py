"""
Test invitation deletion
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestInvitationDeletion:
    """Test deleting invitation codes"""
    
    @pytest.mark.asyncio
    async def test_delete_invitation(
        self,
        client: AsyncClient,
        super_admin_headers: dict,
        invitation_code_institution
    ):
        """Test Super Admin can delete invitation codes"""
        response = await client.delete(
            f"/api/v1/admin/auth/invitations/{invitation_code_institution.id}",
            headers=super_admin_headers
        )
        
        assert response.status_code in [200, 204]
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_invitation(
        self,
        client: AsyncClient,
        super_admin_headers: dict
    ):
        """Test deleting non-existent invitation"""
        response = await client.delete(
            "/api/v1/admin/auth/invitations/99999",
            headers=super_admin_headers
        )
        
        assert response.status_code == 404
