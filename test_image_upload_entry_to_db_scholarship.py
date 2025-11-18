#!/usr/bin/env python3
"""
CampusConnect Gallery Testing Script - SCHOLARSHIP USER
Tests gallery functionality for scholarship entities
"""

import requests
import json
from pathlib import Path
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"
TEST_IMAGES_DIR = Path("/Users/ryze.ai/Downloads/SNHU_Testing_Images")

# Scholarship admin credentials
USERNAME = "daneahern@comcast.net"
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


class ScholarshipGalleryTester:
    def __init__(self):
        self.access_token = None
        self.current_user = None
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
        self.print_header("PHASE 0: AUTHENTICATION - SCHOLARSHIP USER")

        try:
            data = {"username": USERNAME, "password": PASSWORD}

            response = requests.post(f"{API_V1}/admin/auth/login", data=data)

            if response.status_code == 200:
                result = response.json()
                self.access_token = result.get("access_token")
                self.print_test("Login", "PASS", f"Token obtained for {USERNAME}")
                return self.get_current_user()
            else:
                self.print_test("Login", "FAIL", f"Status: {response.status_code}")
                return False

        except Exception as e:
            self.print_test("Login", "FAIL", f"Error: {str(e)}")
            return False

    def get_current_user(self) -> bool:
        """Get current user information"""
        try:
            response = requests.get(
                f"{API_V1}/admin/auth/me", headers=self.get_headers()
            )

            if response.status_code == 200:
                self.current_user = response.json()
                entity_type = self.current_user.get("entity_type", "unknown")
                entity_id = self.current_user.get("entity_id", "unknown")

                # Verify it's a scholarship
                if entity_type != "scholarship":
                    self.print_test(
                        "Verify Entity Type",
                        "FAIL",
                        f"Expected 'scholarship', got '{entity_type}'",
                    )
                    return False

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

    def test_upload_scholarship_images(self):
        """Test uploading images to scholarship gallery"""
        self.print_header("PHASE 1: SCHOLARSHIP GALLERY IMAGE UPLOAD")

        test_images = sorted(TEST_IMAGES_DIR.glob("SNHU_Image_*"))

        if not test_images:
            self.print_test(
                "Upload Gallery Images",
                "FAIL",
                f"No test images found in {TEST_IMAGES_DIR}",
            )
            return

        print(f"{Colors.BLUE}Found {len(test_images)} test images{Colors.RESET}")
        print(
            f"{Colors.YELLOW}Testing scholarship-specific upload paths...{Colors.RESET}\n"
        )

        supported_formats = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

        # Scholarship-specific captions
        captions = [
            "Scholarship Award Ceremony 2024",
            "Recipients of Academic Excellence Award",
            "Scholarship Application Process Overview",
            "Meet Our Scholarship Recipients",
            "Community Impact Through Education",
            "Scholarship Program Information Session",
            "Success Stories from Past Recipients",
            "Application Deadline Information",
            "Scholarship Essay Tips and Guidelines",
        ]

        image_types = [
            "events",
            "students",
            "info",
            "students",
            "events",
            "info",
            "students",
            "info",
            "info",
        ]

        caption_idx = 0

        for img_path in test_images:
            filename = img_path.name
            file_ext = img_path.suffix.lower()

            if file_ext not in supported_formats:
                self._test_invalid_upload(img_path)
                continue

            caption = (
                captions[caption_idx]
                if caption_idx < len(captions)
                else f"Scholarship Image {caption_idx + 1}"
            )
            img_type = (
                image_types[caption_idx] if caption_idx < len(image_types) else "info"
            )

            success, result = self._upload_to_gallery(img_path, caption, img_type)

            if success:
                self.gallery_entries.append(result)
                # Verify scholarship-specific path
                cdn_url = result.get("cdn_url", "")
                if "scholarship" in cdn_url:
                    path_check = "✓ Correct scholarship path"
                else:
                    path_check = "⚠ Path may be incorrect"

                self.print_test(
                    f"Gallery Upload: {filename}",
                    "PASS",
                    f"ID: {result.get('id')}, {path_check}",
                )
                caption_idx += 1
            else:
                self.print_test(
                    f"Gallery Upload: {filename}",
                    "FAIL",
                    f"{result.get('error', 'Unknown error')}",
                )

    def _upload_to_gallery(
        self, image_path: Path, caption: str, image_type: str
    ) -> tuple:
        """Upload image to scholarship gallery"""
        try:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/jpeg")}
                data = {"caption": caption, "image_type": image_type}

                response = requests.post(
                    f"{API_V1}/admin/gallery",
                    headers=self.get_headers(),
                    files=files,
                    data=data,
                )

            if response.status_code in [200, 201]:
                return True, response.json()
            else:
                return False, {
                    "error": f"Status {response.status_code}: {response.text[:100]}"
                }

        except Exception as e:
            return False, {"error": str(e)}

    def _test_invalid_upload(self, image_path: Path):
        """Test uploading invalid format"""
        try:
            with open(image_path, "rb") as f:
                files = {"file": (image_path.name, f, "image/avif")}
                data = {"caption": "Test Image", "image_type": "info"}

                response = requests.post(
                    f"{API_V1}/admin/gallery",
                    headers=self.get_headers(),
                    files=files,
                    data=data,
                )

            if response.status_code in [400, 422]:
                self.print_test(
                    f"Gallery Validation: {image_path.name}",
                    "PASS",
                    f"Correctly rejected invalid format",
                )
            else:
                self.print_test(
                    f"Gallery Validation: {image_path.name}",
                    "FAIL",
                    f"Should reject but got {response.status_code}",
                )
        except Exception as e:
            self.print_test(
                f"Gallery Validation: {image_path.name}", "FAIL", f"Error: {str(e)}"
            )

    def test_list_gallery(self):
        """Test listing scholarship gallery entries"""
        self.print_header("PHASE 2: SCHOLARSHIP GALLERY MANAGEMENT")

        try:
            response = requests.get(
                f"{API_V1}/admin/gallery", headers=self.get_headers()
            )

            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    count = len(data)
                    images = data
                else:
                    count = data.get("count", 0)
                    images = data.get("images", [])

                self.print_test(
                    "List Scholarship Gallery Entries",
                    "PASS",
                    f"Found {count} gallery entries",
                )

                # Verify all are scholarship type
                scholarship_count = sum(
                    1 for img in images if img.get("entity_type") == "scholarship"
                )
                if scholarship_count == count:
                    self.print_test(
                        "Verify Entity Types",
                        "PASS",
                        f"All {count} entries are scholarship type",
                    )
                else:
                    self.print_test(
                        "Verify Entity Types",
                        "FAIL",
                        f"Found mixed entity types: {scholarship_count}/{count} scholarships",
                    )

                # Show first 3 entries
                for img in images[:3]:
                    print(
                        f"  {Colors.BLUE}├─{Colors.RESET} "
                        f"ID: {img.get('id')}, "
                        f"Type: {img.get('entity_type')}, "
                        f"Caption: {img.get('caption', 'N/A')[:35]}..."
                    )
            else:
                self.print_test(
                    "List Scholarship Gallery Entries",
                    "FAIL",
                    f"Status: {response.status_code}",
                )

        except Exception as e:
            self.print_test(
                "List Scholarship Gallery Entries", "FAIL", f"Error: {str(e)}"
            )

    def test_set_featured_image(self):
        """Test setting a featured scholarship image"""
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
                    "Set Featured Scholarship Image",
                    "PASS",
                    f"Set image ID {featured_id} as featured",
                )
            else:
                self.print_test(
                    "Set Featured Scholarship Image",
                    "FAIL",
                    f"Status: {response.status_code}",
                )

        except Exception as e:
            self.print_test(
                "Set Featured Scholarship Image", "FAIL", f"Error: {str(e)}"
            )

    def test_public_scholarship_endpoints(self):
        """Test public scholarship gallery endpoints"""
        self.print_header("PHASE 3: PUBLIC SCHOLARSHIP ENDPOINTS")

        if not self.current_user:
            self.print_test("Public Endpoints", "SKIP", "No user info available")
            return

        scholarship_id = self.current_user.get("entity_id")

        # Test gallery endpoint
        try:
            response = requests.get(
                f"{API_V1}/public/gallery/scholarships/{scholarship_id}/gallery"
            )

            if response.status_code == 200:
                data = response.json()
                count = len(data) if isinstance(data, list) else data.get("count", 0)
                self.print_test(
                    f"Public: Scholarship Gallery ({scholarship_id})",
                    "PASS",
                    f"Retrieved {count} images (no auth required)",
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

        # Test featured image endpoint
        try:
            response = requests.get(
                f"{API_V1}/public/gallery/scholarships/{scholarship_id}/featured-image"
            )

            if response.status_code == 200:
                data = response.json()
                if data:
                    self.print_test(
                        f"Public: Scholarship Featured ({scholarship_id})",
                        "PASS",
                        f"Caption: {data.get('caption', 'N/A')[:40]}",
                    )
                else:
                    self.print_test(
                        f"Public: Scholarship Featured ({scholarship_id})",
                        "PASS",
                        "No featured image",
                    )
            else:
                self.print_test(
                    f"Public: Scholarship Featured ({scholarship_id})",
                    "FAIL",
                    f"Status: {response.status_code}",
                )
        except Exception as e:
            self.print_test(
                f"Public: Scholarship Featured ({scholarship_id})",
                "FAIL",
                f"Error: {str(e)}",
            )

    def print_summary(self):
        """Print test summary"""
        self.print_header("SCHOLARSHIP GALLERY TEST SUMMARY")

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
        results_file = f"scholarship_gallery_test_{timestamp}.json"

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
                    "gallery_entries": self.gallery_entries,
                },
                f,
                indent=2,
            )

        print(
            f"\n{Colors.CYAN}📄 Detailed results saved to: {results_file}{Colors.RESET}"
        )
        print(
            f"{Colors.CYAN}🖼️  Gallery entries created: {len(self.gallery_entries)}{Colors.RESET}"
        )

        # Show CDN URLs and verify paths
        if self.gallery_entries:
            print(
                f"\n{Colors.BOLD}{Colors.GREEN}✅ Scholarship Gallery Images Created:{Colors.RESET}"
            )
            for idx, entry in enumerate(self.gallery_entries[:3], 1):
                url = entry.get("cdn_url", "N/A")
                print(f"  {idx}. {url}")
                if "scholarship" in url:
                    print(
                        f"     {Colors.GREEN}✓ Correct scholarship path{Colors.RESET}"
                    )
                else:
                    print(f"     {Colors.RED}⚠ Path verification needed{Colors.RESET}")
            if len(self.gallery_entries) > 3:
                print(f"  ... and {len(self.gallery_entries) - 3} more")

    def run_all_tests(self):
        """Run all test phases for scholarship"""
        print(f"\n{Colors.BOLD}{Colors.MAGENTA}")
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║       CampusConnect Scholarship Gallery Testing Suite             ║")
        print("║          Testing Scholarship Entity Type Functionality            ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}")

        # Phase 0: Login
        if not self.login():
            print(
                f"\n{Colors.RED}❌ Authentication failed. Cannot proceed.{Colors.RESET}"
            )
            return

        # Phase 1: Upload to Scholarship Gallery
        self.test_upload_scholarship_images()

        # Phase 2: Gallery Management
        self.test_list_gallery()
        self.test_set_featured_image()

        # Phase 3: Public Scholarship Endpoints
        self.test_public_scholarship_endpoints()

        # Summary
        self.print_summary()


def main():
    """Main execution"""
    print(f"\n{Colors.CYAN}CampusConnect Scholarship Gallery Testing{Colors.RESET}")
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

    print(f"{Colors.YELLOW}⚠️  Testing SCHOLARSHIP entity type{Colors.RESET}")
    print(
        f"{Colors.YELLOW}   Images will upload to: campusconnect/scholarship_X/gallery/{Colors.RESET}\n"
    )

    input(f"{Colors.BOLD}Press Enter to start scholarship testing...{Colors.RESET}")

    # Run tests
    tester = ScholarshipGalleryTester()
    tester.run_all_tests()

    print(f"\n{Colors.GREEN}✅ Scholarship testing complete!{Colors.RESET}\n")


if __name__ == "__main__":
    main()
