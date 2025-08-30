export interface PlatformConfig {
  id: number;
  platform: string;
  additional_settings: Record<string, any>;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface PlatformConfigUpdate {
  additional_settings?: Record<string, any>;
  enabled?: boolean;
}

export interface SupportedPlatformsResponse {
  supported_platforms: string[];
  total: number;
}

export interface StreamInfo {
  platform: string;
  streamer_id: string;
  streamer_name: string;
  title: string;
  is_live: boolean;
  viewer_count?: number;
  thumbnail_url?: string;
  started_at?: string;
}

export interface PlatformFieldSchema {
  key: string;
  label: string;
  type: 'text' | 'password' | 'number' | 'select';
  required: boolean;
  description: string;
  help_url?: string;
  placeholder?: string;
  options?: string[];
}

export interface PlatformSchema {
  required_fields: PlatformFieldSchema[];
  optional_fields: PlatformFieldSchema[];
}

export interface PlatformSchemas {
  [platformName: string]: PlatformSchema;
}