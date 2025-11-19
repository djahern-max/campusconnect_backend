"""
Integration tests for Extended Info
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestExtendedInfo:
    """Test Extended Info endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_api_v1_admin_extended-info(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/extended-info"""
        response = await client.get(
            f"/api/v1/admin/extended-info",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_put_api_v1_admin_extended-info(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/extended-info"""
        response = await client.put(
            "/api/v1/admin/extended-info",
            headers=admin_headers,
            json={
                "campus_life": "Test description"
            }
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    @pytest.mark.skip("Destructive test - enable when needed")
    async def test_delete_api_v1_admin_extended-info(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/extended-info"""
        response = await client.delete(
            "/api/v1/admin/extended-info",
            headers=admin_headers,
        )
        assert response.status_code in [200, 204, 404]

