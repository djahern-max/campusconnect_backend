"""
Integration tests for IPEDS Institution endpoints
"""

import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestIPEDSInstitutions:
    """Test new IPEDS-powered institution endpoints"""

    @pytest.mark.asyncio
    async def test_search_filtered_institutions(
        self, client: AsyncClient, test_institution
    ):
        """Test GET /api/v1/institutions/search/filtered"""
        response = await client.get(
            "/api/v1/institutions/search/filtered",
            params={
                "min_completeness": 0,  # Get all for testing
                "limit": 100,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # Test with filters
        response = await client.get(
            "/api/v1/institutions/search/filtered",
            params={
                "state": test_institution.state,
                "min_completeness": 0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert data[0]["state"] == test_institution.state

    @pytest.mark.asyncio
    async def test_search_filtered_with_text_query(
        self, client: AsyncClient, test_institution
    ):
        """Test search with text query"""
        response = await client.get(
            "/api/v1/institutions/search/filtered",
            params={
                "query_text": test_institution.name[:5],  # First 5 chars
                "min_completeness": 0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_filtered_by_completeness(self, client: AsyncClient):
        """Test filtering by completeness score"""
        # High completeness only
        response = await client.get(
            "/api/v1/institutions/search/filtered",
            params={"min_completeness": 80},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for inst in data:
            assert inst["data_completeness_score"] >= 80

    @pytest.mark.asyncio
    async def test_search_filtered_with_cost_data(self, client: AsyncClient):
        """Test filtering institutions with cost data"""
        response = await client.get(
            "/api/v1/institutions/search/filtered",
            params={
                "has_cost_data": True,
                "min_completeness": 0,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for inst in data:
            # Should have at least one tuition field
            assert (
                inst.get("tuition_in_state") is not None
                or inst.get("tuition_out_of_state") is not None
                or inst.get("tuition_private") is not None
            )

    @pytest.mark.asyncio
    async def test_get_completeness_statistics(self, client: AsyncClient):
        """Test GET /api/v1/institutions/stats/completeness"""
        response = await client.get("/api/v1/institutions/stats/completeness")
        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "total_institutions" in data
        assert "tiers" in data
        assert "data_sources" in data
        assert isinstance(data["tiers"], list)
        assert isinstance(data["data_sources"], dict)

        # Verify tier data
        for tier in data["tiers"]:
            assert "tier" in tier
            assert "count" in tier
            assert "percentage" in tier
            assert "avg_score" in tier
            assert isinstance(tier["count"], int)
            assert isinstance(tier["percentage"], (int, float))
            assert 0 <= tier["avg_score"] <= 100

    @pytest.mark.asyncio
    async def test_get_featured_institutions(
        self, client: AsyncClient, test_institution, db_session
    ):
        """Test GET /api/v1/institutions/featured/list"""
        # First, make test institution featured
        test_institution.is_featured = True
        test_institution.data_completeness_score = 75  # Above 70 threshold
        db_session.add(test_institution)
        await db_session.commit()

        response = await client.get(
            "/api/v1/institutions/featured/list",
            params={"limit": 10},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

        # All should be featured and have good scores
        for inst in data:
            assert inst["is_featured"] is True
            assert inst["data_completeness_score"] >= 70

    @pytest.mark.asyncio
    async def test_get_state_summary(self, client: AsyncClient, test_institution):
        """Test GET /api/v1/institutions/by-state/{state}/summary"""
        response = await client.get(
            f"/api/v1/institutions/by-state/{test_institution.state}/summary",
            params={"min_completeness": 0},  # Get all for testing
        )
        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert data["state"] == test_institution.state
        assert "total_count" in data
        assert isinstance(data["total_count"], int)

        if data["total_count"] > 0:
            assert "avg_completeness_score" in data
            assert "statistics" in data
            assert "institutions" in data
            assert isinstance(data["institutions"], list)

            # Verify statistics
            stats = data["statistics"]
            assert "with_cost_data" in stats
            assert "with_admissions_data" in stats

    @pytest.mark.asyncio
    async def test_get_state_summary_invalid_state(self, client: AsyncClient):
        """Test state summary with invalid state code"""
        response = await client.get(
            "/api/v1/institutions/by-state/ZZ/summary",
            params={"min_completeness": 0},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert "message" in data

    @pytest.mark.asyncio
    async def test_test_fields_endpoint(self, client: AsyncClient, test_institution):
        """Test GET /api/v1/institutions/test/fields/{ipeds_id}"""
        response = await client.get(
            f"/api/v1/institutions/test/fields/{test_institution.ipeds_id}"
        )
        assert response.status_code == 200
        data = response.json()

        # Verify all sections exist
        assert "basic_info" in data
        assert "data_tracking" in data
        assert "cost_data" in data
        assert "admissions_data" in data

        # Verify basic info
        basic = data["basic_info"]
        assert basic["ipeds_id"] == test_institution.ipeds_id
        assert basic["name"] == test_institution.name
        assert basic["state"] == test_institution.state

    @pytest.mark.asyncio
    async def test_test_fields_not_found(self, client: AsyncClient):
        """Test test/fields endpoint with invalid IPEDS ID"""
        response = await client.get("/api/v1/institutions/test/fields/999999999")
        assert response.status_code == 404


@pytest.mark.integration
class TestIPEDSPagination:
    """Test pagination on IPEDS endpoints"""

    @pytest.mark.asyncio
    async def test_filtered_search_pagination(self, client: AsyncClient):
        """Test pagination on filtered search"""
        # Get first page
        response1 = await client.get(
            "/api/v1/institutions/search/filtered",
            params={
                "min_completeness": 0,
                "limit": 5,
                "offset": 0,
            },
        )
        assert response1.status_code == 200
        data1 = response1.json()

        # Get second page
        response2 = await client.get(
            "/api/v1/institutions/search/filtered",
            params={
                "min_completeness": 0,
                "limit": 5,
                "offset": 5,
            },
        )
        assert response2.status_code == 200
        data2 = response2.json()

        # Pages should be different (if enough data exists)
        if len(data1) > 0 and len(data2) > 0:
            assert data1[0]["id"] != data2[0]["id"]

    @pytest.mark.asyncio
    async def test_featured_list_limit(self, client: AsyncClient):
        """Test featured list respects limit parameter"""
        response = await client.get(
            "/api/v1/institutions/featured/list",
            params={"limit": 3},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3
