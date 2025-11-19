"""
Integration tests for institutions endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestInstitutionsEndpoints:
    """Test public institutions endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_all_institutions(self, client: AsyncClient, test_institution):
        """Test getting list of institutions"""
        response = await client.get("/api/v1/institutions?limit=10")
        assert response.status_code == 200
        institutions = response.json()
        assert isinstance(institutions, list)
        assert len(institutions) > 0
        
        # Check structure
        first_inst = institutions[0]
        assert "id" in first_inst
        assert "name" in first_inst
        assert "state" in first_inst
    
    @pytest.mark.asyncio
    async def test_filter_institutions_by_state(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test filtering institutions by state"""
        response = await client.get("/api/v1/institutions?state=NH")
        assert response.status_code == 200
        institutions = response.json()
        
        for inst in institutions:
            assert inst["state"] == "NH"
    
    @pytest.mark.asyncio
    async def test_get_single_institution(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test getting a single institution by IPEDS ID"""
        response = await client.get(f"/api/v1/institutions/{test_institution.ipeds_id}")
        assert response.status_code == 200
        institution = response.json()
        assert institution["ipeds_id"] == test_institution.ipeds_id
        assert institution["name"] == test_institution.name
    
    @pytest.mark.asyncio
    async def test_institution_not_found(self, client: AsyncClient):
        """Test 404 for non-existent institution"""
        response = await client.get("/api/v1/institutions/999999999")
        assert response.status_code == 404
