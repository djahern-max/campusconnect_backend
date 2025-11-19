"""
Integration tests for Outreach
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestOutreach:
    """Test Outreach endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_api_v1_admin_outreach_stats(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/outreach/stats"""
        response = await client.get(
            f"/api/v1/admin/outreach/stats",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_api_v1_admin_outreach(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/outreach"""
        response = await client.get(
            f"/api/v1/admin/outreach",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_post_api_v1_admin_outreach(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/outreach"""
        response = await client.post(
            "/api/v1/admin/outreach",
            headers=admin_headers,
            json={
                "recipient_email": "test@example.com",
                "subject": "Test",
                "message": "Test message"
            }
        )
        assert response.status_code in [200, 201, 400]

    @pytest.mark.asyncio
    async def test_put_api_v1_admin_outreach(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/outreach/{outreach_id}"""
        response = await client.put(
            "/api/v1/admin/outreach/1",
            headers=admin_headers,
            json={}
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_api_v1_admin_outreach_templates(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/outreach/templates"""
        response = await client.get(
            f"/api/v1/admin/outreach/templates",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_post_api_v1_admin_outreach_templates(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/outreach/templates"""
        response = await client.post(
            "/api/v1/admin/outreach/templates",
            headers=admin_headers,
            json={
                "recipient_email": "test@example.com",
                "subject": "Test",
                "message": "Test message"
            }
        )
        assert response.status_code in [200, 201, 400]

