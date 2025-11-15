"""
Complete integration test suite for CampusConnect API
Tests all endpoints and generates documentation for frontend developers
"""
import pytest
import httpx
from datetime import datetime
import json
import asyncio

BASE_URL = "http://localhost:8000"

class TestPublicEndpoints:
    """Test public (unauthenticated) endpoints"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self):
        """Test API root returns metadata"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/")
            assert response.status_code == 200
            data = response.json()
            assert data["version"] == "1.0.0"
            assert "endpoints" in data
            print("\n✅ Root endpoint working")
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test health check endpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health")
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"
            print("✅ Health check working")
    
    @pytest.mark.asyncio
    async def test_get_institutions(self):
        """Test getting all institutions"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/institutions?limit=10")
            assert response.status_code == 200
            institutions = response.json()
            assert len(institutions) > 0
            assert "name" in institutions[0]
            assert "state" in institutions[0]
            print(f"✅ Got {len(institutions)} institutions")
            
            # Save sample for frontend docs
            with open("tests/sample_institution.json", "w") as f:
                json.dump(institutions[0], f, indent=2)
    
    @pytest.mark.asyncio
    async def test_get_institutions_by_state(self):
        """Test filtering institutions by state"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/institutions?state=NH")
            assert response.status_code == 200
            institutions = response.json()
            for inst in institutions:
                assert inst["state"] == "NH"
            print(f"✅ NH filter working - {len(institutions)} institutions")
    
    @pytest.mark.asyncio
    async def test_get_single_institution(self):
        """Test getting single institution by IPEDS ID"""
        async with httpx.AsyncClient() as client:
            # First get a valid IPEDS ID
            response = await client.get(f"{BASE_URL}/api/v1/institutions?limit=1")
            ipeds_id = response.json()[0]["ipeds_id"]
            
            # Get specific institution
            response = await client.get(f"{BASE_URL}/api/v1/institutions/{ipeds_id}")
            assert response.status_code == 200
            institution = response.json()
            assert institution["ipeds_id"] == ipeds_id
            print(f"✅ Got institution: {institution['name']}")
    
    @pytest.mark.asyncio
    async def test_institution_not_found(self):
        """Test 404 for non-existent institution"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/institutions/999999999")
            assert response.status_code == 404
            print("✅ 404 handling working")
    
    @pytest.mark.asyncio
    async def test_get_scholarships(self):
        """Test getting all scholarships"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/scholarships?limit=10")
            assert response.status_code == 200
            scholarships = response.json()
            assert len(scholarships) > 0
            print(f"✅ Got {len(scholarships)} scholarships")
            
            # Save sample for frontend docs
            with open("tests/sample_scholarship.json", "w") as f:
                json.dump(scholarships[0], f, indent=2)


class TestAdminAuthentication:
    """Test admin authentication flow"""
    
    @pytest.mark.asyncio
    async def test_admin_registration(self):
        """Test admin registration"""
        await asyncio.sleep(1)  # Rate limit delay
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/register",
                json={
                    "email": f"test_{int(datetime.now().timestamp())}@test.com",
                    "password": "test123456",
                    "entity_type": "institution",
                    "entity_id": 1
                }
            )
            assert response.status_code == 200
            user = response.json()
            assert "email" in user
            assert user["entity_type"] == "institution"
            print(f"✅ Admin registered: {user['email']}")
    
    @pytest.mark.asyncio
    async def test_admin_login(self):
        """Test admin login and token generation"""
        await asyncio.sleep(1)  # Rate limit delay
        async with httpx.AsyncClient() as client:
            # Use existing test account
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            print("✅ Login successful, token received")
            
            # Save token for other tests
            return data["access_token"]
    
    @pytest.mark.asyncio
    async def test_get_current_user(self):
        """Test getting current user info"""
        await asyncio.sleep(1)  # Rate limit delay
        token = await self.test_admin_login()
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/auth/me",
                headers=headers
            )
            assert response.status_code == 200
            user = response.json()
            assert "email" in user
            print(f"✅ Current user: {user['email']}")


class TestAdminProfile:
    """Test admin profile management"""
    
    async def get_auth_token(self):
        """Helper to get auth token"""
        await asyncio.sleep(1)  # Rate limit delay
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"}
            )
            if response.status_code != 200:
                print(f"Login failed: {response.text}")
                return None
            return response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_get_admin_entity(self):
        """Test getting admin's entity (institution/scholarship)"""
        token = await self.get_auth_token()
        assert token is not None
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/profile/entity",
                headers=headers
            )
            assert response.status_code == 200
            entity = response.json()
            assert "name" in entity or "title" in entity
            print(f"✅ Got admin entity")
    
    @pytest.mark.asyncio
    async def test_get_display_settings(self):
        """Test getting display settings"""
        token = await self.get_auth_token()
        assert token is not None
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/profile/display-settings",
                headers=headers
            )
            assert response.status_code == 200
            settings = response.json()
            assert "show_stats" in settings
            print("✅ Got display settings")
            
            # Save sample for frontend docs
            with open("tests/sample_display_settings.json", "w") as f:
                json.dump(settings, f, indent=2)
    
    @pytest.mark.asyncio
    async def test_update_display_settings(self):
        """Test updating display settings"""
        token = await self.get_auth_token()
        assert token is not None
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Update settings
            response = await client.put(
                f"{BASE_URL}/api/v1/admin/profile/display-settings",
                headers=headers,
                json={
                    "custom_tagline": "Test Integration Tagline",
                    "show_image_gallery": True
                }
            )
            assert response.status_code == 200
            updated = response.json()
            assert updated["custom_tagline"] == "Test Integration Tagline"
            assert updated["show_image_gallery"] == True
            print("✅ Display settings updated")


class TestSubscriptions:
    """Test subscription/payment flow"""
    
    async def get_auth_token(self):
        """Helper to get auth token"""
        await asyncio.sleep(2)  # Longer delay for subscription tests
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"}
            )
            if response.status_code != 200:
                print(f"Login failed: {response.text}")
                return None
            return response.json()["access_token"]
    
    @pytest.mark.asyncio
    async def test_create_checkout_session(self):
        """Test creating Stripe checkout session"""
        token = await self.get_auth_token()
        assert token is not None, "Failed to get auth token"
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/subscriptions/create-checkout",
                headers=headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "checkout_url" in data
            assert data["checkout_url"].startswith("https://checkout.stripe.com")
            print(f"✅ Checkout session created")
            print(f"   URL: {data['checkout_url'][:50]}...")
    
    @pytest.mark.asyncio
    async def test_get_current_subscription(self):
        """Test getting current subscription status"""
        token = await self.get_auth_token()
        assert token is not None, "Failed to get auth token"
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/subscriptions/current",
                headers=headers
            )
            assert response.status_code == 200
            subscription = response.json()
            assert "status" in subscription
            print(f"✅ Subscription status: {subscription['status']}")


class TestErrorHandling:
    """Test error handling and validation"""
    
    @pytest.mark.asyncio
    async def test_validation_error(self):
        """Test validation error handling"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/register",
                json={
                    "email": "not-an-email",  # Invalid email
                    "password": "test"
                }
            )
            assert response.status_code == 422
            print("✅ Validation error handling working")
    
    @pytest.mark.asyncio
    async def test_unauthorized_access(self):
        """Test accessing protected endpoint without auth"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/profile/entity"
            )
            assert response.status_code == 401
            print("✅ Unauthorized access blocked")
    
    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """Test accessing with invalid token"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": "Bearer invalid_token_123"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/profile/entity",
                headers=headers
            )
            assert response.status_code == 401
            print("✅ Invalid token rejected")


# Run all tests with: pytest tests/test_integration.py -v -s
