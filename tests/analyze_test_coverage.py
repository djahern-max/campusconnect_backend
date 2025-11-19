#!/usr/bin/env python3
"""
Analyze test coverage and identify missing tests
Compares your routes against existing test files
"""
import os
import re
from pathlib import Path
from collections import defaultdict

# Your routes from MagicScholar_Routes file
ALL_ROUTES = [
    ("POST", "/api/v1/admin/auth/validate-invitation"),
    ("POST", "/api/v1/admin/auth/register"),
    ("POST", "/api/v1/admin/auth/login"),
    ("GET", "/api/v1/admin/auth/me"),
    ("POST", "/api/v1/admin/auth/invitations"),
    ("GET", "/api/v1/admin/auth/invitations"),
    ("DELETE", "/api/v1/admin/auth/invitations/{invitation_id}"),
    ("GET", "/api/v1/admin/profile/entity"),
    ("GET", "/api/v1/admin/profile/display-settings"),
    ("PUT", "/api/v1/admin/profile/display-settings"),
    ("GET", "/api/v1/institutions"),
    ("GET", "/api/v1/institutions/{ipeds_id}"),
    ("GET", "/api/v1/institutions/by-id/{institution_id}"),
    ("GET", "/api/v1/institutions/{ipeds_id}/admissions"),
    ("GET", "/api/v1/institutions/{ipeds_id}/tuition"),
    ("GET", "/api/v1/institutions/{ipeds_id}/financial-overview"),
    ("GET", "/api/v1/admin/data/admissions"),
    ("PUT", "/api/v1/admin/data/admissions/{admission_id}"),
    ("GET", "/api/v1/admin/data/tuition"),
    ("PUT", "/api/v1/admin/data/tuition/{tuition_id}"),
    ("POST", "/api/v1/admin/data/admissions/{admission_id}/verify"),
    ("POST", "/api/v1/admin/data/tuition/{tuition_id}/verify"),
    ("GET", "/api/v1/admin/extended-info"),
    ("PUT", "/api/v1/admin/extended-info"),
    ("DELETE", "/api/v1/admin/extended-info"),
    ("GET", "/api/v1/admin/videos"),
    ("POST", "/api/v1/admin/videos"),
    ("PUT", "/api/v1/admin/videos/{video_id}"),
    ("DELETE", "/api/v1/admin/videos/{video_id}"),
    ("PUT", "/api/v1/admin/videos/reorder"),
    ("POST", "/api/v1/admin/images/upload"),
    ("GET", "/api/v1/admin/images/list"),
    ("DELETE", "/api/v1/admin/images/{filename}"),
    ("GET", "/api/v1/admin/gallery"),
    ("POST", "/api/v1/admin/gallery"),
    ("PUT", "/api/v1/admin/gallery/{image_id}"),
    ("DELETE", "/api/v1/admin/gallery/{image_id}"),
    ("PUT", "/api/v1/admin/gallery/reorder"),
    ("POST", "/api/v1/admin/gallery/set-featured"),
    ("GET", "/api/v1/admin/gallery/featured"),
    ("GET", "/api/v1/public/gallery/institutions/{institution_id}/gallery"),
    ("GET", "/api/v1/public/gallery/institutions/{institution_id}/featured-image"),
    ("GET", "/api/v1/public/gallery/scholarships/{scholarship_id}/gallery"),
    ("GET", "/api/v1/public/gallery/scholarships/{scholarship_id}/featured-image"),
    ("GET", "/api/v1/public/gallery/institutions/ipeds/{ipeds_id}/gallery"),
    ("GET", "/api/v1/scholarships"),
    ("GET", "/api/v1/scholarships/{scholarship_id}"),
    ("GET", "/api/v1/admin/outreach/stats"),
    ("GET", "/api/v1/admin/outreach"),
    ("POST", "/api/v1/admin/outreach"),
    ("PUT", "/api/v1/admin/outreach/{outreach_id}"),
    ("GET", "/api/v1/admin/outreach/templates"),
    ("POST", "/api/v1/admin/outreach/templates"),
    ("POST", "/api/v1/contact/submit"),
    ("GET", "/api/v1/contact/inquiries"),
    ("GET", "/api/v1/contact/inquiries/{inquiry_id}"),
    ("POST", "/api/v1/admin/subscriptions/create-checkout"),
    ("GET", "/api/v1/admin/subscriptions/pricing"),
    ("GET", "/api/v1/admin/subscriptions/current"),
    ("POST", "/api/v1/admin/subscriptions/cancel"),
    ("GET", "/api/v1/admin/subscriptions/portal"),
    ("POST", "/api/v1/webhooks/stripe"),
    ("GET", "/"),
    ("GET", "/health"),
    ("GET", "/routes-simple"),
]


def find_test_files(start_dir="."):
    """Find all test files recursively"""
    test_files = []
    for root, dirs, files in os.walk(start_dir):
        # Skip __pycache__ and other non-test directories
        dirs[:] = [
            d
            for d in dirs
            if d not in ["__pycache__", ".pytest_cache", "venv", "node_modules"]
        ]

        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))
    return test_files


def extract_tested_routes(test_file):
    """Extract routes being tested from a test file"""
    tested_routes = []

    try:
        with open(test_file, "r") as f:
            content = f.read()

            # Look for various route patterns
            patterns = [
                r'["\']/(api/v1/[^"\']+)["\']',  # Standard API routes
                r'f["\']/(api/v1/[^"\'{}]+)["\']',  # F-string routes (without variables)
                r'["\']/(health|routes-simple)["\']',  # System routes
                r'client\.(get|post|put|delete)\(\s*["\']([^"\']+)["\']',  # Client method calls
            ]

            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    # Handle different match patterns
                    if isinstance(match, tuple):
                        route = match[-1] if len(match) > 1 else match[0]
                    else:
                        route = match

                    # Clean and normalize route
                    if not route.startswith("/"):
                        route = "/" + route

                    tested_routes.append(route)

    except Exception as e:
        print(f"⚠️  Error reading {test_file}: {e}")

    return tested_routes


def normalize_route(route):
    """Normalize route for comparison"""
    # Replace path parameters with wildcards
    normalized = re.sub(r"\{[^}]+\}", "*", route)
    return normalized


def routes_match(test_route, actual_route):
    """Check if a test route matches an actual route"""
    # Direct match
    if test_route == actual_route:
        return True

    # Normalize both and compare
    norm_test = normalize_route(test_route)
    norm_actual = normalize_route(actual_route)

    if norm_test == norm_actual:
        return True

    # Partial match (for nested routes)
    if actual_route in test_route or test_route in actual_route:
        return True

    return False


def categorize_routes():
    """Categorize routes by functionality"""
    categories = defaultdict(list)

    for method, route in ALL_ROUTES:
        if "auth" in route:
            categories["Authentication"].append((method, route))
        elif (
            "/institutions" in route
            and "/admin/" not in route
            and "gallery" not in route
        ):
            categories["Public Institutions"].append((method, route))
        elif "/scholarships" in route:
            categories["Scholarships"].append((method, route))
        elif "/profile" in route:
            categories["Admin Profile"].append((method, route))
        elif "/data/" in route:
            categories["Data Management"].append((method, route))
        elif "extended-info" in route:
            categories["Extended Info"].append((method, route))
        elif "videos" in route:
            categories["Videos"].append((method, route))
        elif "/images/" in route or "/gallery" in route:
            categories["Gallery"].append((method, route))
        elif "outreach" in route:
            categories["Outreach"].append((method, route))
        elif "contact" in route:
            categories["Contact Forms"].append((method, route))
        elif "subscriptions" in route:
            categories["Subscriptions"].append((method, route))
        elif "webhooks" in route:
            categories["Webhooks"].append((method, route))
        else:
            categories["System"].append((method, route))

    return categories


def main():
    print("=" * 70)
    print("MAGICSCHOLAR TEST COVERAGE ANALYSIS")
    print("=" * 70)
    print()

    # Find test files
    test_files = find_test_files()
    print(f"📁 Found {len(test_files)} test files:")

    if not test_files:
        print("   ⚠️  No test files found!")
        print("   Make sure you're running from the tests/ directory")
        print()
        return

    for tf in sorted(test_files):
        print(f"   - {tf}")
    print()

    # Extract tested routes
    all_tested_routes = set()
    file_route_count = {}

    for test_file in test_files:
        routes = extract_tested_routes(test_file)
        file_route_count[test_file] = len(routes)
        all_tested_routes.update(routes)

    print(f"✅ Found references to {len(all_tested_routes)} unique routes")
    print()

    # Show routes per file
    print("📊 Routes per test file:")
    for test_file, count in sorted(file_route_count.items()):
        if count > 0:
            print(f"   {test_file}: {count} routes")
    print()

    # Categorize and analyze
    categories = categorize_routes()

    print("=" * 70)
    print("COVERAGE BY CATEGORY")
    print("=" * 70)
    print()

    total_routes = len(ALL_ROUTES)
    tested_count = 0
    untested_routes = []

    for category, routes in sorted(categories.items()):
        print(f"📂 {category}")
        print(f"   Total: {len(routes)} endpoints")

        category_tested = 0
        category_untested = []

        for method, route in routes:
            # Check if route is tested
            is_tested = False
            for tested_route in all_tested_routes:
                if routes_match(tested_route, route):
                    is_tested = True
                    break

            if is_tested:
                category_tested += 1
                tested_count += 1
            else:
                category_untested.append((method, route))
                untested_routes.append((category, method, route))

        coverage = (category_tested / len(routes) * 100) if routes else 0

        if category_tested == len(routes):
            print(f"   ✅ Tested: {category_tested}/{len(routes)} (100%)")
        elif category_tested > 0:
            print(f"   🟡 Tested: {category_tested}/{len(routes)} ({coverage:.0f}%)")
        else:
            print(f"   ❌ Tested: {category_tested}/{len(routes)} (0%)")

        if category_untested:
            print(f"   ⚠️  Missing tests:")
            for method, route in category_untested[:3]:  # Show first 3
                print(f"      - {method} {route}")
            if len(category_untested) > 3:
                print(f"      ... and {len(category_untested) - 3} more")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Total endpoints: {total_routes}")
    print(f"✅ Tested: {tested_count} ({tested_count/total_routes*100:.1f}%)")
    print(
        f"❌ Not tested: {len(untested_routes)} ({len(untested_routes)/total_routes*100:.1f}%)"
    )
    print()

    # Progress bar
    bar_length = 50
    filled = int(bar_length * tested_count / total_routes)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"Progress: [{bar}] {tested_count}/{total_routes}")
    print()

    if untested_routes:
        print("=" * 70)
        print("UNTESTED ENDPOINTS BY PRIORITY")
        print("=" * 70)
        print()

        # Group by category
        by_category = defaultdict(list)
        for cat, method, route in untested_routes:
            by_category[cat].append((method, route))

        # Sort by category importance
        priority_order = [
            "System",
            "Authentication",
            "Public Institutions",
            "Scholarships",
            "Admin Profile",
            "Gallery",
            "Data Management",
            "Extended Info",
            "Videos",
            "Contact Forms",
            "Outreach",
            "Subscriptions",
            "Webhooks",
        ]

        for category in priority_order:
            if category in by_category:
                routes = by_category[category]
                print(f"📂 {category} ({len(routes)} missing):")
                for method, route in routes:
                    print(f"   ❌ {method:6} {route}")
                print()

    print("=" * 70)
    print("RECOMMENDED NEXT STEPS")
    print("=" * 70)
    print()

    if tested_count == 0:
        print("⚠️  No tests detected!")
        print("This might mean:")
        print("1. Test files use different patterns")
        print("2. Tests are in a different location")
        print("3. You need to create the test files")
        print()
        print("Try running: pytest tests/ -v")
        print("to see what tests actually exist")
    elif tested_count < total_routes * 0.5:
        print("1. Great start! You have tests for some endpoints")
        print("2. Focus on adding tests for critical paths (auth, institutions)")
        print("3. Use your existing test patterns as templates")
        print(f"4. Copy generated test files to integration/ directory")
        print("5. Run: pytest tests/integration/ -v")
    else:
        print("1. Excellent progress! You're over halfway there!")
        print("2. Add tests for remaining endpoints")
        print("3. Run: pytest tests/ -v --tb=short")
        print("4. Check for any failing tests")
    print()


if __name__ == "__main__":
    main()
