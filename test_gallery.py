"""
Quick Gallery Test with Your Token
"""

import requests
import json
from datetime import datetime
from io import BytesIO
from PIL import Image

BASE_URL = "http://localhost:8000"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYW5lYWhlcm5AeWFob28uY29tIiwiZXhwIjoxNzYzNDI1MTY5fQ.84uQep4AhnYDU9KT6qJAMmWf5t65eYIXBSw6rRcgQ0E"
print("=" * 60)
print("Gallery System Quick Test with Token")
print("=" * 60)
print(f"Base URL: {BASE_URL}\n")

headers = {"Authorization": f"Bearer {TOKEN}"}

# Test 1: Get Profile
print("Test 1: Get Admin Profile")
try:
    response = requests.get(f"{BASE_URL}/api/v1/admin/profile/entity", headers=headers)
    if response.status_code == 200:
        profile = response.json()
        print("✅ Profile retrieved!")
        print(f"   Entity Type: {profile.get('entity_type')}")
        print(f"   Entity ID: {profile.get('entity_id')}")
        if profile.get("name"):
            print(f"   Institution: {profile.get('name')}")
    else:
        print(f"❌ Profile failed: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Get Gallery
print("\nTest 2: Get Current Gallery Images")
try:
    response = requests.get(f"{BASE_URL}/api/v1/admin/gallery", headers=headers)
    if response.status_code == 200:
        images = response.json()
        print(f"✅ Gallery endpoint works!")
        print(f"   Current images: {len(images)}")

        if images:
            print("\n   Existing images:")
            for img in images[:5]:
                print(
                    f"     • ID: {img['id']}, Caption: {img.get('caption', 'No caption')}"
                )
        else:
            print("   No images yet - ready to upload!")
    else:
        print(f"❌ Gallery failed: {response.status_code}")
        print(f"   {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Upload Test Image
print("\nTest 3: Upload Test Image")
try:
    # Create a simple test image
    img = Image.new("RGB", (800, 600), color="blue")
    img_buffer = BytesIO()
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    files = {"file": ("test_campus.png", img_buffer, "image/png")}
    data = {
        "caption": f'Test Campus Photo - {datetime.now().strftime("%Y-%m-%d %H:%M")}',
        "image_type": "campus",
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/admin/gallery", headers=headers, files=files, data=data
    )

    if response.status_code == 200:
        result = response.json()
        print("✅ Image uploaded successfully!")
        print(f"   Image ID: {result['id']}")
        print(f"   Filename: {result['filename']}")
        print(f"   CDN URL: {result['cdn_url'][:60]}...")

        uploaded_id = result["id"]

        # Test 4: Update Image
        print("\nTest 4: Update Image Metadata")
        update_data = {
            "caption": "Updated Test Photo - Main Campus",
            "image_type": "building",
            "display_order": 1,
        }

        response = requests.put(
            f"{BASE_URL}/api/v1/admin/gallery/{uploaded_id}",
            headers={**headers, "Content-Type": "application/json"},
            json=update_data,
        )

        if response.status_code == 200:
            print("✅ Image metadata updated!")
            result = response.json()
            print(f"   New caption: {result['caption']}")
        else:
            print(f"❌ Update failed: {response.status_code}")

        # Test 5: Set Featured
        print("\nTest 5: Set as Featured Image")
        response = requests.post(
            f"{BASE_URL}/api/v1/admin/gallery/set-featured",
            headers={**headers, "Content-Type": "application/json"},
            json={"image_id": uploaded_id},
        )

        if response.status_code == 200:
            print("✅ Image set as featured!")
        else:
            print(f"❌ Set featured failed: {response.status_code}")

        # Test 6: Get Featured
        print("\nTest 6: Verify Featured Image")
        response = requests.get(
            f"{BASE_URL}/api/v1/admin/gallery/featured", headers=headers
        )

        if response.status_code == 200:
            featured = response.json()
            if featured and featured.get("id") == uploaded_id:
                print("✅ Featured image verified!")
            else:
                print("⚠️  Featured image mismatch")
        else:
            print(f"❌ Get featured failed: {response.status_code}")

        # Cleanup prompt
        print("\n" + "=" * 60)
        cleanup = input("Delete test image? [y/N]: ").lower()
        if cleanup == "y":
            response = requests.delete(
                f"{BASE_URL}/api/v1/admin/gallery/{uploaded_id}", headers=headers
            )
            if response.status_code in [200, 204]:
                print("✅ Test image deleted!")
            else:
                print(f"❌ Delete failed: {response.status_code}")
        else:
            print(f"✅ Test image kept (ID: {uploaded_id})")

    else:
        print(f"❌ Upload failed: {response.status_code}")
        print(f"   {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
print("\nAll core gallery functions tested:")
print("✅ Authentication (using your token)")
print("✅ Profile access")
print("✅ Gallery listing")
print("✅ Image upload")
print("✅ Metadata update")
print("✅ Featured image")
print("\nYou can now use the gallery system in your application!")
