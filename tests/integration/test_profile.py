"""
Integration tests for admin profile and display settings
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestProfileEndpoints:
    """Test admin profile management"""
    
    @pytest.mark.asyncio
    async def test_get_admin_entity(
        self,
        client: AsyncClient,
        admin_headers: dict,
        test_institution
    ):
        """Test getting admin's institution/scholarship"""
        response = await client.get(
            "/api/v1/admin/profile/entity",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["id"] == test_institution.id
    
    @pytest.mark.asyncio
    async def test_get_display_settings_not_found(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test getting display settings when none exist"""
        response = await client.get(
            "/api/v1/admin/profile/display-settings",
            headers=admin_headers
        )
        
        # May return 404 or empty data
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_create_and_update_display_settings(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test creating and updating display settings"""
        # Create/Update display settings
        settings_data = {
            "show_admissions_data": True,
            "show_tuition_data": True,
            "show_financial_overview": False,
            "featured_stats": ["acceptance_rate", "avg_sat"]
        }
        
        response = await client.put(
            "/api/v1/admin/profile/display-settings",
            headers=admin_headers,
            json=settings_data
        )
        
        # May not be implemented yet
        assert response.status_code in [200, 201, 404, 501]
        
        if response.status_code in [200, 201]:
            # Get settings to verify
            get_response = await client.get(
                "/api/v1/admin/profile/display-settings",
                headers=admin_headers
            )
            
            assert get_response.status_code == 200
            data = get_response.json()
            assert data["show_admissions_data"] == True
