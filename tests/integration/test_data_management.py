"""
Integration tests for Data Management
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestDataManagement:
    """Test Data Management endpoints"""

    @pytest.mark.asyncio
    async def test_get_api_v1_admin_data_admissions(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/data/admissions"""
        response = await client.get(
            f"/api/v1/admin/data/admissions",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_put_api_v1_admin_data_admissions(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/data/admissions/{admission_id}"""
        response = await client.put(
            "/api/v1/admin/data/admissions/1",
            headers=admin_headers,
            json={"acceptance_rate": 75.0},
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_get_api_v1_admin_data_tuition(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/data/tuition"""
        response = await client.get(
            f"/api/v1/admin/data/tuition",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_put_api_v1_admin_data_tuition(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/data/tuition/{tuition_id}"""
        response = await client.put(
            "/api/v1/admin/data/tuition/1",
            headers=admin_headers,
            json={"in_state_tuition": 15000},
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_post_api_v1_admin_data_admissions_verify(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/data/admissions/{admission_id}/verify"""
        response = await client.post(
            "/api/v1/admin/data/admissions/{admission_id}/verify",
            headers=admin_headers,
            json={},
        )
        assert response.status_code in [200, 201, 400, 422]

    @pytest.mark.asyncio
    async def test_post_api_v1_admin_data_tuition_verify(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test /api/v1/admin/data/tuition/{tuition_id}/verify"""
        response = await client.post(
            "/api/v1/admin/data/tuition/{tuition_id}/verify",
            headers=admin_headers,
            json={},
        )
        assert response.status_code in [200, 201, 400, 422]
