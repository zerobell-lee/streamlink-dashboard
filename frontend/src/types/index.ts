// User related types
export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

// Platform configuration types
export interface PlatformConfig {
  platform: string;
  enabled: boolean;
  api_key?: string;
  api_secret?: string;
  custom_arguments?: string;
  created_at: string;
  updated_at: string;
}

// System configuration types
export interface SystemConfig {
  key: string;
  value: string;
  description?: string;
}

// Rotation policy types
export interface RotationPolicy {
  id: number;
  name: string;
  policy_type: 'time' | 'count' | 'size';
  max_age_days?: number;
  max_count?: number;
  max_size_gb?: number;
  enabled: boolean;
  priority: number;
  protect_favorites: boolean;
  delete_empty_files: boolean;
  min_file_size_mb?: number;
  exclude_patterns?: string;
  created_at: string;
  updated_at: string;
}

// Recording schedule types
export interface RecordingSchedule {
  id: number;
  platform: string;
  streamer_id: string;
  streamer_name: string;
  quality: string;
  custom_arguments?: string;
  enabled: boolean;
  
  // Output file configuration
  output_format?: string;
  filename_template?: string;
  
  // Inline rotation settings
  rotation_enabled: boolean;
  rotation_type?: 'time' | 'count' | 'size';
  max_age_days?: number;
  max_count?: number;
  max_size_gb?: number;
  protect_favorites: boolean;
  delete_empty_files: boolean;
  
  created_at: string;
  updated_at: string;
}

// Recording types
export interface Recording {
  id: number;
  schedule_id: number;
  schedule?: RecordingSchedule;
  file_name: string;
  file_path: string;
  file_size: number;
  duration?: number;
  status: 'recording' | 'completed' | 'failed' | 'paused';
  error_message?: string;
  is_favorite: boolean;
  start_time: string;
  end_time?: string;
  platform: string;
  streamer_id: string;
  streamer_name: string;
  quality: string;
  created_at: string;
  updated_at: string;
}

// Recording job types
export interface RecordingJob {
  id: number;
  schedule_id: number;
  schedule?: RecordingSchedule;
  status: 'running' | 'paused' | 'completed' | 'failed';
  start_time?: string;
  end_time?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

// Storage usage statistics types
export interface StorageUsage {
  total_recordings: number;
  total_size_bytes: number;
  total_size_gb: number;
  favorite_recordings: number;
  favorite_size_bytes: number;
  favorite_size_gb: number;
  schedule_statistics: ScheduleStatistics[];
}

export interface ScheduleStatistics {
  schedule_id: number;
  streamer_name: string;
  platform: string;
  policy_name?: string;
  recordings_count: number;
  size_bytes: number;
  size_gb: number;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Form data types
export interface CreateScheduleForm {
  platform: string;
  streamer_id: string;
  streamer_name: string;
  quality: string;
  custom_arguments?: string;
  
  // Output file configuration
  output_format?: string;
  filename_template?: string;
  
  // Inline rotation settings
  rotation_enabled?: boolean;
  rotation_type?: 'time' | 'count' | 'size';
  max_age_days?: number;
  max_count?: number;
  max_size_gb?: number;
  protect_favorites?: boolean;
  delete_empty_files?: boolean;
}

export interface UpdateScheduleForm extends Partial<CreateScheduleForm> {
  enabled?: boolean;
}

export interface CreateRotationPolicyForm {
  name: string;
  policy_type: 'time' | 'count' | 'size';
  max_age_days?: number;
  max_count?: number;
  max_size_gb?: number;
  priority: number;
  protect_favorites: boolean;
  delete_empty_files: boolean;
  min_file_size_mb?: number;
  exclude_patterns?: string;
}

// Authentication types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Logging related types
export interface LoggingConfig {
  enable_file_logging: boolean;
  enable_json_logging: boolean;
  log_level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL';
  log_retention_days: number;
  categories: {
    app: boolean;
    database: boolean;
    api: boolean;
    scheduler: boolean;
    error: boolean;
  };
}

export interface LogFileInfo {
  path: string;
  size: number;
  size_mb: number;
  modified: string;
  exists: boolean;
  error?: string;
}

export interface LogFilesResponse {
  log_files: { [filename: string]: LogFileInfo };
  logs_directory: string;
}

export interface LogFileContent {
  filename: string;
  total_lines: number;
  showing_lines: number;
  content: string[];
}

export interface LogCleanupResponse {
  message: string;
  cleaned_files_count: number;
  cleaned_files: string[];
  max_age_days: number;
}

// Enhanced Log Management Types
export interface LogSearchRequest {
  query: string;
  category?: string;
  level?: string;
  start_time?: string;
  end_time?: string;
  limit: number;
}

export interface LogEntry {
  timestamp?: string;
  logger?: string;
  level: string;
  message: string;
}

export interface LogSearchResult {
  file: string;
  line_number: number;
  content: string;
  parsed: LogEntry;
}

export interface LogSearchResponse {
  results: LogSearchResult[];
  total_found: number;
  search_params: LogSearchRequest;
  truncated: boolean;
}

export interface LogAnalytics {
  time_range: {
    start: string;
    end: string;
    hours: number;
  };
  by_level: { [level: string]: number };
  by_category: { [category: string]: number };
  by_hour: { [hour: string]: number };
  error_patterns: Array<{
    timestamp?: string;
    level: string;
    message: string;
    category: string;
  }>;
  total_entries: number;
}

export interface EnhancedLogFileInfo extends LogFileInfo {
  line_count?: number;
  category: string;
  is_json: boolean;
  can_search: boolean;
}

export interface EnhancedLogFilesResponse {
  log_files: { [filename: string]: EnhancedLogFileInfo };
  logs_directory: string;
  total_files: number;
}

export interface PaginatedLogContent {
  filename: string;
  total_lines: number;
  total_pages: number;
  current_page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
  content: string[];
  reversed: boolean;
}

export interface LogCategoriesResponse {
  categories: string[];
  category_info: { [category: string]: any };
}

export interface LogStreamMessage {
  timestamp: string;
  file: string;
  category: string;
  content: string;
  parsed: LogEntry;
  error?: string;
}
