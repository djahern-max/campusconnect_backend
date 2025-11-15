// CampusConnect API TypeScript Interfaces
// Auto-generated - Do not edit manually


export interface Institution {
  id: number;
  ipeds_id: number;
  name: string;
  city: string;
  state: string;
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
  show_image_gallery: boolean;
  show_video: boolean;
  show_extended_info: boolean;
  custom_tagline: string | null;
  custom_description: string | null;
  extended_description: string | null;
  layout_style: string;
  primary_color: string | null;
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
