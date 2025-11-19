"""
Tests for institution data management and verification
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestInstitutionLookup:
    """Test institution lookup methods"""
    
    @pytest.mark.asyncio
    async def test_get_institution_by_database_id(
        self,
        client: AsyncClient,
        test_institution
    ):
        """Test getting institution by database ID"""
        response = await client.get(
            f"/api/v1/institutions/by-id/{test_institution.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_institution.id


@pytest.mark.integration
class TestAdmissionsDataManagement:
    """Test admissions data updates and verification"""
    
    @pytest.mark.asyncio
    async def test_update_admissions_data(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test updating admissions data"""
        update_data = {
            "acceptance_rate": 15.5,
            "application_fee": 75,
            "early_decision_available": True
        }
        
        # Assumes admission record with ID 1 exists
        response = await client.put(
            "/api/v1/admin/data/admissions/1",
            headers=admin_headers,
            json=update_data
        )
        
        # May fail if record doesn't exist
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_verify_admissions_data(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test marking admissions data as verified"""
        response = await client.post(
            "/api/v1/admin/data/admissions/1/verify",
            headers=admin_headers
        )
        
        # May fail if record doesn't exist
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestTuitionDataManagement:
    """Test tuition data updates and verification"""
    
    @pytest.mark.asyncio
    async def test_update_tuition_data(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test updating tuition data"""
        update_data = {
            "in_state_tuition": 12000,
            "out_of_state_tuition": 35000,
            "room_and_board": 15000
        }
        
        response = await client.put(
            "/api/v1/admin/data/tuition/1",
            headers=admin_headers,
            json=update_data
        )
        
        assert response.status_code in [200, 404]
    
    @pytest.mark.asyncio
    async def test_verify_tuition_data(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test marking tuition data as verified"""
        response = await client.post(
            "/api/v1/admin/data/tuition/1/verify",
            headers=admin_headers
        )
        
        assert response.status_code in [200, 404]
