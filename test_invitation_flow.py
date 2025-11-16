"""
Comprehensive test script for CampusConnect invitation and subscription process
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
SUPER_ADMIN_EMAIL = "danielaherniv@gmail.com"
SUPER_ADMIN_PASSWORD = "123456"

# Test data
TEST_ADMIN_EMAIL = "admin@gmail.com"
TEST_ADMIN_PASSWORD = "12345678"


class Colors:
    """ANSI color codes"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{Colors.HEADER}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'=' * 60}{Colors.ENDC}\n")


def print_success(message):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")


def print_info(message):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {message}{Colors.ENDC}")


def print_json(data):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2))


class CampusConnectTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.super_admin_token = None
        self.admin_token = None
        self.invitation_code = None

    def test_1_super_admin_login(self):
        """Test 1: Super Admin Login"""
        print_section("TEST 1: Super Admin Login")

        try:
            # Login as super admin
            response = requests.post(
                f"{self.base_url}/admin/auth/login",
                data={"username": SUPER_ADMIN_EMAIL, "password": SUPER_ADMIN_PASSWORD},
            )

            if response.status_code == 200:
                data = response.json()
                self.super_admin_token = data["access_token"]
                print_success("Super Admin logged in successfully!")
                print_info(f"Token: {self.super_admin_token[:50]}...")
                return True
            else:
                print_error(f"Login failed: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_2_get_super_admin_info(self):
        """Test 2: Get Super Admin Info"""
        print_section("TEST 2: Get Super Admin Info")

        try:
            response = requests.get(
                f"{self.base_url}/admin/auth/me",
                headers={"Authorization": f"Bearer {self.super_admin_token}"},
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Super Admin info retrieved!")
                print_json(data)
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_3_create_invitation(self, entity_type="institution", entity_id=1):
        """Test 3: Create Invitation Code"""
        print_section("TEST 3: Create Invitation Code")

        print_info(f"Creating invitation for {entity_type} ID: {entity_id}")

        try:
            response = requests.post(
                f"{self.base_url}/admin/auth/invitations",
                headers={"Authorization": f"Bearer {self.super_admin_token}"},
                json={
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "assigned_email": TEST_ADMIN_EMAIL,
                    "expires_in_days": 30,
                },
            )

            if response.status_code == 200:
                data = response.json()
                self.invitation_code = data["code"]
                print_success("Invitation code created!")
                print_info(f"Code: {self.invitation_code}")
                print_info(f"Entity: {data['entity_type']} (ID: {data['entity_id']})")
                print_info(f"Expires: {data['expires_at']}")
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_4_list_invitations(self):
        """Test 4: List All Invitations"""
        print_section("TEST 4: List All Invitations")

        try:
            response = requests.get(
                f"{self.base_url}/admin/auth/invitations",
                headers={"Authorization": f"Bearer {self.super_admin_token}"},
            )

            if response.status_code == 200:
                data = response.json()
                print_success(f"Retrieved {len(data)} invitation(s)")
                for inv in data[:3]:  # Show first 3
                    print_info(f"Code: {inv['code']} - Status: {inv['status']}")
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_5_validate_invitation(self):
        """Test 5: Validate Invitation Code"""
        print_section("TEST 5: Validate Invitation Code")

        print_info(f"Validating code: {self.invitation_code}")

        try:
            response = requests.post(
                f"{self.base_url}/admin/auth/validate-invitation",
                json={"code": self.invitation_code},
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Invitation validated!")
                print_json(data)
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_6_register_admin(self):
        """Test 6: Register Admin User"""
        print_section("TEST 6: Register Admin User")

        print_info(f"Registering {TEST_ADMIN_EMAIL} with invitation code")

        try:
            response = requests.post(
                f"{self.base_url}/admin/auth/register",
                json={
                    "email": TEST_ADMIN_EMAIL,
                    "password": TEST_ADMIN_PASSWORD,
                    "invitation_code": self.invitation_code,
                },
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Admin user registered!")
                print_json(data)
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_7_admin_login(self):
        """Test 7: Admin User Login"""
        print_section("TEST 7: Admin User Login")

        try:
            response = requests.post(
                f"{self.base_url}/admin/auth/login",
                data={"username": TEST_ADMIN_EMAIL, "password": TEST_ADMIN_PASSWORD},
            )

            if response.status_code == 200:
                data = response.json()
                self.admin_token = data["access_token"]
                print_success("Admin logged in successfully!")
                print_info(f"Token: {self.admin_token[:50]}...")
                return True
            else:
                print_error(f"Login failed: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_8_get_admin_entity(self):
        """Test 8: Get Admin's Entity (Institution/Scholarship)"""
        print_section("TEST 8: Get Admin's Entity")

        try:
            response = requests.get(
                f"{self.base_url}/admin/profile/entity",
                headers={"Authorization": f"Bearer {self.admin_token}"},
            )

            if response.status_code == 200:
                data = response.json()
                print_success("Entity retrieved!")
                print_json(data)
                return True
            else:
                print_error(f"Failed: {response.status_code}")
                print_json(response.json())
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def test_9_invitation_status_claimed(self):
        """Test 9: Check Invitation Status (Should be CLAIMED)"""
        print_section("TEST 9: Check Invitation Status")

        try:
            response = requests.get(
                f"{self.base_url}/admin/auth/invitations",
                headers={"Authorization": f"Bearer {self.super_admin_token}"},
            )

            if response.status_code == 200:
                data = response.json()
                for inv in data:
                    if inv["code"] == self.invitation_code:
                        print_success(f"Invitation status: {inv['status']}")
                        print_info(f"Claimed at: {inv.get('claimed_at', 'N/A')}")
                        if inv["status"] == "CLAIMED":
                            print_success("✅ Invitation properly marked as CLAIMED!")
                            return True
                        else:
                            print_error(f"Expected CLAIMED, got {inv['status']}")
                            return False

                print_error("Invitation code not found!")
                return False
            else:
                print_error(f"Failed: {response.status_code}")
                return False

        except Exception as e:
            print_error(f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"\n{Colors.BOLD}{Colors.HEADER}")
        print("=" * 60)
        print("CampusConnect - Invitation & Subscription Flow Test")
        print("=" * 60)
        print(f"{Colors.ENDC}\n")

        print_info(f"Base URL: {self.base_url}")
        print_info(f"Super Admin: {SUPER_ADMIN_EMAIL}")
        print_info(f"Test Admin: {TEST_ADMIN_EMAIL}")

        tests = [
            ("Super Admin Login", self.test_1_super_admin_login),
            ("Get Super Admin Info", self.test_2_get_super_admin_info),
            ("Create Invitation Code", lambda: self.test_3_create_invitation()),
            ("List All Invitations", self.test_4_list_invitations),
            ("Validate Invitation", self.test_5_validate_invitation),
            ("Register Admin User", self.test_6_register_admin),
            ("Admin User Login", self.test_7_admin_login),
            ("Get Admin's Entity", self.test_8_get_admin_entity),
            ("Check Invitation Status", self.test_9_invitation_status_claimed),
        ]

        results = []
        for name, test_func in tests:
            try:
                result = test_func()
                results.append((name, result))
            except Exception as e:
                print_error(f"Test failed with exception: {str(e)}")
                results.append((name, False))

        # Print summary
        print_section("TEST SUMMARY")

        passed = sum(1 for _, result in results if result)
        total = len(results)

        for name, result in results:
            if result:
                print_success(f"{name}")
            else:
                print_error(f"{name}")

        print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.ENDC}")

        if passed == total:
            print(
                f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.ENDC}"
            )
        else:
            print(
                f"\n{Colors.WARNING}{Colors.BOLD}⚠️  Some tests failed. Check the output above.{Colors.ENDC}"
            )

        # Next steps
        print_section("NEXT STEPS FOR SUBSCRIPTION TESTING")
        print("1. Set up Stripe webhook endpoint")
        print("2. Create a Stripe product and price")
        print("3. Test subscription creation")
        print("4. Test webhook events (subscription created, payment success)")
        print("5. Test 30-day trial period")
        print("6. Test subscription cancellation\n")


def main():
    """Main function"""
    # Check if server is running
    print_info("Checking if server is running...")
    try:
        response = requests.get(f"{BASE_URL}/../docs")
        print_success("Server is running!")
    except:
        print_error(
            "Server is not running! Start it with: uvicorn app.main:app --reload"
        )
        return

    # Get entity ID for invitation
    print_info("\nWhich entity type do you want to test?")
    print("1. Institution")
    print("2. Scholarship")
    choice = input("Enter choice (1 or 2, default=1): ").strip()

    entity_type = "institution" if choice != "2" else "scholarship"
    entity_id = input(f"Enter {entity_type} ID (default=1): ").strip()
    entity_id = int(entity_id) if entity_id else 1

    # Run tests
    tester = CampusConnectTester(BASE_URL)
    tester.run_all_tests()


if __name__ == "__main__":
    main()
