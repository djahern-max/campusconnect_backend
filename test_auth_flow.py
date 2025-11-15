#!/usr/bin/env python3
"""
Authentication Flow Testing Script for RYZE.ai
Tests the complete invitation-based registration and login flow
"""

import requests
import json
from datetime import datetime
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"


class AuthTester:
    def __init__(self):
        self.token: Optional[str] = None
        self.invitation_code: Optional[str] = None
        self.test_results = []

    def log(self, test_name: str, success: bool, message: str, data: dict = None):
        """Log test results"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status}: {test_name}")
        print(f"   {message}")
        if data:
            print(f"   Data: {json.dumps(data, indent=2)}")

    def test_create_invitation(
        self, entity_type: str = "institution", entity_id: int = 1
    ):
        """Test: Create an invitation code (Super Admin function)"""
        print("\n" + "=" * 80)
        print("TEST 1: Create Invitation Code")
        print("=" * 80)

        # For testing, you'll need to be authenticated as a super admin
        # For now, let's document what the super admin needs to call
        payload = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "assigned_email": "testadmin@university.edu",
            "expires_in_days": 30,
        }

        print("\n📋 Super Admin Action Required:")
        print(
            "You need to create an invitation code manually using the authenticated endpoint."
        )
        print(f"\nEndpoint: POST {BASE_URL}/admin/auth/invitations")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        print("\nHeaders:")
        print("  Authorization: Bearer <YOUR_SUPER_ADMIN_TOKEN>")
        print("  Content-Type: application/json")

        print("\n⚠️  For testing, you can either:")
        print("   1. Use the Swagger UI at http://localhost:8000/docs")
        print("   2. Create a super admin user first and get their token")
        print("   3. Manually insert an invitation code into the database")

        # Let user input the invitation code
        invitation_code = input("\n📝 Enter the invitation code you created: ").strip()

        if invitation_code:
            self.invitation_code = invitation_code
            self.log(
                "Create Invitation", True, f"Invitation code set: {invitation_code}"
            )
            return True
        else:
            self.log("Create Invitation", False, "No invitation code provided")
            return False

    def test_validate_invitation(self):
        """Test: Validate an invitation code"""
        print("\n" + "=" * 80)
        print("TEST 2: Validate Invitation Code")
        print("=" * 80)

        if not self.invitation_code:
            self.log("Validate Invitation", False, "No invitation code available")
            return False

        try:
            response = requests.post(
                f"{BASE_URL}/admin/auth/validate-invitation",
                json={"code": self.invitation_code},
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    self.log(
                        "Validate Invitation",
                        True,
                        f"Invitation is valid for {data.get('entity_type')}: {data.get('entity_name')}",
                        data,
                    )
                    return True
                else:
                    self.log(
                        "Validate Invitation",
                        False,
                        data.get("message", "Invalid code"),
                        data,
                    )
                    return False
            else:
                self.log(
                    "Validate Invitation",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            self.log("Validate Invitation", False, f"Request failed: {str(e)}")
            return False

    def test_register(
        self,
        email: str = "testadmin@university.edu",
        password: str = "TestPassword123!",
    ):
        """Test: Register a new admin user"""
        print("\n" + "=" * 80)
        print("TEST 3: Register New Admin User")
        print("=" * 80)

        if not self.invitation_code:
            self.log("Register User", False, "No invitation code available")
            return False

        try:
            payload = {
                "email": email,
                "password": password,
                "invitation_code": self.invitation_code,
            }

            response = requests.post(f"{BASE_URL}/admin/auth/register", json=payload)

            if response.status_code == 200:
                data = response.json()
                self.log(
                    "Register User",
                    True,
                    f"Successfully registered user: {data.get('email')}",
                    {k: v for k, v in data.items() if k != "hashed_password"},
                )
                return True
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "Unknown error")
                if "already registered" in error_detail:
                    self.log(
                        "Register User",
                        True,
                        f"User already exists (expected): {error_detail}",
                    )
                    return True
                else:
                    self.log(
                        "Register User", False, f"Registration failed: {error_detail}"
                    )
                    return False
            else:
                self.log(
                    "Register User",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            self.log("Register User", False, f"Request failed: {str(e)}")
            return False

    def test_login(
        self,
        email: str = "testadmin@university.edu",
        password: str = "TestPassword123!",
    ):
        """Test: Login with credentials"""
        print("\n" + "=" * 80)
        print("TEST 4: Login")
        print("=" * 80)

        try:
            # OAuth2 expects form data, not JSON
            response = requests.post(
                f"{BASE_URL}/admin/auth/login",
                data={
                    "username": email,  # OAuth2 uses 'username' field
                    "password": password,
                },
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.log(
                    "Login",
                    True,
                    f"Successfully logged in. Token: {self.token[:20]}...",
                    {"token_type": data.get("token_type")},
                )
                return True
            else:
                self.log(
                    "Login", False, f"HTTP {response.status_code}: {response.text}"
                )
                return False

        except Exception as e:
            self.log("Login", False, f"Request failed: {str(e)}")
            return False

    def test_get_current_user(self):
        """Test: Get current user information"""
        print("\n" + "=" * 80)
        print("TEST 5: Get Current User Info")
        print("=" * 80)

        if not self.token:
            self.log("Get Current User", False, "No authentication token available")
            return False

        try:
            response = requests.get(
                f"{BASE_URL}/admin/auth/me",
                headers={"Authorization": f"Bearer {self.token}"},
            )

            if response.status_code == 200:
                data = response.json()
                self.log(
                    "Get Current User",
                    True,
                    f"Retrieved user info for: {data.get('email')}",
                    {k: v for k, v in data.items() if k != "hashed_password"},
                )
                return True
            else:
                self.log(
                    "Get Current User",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            self.log("Get Current User", False, f"Request failed: {str(e)}")
            return False

    def test_list_invitations(self):
        """Test: List invitation codes (authenticated)"""
        print("\n" + "=" * 80)
        print("TEST 6: List Invitation Codes")
        print("=" * 80)

        if not self.token:
            self.log("List Invitations", False, "No authentication token available")
            return False

        try:
            response = requests.get(
                f"{BASE_URL}/admin/auth/invitations",
                headers={"Authorization": f"Bearer {self.token}"},
            )

            if response.status_code == 200:
                data = response.json()
                self.log(
                    "List Invitations",
                    True,
                    f"Retrieved {len(data)} invitation codes",
                    {"count": len(data), "sample": data[0] if data else None},
                )
                return True
            else:
                self.log(
                    "List Invitations",
                    False,
                    f"HTTP {response.status_code}: {response.text}",
                )
                return False

        except Exception as e:
            self.log("List Invitations", False, f"Request failed: {str(e)}")
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)

        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r["success"])
        failed = total - passed

        print(f"\nTotal Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"\nSuccess Rate: {(passed/total*100):.1f}%")

        if failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['message']}")

        # Save results to file
        with open("/home/claude/test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        print(f"\n📄 Full results saved to: test_results.json")


def main():
    """Run all authentication tests"""
    print("🚀 RYZE.ai Authentication Flow Testing")
    print("=" * 80)
    print("\n⚠️  Prerequisites:")
    print("  1. Backend server running at http://localhost:8000")
    print("  2. Database properly configured")
    print("  3. Super admin account created (for invitation generation)")

    input("\n▶️  Press Enter to continue...")

    tester = AuthTester()

    # Run tests
    if tester.test_create_invitation():
        if tester.test_validate_invitation():
            if tester.test_register():
                if tester.test_login():
                    tester.test_get_current_user()
                    tester.test_list_invitations()

    # Print summary
    tester.print_summary()

    print("\n✅ Testing complete!")


if __name__ == "__main__":
    main()
