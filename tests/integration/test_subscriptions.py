"""
Integration tests for Subscriptions
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestSubscriptions:
    """Test Subscriptions endpoints"""

    @pytest.mark.asyncio
    async def test_post_api_v1_admin_subscriptions_create_checkout(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/subscriptions/create-checkout"""
        response = await client.post(
            "/api/v1/admin/subscriptions/create-checkout",
            headers=admin_headers,
            json={},
        )
        assert response.status_code in [200, 201, 400]

    @pytest.mark.asyncio
    async def test_get_api_v1_admin_subscriptions_pricing(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/subscriptions/pricing"""
        response = await client.get(
            f"/api/v1/admin/subscriptions/pricing",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_api_v1_admin_subscriptions_current(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/subscriptions/current"""
        response = await client.get(
            f"/api/v1/admin/subscriptions/current",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_post_api_v1_admin_subscriptions_cancel(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/subscriptions/cancel"""
        response = await client.post(
            "/api/v1/admin/subscriptions/cancel", headers=admin_headers, json={}
        )
        assert response.status_code in [200, 201, 400, 404]

    @pytest.mark.asyncio
    async def test_get_api_v1_admin_subscriptions_portal(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/subscriptions/portal"""
        response = await client.get(
            f"/api/v1/admin/subscriptions/portal",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]
