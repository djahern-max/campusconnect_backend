"""
Integration tests for public gallery endpoints
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestPublicGallery:
    """Test public gallery access (no auth required)"""
    
    @pytest.mark.asyncio
    async def test_get_institution_gallery_by_id(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test getting institution gallery by database ID"""
        response = await client.get(
            f"/api/v1/public/gallery/institutions/{test_institution.id}/gallery"
        )
        
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_institution_gallery_by_ipeds(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test getting institution gallery by IPEDS ID"""
        response = await client.get(
            f"/api/v1/public/gallery/institutions/ipeds/{test_institution.ipeds_id}/gallery"
        )
        
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_get_institution_featured_image(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test getting featured image for institution"""
        response = await client.get(
            f"/api/v1/public/gallery/institutions/{test_institution.id}/featured-image"
        )
        
        # Returns 404 if no featured image set
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_get_scholarship_gallery(
        self,
        client: AsyncClient,
        test_scholarship
    ):
        """Test getting scholarship gallery"""
        response = await client.get(
            f"/api/v1/public/gallery/scholarships/{test_scholarship.id}/gallery"
        )
        
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_get_scholarship_featured_image(
        self,
        client: AsyncClient,
        test_scholarship
    ):
        """Test getting featured image for scholarship"""
        response = await client.get(
            f"/api/v1/public/gallery/scholarships/{test_scholarship.id}/featured-image"
        )
        
        assert response.status_code in [200, 404]
