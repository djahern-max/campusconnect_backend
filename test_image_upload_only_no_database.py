#!/usr/bin/env python3
"""
CampusConnect Image Gallery Testing Script
Configured for: daneahern@yahoo.com
"""

import requests
import json
from pathlib import Path
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"
TEST_IMAGES_DIR = Path("/Users/ryze.ai/Downloads/SNHU_Testing_Images")

# Your credentials
USERNAME = "daneahern@yahoo.com"
PASSWORD = "12345678"


# ANSI colors
class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


class ImageTester:
    def __init__(self):
        self.access_token = None
        self.current_user = None
        self.uploaded_images = []
        self.gallery_entries = []
        self.test_results = []

    def print_header(self, text: str):
        """Print a section header"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")

    def print_test(self, test_name: str, status: str, details: str = ""):
        """Print test result"""
        if status == "PASS":
            icon = "✓"
            color = Colors.GREEN
        elif status == "FAIL":
            icon = "✗"
            color = Colors.RED
        elif status == "SKIP":
            icon = "○"
            color = Colors.YELLOW
        else:
            icon = "●"
            color = Colors.BLUE

        print(f"{color}{icon} {test_name}{Colors.RESET}")
        if details:
            print(f"  {Colors.MAGENTA}└─{Colors.RESET} {details}")

        self.test_results.append(
            {
                "test": test_name,
                "status": status,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def get_headers(self) -> dict:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.access_token}"}

    def login(self) -> bool:
        """Authenticate and get access token"""
        self.print_header("PHASE 0: AUTHENTICATION")

        try:
            # Login using OAuth2 form format
            data = {"username": USERNAME, "password": PASSWORD}

            response = requests.post(
                f"{API_V1}/admin/auth/login",
                data=data,  # Use data instead of json for form-encoded
            )

            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                self.print_test("Login", "PASS", f"Token obtained for {USERNAME}")

                # Get current user info to see entity details
                return self.get_current_user()
            else:
                self.print_test(
                    "Login",
                    "FAIL",
                    f"Status: {response.status_code}, {response.text[:200]}",
                )
                return False

        except Exception as e:
            self.print_test("Login", "FAIL", f"Error: {str(e)}")
            return False

    def get_current_user(self) -> bool:
        """Get current user information including entity details"""
        try:
            response = requests.get(
                f"{API_V1}/admin/auth/me", headers=self.get_headers()
            )

            if response.status_code == 200:
                self.current_user = response.json()
                entity_type = self.current_user.get("entity_type", "unknown")
                entity_id = self.current_user.get("entity_id", "unknown")

                self.print_test(
                    "Get Current User", "PASS", f"Entity: {entity_type} #{entity_id}"
                )
                return True
            else:
                self.print_test(
                    "Get Current User", "FAIL", f"Status: {response.status_code}"
                )
                return False
        except Exception as e:
            self.print_test("Get Current User", "FAIL", f"Error: {str(e)}")
            return False

    # =========================================================================
    # PHASE 1: IMAGE UPLOAD & MANAGEMENT
    # =========================================================================

    def test_upload_images(self):
        """Test uploading all SNHU images"""
        self.print_header("PHASE 1: IMAGE UPLOAD & MANAGEMENT")

        test_images = sorted(TEST_IMAGES_DIR.glob("SNHU_Image_*"))

        if not test_images:
            self.print_test(
                "Upload Images", "FAIL", f"No test images found in {TEST_IMAGES_DIR}"
            )
            return

        print(f"{Colors.BLUE}Found {len(test_images)} test images{Colors.RESET}\n")

        supported_formats = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

        for img_path in test_images:
            filename = img_path.name
            file_ext = img_path.suffix.lower()

            if file_ext not in supported_formats:
                # Test that validation works
                self._test_invalid_upload(img_path)
                continue

            # Try to upload valid image
            success, result = self._upload_image(img_path)

            if success:
                self.uploaded_images.append(result)
                self.print_test(
                    f"Upload: {filename}",
                    "PASS",
                    f"Size: {result.get('size_bytes', 0)} bytes",
                )
            else:
                self.print_test(
                    f"Upload: {filename}",
                    "FAIL",
                    f"{result.get('error', 'Unknown error')}",
                )

    def _upload_image(self, image_path: Path) -> tuple:
        """Upload a single image"""
        try:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/jpeg")}
                response = requests.post(
                    f"{API_V1}/admin/images/upload",
                    headers=self.get_headers(),
                    files=files,
                )

            if response.status_code == 200:
                return True, response.json()
            else:
                return False, {
                    "error": f"Status {response.status_code}: {response.text[:100]}"
                }

        except Exception as e:
            return False, {"error": str(e)}

    def _test_invalid_upload(self, image_path: Path):
        """Test uploading an invalid format (should fail)"""
        try:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/avif")}
                response = requests.post(
                    f"{API_V1}/admin/images/upload",
                    headers=self.get_headers(),
                    files=files,
                )

            if response.status_code == 400:
                self.print_test(
                    f"Upload Validation: {image_path.name}",
                    "PASS",
                    f"Correctly rejected: {response.json().get('detail', '')[:60]}",
                )
            else:
                self.print_test(
                    f"Upload Validation: {image_path.name}",
                    "FAIL",
                    f"Should have rejected but got {response.status_code}",
                )
        except Exception as e:
            self.print_test(
                f"Upload Validation: {image_path.name}", "FAIL", f"Error: {str(e)}"
            )

    def test_list_images(self):
        """Test listing uploaded images"""
        try:
            response = requests.get(
                f"{API_V1}/admin/images/list", headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                self.print_test("List Images", "PASS", f"Found {count} images")
            else:
                self.print_test(
                    "List Images", "FAIL", f"Status: {response.status_code}"
                )

        except Exception as e:
            self.print_test("List Images", "FAIL", f"Error: {str(e)}")

    # =========================================================================
    # PHASE 2: GALLERY MANAGEMENT
    # =========================================================================

    def test_create_gallery_entries(self):
        """Create gallery entries for uploaded images"""
        self.print_header("PHASE 2: GALLERY ENTRY MANAGEMENT")

        if not self.uploaded_images:
            self.print_test("Create Gallery Entries", "SKIP", "No uploaded images")
            return

        captions = [
            "Main Campus Building - SNHU",
            "Student Life at Southern New Hampshire University",
            "Modern Learning Facilities",
            "Campus Events and Activities",
            "Beautiful Campus Grounds",
        ]

        image_types = ["campus", "students", "facilities", "events", "campus"]

        for idx, image in enumerate(self.uploaded_images[:5]):
            gallery_data = {
                "image_url": image["url"],
                "cdn_url": image["cdn_url"],
                "filename": image["filename"],
                "caption": (
                    captions[idx] if idx < len(captions) else f"SNHU Image {idx + 1}"
                ),
                "image_type": image_types[idx] if idx < len(image_types) else "campus",
                "display_order": idx + 1,
            }

            try:
                response = requests.post(
                    f"{API_V1}/admin/gallery",
                    headers=self.get_headers(),
                    json=gallery_data,
                )

                if response.status_code in [200, 201]:
                    gallery_entry = response.json()
                    self.gallery_entries.append(gallery_entry)
                    self.print_test(
                        f"Create Gallery Entry #{idx + 1}",
                        "PASS",
                        f"ID: {gallery_entry.get('id')}, Caption: {gallery_entry.get('caption')[:40]}",
                    )
                else:
                    self.print_test(
                        f"Create Gallery Entry #{idx + 1}",
                        "FAIL",
                        f"Status: {response.status_code}, {response.text[:100]}",
                    )

            except Exception as e:
                self.print_test(
                    f"Create Gallery Entry #{idx + 1}", "FAIL", f"Error: {str(e)}"
                )

    def test_list_gallery(self):
        """Test listing gallery entries"""
        try:
            response = requests.get(
                f"{API_V1}/admin/gallery", headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                # Handle both list response and dict with images key
                if isinstance(data, list):
                    count = len(data)
                    images = data
                else:
                    count = data.get("count", len(data.get("images", [])))
                    images = data.get("images", [])

                self.print_test(
                    "List Gallery Entries", "PASS", f"Found {count} gallery entries"
                )

                # Show first 3 entries
                for img in images[:3]:
                    print(
                        f"  {Colors.BLUE}├─{Colors.RESET} "
                        f"ID: {img.get('id')}, "
                        f"Order: {img.get('display_order')}, "
                        f"Caption: {img.get('caption', 'N/A')[:30]}"
                    )
            else:
                self.print_test(
                    "List Gallery Entries", "FAIL", f"Status: {response.status_code}"
                )

        except Exception as e:
            self.print_test("List Gallery Entries", "FAIL", f"Error: {str(e)}")

    def test_set_featured_image(self):
        """Test setting a featured image"""
        if not self.gallery_entries:
            self.print_test("Set Featured Image", "SKIP", "No gallery entries")
            return

        featured_id = self.gallery_entries[0]["id"]

        try:
            response = requests.post(
                f"{API_V1}/admin/gallery/set-featured",
                headers=self.get_headers(),
                json={"image_id": featured_id},
            )

            if response.status_code == 200:
                self.print_test(
                    "Set Featured Image",
                    "PASS",
                    f"Set image ID {featured_id} as featured",
                )
            else:
                self.print_test(
                    "Set Featured Image",
                    "FAIL",
                    f"Status: {response.status_code}, {response.text[:100]}",
                )

        except Exception as e:
            self.print_test("Set Featured Image", "FAIL", f"Error: {str(e)}")

    def test_get_featured_image(self):
        """Test getting the featured image"""
        try:
            response = requests.get(
                f"{API_V1}/admin/gallery/featured", headers=self.get_headers()
            )

            if response.status_code == 200:
                featured = response.json()
                if featured:
                    self.print_test(
                        "Get Featured Image",
                        "PASS",
                        f"Caption: {featured.get('caption', 'N/A')[:40]}",
                    )
                else:
                    self.print_test(
                        "Get Featured Image", "PASS", "No featured image set"
                    )
            else:
                self.print_test(
                    "Get Featured Image", "FAIL", f"Status: {response.status_code}"
                )

        except Exception as e:
            self.print_test("Get Featured Image", "FAIL", f"Error: {str(e)}")

    # =========================================================================
    # PHASE 3: PUBLIC ACCESS
    # =========================================================================

    def test_public_endpoints(self):
        """Test public gallery endpoints"""
        self.print_header("PHASE 3: PUBLIC ACCESS TESTING")

        if not self.current_user:
            self.print_test("Public Endpoints", "SKIP", "No user info available")
            return

        entity_type = self.current_user.get("entity_type")
        entity_id = self.current_user.get("entity_id")

        if entity_type == "institution":
            self._test_public_institution_endpoints(entity_id)
        elif entity_type == "scholarship":
            self._test_public_scholarship_endpoints(entity_id)
        else:
            self.print_test(
                "Public Endpoints", "SKIP", f"Unknown entity type: {entity_type}"
            )

    def _test_public_institution_endpoints(self, institution_id):
        """Test public institution endpoints"""
        # Test gallery endpoint
        try:
            response = requests.get(
                f"{API_V1}/public/gallery/institutions/{institution_id}/gallery"
            )

            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                self.print_test(
                    f"Public: Institution Gallery ({institution_id})",
                    "PASS",
                    f"Retrieved {count} images (no auth required)",
                )
            else:
                self.print_test(
                    f"Public: Institution Gallery ({institution_id})",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.print_test(
                f"Public: Institution Gallery ({institution_id})",
                "FAIL",
                f"Error: {str(e)}",
            )

        # Test featured image endpoint
        try:
            response = requests.get(
                f"{API_V1}/public/gallery/institutions/{institution_id}/featured-image"
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    self.print_test(
                        f"Public: Institution Featured ({institution_id})",
                        "PASS",
                        f"Caption: {data.get('caption', 'N/A')[:40]}",
                    )
                else:
                    self.print_test(
                        f"Public: Institution Featured ({institution_id})",
                        "PASS",
                        "No featured image set",
                    )
            else:
                self.print_test(
                    f"Public: Institution Featured ({institution_id})",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.print_test(
                f"Public: Institution Featured ({institution_id})",
                "FAIL",
                f"Error: {str(e)}",
            )

    def _test_public_scholarship_endpoints(self, scholarship_id):
        """Test public scholarship endpoints"""
        # Test gallery endpoint
        try:
            response = requests.get(
                f"{API_V1}/public/gallery/scholarships/{scholarship_id}/gallery"
            )

            if response.status_code == 200:
                data = response.json()
                count = data.get("count", 0)
                self.print_test(
                    f"Public: Scholarship Gallery ({scholarship_id})",
                    "PASS",
                    f"Retrieved {count} images",
                )
            else:
                self.print_test(
                    f"Public: Scholarship Gallery ({scholarship_id})",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.print_test(
                f"Public: Scholarship Gallery ({scholarship_id})",
                "FAIL",
                f"Error: {str(e)}",
            )

    # =========================================================================
    # TEST SUMMARY
    # =========================================================================

    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["status"] == "PASS")
        failed = sum(1 for r in self.test_results if r["status"] == "FAIL")
        skipped = sum(1 for r in self.test_results if r["status"] == "SKIP")

        print(f"{Colors.BOLD}Total Tests:{Colors.RESET} {total}")
        print(f"{Colors.GREEN}✓ Passed:{Colors.RESET} {passed}")
        print(f"{Colors.RED}✗ Failed:{Colors.RESET} {failed}")
        print(f"{Colors.YELLOW}○ Skipped:{Colors.RESET} {skipped}")

        if passed > 0:
            success_rate = (
                (passed / (total - skipped) * 100) if (total - skipped) > 0 else 0
            )
            print(f"\n{Colors.CYAN}Success Rate:{Colors.RESET} {success_rate:.1f}%")

        if failed > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.RESET}")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  {Colors.RED}✗{Colors.RESET} {result['test']}")
                    if result["details"]:
                        print(f"    {result['details'][:80]}")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"test_results_{timestamp}.json"

        with open(results_file, "w") as f:
            json.dump(
                {
                    "summary": {
                        "total": total,
                        "passed": passed,
                        "failed": failed,
                        "skipped": skipped,
                        "success_rate": f"{(passed / (total - skipped) * 100) if (total - skipped) > 0 else 0:.1f}%",
                    },
                    "user": {
                        "email": USERNAME,
                        "entity_type": (
                            self.current_user.get("entity_type")
                            if self.current_user
                            else None
                        ),
                        "entity_id": (
                            self.current_user.get("entity_id")
                            if self.current_user
                            else None
                        ),
                    },
                    "tests": self.test_results,
                    "uploaded_images": self.uploaded_images,
                    "gallery_entries": self.gallery_entries,
                },
                f,
                indent=2,
            )

        print(
            f"\n{Colors.CYAN}📄 Detailed results saved to: {results_file}{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}📁 Images uploaded: {len(self.uploaded_images)}{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}🖼️  Gallery entries created: {len(self.gallery_entries)}{Colors.RESET}"
        )

    def run_all_tests(self):
        """Run all test phases"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║          CampusConnect Image Gallery Testing Suite                ║")
        print("║                    SNHU Test Images                                ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")

        # Phase 0: Login
        if not self.login():
            print(
                f"\n{Colors.RED}❌ Authentication failed. Cannot proceed.{Colors.RESET}"
            )
            print(f"\n{Colors.YELLOW}Check:{Colors.RESET}")
            print(f"  1. Backend is running: http://localhost:8000")
            print(f"  2. Credentials are correct: {USERNAME}")
            print(f"  3. Admin user exists in database")
            return

        # Phase 1: Upload & Management
        self.test_upload_images()
        self.test_list_images()

        # Phase 2: Gallery Management
        self.test_create_gallery_entries()
        self.test_list_gallery()
        self.test_set_featured_image()
        self.test_get_featured_image()

        # Phase 3: Public Access
        self.test_public_endpoints()

        # Summary
        self.print_summary()


def main():
    """Main execution"""
    print(f"\n{Colors.CYAN}CampusConnect Image Testing Script{Colors.RESET}")
    print(f"{Colors.CYAN}User: {USERNAME}{Colors.RESET}")
    print(f"{Colors.CYAN}Images: {TEST_IMAGES_DIR}{Colors.RESET}\n")

    # Check if test images exist
    if not TEST_IMAGES_DIR.exists():
        print(f"{Colors.RED}❌ Error: Test images directory not found!{Colors.RESET}")
        print(f"Expected: {TEST_IMAGES_DIR}")
        return

    # Count available test images
    test_images = list(TEST_IMAGES_DIR.glob("SNHU_Image_*"))
    print(f"✓ Found {len(test_images)} test images\n")

    # Check backend availability
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        print(f"✓ Backend is responding\n")
    except:
        print(f"{Colors.RED}❌ Backend not responding at {BASE_URL}{Colors.RESET}")
        print(f"Make sure backend is running: uvicorn app.main:app --reload\n")
        return

    # Run tests
    tester = ImageTester()
    tester.run_all_tests()

    print(f"\n{Colors.GREEN}✅ Testing complete!{Colors.RESET}\n")


if __name__ == "__main__":
    main()
