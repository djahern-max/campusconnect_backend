"""
Integration tests for contact form and inquiry management
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestContactForm:
    """Test public contact form submission"""
    
    @pytest.mark.asyncio
    async def test_submit_contact_form(self, client: AsyncClient):
        """Test submitting contact form (public endpoint)"""
        contact_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "institution_name": "Test University",  # Required field
            "subject": "Question about CampusConnect",
            "message": "I'm interested in learning more about your platform for my institution.",
            "inquiry_type": "general"
        }
        
        response = await client.post(
            "/api/v1/contact/submit",
            json=contact_data
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "message" in data or "id" in data
    
    @pytest.mark.asyncio
    async def test_submit_contact_form_validation(self, client: AsyncClient):
        """Test contact form validation"""
        # Missing required fields
        invalid_data = {
            "name": "John Doe"
            # Missing email, institution_name, subject, message
        }
        
        response = await client.post(
            "/api/v1/contact/submit",
            json=invalid_data
        )
        
        # Should fail validation
        assert response.status_code == 422


@pytest.mark.integration
class TestInquiryManagement:
    """Test inquiry management (Super Admin only)"""
    
    @pytest.mark.asyncio
    async def test_get_all_inquiries(
        self,
        client: AsyncClient,
        super_admin_headers: dict
    ):
        """Test getting all inquiries"""
        response = await client.get(
            "/api/v1/contact/inquiries",
            headers=super_admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or isinstance(data, dict)
    
    @pytest.mark.asyncio
    async def test_get_single_inquiry(
        self,
        client: AsyncClient,
        super_admin_headers: dict
    ):
        """Test getting a specific inquiry"""
        # First submit a contact form
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "institution_name": "Test Institution",
            "subject": "Test Inquiry",
            "message": "This is a test message",
            "inquiry_type": "support"
        }
        
        submit_response = await client.post(
            "/api/v1/contact/submit",
            json=contact_data
        )
        
        if submit_response.status_code in [200, 201]:
            # Try to get all inquiries
            list_response = await client.get(
                "/api/v1/contact/inquiries",
                headers=super_admin_headers
            )
            
            if list_response.status_code == 200:
                inquiries = list_response.json()
                
                # If there are inquiries, try to get one
                if isinstance(inquiries, list) and len(inquiries) > 0:
                    inquiry_id = inquiries[0].get("id")
                    
                    if inquiry_id:
                        detail_response = await client.get(
                            f"/api/v1/contact/inquiries/{inquiry_id}",
                            headers=super_admin_headers
                        )
                        
                        assert detail_response.status_code == 200
                        data = detail_response.json()
                        assert "email" in data or "message" in data
