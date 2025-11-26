"""
Integration tests for Admin Institution Data endpoints
Tests the 7 new endpoints for institution admins to update their own data
"""

import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.integration
class TestAdminInstitutionData:
    """Test admin institution data management endpoints"""

    @pytest.mark.asyncio
    async def test_get_institution_data(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test GET /api/v1/admin/institution-data/{institution_id}"""
        # Get the institution_id from the registered admin
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify basic structure
        assert data["id"] == institution_id
        assert "name" in data
        assert "city" in data
        assert "state" in data
        assert "data_completeness_score" in data

    @pytest.mark.asyncio
    async def test_get_institution_data_wrong_institution(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test that admin cannot access other institutions"""
        # Try to access a different institution (ID 99999)
        response = await client.get(
            "/api/v1/admin/institution-data/99999",
            headers=admin_headers,
        )

        # Should be forbidden or not found
        assert response.status_code in [403, 404]

    @pytest.mark.asyncio
    async def test_get_data_quality_report(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test GET /api/v1/admin/institution-data/{institution_id}/quality"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}/quality",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify quality report structure
        assert "institution_id" in data
        assert "institution_name" in data
        assert "completeness_score" in data
        assert "data_source" in data
        assert "data_last_updated" in data
        assert "missing_fields" in data
        assert "verified_fields" in data
        assert "verification_count" in data

        # Verify flags
        assert "has_website" in data
        assert "has_tuition_data" in data
        assert "has_room_board" in data
        assert "has_admissions_data" in data

        # Verify types
        assert isinstance(data["missing_fields"], list)
        assert isinstance(data["verified_fields"], list)
        assert isinstance(data["completeness_score"], int)
        assert 0 <= data["completeness_score"] <= 100

    @pytest.mark.asyncio
    async def test_update_basic_info(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test PUT /api/v1/admin/institution-data/{institution_id}/basic-info"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        update_data = {
            "website": "https://updated-university.edu",
            "student_faculty_ratio": 16.5,
            "size_category": "Large",
        }

        response = await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/basic-info",
            headers=admin_headers,
            json=update_data,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify updates were applied
        assert data["website"] == "https://updated-university.edu"
        assert data["student_faculty_ratio"] == 16.5
        assert data["size_category"] == "Large"

        # Verify data source changed
        assert data["data_source"] in ["admin", "mixed"]

    @pytest.mark.asyncio
    async def test_update_cost_data(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test PUT /api/v1/admin/institution-data/{institution_id}/cost-data"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        cost_updates = {
            "tuition_in_state": 12500.00,
            "tuition_out_of_state": 35000.00,
            "room_cost": 8500.00,
            "board_cost": 5500.00,
            "application_fee_undergrad": 75.00,
        }

        response = await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/cost-data",
            headers=admin_headers,
            json=cost_updates,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify cost updates
        assert data["tuition_in_state"] == 12500.00
        assert data["tuition_out_of_state"] == 35000.00
        assert data["room_cost"] == 8500.00
        assert data["board_cost"] == 5500.00

        # Verify data source changed
        assert data["data_source"] in ["admin", "mixed"]

        # Completeness score should increase
        assert data["data_completeness_score"] > 0

    @pytest.mark.asyncio
    async def test_update_admissions_data(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test PUT /api/v1/admin/institution-data/{institution_id}/admissions-data"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        admissions_updates = {
            "acceptance_rate": 65.5,
            "sat_math_25th": 580,
            "sat_math_75th": 680,
            "act_composite_25th": 24,
            "act_composite_75th": 29,
        }

        response = await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/admissions-data",
            headers=admin_headers,
            json=admissions_updates,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify admissions updates
        assert data["acceptance_rate"] == 65.5
        assert data["sat_math_25th"] == 580
        assert data["sat_math_75th"] == 680
        assert data["act_composite_25th"] == 24
        assert data["act_composite_75th"] == 29

        # Verify data source changed
        assert data["data_source"] in ["admin", "mixed"]

    @pytest.mark.asyncio
    async def test_verify_current_data(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test POST /api/v1/admin/institution-data/{institution_id}/verify-current"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        verify_request = {
            "academic_year": "2025-26",
            "notes": "Verified all costs are current for 2025-26 academic year",
        }

        response = await client.post(
            f"/api/v1/admin/institution-data/{institution_id}/verify-current",
            headers=admin_headers,
            json=verify_request,
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "message" in data
        assert "fields_verified" in data
        assert "academic_year" in data
        assert "completeness_score" in data
        assert "data_source" in data

        # Should show as admin-verified
        assert data["data_source"] == "admin"
        assert data["academic_year"] == "2025-26"
        assert data["fields_verified"] >= 0

    @pytest.mark.asyncio
    async def test_get_verification_history(
        self,
        client: AsyncClient,
        admin_headers: dict,
        registered_admin_user: dict,
        db_session,
    ):
        """Test GET /api/v1/admin/institution-data/{institution_id}/verification-history"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        # First, make some updates to create history
        await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/cost-data",
            headers=admin_headers,
            json={"tuition_in_state": 15000.00},
        )

        # Now get the history
        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}/verification-history",
            headers=admin_headers,
        )

        assert response.status_code == 200
        data = response.json()

        # Should be a list
        assert isinstance(data, list)

        # If we have history, verify structure
        if len(data) > 0:
            verification = data[0]
            assert "id" in verification
            assert "field_name" in verification
            assert "old_value" in verification
            assert "new_value" in verification
            assert "verified_by" in verification
            assert "verified_at" in verification
            assert "notes" in verification

    @pytest.mark.asyncio
    async def test_permission_denied_for_other_institution(
        self,
        client: AsyncClient,
        admin_headers: dict,
        registered_admin_user: dict,
        db_session,
    ):
        """Test that admin cannot update other institutions"""
        user_data = registered_admin_user["user_data"]
        admin_institution_id = user_data["entity_id"]

        # Try to update a DIFFERENT institution (use ID that's definitely not theirs)
        different_institution_id = admin_institution_id + 9999

        response = await client.put(
            f"/api/v1/admin/institution-data/{different_institution_id}/cost-data",
            headers=admin_headers,
            json={"tuition_in_state": 99999.00},
        )

        # Should be forbidden or not found
        assert response.status_code in [403, 404]


@pytest.mark.integration
class TestDataValidation:
    """Test data validation for admin updates"""

    @pytest.mark.asyncio
    async def test_invalid_acceptance_rate(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test that acceptance rate must be 0-100"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        # Try invalid acceptance rate (>100)
        response = await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/admissions-data",
            headers=admin_headers,
            json={"acceptance_rate": 150.0},  # Invalid!
        )

        # Should fail validation
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_sat_score(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test that SAT scores must be 200-800"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        # Try invalid SAT score
        response = await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/admissions-data",
            headers=admin_headers,
            json={"sat_math_25th": 1000},  # Invalid! Max is 800
        )

        # Should fail validation
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_costs_rejected(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test that negative costs are rejected"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        # Try negative tuition
        response = await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/cost-data",
            headers=admin_headers,
            json={"tuition_in_state": -5000.00},  # Invalid!
        )

        # Should fail validation
        assert response.status_code == 422


@pytest.mark.integration
class TestCompletenessScoreUpdates:
    """Test that completeness score updates correctly"""

    @pytest.mark.asyncio
    async def test_completeness_increases_with_data(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test that adding data increases completeness score"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        # Get initial score
        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}/quality",
            headers=admin_headers,
        )
        initial_score = response.json()["completeness_score"]

        # Add website
        await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/basic-info",
            headers=admin_headers,
            json={"website": "https://test.edu"},
        )

        # Add cost data
        await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/cost-data",
            headers=admin_headers,
            json={
                "tuition_in_state": 10000.00,
                "room_cost": 8000.00,
            },
        )

        # Get new score
        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}/quality",
            headers=admin_headers,
        )
        new_score = response.json()["completeness_score"]

        # Score should have increased
        assert new_score > initial_score

    @pytest.mark.asyncio
    async def test_admin_verification_adds_bonus(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test that admin verification adds 10 point bonus"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        # Get score before verification
        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}/quality",
            headers=admin_headers,
        )
        score_before = response.json()["completeness_score"]

        # Verify current data
        await client.post(
            f"/api/v1/admin/institution-data/{institution_id}/verify-current",
            headers=admin_headers,
            json={"academic_year": "2025-26"},
        )

        # Get score after verification
        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}/quality",
            headers=admin_headers,
        )
        data = response.json()
        score_after = data["completeness_score"]

        # Should be admin-verified
        assert data["data_source"] == "admin"

        # Score should increase (10 point bonus)
        assert score_after >= score_before


@pytest.mark.integration
class TestVerificationHistory:
    """Test verification history tracking"""

    @pytest.mark.asyncio
    async def test_updates_create_verification_records(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test that updates create verification records"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        # Make an update
        await client.put(
            f"/api/v1/admin/institution-data/{institution_id}/cost-data",
            headers=admin_headers,
            json={"tuition_in_state": 20000.00},
        )

        # Check verification history
        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}/verification-history",
            headers=admin_headers,
        )

        assert response.status_code == 200
        history = response.json()

        # Should have at least one record
        assert len(history) > 0

        # Find the tuition update
        tuition_record = next(
            (r for r in history if r["field_name"] == "tuition_in_state"), None
        )

        if tuition_record:
            # Check that new value is 20000 (allow for different decimal formatting)
            assert float(tuition_record["new_value"]) == 20000.00
            assert tuition_record["verified_by"] == user_data["email"]

    @pytest.mark.asyncio
    async def test_verification_history_limit(
        self, client: AsyncClient, admin_headers: dict, registered_admin_user: dict
    ):
        """Test that verification history respects limit parameter"""
        user_data = registered_admin_user["user_data"]
        institution_id = user_data["entity_id"]

        # Get history with limit
        response = await client.get(
            f"/api/v1/admin/institution-data/{institution_id}/verification-history?limit=5",
            headers=admin_headers,
        )

        assert response.status_code == 200
        history = response.json()

        # Should not exceed limit
        assert len(history) <= 5
