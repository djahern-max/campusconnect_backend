"""
Integration tests for Contact Forms
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestContactForms:
    """Test Contact Forms endpoints"""
    
    @pytest.mark.asyncio
    async def test_post_api_v1_contact_submit(
        self,
        client: AsyncClient
    ):
        """Test /api/v1/contact/submit"""
        response = await client.post(
            "/api/v1/contact/submit",
            json={
                "name": "Test User",
                "email": "test@example.com",
                "message": "Test inquiry"
            }
        )
        assert response.status_code in [200, 201, 400]

    @pytest.mark.asyncio
    async def test_get_api_v1_contact_inquiries(
        self,
        client: AsyncClient
    ):
        """Test /api/v1/contact/inquiries"""
        response = await client.get(
            f"/api/v1/contact/inquiries",
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_api_v1_contact_inquiries(
        self,
        client: AsyncClient
    ):
        """Test /api/v1/contact/inquiries/{inquiry_id}"""
        response = await client.get(
            f"/api/v1/contact/inquiries/1",
        )
        assert response.status_code in [200, 404]

