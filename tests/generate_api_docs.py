"""
Generate comprehensive API documentation for frontend developers
Exports OpenAPI schema and creates sample requests/responses
"""
import httpx
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
DOCS_DIR = Path("api_docs")
DOCS_DIR.mkdir(exist_ok=True)

async def generate_docs():
    """Generate API documentation"""
    print("📝 Generating API documentation...")
    
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
        
        print("\n🎉 Documentation generated in api_docs/")

def generate_typescript_interfaces(schema):
    """Generate TypeScript interfaces from OpenAPI schema"""
    interfaces = []
    
    # Institution interface
    interfaces.append("""
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
""")
    
    # Scholarship interface
    interfaces.append("""
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
""")
    
    # Admin User interface
    interfaces.append("""
export interface AdminUser {
  id: number;
  email: string;
  entity_type: 'institution' | 'scholarship';
  entity_id: number;
  role: string;
  is_active: boolean;
}
""")
    
    # Display Settings interface
    interfaces.append("""
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
""")
    
    # Institution Image interface
    interfaces.append("""
export interface InstitutionImage {
  id: number;
  institution_id: number;
  image_url: string;
  cdn_url: string;
  filename: string;
  caption: string | null;
  display_order: number;
  is_featured: boolean;
  image_type: string | null; // 'campus' | 'students' | 'facilities' | 'events'
  created_at: string;
}
""")
    
    # Institution Video interface
    interfaces.append("""
export interface InstitutionVideo {
  id: number;
  institution_id: number;
  video_url: string;
  title: string | null;
  description: string | null;
  thumbnail_url: string | null;
  video_type: string | null; // 'tour' | 'testimonial' | 'overview' | 'custom'
  display_order: number;
  is_featured: boolean;
  created_at: string;
}
""")
    
    # Extended Info interface
    interfaces.append("""
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
""")
    
    # Subscription interface
    interfaces.append("""
export interface Subscription {
  status: string;
  plan_tier: string;
  current_period_start?: number;
  current_period_end?: number;
  cancel_at_period_end?: boolean;
  trial_end?: number | null;
}
""")
    
    # Auth Token interface
    interfaces.append("""
export interface AuthToken {
  access_token: string;
  token_type: 'bearer';
}
""")
    
    # Write to file
    with open(DOCS_DIR / "types.ts", "w") as f:
        f.write("// CampusConnect API TypeScript Interfaces\n")
        f.write("// Auto-generated - Do not edit manually\n\n")
        f.write("\n".join(interfaces))
    
    print("✅ TypeScript interfaces generated")

def generate_example_requests():
    """Generate example API requests"""
    examples = {
        "authentication": {
            "register": {
                "method": "POST",
                "url": "/api/v1/admin/auth/register",
                "body": {
                    "email": "admin@example.com",
                    "password": "securepassword123",
                    "entity_type": "institution",
                    "entity_id": 1
                }
            },
            "login": {
                "method": "POST",
                "url": "/api/v1/admin/auth/login",
                "content_type": "application/x-www-form-urlencoded",
                "body": {
                    "username": "admin@example.com",
                    "password": "securepassword123"
                }
            }
        },
        "institutions": {
            "list_all": {
                "method": "GET",
                "url": "/api/v1/institutions?limit=100&offset=0"
            },
            "filter_by_state": {
                "method": "GET",
                "url": "/api/v1/institutions?state=NH"
            }
        },
        "gallery": {
            "upload_image": {
                "method": "POST",
                "url": "/api/v1/admin/gallery",
                "headers": {"Authorization": "Bearer TOKEN"},
                "content_type": "multipart/form-data",
                "body": {
                    "file": "[binary]",
                    "caption": "Beautiful campus view",
                    "image_type": "campus"
                }
            },
            "list_images": {
                "method": "GET",
                "url": "/api/v1/admin/gallery",
                "headers": {"Authorization": "Bearer TOKEN"}
            },
            "reorder": {
                "method": "PUT",
                "url": "/api/v1/admin/gallery/reorder",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "image_ids": [3, 1, 2]
                }
            }
        },
        "videos": {
            "add_video": {
                "method": "POST",
                "url": "/api/v1/admin/videos",
                "headers": {"Authorization": "Bearer TOKEN"},
                "body": {
                    "video_url": "https://youtube.com/watch?v=...",
                    "title": "Campus Tour 2025",
                    "description": "Virtual tour",
                    "video_type": "tour",
                    "is_featured": True
                }
            },
            "list_videos": {
                "method": "GET",
                "url": "/api/v1/admin/videos",
                "headers": {"Authorization": "Bearer TOKEN"}
            }
        },
        "extended_info": {
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
                            "content": "Excellence...",
                            "order": 1
                        }
                    ]
                }
            }
        }
    }
    
    with open(DOCS_DIR / "example_requests.json", "w") as f:
        json.dump(examples, f, indent=2)
    
    print("✅ Example requests generated")

if __name__ == "__main__":
    import asyncio
    asyncio.run(generate_docs())
