"""
Complete integration test suite for CampusConnect API - UPDATED FOR INVITATION SYSTEM
Tests all endpoints including new Super Admin invitation flow
"""

import pytest
import httpx
from datetime import datetime
import json
import asyncio

BASE_URL = "http://localhost:8000"

# Store created invitation codes for tests
INVITATION_CODES = {}


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


class TestSuperAdminInvitations:
    """Test Super Admin invitation code management"""

    async def get_super_admin_token(self):
        """Helper to get super admin token"""
        await asyncio.sleep(1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"},
            )
            if response.status_code != 200:
                print(f"Super admin login failed: {response.text}")
                return None
            return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_create_invitation_code(self):
        """Test creating an invitation code"""
        token = await self.get_super_admin_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/invitations",
                headers=headers,
                json={
                    "entity_type": "institution",
                    "entity_id": 2,  # Different from existing test user
                    "assigned_email": "newadmin@test.com",
                    "expires_in_days": 30,
                },
            )
            assert response.status_code == 200
            invitation = response.json()
            assert "code" in invitation
            assert invitation["status"] == "PENDING"
            assert invitation["entity_type"] == "institution"

            # Store for other tests
            INVITATION_CODES["test_registration"] = invitation["code"]
            print(f"✅ Invitation code created: {invitation['code']}")

    @pytest.mark.asyncio
    async def test_list_invitations(self):
        """Test listing invitation codes"""
        token = await self.get_super_admin_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/auth/invitations", headers=headers
            )
            assert response.status_code == 200
            invitations = response.json()
            assert isinstance(invitations, list)
            print(f"✅ Found {len(invitations)} invitation codes")

    @pytest.mark.asyncio
    async def test_validate_invitation_code(self):
        """Test validating an invitation code"""
        # First create a code
        token = await self.get_super_admin_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}

            # Create invitation
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/invitations",
                headers=headers,
                json={
                    "entity_type": "institution",
                    "entity_id": 3,
                    "expires_in_days": 30,
                },
            )
            assert response.status_code == 200
            invitation_code = response.json()["code"]

            # Validate it (no auth needed for validation)
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/validate-invitation",
                json={"code": invitation_code},
            )
            assert response.status_code == 200
            validation = response.json()
            assert validation["valid"] == True
            assert "entity_name" in validation
            print(f"✅ Invitation code validated: {validation['entity_name']}")


class TestAdminAuthentication:
    """Test admin authentication flow with invitation codes"""

    async def get_or_create_invitation_code(self):
        """Helper to get or create an invitation code for testing"""
        if "test_registration" in INVITATION_CODES:
            return INVITATION_CODES["test_registration"]

        # Create new invitation as super admin
        await asyncio.sleep(1)
        async with httpx.AsyncClient() as client:
            # Login as super admin
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"},
            )
            if response.status_code != 200:
                return None

            token = response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

            # Create invitation
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/invitations",
                headers=headers,
                json={
                    "entity_type": "institution",
                    "entity_id": 5,
                    "expires_in_days": 30,
                },
            )
            if response.status_code == 200:
                code = response.json()["code"]
                INVITATION_CODES["test_registration"] = code
                return code
            return None

    @pytest.mark.asyncio
    async def test_admin_registration(self):
        """Test admin registration with invitation code"""
        await asyncio.sleep(1)

        # Get an invitation code
        invitation_code = await self.get_or_create_invitation_code()
        assert invitation_code is not None, "Failed to get invitation code"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/register",
                json={
                    "email": f"test_{int(datetime.now().timestamp())}@test.com",
                    "password": "test123456",
                    "invitation_code": invitation_code,
                },
            )
            assert response.status_code == 200
            user = response.json()
            assert "email" in user
            assert "entity_type" in user
            print(f"✅ Admin registered: {user['email']}")

    @pytest.mark.asyncio
    async def test_admin_login(self):
        """Test admin login and token generation"""
        await asyncio.sleep(1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"},
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            print("✅ Login successful, token received")
            return data["access_token"]

    @pytest.mark.asyncio
    async def test_get_current_user(self):
        """Test getting current user info"""
        await asyncio.sleep(1)
        token = await self.test_admin_login()

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/auth/me", headers=headers
            )
            assert response.status_code == 200
            user = response.json()
            assert "email" in user
            assert "role" in user
            print(f"✅ Current user: {user['email']} (Role: {user['role']})")


class TestAdminProfile:
    """Test admin profile management"""

    async def get_auth_token(self):
        """Helper to get auth token"""
        await asyncio.sleep(1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"},
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
                f"{BASE_URL}/api/v1/admin/profile/entity", headers=headers
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
                f"{BASE_URL}/api/v1/admin/profile/display-settings", headers=headers
            )
            assert response.status_code == 200
            settings = response.json()
            assert "show_stats" in settings
            print("✅ Got display settings")

            with open("tests/sample_display_settings.json", "w") as f:
                json.dump(settings, f, indent=2)

    @pytest.mark.asyncio
    async def test_update_display_settings(self):
        """Test updating display settings"""
        token = await self.get_auth_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}

            response = await client.put(
                f"{BASE_URL}/api/v1/admin/profile/display-settings",
                headers=headers,
                json={
                    "custom_tagline": "Test Integration Tagline",
                    "show_image_gallery": True,
                },
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
        await asyncio.sleep(2)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"},
            )
            if response.status_code != 200:
                print(f"Login failed: {response.text}")
                return None
            return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_create_checkout_session(self):
        """Test creating Stripe checkout session"""
        token = await self.get_auth_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/subscriptions/create-checkout",
                headers=headers,
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
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/subscriptions/current", headers=headers
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
                    "email": "not-an-email",
                    "password": "test",
                    "invitation_code": "INVALID",
                },
            )
            assert response.status_code == 422
            print("✅ Validation error handling working")

    @pytest.mark.asyncio
    async def test_unauthorized_access(self):
        """Test accessing protected endpoint without auth"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/v1/admin/profile/entity")
            assert response.status_code == 401
            print("✅ Unauthorized access blocked")

    @pytest.mark.asyncio
    async def test_invalid_token(self):
        """Test accessing with invalid token"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": "Bearer invalid_token_123"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/profile/entity", headers=headers
            )
            assert response.status_code == 401
            print("✅ Invalid token rejected")


class TestGalleryManagement:
    """Test gallery management features (Phase 1)"""

    async def get_auth_token(self):
        """Helper to get auth token"""
        await asyncio.sleep(1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"},
            )
            if response.status_code != 200:
                print(f"Login failed: {response.text}")
                return None
            return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_upload_gallery_image(self):
        """Test uploading image to gallery"""
        token = await self.get_auth_token()
        assert token is not None

        try:
            from PIL import Image
            import io

            img = Image.new("RGB", (100, 100), color="red")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {"Authorization": f"Bearer {token}"}
                files = {"file": ("test.png", img_bytes, "image/png")}
                data = {"caption": "Test gallery image", "image_type": "campus"}

                response = await client.post(
                    f"{BASE_URL}/api/v1/admin/gallery",
                    headers=headers,
                    files=files,
                    data=data,
                )

                if response.status_code != 200:
                    print(f"Gallery upload failed: {response.text}")

                assert response.status_code == 200
                result = response.json()
                assert result["caption"] == "Test gallery image"
                print(f"✅ Gallery image uploaded: {result['filename']}")
        except ImportError:
            print("⚠️  PIL not available, skipping gallery upload test")
            pytest.skip("PIL not installed")

    @pytest.mark.asyncio
    async def test_get_gallery_images(self):
        """Test getting all gallery images"""
        token = await self.get_auth_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/gallery", headers=headers
            )

            if response.status_code != 200:
                print(f"Get gallery failed: {response.text}")

            assert response.status_code == 200
            images = response.json()
            assert isinstance(images, list)
            print(f"✅ Got {len(images)} gallery images")


class TestVideoManagement:
    """Test video management features (Phase 1)"""

    async def get_auth_token(self):
        """Helper to get auth token"""
        await asyncio.sleep(1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"},
            )
            if response.status_code != 200:
                return None
            return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_add_video(self):
        """Test adding a video embed"""
        token = await self.get_auth_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/videos",
                headers=headers,
                json={
                    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "title": "Campus Tour 2024",
                    "description": "Virtual tour of our campus",
                    "video_type": "campus_tour",
                },
            )

            if response.status_code != 200:
                print(f"Add video failed: {response.text}")

            assert response.status_code == 200
            video = response.json()
            assert video["title"] == "Campus Tour 2024"
            print(f"✅ Video added: {video['title']}")

    @pytest.mark.asyncio
    async def test_get_videos(self):
        """Test getting all videos"""
        token = await self.get_auth_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/videos", headers=headers
            )

            if response.status_code != 200:
                print(f"Get videos failed: {response.text}")

            assert response.status_code == 200
            videos = response.json()
            assert isinstance(videos, list)
            print(f"✅ Got {len(videos)} videos")


class TestExtendedInfo:
    """Test extended information features (Phase 1)"""

    async def get_auth_token(self):
        """Helper to get auth token"""
        await asyncio.sleep(1)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/admin/auth/login",
                data={"username": "admin@snhu.edu", "password": "test123"},
            )
            if response.status_code != 200:
                return None
            return response.json()["access_token"]

    @pytest.mark.asyncio
    async def test_update_extended_info(self):
        """Test updating extended information"""
        token = await self.get_auth_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.put(
                f"{BASE_URL}/api/v1/admin/extended-info",
                headers=headers,
                json={
                    "mission_statement": "Test mission statement",
                    "campus_life": "Test campus life description",
                    "athletics": "Test athletics info",
                },
            )

            if response.status_code != 200:
                print(f"Update extended info failed: {response.text}")

            assert response.status_code == 200
            info = response.json()
            assert info["mission_statement"] == "Test mission statement"
            print("✅ Extended info updated")

    @pytest.mark.asyncio
    async def test_get_extended_info(self):
        """Test getting extended information"""
        token = await self.get_auth_token()
        assert token is not None

        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {token}"}
            response = await client.get(
                f"{BASE_URL}/api/v1/admin/extended-info", headers=headers
            )

            if response.status_code != 200:
                print(f"Get extended info failed: {response.text}")

            assert response.status_code == 200
            info = response.json()
            assert "mission_statement" in info or info is not None
            print("✅ Extended info retrieved")


# Run with: pytest test_integration_fixed.py -v -s
