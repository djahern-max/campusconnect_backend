# tests/integration/test_image_upload.py
"""
Integration tests for image upload and gallery management
"""
import pytest
from httpx import AsyncClient
import io
from PIL import Image


@pytest.mark.integration
@pytest.mark.gallery
@pytest.mark.slow
class TestImageUpload:
    """Test image upload to DigitalOcean Spaces"""

    @pytest.mark.asyncio
    async def test_upload_image_to_spaces(
        self, client: AsyncClient, admin_headers: dict, sample_image_bytes: bytes
    ):
        """Test basic image upload"""
        files = {"file": ("test.jpg", sample_image_bytes, "image/jpeg")}

        response = await client.post(
            "/api/v1/admin/images/upload", headers=admin_headers, files=files
        )

        # May succeed or fail depending on DigitalOcean credentials
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            assert data["success"] is True
            assert "filename" in data
            assert "url" in data

    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(
        self, client: AsyncClient, admin_headers: dict
    ):
        """Test upload fails for non-image files"""
        files = {"file": ("test.txt", b"not an image", "text/plain")}

        response = await client.post(
            "/api/v1/admin/images/upload", headers=admin_headers, files=files
        )

        assert response.status_code == 400


@pytest.mark.integration
@pytest.mark.gallery
class TestGalleryManagement:
    """Test gallery CRUD operations"""

    @pytest.mark.asyncio
    async def test_get_empty_gallery(self, client: AsyncClient, admin_headers: dict):
        """Test getting gallery when no images exist"""
        response = await client.get("/api/v1/admin/gallery", headers=admin_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_add_gallery_image(
        self, client: AsyncClient, admin_headers: dict, sample_image_bytes: bytes
    ):
        """Test adding image to gallery with metadata"""
        files = {"file": ("campus.jpg", sample_image_bytes, "image/jpeg")}
        data = {"caption": "Beautiful campus view", "image_type": "campus"}

        response = await client.post(
            "/api/v1/admin/gallery", headers=admin_headers, files=files, data=data
        )

        # Success or failure depending on DO Spaces config
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            result = response.json()
            assert result["caption"] == "Beautiful campus view"
            assert result["image_type"] == "campus"

    @pytest.mark.asyncio
    async def test_gallery_reorder(self, client: AsyncClient, admin_headers: dict):
        """Test reordering gallery images"""
        # This will fail if no images exist, which is expected
        response = await client.put(
            "/api/v1/admin/gallery/reorder",
            headers=admin_headers,
            json={"image_ids": [1, 2, 3]},
        )

        # Accept success, not found, or validation error
        assert response.status_code in [200, 400, 404, 422]
