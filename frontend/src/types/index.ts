// 사용자 관련 타입
export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
}

// 플랫폼 설정 타입
export interface PlatformConfig {
  platform: string;
  enabled: boolean;
  api_key?: string;
  api_secret?: string;
  custom_arguments?: string;
  created_at: string;
  updated_at: string;
}

// 시스템 설정 타입
export interface SystemConfig {
  key: string;
  value: string;
  description?: string;
}

// 회전 정책 타입
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

// 녹화 스케줄 타입
export interface RecordingSchedule {
  id: number;
  platform: string;
  streamer_id: string;
  streamer_name: string;
  quality: string;
  custom_arguments?: string;
  enabled: boolean;
  
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

// 녹화 타입
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

// 녹화 작업 타입
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

// 스토리지 사용량 통계 타입
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

// API 응답 타입
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

// 폼 데이터 타입
export interface CreateScheduleForm {
  platform: string;
  streamer_id: string;
  streamer_name: string;
  quality: string;
  custom_arguments?: string;
  
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

// 인증 타입
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
