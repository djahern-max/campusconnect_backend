"""
Integration tests for scholarships endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestScholarshipsEndpoints:
    """Test public scholarships endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_all_scholarships(
        self,
        client: AsyncClient,
        test_scholarship
    ):
        """Test getting list of scholarships"""
        response = await client.get("/api/v1/scholarships?limit=10")
        assert response.status_code == 200
        scholarships = response.json()
        assert isinstance(scholarships, list)
        assert len(scholarships) > 0
        
        # Check structure
        first_scholarship = scholarships[0]
        assert "id" in first_scholarship
        assert "title" in first_scholarship
        assert "organization" in first_scholarship
    
    @pytest.mark.asyncio
    async def test_get_single_scholarship(
        self,
        client: AsyncClient,
        test_scholarship
    ):
        """Test getting a single scholarship"""
        response = await client.get(f"/api/v1/scholarships/{test_scholarship.id}")
        assert response.status_code == 200
        scholarship = response.json()
        assert scholarship["id"] == test_scholarship.id
        assert scholarship["title"] == test_scholarship.title
    
    @pytest.mark.asyncio
    async def test_scholarship_not_found(self, client: AsyncClient):
        """Test 404 for non-existent scholarship"""
        response = await client.get("/api/v1/scholarships/999999")
        assert response.status_code == 404
