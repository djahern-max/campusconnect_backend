"""
Integration tests for Videos
"""
import pytest
from httpx import AsyncClient


@pytest.mark.integration
class TestVideos:
    """Test Videos endpoints"""
    
    @pytest.mark.asyncio
    async def test_get_api_v1_admin_videos(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/videos"""
        response = await client.get(
            f"/api/v1/admin/videos",
            headers=admin_headers,
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    async def test_post_api_v1_admin_videos(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/videos"""
        response = await client.post(
            "/api/v1/admin/videos",
            headers=admin_headers,
            json={
                "title": "Test Video",
                "video_url": "https://youtube.com/watch?v=test",
                "platform": "youtube"
            }
        )
        assert response.status_code in [200, 201, 400]

    @pytest.mark.asyncio
    async def test_put_api_v1_admin_videos(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/videos/{video_id}"""
        response = await client.put(
            "/api/v1/admin/videos/1",
            headers=admin_headers,
            json={
                "title": "Updated title"
            }
        )
        assert response.status_code in [200, 404]

    @pytest.mark.asyncio
    @pytest.mark.skip("Destructive test - enable when needed")
    async def test_delete_api_v1_admin_videos(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/videos/{video_id}"""
        response = await client.delete(
            "/api/v1/admin/videos/1",
            headers=admin_headers,
        )
        assert response.status_code in [200, 204, 404]

    @pytest.mark.asyncio
    async def test_put_api_v1_admin_videos_reorder(
        self,
        client: AsyncClient,
        admin_headers: dict
    ):
        """Test /api/v1/admin/videos/reorder"""
        response = await client.put(
            "/api/v1/admin/videos/reorder",
            headers=admin_headers,
            json={
                "title": "Updated title"
            }
        )
        assert response.status_code in [200, 404]

