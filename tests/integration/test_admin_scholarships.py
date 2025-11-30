"""
Integration tests for admin scholarship management endpoints.

Tests cover:
- CRUD operations (create, update, delete)
- Verification and featuring
- Bulk status updates
- Admin dashboard and statistics
- Advanced search and filtering
"""

import pytest
from fastapi import status
from datetime import date, datetime, timedelta


class TestScholarshipCRUD:
    """Test create, read, update, delete operations for scholarships"""

    async def test_create_scholarship(self, client, admin_token):
        """Test creating a new scholarship with valid data"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        scholarship_data = {
            "title": "STEM Excellence Scholarship",
            "organization": "Tech Foundation",
            "scholarship_type": "STEM",
            "status": "ACTIVE",
            "difficulty_level": "MODERATE",
            "amount_min": 5000,
            "amount_max": 10000,
            "is_renewable": True,
            "number_of_awards": 10,
            "deadline": "2025-06-01",
            "application_opens": "2025-01-01",
            "for_academic_year": "2025-2026",
            "description": "For outstanding STEM students",
            "website_url": "https://example.com/scholarship",
            "min_gpa": 3.5,
            "verified": False,
            "featured": False
        }
        
        response = await client.post(
            "/api/v1/admin/scholarships",
            json=scholarship_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["title"] == scholarship_data["title"]
        assert data["organization"] == scholarship_data["organization"]
        assert data["amount_min"] == scholarship_data["amount_min"]
        assert data["amount_max"] == scholarship_data["amount_max"]
        assert data["min_gpa"] == scholarship_data["min_gpa"]
        assert "id" in data
        assert "created_at" in data

    async def test_create_scholarship_invalid_amounts(self, client, admin_token):
        """Test that creating a scholarship with amount_max < amount_min fails"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        scholarship_data = {
            "title": "Invalid Scholarship",
            "organization": "Test Org",
            "scholarship_type": "ACADEMIC",
            "amount_min": 10000,  # Max is less than min - should fail
            "amount_max": 5000,
        }
        
        response = await client.post(
            "/api/v1/admin/scholarships",
            json=scholarship_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "amount_max must be greater than or equal to amount_min" in response.json()["detail"]

    async def test_create_scholarship_minimum_required_fields(self, client, admin_token):
        """Test creating a scholarship with only required fields"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        scholarship_data = {
            "title": "Minimal Scholarship",
            "organization": "Basic Org",
            "scholarship_type": "ACADEMIC_MERIT",
            "amount_min": 1000,
            "amount_max": 1000,
        }
        
        response = await client.post(
            "/api/v1/admin/scholarships",
            json=scholarship_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == scholarship_data["title"]

    async def test_update_scholarship(self, client, admin_token):
        """Test updating an existing scholarship"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # First create a scholarship
        create_data = {
            "title": "Original Title",
            "organization": "Original Org",
            "scholarship_type": "STEM",
            "amount_min": 5000,
            "amount_max": 10000,
        }
        
        create_response = await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        scholarship_id = create_response.json()["id"]
        
        # Now update it
        update_data = {
            "title": "Updated Title",
            "organization": "Updated Org",
            "amount_max": 15000,
            "description": "Updated description"
        }
        
        response = await client.patch(
            f"/api/v1/admin/scholarships/{scholarship_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["organization"] == update_data["organization"]
        assert data["amount_max"] == update_data["amount_max"]
        assert data["description"] == update_data["description"]
        assert data["amount_min"] == 5000  # Unchanged

    async def test_update_scholarship_invalid_amounts(self, client, admin_token):
        """Test that updating amounts with amount_max < amount_min fails"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create scholarship
        create_data = {
            "title": "Test Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 5000,
            "amount_max": 10000,
        }
        
        create_response = await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        scholarship_id = create_response.json()["id"]
        
        # Try to update with invalid amounts
        update_data = {
            "amount_min": 15000,  # Higher than current max of 10000
        }
        
        response = await client.patch(
            f"/api/v1/admin/scholarships/{scholarship_id}",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_update_nonexistent_scholarship(self, client, admin_token):
        """Test updating a scholarship that doesn't exist returns 404"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        update_data = {"title": "Updated Title"}
        
        response = await client.patch(
            "/api/v1/admin/scholarships/999999",
            json=update_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    async def test_delete_scholarship(self, client, admin_token):
        """Test deleting a scholarship"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create scholarship
        create_data = {
            "title": "To Be Deleted",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 1000,
            "amount_max": 2000,
        }
        
        create_response = await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        scholarship_id = create_response.json()["id"]
        
        # Delete it
        response = await client.delete(
            f"/api/v1/admin/scholarships/{scholarship_id}",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify it's gone
        get_response = await client.get(f"/api/v1/scholarships/{scholarship_id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_nonexistent_scholarship(self, client, admin_token):
        """Test deleting a non-existent scholarship returns 404"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.delete(
            "/api/v1/admin/scholarships/999999",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestScholarshipVerificationAndFeaturing:
    """Test verification and featuring functionality"""

    async def test_verify_scholarship(self, client, admin_token):
        """Test marking a scholarship as verified"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create scholarship
        create_data = {
            "title": "Unverified Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 1000,
            "amount_max": 2000,
            "verified": False
        }
        
        create_response = await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        scholarship_id = create_response.json()["id"]
        
        # Verify it
        verify_data = {"verified": True}
        
        response = await client.patch(
            f"/api/v1/admin/scholarships/{scholarship_id}/verify",
            json=verify_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["verified"] is True

    async def test_unverify_scholarship(self, client, admin_token):
        """Test removing verification from a scholarship"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create verified scholarship
        create_data = {
            "title": "Verified Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 1000,
            "amount_max": 2000,
            "verified": True
        }
        
        create_response = await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        scholarship_id = create_response.json()["id"]
        
        # Unverify it
        verify_data = {"verified": False}
        
        response = await client.patch(
            f"/api/v1/admin/scholarships/{scholarship_id}/verify",
            json=verify_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["verified"] is False

    async def test_verify_nonexistent_scholarship(self, client, admin_token):
        """Test verifying a non-existent scholarship returns 404"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        verify_data = {"verified": True}
        
        response = await client.patch(
            "/api/v1/admin/scholarships/999999/verify",
            json=verify_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_feature_scholarship(self, client, admin_token):
        """Test marking a scholarship as featured"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create scholarship
        create_data = {
            "title": "Regular Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 1000,
            "amount_max": 2000,
            "featured": False
        }
        
        create_response = await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        scholarship_id = create_response.json()["id"]
        
        # Feature it
        feature_data = {"featured": True}
        
        response = await client.patch(
            f"/api/v1/admin/scholarships/{scholarship_id}/feature",
            json=feature_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["featured"] is True

    async def test_unfeature_scholarship(self, client, admin_token):
        """Test removing featured status from a scholarship"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create featured scholarship
        create_data = {
            "title": "Featured Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 1000,
            "amount_max": 2000,
            "featured": True
        }
        
        create_response = await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        scholarship_id = create_response.json()["id"]
        
        # Unfeature it
        feature_data = {"featured": False}
        
        response = await client.patch(
            f"/api/v1/admin/scholarships/{scholarship_id}/feature",
            json=feature_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["featured"] is False


class TestBulkOperations:
    """Test bulk status update operations"""

    async def test_bulk_status_update(self, client, admin_token):
        """Test updating status for multiple scholarships at once"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create multiple scholarships
        scholarship_ids = []
        for i in range(3):
            create_data = {
                "title": f"Bulk Test Scholarship {i}",
                "organization": "Test Org",
                "scholarship_type": "STEM",
                "amount_min": 1000,
                "amount_max": 2000,
                "status": "ACTIVE"
            }
            
            create_response = await client.post(
                "/api/v1/admin/scholarships",
                json=create_data,
                headers=headers
            )
            scholarship_ids.append(create_response.json()["id"])
        
        # Bulk update to EXPIRED
        bulk_data = {
            "scholarship_ids": scholarship_ids,
            "status": "EXPIRED"
        }
        
        response = await client.post(
            "/api/v1/admin/scholarships/bulk-status-update",
            json=bulk_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["updated_count"] == 3
        assert data["new_status"] == "EXPIRED"
        assert len(data["scholarship_ids"]) == 3

    async def test_bulk_update_invalid_status(self, client, admin_token):
        """Test bulk update with invalid status fails"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        bulk_data = {
            "scholarship_ids": [1, 2, 3],
            "status": "INVALID_STATUS"
        }
        
        response = await client.post(
            "/api/v1/admin/scholarships/bulk-status-update",
            json=bulk_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "must be one of" in response.json()["detail"]

    async def test_bulk_update_too_many_scholarships(self, client, admin_token):
        """Test that bulk updating more than 100 scholarships fails"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Try to update 101 scholarships
        bulk_data = {
            "scholarship_ids": list(range(1, 102)),  # 101 IDs
            "status": "INACTIVE"
        }
        
        response = await client.post(
            "/api/v1/admin/scholarships/bulk-status-update",
            json=bulk_data,
            headers=headers
        )
        
        assert response.status_code == 422

        assert response.status_code == 422
        # Response has validation error for exceeding max items
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        bulk_data = {
            "scholarship_ids": [999998, 999999],
            "status": "INACTIVE"
        }
        
        response = await client.post(
            "/api/v1/admin/scholarships/bulk-status-update",
            json=bulk_data,
            headers=headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestAdminDashboard:
    """Test admin dashboard and statistics endpoints"""

    async def test_get_scholarship_statistics(self, client, admin_token):
        """Test getting scholarship statistics for admin dashboard"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a few scholarships with different properties
        scholarships_data = [
            {
                "title": "Active Verified STEM",
                "organization": "Test Org",
                "scholarship_type": "STEM",
                "amount_min": 5000,
                "amount_max": 10000,
                "status": "ACTIVE",
                "verified": True,
                "featured": True
            },
            {
                "title": "Active Unverified Arts",
                "organization": "Test Org",
                "scholarship_type": "ARTS",
                "amount_min": 3000,
                "amount_max": 5000,
                "status": "ACTIVE",
                "verified": False,
                "featured": False
            },
            {
                "title": "Inactive Scholarship",
                "organization": "Test Org",
                "scholarship_type": "STEM",
                "amount_min": 1000,
                "amount_max": 2000,
                "status": "INACTIVE",
                "verified": False,
                "featured": False
            }
        ]
        
        for scholarship_data in scholarships_data:
            await client.post(
                "/api/v1/admin/scholarships",
                json=scholarship_data,
                headers=headers
            )
        
        # Get statistics
        response = await client.get(
            "/api/v1/admin/scholarships/stats/overview",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "summary" in data
        assert "total_scholarships" in data["summary"]
        assert "active_scholarships" in data["summary"]
        assert "verified_scholarships" in data["summary"]
        assert "featured_scholarships" in data["summary"]
        assert "total_amount_available" in data["summary"]
        assert "verification_rate" in data["summary"]
        
        assert "by_type" in data
        assert isinstance(data["by_type"], list)

    async def test_get_scholarships_needing_review(self, client, admin_token):
        """Test getting scholarships that need admin review"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create an unverified scholarship
        create_data = {
            "title": "Needs Review",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 1000,
            "amount_max": 2000,
            "verified": False
        }
        
        await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        
        # Get unverified scholarships
        response = await client.get(
            "/api/v1/admin/scholarships/needs-review?verified=false",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "filters" in data
        assert "count" in data
        assert "scholarships" in data
        assert isinstance(data["scholarships"], list)

    async def test_get_expired_scholarships(self, client, admin_token):
        """Test getting expired scholarships"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create an expired scholarship
        past_date = (date.today() - timedelta(days=30)).isoformat()
        
        create_data = {
            "title": "Expired Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 1000,
            "amount_max": 2000,
            "deadline": past_date
        }
        
        await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        
        # Get expired scholarships
        response = await client.get(
            "/api/v1/admin/scholarships/needs-review?expired=true",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["filters"]["expired"] is True
        assert "scholarships" in data

    async def test_get_recent_scholarships(self, client, admin_token):
        """Test getting recently created or updated scholarships"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a scholarship
        create_data = {
            "title": "Recent Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 1000,
            "amount_max": 2000,
        }
        
        await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        
        # Get recent scholarships (last 7 days by default)
        response = await client.get(
            "/api/v1/admin/scholarships/recent",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "lookback_days" in data
        assert "count" in data
        assert "scholarships" in data
        assert isinstance(data["scholarships"], list)

    async def test_get_recent_scholarships_custom_days(self, client, admin_token):
        """Test getting recent scholarships with custom lookback period"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.get(
            "/api/v1/admin/scholarships/recent?days=30&limit=50",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert data["lookback_days"] == 30


class TestAdminSearch:
    """Test advanced admin search functionality"""

    async def test_admin_search_scholarships(self, client, admin_token):
        """Test basic admin scholarship search"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create a searchable scholarship
        create_data = {
            "title": "Searchable STEM Award",
            "organization": "Search Test Org",
            "scholarship_type": "STEM",
            "amount_min": 5000,
            "amount_max": 10000,
        }
        
        await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        
        # Search for it
        response = await client.get(
            "/api/v1/admin/scholarships/search?query_text=Searchable",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_admin_search_with_filters(self, client, admin_token):
        """Test admin search with multiple filters"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create scholarships with different attributes
        create_data = {
            "title": "STEM Verified Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 5000,
            "amount_max": 10000,
            "verified": True,
            "featured": True,
            "status": "ACTIVE"
        }
        
        await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        
        # Search with filters
        response = await client.get(
            "/api/v1/admin/scholarships/search?scholarship_type=STEM&verified=true&featured=true",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_admin_search_by_amount_range(self, client, admin_token):
        """Test searching scholarships by amount range"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        # Create scholarship in specific amount range
        create_data = {
            "title": "Medium Amount Scholarship",
            "organization": "Test Org",
            "scholarship_type": "STEM",
            "amount_min": 5000,
            "amount_max": 7500,
        }
        
        await client.post(
            "/api/v1/admin/scholarships",
            json=create_data,
            headers=headers
        )
        
        # Search for scholarships in amount range
        response = await client.get(
            "/api/v1/admin/scholarships/search?min_amount=4000&max_amount=8000",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    async def test_admin_search_pagination(self, client, admin_token):
        """Test search with pagination parameters"""
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        response = await client.get(
            "/api/v1/admin/scholarships/search?limit=10&offset=0",
            headers=headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 10
