"""
Integration tests for health and meta endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check and meta endpoints"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root endpoint"""
        response = await client.get("/")
        
        assert response.status_code == 200
        # May return JSON or HTML
        if response.headers.get("content-type", "").startswith("application/json"):
            data = response.json()
            assert "message" in data or "name" in data
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint"""
        response = await client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_routes_simple(self, client: AsyncClient):
        """Test routes listing endpoint"""
        response = await client.get("/routes-simple")
        
        assert response.status_code == 200
        
        # May return HTML or JSON depending on implementation
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) > 0
        elif "text/html" in content_type:
            # Returns HTML list of routes
            assert len(response.text) > 0
            assert "api/v1" in response.text.lower()
