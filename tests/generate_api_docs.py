"""
Generate comprehensive API documentation for frontend developers
Exports OpenAPI schema and creates sample requests/responses
UPDATED: November 2025 - Includes all endpoints
"""

import httpx
import json
from pathlib import Path
import asyncio

BASE_URL = "http://localhost:8000"
DOCS_DIR = Path("api_docs")
DOCS_DIR.mkdir(exist_ok=True)


async def generate_docs():
    """Generate API documentation"""
    print("📝 Generating comprehensive API documentation...")
    print("=" * 70)

    async with httpx.AsyncClient() as client:
        # Get OpenAPI schema
        response = await client.get(f"{BASE_URL}/openapi.json")
        schema = response.json()

        # Save full OpenAPI schema
        with open(DOCS_DIR / "openapi.json", "w") as f:
            json.dump(schema, f, indent=2)
        print("✅ OpenAPI schema saved")

        # Generate TypeScript interfaces
        generate_typescript_interfaces(schema)

        # Generate example requests
        generate_example_requests()

        # Generate endpoint list
        generate_endpoint_list()

        print("=" * 70)
        print("\n🎉 Documentation generated in api_docs/")
        print("   - openapi.json (Full OpenAPI 3.0 spec)")
        print("   - types.ts (TypeScript interfaces)")
        print("   - example_requests.json (Request examples)")
        print("   - endpoints.md (Endpoint reference)")


def generate_typescript_interfaces(schema):
    """Generate TypeScript interfaces from OpenAPI schema"""
    interfaces = []

    # Institution interface
    interfaces.append(
        """
export interface Institution {
  id: number;
  ipeds_id: number;
  name: string;
  city: string;
  state: string;  // 2-letter code
  control_type: 'PUBLIC' | 'PRIVATE_NONPROFIT' | 'PRIVATE_FOR_PROFIT';
  primary_image_url: string | null;
  student_faculty_ratio: number | null;
  size_category: string | null;
  locale: string | null;
  created_at: string;
  updated_at: string;
}
"""
    )

    # Scholarship interface
    interfaces.append(
        """
export interface Scholarship {
  id: number;
  title: string;
  organization: string;
  scholarship_type: string;
  status: string;
  difficulty_level: string;
  amount_min: number;
  amount_max: number;
  is_renewable: boolean;
  deadline: string | null;
  description: string | null;
  website_url: string | null;
  min_gpa: number | null;
  primary_image_url: string | null;
  created_at: string;
}
"""
    )

    # Admin User interface
    interfaces.append(
        """
export interface AdminUser {
  id: number;
  email: string;
  entity_type: 'institution' | 'scholarship';
  entity_id: number;
  role: 'admin' | 'super_admin';
  is_active: boolean;
}
"""
    )

    # Invitation interfaces
    interfaces.append(
        """
export interface Invitation {
  id: number;
  code: string;
  entity_type: 'institution' | 'scholarship';
  entity_id: number;
  assigned_email: string | null;
  status: 'PENDING' | 'ACCEPTED' | 'EXPIRED';
  created_by: number;
  expires_at: string;
  used_at: string | null;
  created_at: string;
}

export interface InvitationValidation {
  valid: boolean;
  entity_type?: string;
  entity_id?: number;
  entity_name?: string;
  error?: string;
}
"""
    )

    # Display Settings interface
    interfaces.append(
        """
export interface DisplaySettings {
  id: number;
  entity_type: 'institution' | 'scholarship';
  entity_id: number;
  show_stats: boolean;
  show_financial: boolean;
  show_requirements: boolean;
  show_image_gallery: boolean;  // Premium only
  show_video: boolean;           // Premium only
  show_extended_info: boolean;   // Premium only
  custom_tagline: string | null; // Premium only
  custom_description: string | null;
  extended_description: string | null;
  layout_style: string;
  primary_color: string | null;  // Hex color
}
"""
    )

    # Gallery interface
    interfaces.append(
        """
export interface InstitutionImage {
  id: number;
  institution_id: number;
  image_url: string;
  cdn_url: string;
  filename: string;
  caption: string | null;
  display_order: number;
  is_featured: boolean;
  image_type: 'campus' | 'students' | 'facilities' | 'events' | null;
  created_at: string;
}
"""
    )

    # Video interface
    interfaces.append(
        """
export interface InstitutionVideo {
  id: number;
  institution_id: number;
  video_url: string;
  title: string | null;
  description: string | null;
  thumbnail_url: string | null;
  video_type: 'tour' | 'testimonial' | 'overview' | 'custom' | null;
  display_order: number;
  is_featured: boolean;
  created_at: string;
}
"""
    )

    # Extended Info interface
    interfaces.append(
        """
export interface CustomSection {
  title: string;
  content: string;
  order: number;
}

export interface InstitutionExtendedInfo {
  id: number;
  institution_id: number;
  
  // Campus Life
  campus_description: string | null;
  student_life: string | null;
  housing_info: string | null;
  dining_info: string | null;
  
  // Academics
  programs_overview: string | null;
  faculty_highlights: string | null;
  research_opportunities: string | null;
  study_abroad: string | null;
  
  // Admissions
  application_tips: string | null;
  financial_aid_info: string | null;
  scholarship_opportunities: string | null;
  
  // Athletics & Activities
  athletics_overview: string | null;
  clubs_organizations: string | null;
  
  // Location & Facilities
  location_highlights: string | null;
  facilities_overview: string | null;
  
  // Custom Sections
  custom_sections: CustomSection[] | null;
  
  created_at: string;
  updated_at: string;
}
"""
    )

    # Admissions Data interface
    interfaces.append(
        """
export interface AdmissionsData {
  id: number;
  ipeds_id: number;
  institution_id: number;
  academic_year: string;
  acceptance_rate: number | null;
  yield_rate: number | null;
  applications_total: number | null;
  admissions_total: number | null;
  enrolled_total: number | null;
  application_fee: number | null;
  sat_reading_25th: number | null;
  sat_reading_75th: number | null;
  sat_math_25th: number | null;
  sat_math_75th: number | null;
  act_composite_25th: number | null;
  act_composite_75th: number | null;
  is_verified: boolean;
  verified_at: string | null;
  verified_by: number | null;
  created_at: string;
  updated_at: string;
}
"""
    )

    # Tuition Data interface
    interfaces.append(
        """
export interface TuitionData {
  id: number;
  ipeds_id: number;
  institution_id: number;
  academic_year: string;
  in_state_tuition: number | null;
  out_of_state_tuition: number | null;
  in_state_fees: number | null;
  out_of_state_fees: number | null;
  books_supplies: number | null;
  on_campus_room_board: number | null;
  off_campus_room_board: number | null;
  on_campus_other: number | null;
  off_campus_other: number | null;
  is_verified: boolean;
  verified_at: string | null;
  verified_by: number | null;
  created_at: string;
  updated_at: string;
}

export interface FinancialOverview {
  tuition: TuitionData | null;
  admissions: AdmissionsData | null;
  total_cost_in_state: number | null;
  total_cost_out_of_state: number | null;
}
"""
    )

    # Outreach interfaces
    interfaces.append(
        """
export interface OutreachMessage {
  id: number;
  institution_id: number;
  recipient_email: string;
  recipient_name: string | null;
  subject: string;
  message: string;
  campaign_name: string | null;
  status: 'DRAFT' | 'SENT' | 'DELIVERED' | 'BOUNCED' | 'FAILED';
  sent_at: string | null;
  delivered_at: string | null;
  opened_at: string | null;
  clicked_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface OutreachTemplate {
  id: number;
  institution_id: number;
  name: string;
  subject: string;
  body: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface OutreachStats {
  total_sent: number;
  total_delivered: number;
  total_opened: number;
  total_clicked: number;
  total_bounced: number;
  total_failed: number;
  delivery_rate: number;
  open_rate: number;
  click_rate: number;
}
"""
    )

    # Subscription interface
    interfaces.append(
        """
export interface Subscription {
  status: string;
  plan_tier: string;
  current_period_start?: number;
  current_period_end?: number;
  cancel_at_period_end?: boolean;
  trial_end?: number | null;
}
"""
    )

    # Auth Token interface
    interfaces.append(
        """
export interface AuthToken {
  access_token: string;
  token_type: 'bearer';
}
"""
    )

    # Write to file
    with open(DOCS_DIR / "types.ts", "w") as f:
        f.write("// CampusConnect API TypeScript Interfaces\n")
        f.write("// Auto-generated - Do not edit manually\n")
        f.write("// Updated: November 2025\n\n")
        f.write("\n".join(interfaces))

    print("✅ TypeScript interfaces generated (13 interfaces)")


def generate_example_requests():
    """Generate example API requests for all endpoints"""
    examples = {
        "public_institutions": {
            "list_all": {
                "method": "GET",
                "url": "/api/v1/institutions?limit=100&offset=0",
                "description": "Get paginated list of institutions",
            },
            "filter_by_state": {
                "method": "GET",
                "url": "/api/v1/institutions?state=NH",
                "description": "Filter institutions by state",
            },
            "get_by_ipeds": {
                "method": "GET",
                "url": "/api/v1/institutions/{ipeds_id}",
                "description": "Get institution by IPEDS ID",
            },
            "get_by_db_id": {
                "method": "GET",
                "url": "/api/v1/institutions/by-id/{institution_id}",
                "description": "Get institution by database ID",
            },
            "get_admissions": {
                "method": "GET",
                "url": "/api/v1/institutions/{ipeds_id}/admissions",
                "description": "Get admissions data for institution",
            },
            "get_tuition": {
                "method": "GET",
                "url": "/api/v1/institutions/{ipeds_id}/tuition",
                "description": "Get tuition data for institution",
            },
            "get_financial": {
                "method": "GET",
                "url": "/api/v1/institutions/{ipeds_id}/financial-overview",
                "description": "Get complete financial overview",
            },
        },
        "public_scholarships": {
            "list_all": {
                "method": "GET",
                "url": "/api/v1/scholarships?limit=100&offset=0",
                "description": "Get paginated list of scholarships",
            },
            "get_single": {
                "method": "GET",
                "url": "/api/v1/scholarships/{scholarship_id}",
                "description": "Get single scholarship by ID",
            },
        },
        "authentication": {
            "validate_invitation": {
                "method": "POST",
                "url": "/api/v1/admin/auth/validate-invitation",
                "body": {"code": "INV-ABC123"},
                "description": "Validate invitation code before registration",
            },
            "register": {
                "method": "POST",
                "url": "/api/v1/admin/auth/register",
                "body": {
                    "email": "admin@example.com",
                    "password": "securepassword123",
                    "invitation_code": "INV-ABC123",
                },
                "description": "Register new admin with invitation code",
            },
            "login": {
                "method": "POST",
                "url": "/api/v1/admin/auth/login",
                "content_type": "application/x-www-form-urlencoded",
                "body": {
                    "username": "admin@example.com",
                    "password": "securepassword123",
                },
                "description": "Login and get JWT token",
            },
            "get_current_user": {
                "method": "GET",
                "url": "/api/v1/admin/auth/me",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get current authenticated user",
            },
        },
        "invitations": {
            "create": {
                "method": "POST",
                "url": "/api/v1/admin/auth/invitations",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "entity_type": "institution",
                    "entity_id": 1,
                    "assigned_email": "newadmin@example.com",
                    "expires_in_days": 30,
                },
                "description": "Create invitation code (super admin only)",
            },
            "list": {
                "method": "GET",
                "url": "/api/v1/admin/auth/invitations",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "List all invitations (super admin only)",
            },
            "delete": {
                "method": "DELETE",
                "url": "/api/v1/admin/auth/invitations/{invitation_id}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Delete invitation (super admin only)",
            },
        },
        "admin_profile": {
            "get_entity": {
                "method": "GET",
                "url": "/api/v1/admin/profile/entity",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get admin's managed entity",
            },
            "get_settings": {
                "method": "GET",
                "url": "/api/v1/admin/profile/display-settings",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get display settings",
            },
            "update_settings": {
                "method": "PUT",
                "url": "/api/v1/admin/profile/display-settings",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "custom_tagline": "Excellence in Education",
                    "show_image_gallery": True,
                    "show_video": True,
                },
                "description": "Update display settings",
            },
        },
        "gallery": {
            "upload": {
                "method": "POST",
                "url": "/api/v1/admin/gallery",
                "headers": {"Authorization": "Bearer TOKEN"},
                "content_type": "multipart/form-data",
                "body": {
                    "file": "[binary]",
                    "caption": "Beautiful campus view",
                    "image_type": "campus",
                },
                "description": "Upload image to gallery",
            },
            "list": {
                "method": "GET",
                "url": "/api/v1/admin/gallery",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "List all gallery images",
            },
            "update": {
                "method": "PUT",
                "url": "/api/v1/admin/gallery/{image_id}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {"caption": "Updated caption", "image_type": "students"},
                "description": "Update image metadata",
            },
            "delete": {
                "method": "DELETE",
                "url": "/api/v1/admin/gallery/{image_id}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Delete gallery image",
            },
            "reorder": {
                "method": "PUT",
                "url": "/api/v1/admin/gallery/reorder",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {"image_ids": [3, 1, 2, 4]},
                "description": "Reorder gallery images",
            },
        },
        "videos": {
            "add": {
                "method": "POST",
                "url": "/api/v1/admin/videos",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "video_url": "https://youtube.com/watch?v=...",
                    "title": "Campus Tour 2025",
                    "description": "Virtual tour of our campus",
                    "video_type": "tour",
                    "is_featured": True,
                },
                "description": "Add video embed",
            },
            "list": {
                "method": "GET",
                "url": "/api/v1/admin/videos",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "List all videos",
            },
            "update": {
                "method": "PUT",
                "url": "/api/v1/admin/videos/{video_id}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "title": "Updated Title",
                    "description": "Updated description",
                },
                "description": "Update video metadata",
            },
            "delete": {
                "method": "DELETE",
                "url": "/api/v1/admin/videos/{video_id}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Delete video",
            },
            "reorder": {
                "method": "PUT",
                "url": "/api/v1/admin/videos/reorder",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {"video_ids": [2, 1, 3]},
                "description": "Reorder videos",
            },
        },
        "extended_info": {
            "get": {
                "method": "GET",
                "url": "/api/v1/admin/extended-info",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get extended information",
            },
            "update": {
                "method": "PUT",
                "url": "/api/v1/admin/extended-info",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "campus_description": "Beautiful campus...",
                    "student_life": "Vibrant community...",
                    "custom_sections": [
                        {
                            "title": "Why Choose Us",
                            "content": "Excellence in education",
                            "order": 1,
                        }
                    ],
                },
                "description": "Update extended information",
            },
            "delete": {
                "method": "DELETE",
                "url": "/api/v1/admin/extended-info",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Clear extended information",
            },
        },
        "outreach": {
            "stats": {
                "method": "GET",
                "url": "/api/v1/admin/outreach/stats",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get outreach statistics",
            },
            "list": {
                "method": "GET",
                "url": "/api/v1/admin/outreach",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "List outreach messages",
            },
            "create": {
                "method": "POST",
                "url": "/api/v1/admin/outreach",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "recipient_email": "student@example.com",
                    "subject": "Welcome!",
                    "message": "We're excited to have you...",
                    "campaign_name": "Welcome Campaign",
                },
                "description": "Create outreach message",
            },
            "update": {
                "method": "PUT",
                "url": "/api/v1/admin/outreach/{outreach_id}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {"subject": "Updated Subject", "message": "Updated message"},
                "description": "Update outreach message",
            },
            "list_templates": {
                "method": "GET",
                "url": "/api/v1/admin/outreach/templates",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "List outreach templates",
            },
            "create_template": {
                "method": "POST",
                "url": "/api/v1/admin/outreach/templates",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "name": "Welcome Template",
                    "subject": "Welcome!",
                    "body": "Welcome message...",
                },
                "description": "Create outreach template",
            },
        },
        "admin_data": {
            "get_admissions": {
                "method": "GET",
                "url": "/api/v1/admin/data/admissions",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get admissions data for admin's institution",
            },
            "update_admissions": {
                "method": "PUT",
                "url": "/api/v1/admin/data/admissions/{admission_id}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {"acceptance_rate": 0.65, "application_fee": 50},
                "description": "Update admissions data",
            },
            "verify_admissions": {
                "method": "POST",
                "url": "/api/v1/admin/data/admissions/{admission_id}/verify",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Mark admissions data as verified",
            },
            "get_tuition": {
                "method": "GET",
                "url": "/api/v1/admin/data/tuition",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get tuition data for admin's institution",
            },
            "update_tuition": {
                "method": "PUT",
                "url": "/api/v1/admin/data/tuition/{tuition_id}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {"in_state_tuition": 15000, "out_of_state_tuition": 30000},
                "description": "Update tuition data",
            },
            "verify_tuition": {
                "method": "POST",
                "url": "/api/v1/admin/data/tuition/{tuition_id}/verify",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Mark tuition data as verified",
            },
        },
        "subscriptions": {
            "create_checkout": {
                "method": "POST",
                "url": "/api/v1/admin/subscriptions/create-checkout",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Create Stripe checkout session",
            },
            "get_current": {
                "method": "GET",
                "url": "/api/v1/admin/subscriptions/current",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get current subscription status",
            },
            "cancel": {
                "method": "POST",
                "url": "/api/v1/admin/subscriptions/cancel",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Cancel subscription at period end",
            },
            "get_portal": {
                "method": "GET",
                "url": "/api/v1/admin/subscriptions/portal",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Get customer portal URL",
            },
        },
        "images": {
            "upload": {
                "method": "POST",
                "url": "/api/v1/admin/images/upload",
                "headers": {"Authorization": "Bearer TOKEN"},
                "content_type": "multipart/form-data",
                "body": {"file": "[binary]"},
                "description": "Upload image to DigitalOcean Spaces",
            },
            "list": {
                "method": "GET",
                "url": "/api/v1/admin/images/list",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "List uploaded images",
            },
            "delete": {
                "method": "DELETE",
                "url": "/api/v1/admin/images/{filename}",
                "headers": {"Authorization": "Bearer TOKEN"},
                "description": "Delete uploaded image",
            },
        },
        "webhooks": {
            "stripe": {
                "method": "POST",
                "url": "/api/v1/webhooks/stripe",
                "description": "Stripe webhook endpoint (internal use)",
            }
        },
        "utility": {
            "root": {
                "method": "GET",
                "url": "/",
                "description": "API metadata and available endpoints",
            },
            "health": {
                "method": "GET",
                "url": "/health",
                "description": "Health check endpoint",
            },
            "routes": {
                "method": "GET",
                "url": "/routes-simple",
                "description": "List all routes (simple format)",
            },
        },
    }

    with open(DOCS_DIR / "example_requests.json", "w") as f:
        json.dump(examples, f, indent=2)

    print(f"✅ Example requests generated ({len(examples)} categories)")


def generate_endpoint_list():
    """Generate markdown list of all endpoints"""
    endpoints_md = """# CampusConnect API Endpoints

## Public Endpoints (No Authentication Required)

### Institutions
- `GET /api/v1/institutions` - List institutions
- `GET /api/v1/institutions/{ipeds_id}` - Get institution by IPEDS ID
- `GET /api/v1/institutions/by-id/{institution_id}` - Get institution by database ID
- `GET /api/v1/institutions/{ipeds_id}/admissions` - Get admissions data
- `GET /api/v1/institutions/{ipeds_id}/tuition` - Get tuition data
- `GET /api/v1/institutions/{ipeds_id}/financial-overview` - Get financial overview

### Scholarships
- `GET /api/v1/scholarships` - List scholarships
- `GET /api/v1/scholarships/{scholarship_id}` - Get scholarship by ID

### Utility
- `GET /` - API metadata
- `GET /health` - Health check
- `GET /routes-simple` - List all routes

---

## Admin Endpoints (Authentication Required)

### Authentication
- `POST /api/v1/admin/auth/validate-invitation` - Validate invitation code
- `POST /api/v1/admin/auth/register` - Register new admin
- `POST /api/v1/admin/auth/login` - Login
- `GET /api/v1/admin/auth/me` - Get current user

### Invitations (Super Admin Only)
- `POST /api/v1/admin/auth/invitations` - Create invitation
- `GET /api/v1/admin/auth/invitations` - List invitations
- `DELETE /api/v1/admin/auth/invitations/{invitation_id}` - Delete invitation

### Profile & Settings
- `GET /api/v1/admin/profile/entity` - Get managed entity
- `GET /api/v1/admin/profile/display-settings` - Get display settings
- `PUT /api/v1/admin/profile/display-settings` - Update display settings

### Gallery Management (Premium)
- `GET /api/v1/admin/gallery` - List gallery images
- `POST /api/v1/admin/gallery` - Upload image
- `PUT /api/v1/admin/gallery/{image_id}` - Update image metadata
- `DELETE /api/v1/admin/gallery/{image_id}` - Delete image
- `PUT /api/v1/admin/gallery/reorder` - Reorder images

### Video Management (Premium)
- `GET /api/v1/admin/videos` - List videos
- `POST /api/v1/admin/videos` - Add video
- `PUT /api/v1/admin/videos/{video_id}` - Update video
- `DELETE /api/v1/admin/videos/{video_id}` - Delete video
- `PUT /api/v1/admin/videos/reorder` - Reorder videos

### Extended Information (Premium)
- `GET /api/v1/admin/extended-info` - Get extended info
- `PUT /api/v1/admin/extended-info` - Update extended info
- `DELETE /api/v1/admin/extended-info` - Clear extended info

### Outreach
- `GET /api/v1/admin/outreach/stats` - Get outreach statistics
- `GET /api/v1/admin/outreach` - List outreach messages
- `POST /api/v1/admin/outreach` - Create outreach message
- `PUT /api/v1/admin/outreach/{outreach_id}` - Update outreach message
- `GET /api/v1/admin/outreach/templates` - List templates
- `POST /api/v1/admin/outreach/templates` - Create template

### Data Management
- `GET /api/v1/admin/data/admissions` - Get admissions data
- `PUT /api/v1/admin/data/admissions/{admission_id}` - Update admissions data
- `POST /api/v1/admin/data/admissions/{admission_id}/verify` - Verify admissions data
- `GET /api/v1/admin/data/tuition` - Get tuition data
- `PUT /api/v1/admin/data/tuition/{tuition_id}` - Update tuition data
- `POST /api/v1/admin/data/tuition/{tuition_id}/verify` - Verify tuition data

### Image Upload
- `POST /api/v1/admin/images/upload` - Upload image
- `GET /api/v1/admin/images/list` - List images
- `DELETE /api/v1/admin/images/{filename}` - Delete image

### Subscriptions
- `POST /api/v1/admin/subscriptions/create-checkout` - Create checkout session
- `GET /api/v1/admin/subscriptions/current` - Get current subscription
- `POST /api/v1/admin/subscriptions/cancel` - Cancel subscription
- `GET /api/v1/admin/subscriptions/portal` - Get customer portal

---

## Webhooks

- `POST /api/v1/webhooks/stripe` - Stripe webhook handler

---

**Total Endpoints:** 50+

**Last Updated:** November 2025
"""

    with open(DOCS_DIR / "endpoints.md", "w") as f:
        f.write(endpoints_md)

    print("✅ Endpoint reference generated (50+ endpoints)")


if __name__ == "__main__":
    asyncio.run(generate_docs())
