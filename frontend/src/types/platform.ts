// Platform Definition (Registry-based, code-managed)
export interface PlatformDefinition {
  name: string;
  display_name: string;
  description: string;
  requires_auth: boolean;
  supports_chat: boolean;
  supports_vod: boolean;
  help_text: string;
  setup_instructions: string;
  config_schema: Record<string, any>; // JSON Schema
  supported_qualities: string[];
  default_streamlink_args: string[];
}

// User Configuration (Database-managed)
export interface PlatformUserConfig {
  platform_name: string;
  user_credentials: Record<string, any>;
  custom_settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface PlatformUserConfigCreate {
  user_credentials?: Record<string, any>;
  custom_settings?: Record<string, any>;
}

export interface PlatformUserConfigUpdate {
  user_credentials?: Record<string, any> | null;
  custom_settings?: Record<string, any> | null;
}

// Combined Platform Information
export interface PlatformInfo {
  definition: PlatformDefinition;
  user_config?: PlatformUserConfig;
  is_configured: boolean;
}

// API Responses
export interface PlatformListResponse {
  platforms: PlatformInfo[];
  total: number;
}

export interface PlatformDefinitionListResponse {
  platforms: PlatformDefinition[];
  total: number;
}

export interface PlatformSchemaResponse {
  platform_name: string;
  schema: Record<string, any>;
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

export interface StreamUrl {
  url: string;
  quality: string;
  format: string;
  bandwidth?: number;
}

export interface StreamUrlsResponse {
  platform: string;
  streamer_id: string;
  stream_urls: StreamUrl[];
}

export interface StreamlinkArgsResponse {
  platform: string;
  streamer_id: string;
  quality: string;
  arguments: string[];
  command: string;
}