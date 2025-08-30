import axios from 'axios';

// API base configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add auth token)
apiClient.interceptors.request.use(
  (config) => {
    // Get token from Zustand auth store
    const authStorage = localStorage.getItem('auth-storage');
    let token = null;
    
    if (authStorage) {
      try {
        const parsed = JSON.parse(authStorage);
        token = parsed.state?.token;
      } catch (e) {
        console.warn('Failed to parse auth storage');
      }
    }
    
    if (token) {
      // Check if token is expired before using it
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const currentTime = Math.floor(Date.now() / 1000);
        
        if (payload.exp && payload.exp < currentTime) {
          // Token is expired, remove from storage and redirect to login
          localStorage.removeItem('auth-storage');
          if (!window.location.pathname.includes('/login')) {
            window.location.href = '/login';
          }
          return Promise.reject(new Error('Token expired'));
        }
      } catch (e) {
        console.warn('Failed to parse JWT token');
      }
      
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (error handling)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear auth storage and redirect to login page on 401 error
      localStorage.removeItem('auth-storage');
      localStorage.removeItem('auth_token'); // legacy cleanup
      
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const api = {
  // Authentication
  auth: {
    login: (credentials: { username: string; password: string }) =>
      apiClient.post('/api/v1/auth/login', credentials),
    register: (userData: { username: string; email: string; password: string }) =>
      apiClient.post('/api/v1/auth/register', userData),
    logout: () => apiClient.post('/api/v1/auth/logout'),
    changePassword: (data: { current_password: string; new_password: string }) =>
      apiClient.put('/api/v1/auth/password', data),
  },

  // Users
  users: {
    getCurrentUser: () => apiClient.get('/api/v1/users/me'),
    updateProfile: (data: any) => apiClient.put('/api/v1/users/me', data),
  },

  // Schedules
  schedules: {
    getAll: () => apiClient.get('/api/v1/scheduler/schedules'),
    getById: (id: number) => apiClient.get(`/api/v1/schedules/${id}`),
    create: (data: any) => apiClient.post('/api/v1/scheduler/schedules', data),
    update: (id: number, data: any) => apiClient.put(`/api/v1/schedules/${id}`, data),
    delete: (id: number) => apiClient.delete(`/api/v1/schedules/${id}`),
    toggle: (id: number) => apiClient.post(`/api/v1/schedules/${id}/toggle`),
  },


  // Recordings
  recordings: {
    getAll: (params?: any) => apiClient.get('/api/v1/recordings', { params }),
    getById: (id: number) => apiClient.get(`/api/v1/recordings/${id}`),
    delete: (id: number) => apiClient.delete(`/api/v1/recordings/${id}`),
    toggleFavorite: (id: number) => apiClient.put(`/api/v1/recordings/${id}/favorite`),
    download: (id: number) => apiClient.get(`/api/v1/recordings/${id}/download`, { responseType: 'blob' }),
  },


  // System settings
  system: {
    getTime: () => apiClient.get('/api/v1/system/time'),
    getConfigs: () => apiClient.get('/api/v1/system/configs'),
    updateConfig: (key: string, value: any) => apiClient.put('/api/v1/system/configs', { key, value }),
    getRotationPolicies: () => apiClient.get('/api/v1/system/rotation/policies'),
    applyRotationPolicies: () => apiClient.post('/api/v1/system/rotation/apply'),
    getStorageUsage: () => apiClient.get('/api/v1/system/rotation/storage'),
    getMonitoringInterval: () => apiClient.get('/api/v1/system/monitoring-interval'),
    setMonitoringInterval: (intervalSeconds: number) => 
      apiClient.post('/api/v1/system/monitoring-interval', { interval_seconds: intervalSeconds }),
  },

  // Scheduler
  scheduler: {
    getStatus: () => apiClient.get('/api/v1/scheduler/status'),
    start: () => apiClient.post('/api/v1/scheduler/start'),
    stop: () => apiClient.post('/api/v1/scheduler/stop'),
    getActiveRecordings: () => apiClient.get('/api/v1/scheduler/active-recordings'),
    stopAllRecordings: () => apiClient.post('/api/v1/scheduler/stop-all-recordings'),
  },

  // Platforms
  platforms: {
    getAll: () => apiClient.get('/api/v1/platforms/'),
    getSupported: () => apiClient.get('/api/v1/platforms/supported'),
    getSchemas: () => apiClient.get('/api/v1/platforms/schema'),
    getConfig: (platformName: string) => apiClient.get(`/api/v1/platforms/${platformName}/config`),
    updateConfig: (platformName: string, data: any) => apiClient.put(`/api/v1/platforms/${platformName}/config`, data),
    initialize: () => apiClient.post('/api/v1/platforms/initialize'),
    getStreamInfo: (platformName: string, streamerId: string) => 
      apiClient.get(`/api/v1/platforms/${platformName}/stream-info?streamer_id=${streamerId}`),
  },
};
