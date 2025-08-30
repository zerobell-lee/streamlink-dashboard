import { api } from './api';

// Server time management
let serverTimeOffset: number | null = null;
let isInitializing = false;

// Initialize server time offset
const initializeServerTime = async () => {
  if (serverTimeOffset !== null || isInitializing) return;
  
  isInitializing = true;
  try {
    const response = await api.system.getTime();
    const serverTime = new Date(response.data.current_time);
    const clientTime = new Date();
    serverTimeOffset = serverTime.getTime() - clientTime.getTime();
    console.log('Server time offset initialized:', serverTimeOffset, 'ms');
  } catch (error) {
    console.warn('Failed to get server time, using client time:', error);
    serverTimeOffset = 0;
  }
  isInitializing = false;
};

// Get current server time
export const getServerTime = async (): Promise<Date> => {
  await initializeServerTime();
  return new Date(Date.now() + (serverTimeOffset || 0));
};

// Get server time synchronously (after initialization)
export const getServerTimeSync = (): Date => {
  return new Date(Date.now() + (serverTimeOffset || 0));
};

// Date and time utilities
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  
  // Use system timezone and locale
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false
  });
};

export const formatRelativeTime = (dateString: string): string => {
  const now = new Date();
  
  // Backend sends system timezone datetime, parse normally
  const date = new Date(dateString);
  
  const diffMs = now.getTime() - date.getTime();
  const diffMinutes = Math.floor(diffMs / (1000 * 60));
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMinutes < 1) {
    return 'just now';
  } else if (diffMinutes < 60) {
    return `${diffMinutes}m ago`;
  } else if (diffHours < 24) {
    return `${diffHours}h ago`;
  } else if (diffDays < 7) {
    return `${diffDays}d ago`;
  } else {
    return formatDate(dateString);
  }
};

export const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
};

export const formatFileSize = (bytes: number): string => {
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  if (bytes === 0) return '0 B';
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
};