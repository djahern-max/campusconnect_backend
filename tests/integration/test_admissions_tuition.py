"""
Integration tests for admissions and tuition data management
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestAdmissionsData:
    """Test admissions data endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_admissions_data(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test getting admissions data for admin's institution"""
        response = await client.get(
            "/api/v1/admin/data/admissions",
            headers=admin_headers
        )
        
        # May return empty list or data
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_get_public_admissions_data(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test getting public admissions data"""
        response = await client.get(
            f"/api/v1/institutions/{test_institution.ipeds_id}/admissions"
        )
        
        # May return 404 if no data exists
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestTuitionData:
    """Test tuition data endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_tuition_data(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test getting tuition data for admin's institution"""
        response = await client.get(
            "/api/v1/admin/data/tuition",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_get_public_tuition_data(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test getting public tuition data"""
        response = await client.get(
            f"/api/v1/institutions/{test_institution.ipeds_id}/tuition"
        )
        
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_get_financial_overview(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test getting financial overview"""
        response = await client.get(
            f"/api/v1/institutions/{test_institution.ipeds_id}/financial-overview"
        )
        
        assert response.status_code in [200, 404]
