// CampusConnect API TypeScript Interfaces
// Auto-generated - Do not edit manually


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


export interface AdminUser {
  id: number;
  email: string;
  entity_type: 'institution' | 'scholarship';
  entity_id: number;
  role: string;
  is_active: boolean;
}


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


export interface Subscription {
  status: string;
  plan_tier: string;
  current_period_start?: number;
  current_period_end?: number;
  cancel_at_period_end?: boolean;
  trial_end?: number | null;
}


export interface AuthToken {
  access_token: string;
  token_type: 'bearer';
}
