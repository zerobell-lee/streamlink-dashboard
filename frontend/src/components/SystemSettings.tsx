'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/auth-store';
import { api } from '@/lib/api';
import { 
  Settings, 
  Key, 
  Clock,
  Save,
  User,
  FileText,
  Eye,
  Trash2,
  Activity
} from 'lucide-react';
import type { 
  LoggingConfig, 
  LogFilesResponse, 
  LogFileContent,
  LogCleanupResponse 
} from '@/types';

type TabType = 'security' | 'monitoring' | 'logging';

// Security Tab Component
function SecurityTab() {
  const { user } = useAuthStore();
  const [passwords, setPasswords] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [passwordLoading, setPasswordLoading] = useState(false);
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState(false);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordLoading(true);

    if (passwords.newPassword !== passwords.confirmPassword) {
      setPasswordError('New passwords do not match');
      setPasswordLoading(false);
      return;
    }

    if (passwords.newPassword.length < 6) {
      setPasswordError('New password must be at least 6 characters');
      setPasswordLoading(false);
      return;
    }

    try {
      await api.auth.changePassword({
        current_password: passwords.currentPassword,
        new_password: passwords.newPassword
      });
      setPasswordSuccess(true);
      setPasswords({ currentPassword: '', newPassword: '', confirmPassword: '' });
      setTimeout(() => setPasswordSuccess(false), 3000);
    } catch (err: any) {
      setPasswordError(err.response?.data?.detail || 'Password change failed');
    } finally {
      setPasswordLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 flex items-center mb-4">
          <Key className="h-5 w-5 mr-2 text-gray-600" />
          Change Password
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Current user: <span className="font-medium">{user?.username}</span>
        </p>
        
        <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
          {passwordError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{passwordError}</p>
            </div>
          )}
          
          {passwordSuccess && (
            <div className="bg-green-50 border border-green-200 rounded-md p-3">
              <p className="text-sm text-green-600">Password changed successfully!</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Password
            </label>
            <input
              type="password"
              required
              value={passwords.currentPassword}
              onChange={(e) => setPasswords(prev => ({ ...prev, currentPassword: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <input
              type="password"
              required
              value={passwords.newPassword}
              onChange={(e) => setPasswords(prev => ({ ...prev, newPassword: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password
            </label>
            <input
              type="password"
              required
              value={passwords.confirmPassword}
              onChange={(e) => setPasswords(prev => ({ ...prev, confirmPassword: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700"
            />
          </div>

          <button
            type="submit"
            disabled={passwordLoading}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50"
          >
            <Key className="h-4 w-4 mr-2" />
            {passwordLoading ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      </div>
    </div>
  );
}

// Monitoring Tab Component  
function MonitoringTab() {
  const [monitoringInterval, setMonitoringInterval] = useState(60);
  const [intervalLoading, setIntervalLoading] = useState(false);
  const [intervalError, setIntervalError] = useState('');
  const [intervalSuccess, setIntervalSuccess] = useState(false);

  useEffect(() => {
    const loadMonitoringInterval = async () => {
      try {
        const response = await api.system.getMonitoringInterval();
        setMonitoringInterval(response.data.interval_seconds);
      } catch (error) {
        console.warn('Failed to load monitoring interval:', error);
      }
    };

    loadMonitoringInterval();
  }, []);

  const handleIntervalChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setIntervalError('');
    setIntervalLoading(true);

    if (monitoringInterval < 5 || monitoringInterval > 3600) {
      setIntervalError('Monitoring interval must be between 5 seconds and 1 hour');
      setIntervalLoading(false);
      return;
    }

    try {
      await api.system.setMonitoringInterval(monitoringInterval);
      setIntervalSuccess(true);
      setTimeout(() => setIntervalSuccess(false), 3000);
    } catch (err: any) {
      setIntervalError(err.response?.data?.detail || 'Failed to update monitoring interval');
    } finally {
      setIntervalLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Stream Monitoring Interval
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          How often the system checks if streams are live. Lower values provide faster detection but use more resources.
        </p>
        
        <form onSubmit={handleIntervalChange} className="space-y-4 max-w-md">
          {intervalError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{intervalError}</p>
            </div>
          )}
          
          {intervalSuccess && (
            <div className="bg-green-50 border border-green-200 rounded-md p-3">
              <p className="text-sm text-green-600">Monitoring interval updated successfully!</p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Interval (seconds)
            </label>
            <div className="flex items-center space-x-2">
              <input
                type="number"
                min="5"
                max="3600"
                required
                value={monitoringInterval}
                onChange={(e) => setMonitoringInterval(Number(e.target.value))}
                className="w-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700"
              />
              <span className="text-sm text-gray-500">
                ({monitoringInterval} seconds = {Math.round(monitoringInterval / 60 * 100) / 100} minutes)
              </span>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Minimum: 5 seconds, Maximum: 3600 seconds (1 hour)
            </p>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => setMonitoringInterval(5)}
              className="px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              5s (Fast)
            </button>
            <button
              type="button"
              onClick={() => setMonitoringInterval(30)}
              className="px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              30s
            </button>
            <button
              type="button"
              onClick={() => setMonitoringInterval(60)}
              className="px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors"
            >
              60s (Default)
            </button>
          </div>

          <button
            type="submit"
            disabled={intervalLoading}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-md transition-colors disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2" />
            {intervalLoading ? 'Saving...' : 'Save Interval'}
          </button>
        </form>
      </div>
    </div>
  );
}

// Logging Tab Component
function LoggingTab() {
  const [loggingConfig, setLoggingConfig] = useState<LoggingConfig>({
    enable_file_logging: true,
    enable_json_logging: false,
    log_level: 'INFO',
    log_retention_days: 30,
    categories: {
      app: true,
      database: true,
      api: true,
      scheduler: true,
      error: true
    }
  });
  const [loggingLoading, setLoggingLoading] = useState(false);
  const [loggingError, setLoggingError] = useState('');
  const [loggingSuccess, setLoggingSuccess] = useState(false);
  
  const [logFiles, setLogFiles] = useState<LogFilesResponse | null>(null);
  const [logFilesLoading, setLogFilesLoading] = useState(false);
  const [selectedLogFile, setSelectedLogFile] = useState<string | null>(null);
  const [logContent, setLogContent] = useState<LogFileContent | null>(null);
  const [logContentLoading, setLogContentLoading] = useState(false);
  
  const [cleanupLoading, setCleanupLoading] = useState(false);
  const [cleanupSuccess, setCleanupSuccess] = useState(false);

  useEffect(() => {
    const loadLoggingData = async () => {
      try {
        const response = await api.system.getLoggingConfig();
        setLoggingConfig(response.data);
      } catch (error) {
        console.warn('Failed to load logging config:', error);
      }

      await loadLogFiles();
    };

    loadLoggingData();
  }, []);

  const loadLogFiles = async () => {
    setLogFilesLoading(true);
    try {
      const response = await api.system.getLogFiles();
      setLogFiles(response.data);
    } catch (error) {
      console.warn('Failed to load log files:', error);
    } finally {
      setLogFilesLoading(false);
    }
  };

  const handleLoggingConfigChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoggingError('');
    setLoggingLoading(true);

    try {
      await api.system.updateLoggingConfig(loggingConfig);
      setLoggingSuccess(true);
      setTimeout(() => setLoggingSuccess(false), 3000);
    } catch (err: any) {
      setLoggingError(err.response?.data?.detail || 'Failed to update logging configuration');
    } finally {
      setLoggingLoading(false);
    }
  };

  const handleLogFileView = async (filename: string) => {
    setSelectedLogFile(filename);
    setLogContentLoading(true);
    
    try {
      const response = await api.system.getLogFileContent(filename, 100);
      setLogContent(response.data);
    } catch (error) {
      console.error('Failed to load log file content:', error);
    } finally {
      setLogContentLoading(false);
    }
  };

  const handleLogCleanup = async () => {
    setCleanupLoading(true);
    
    try {
      await api.system.cleanupLogs(loggingConfig.log_retention_days);
      setCleanupSuccess(true);
      setTimeout(() => setCleanupSuccess(false), 3000);
      await loadLogFiles();
    } catch (error) {
      console.error('Failed to cleanup logs:', error);
    } finally {
      setCleanupLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Logging Configuration */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 flex items-center mb-4">
          <Settings className="h-5 w-5 mr-2 text-gray-600" />
          Logging Configuration
        </h3>
        <p className="text-sm text-gray-600 mb-4">
          Configure system logging settings and categories.
        </p>
        
        <form onSubmit={handleLoggingConfigChange} className="space-y-6 max-w-2xl">
          {loggingError && (
            <div className="bg-red-50 border border-red-200 rounded-md p-3">
              <p className="text-sm text-red-600">{loggingError}</p>
            </div>
          )}
          
          {loggingSuccess && (
            <div className="bg-green-50 border border-green-200 rounded-md p-3">
              <p className="text-sm text-green-600">Logging configuration updated successfully!</p>
            </div>
          )}

          {/* Basic Settings */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Log Level
              </label>
              <select
                value={loggingConfig.log_level}
                onChange={(e) => setLoggingConfig(prev => ({ ...prev, log_level: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700"
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
                <option value="CRITICAL">CRITICAL</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Retention Days
              </label>
              <input
                type="number"
                min="1"
                max="365"
                value={loggingConfig.log_retention_days}
                onChange={(e) => setLoggingConfig(prev => ({ ...prev, log_retention_days: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-700"
              />
            </div>
          </div>

          {/* Feature Toggles */}
          <div className="space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="file-logging"
                checked={loggingConfig.enable_file_logging}
                onChange={(e) => setLoggingConfig(prev => ({ ...prev, enable_file_logging: e.target.checked }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="file-logging" className="ml-2 block text-sm text-gray-900">
                Enable File Logging
              </label>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                id="json-logging"
                checked={loggingConfig.enable_json_logging}
                onChange={(e) => setLoggingConfig(prev => ({ ...prev, enable_json_logging: e.target.checked }))}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label htmlFor="json-logging" className="ml-2 block text-sm text-gray-900">
                Enable JSON Logging (for analysis tools)
              </label>
            </div>
          </div>

          {/* Categories */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Log Categories
            </label>
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(loggingConfig.categories).map(([category, enabled]) => (
                <div key={category} className="flex items-center">
                  <input
                    type="checkbox"
                    id={`category-${category}`}
                    checked={enabled}
                    onChange={(e) => setLoggingConfig(prev => ({
                      ...prev,
                      categories: { ...prev.categories, [category]: e.target.checked }
                    }))}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor={`category-${category}`} className="ml-2 block text-sm text-gray-900 capitalize">
                    {category}
                  </label>
                </div>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={loggingLoading}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50"
          >
            <Save className="h-4 w-4 mr-2" />
            {loggingLoading ? 'Saving...' : 'Save Configuration'}
          </button>
        </form>
      </div>

      {/* Log Files Management */}
      <div className="border-t pt-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <Activity className="h-5 w-5 mr-2 text-gray-600" />
            Log Files
          </h3>
          <div className="flex space-x-2">
            <button
              onClick={loadLogFiles}
              disabled={logFilesLoading}
              className="flex items-center px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors disabled:opacity-50"
            >
              <Activity className="h-3 w-3 mr-1" />
              {logFilesLoading ? 'Loading...' : 'Refresh'}
            </button>
            <button
              onClick={handleLogCleanup}
              disabled={cleanupLoading}
              className="flex items-center px-3 py-1 text-xs font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors disabled:opacity-50"
            >
              <Trash2 className="h-3 w-3 mr-1" />
              {cleanupLoading ? 'Cleaning...' : 'Cleanup Old'}
            </button>
          </div>
        </div>

        {cleanupSuccess && (
          <div className="bg-green-50 border border-green-200 rounded-md p-3 mb-4">
            <p className="text-sm text-green-600">Log cleanup completed successfully!</p>
          </div>
        )}

        {logFiles && (
          <div className="space-y-3">
            {Object.entries(logFiles.log_files).map(([filename, fileInfo]) => (
              <div key={filename} className="border rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">{filename}</h4>
                    <p className="text-xs text-gray-500">
                      Size: {fileInfo.size_mb} MB • Modified: {new Date(fileInfo.modified).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => handleLogFileView(filename)}
                    className="flex items-center px-2 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors"
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Log Content Viewer */}
      {selectedLogFile && (
        <div className="border-t pt-8">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">
              {selectedLogFile} Content
            </h3>
            <button
              onClick={() => setSelectedLogFile(null)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              ✕
            </button>
          </div>
          
          {logContentLoading ? (
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-500">Loading log content...</p>
            </div>
          ) : logContent ? (
            <div className="bg-gray-900 text-gray-100 rounded-lg p-4 max-h-96 overflow-y-auto">
              <div className="text-xs mb-2 text-gray-400">
                Showing last {logContent.showing_lines} lines of {logContent.total_lines} total lines
              </div>
              <pre className="text-xs leading-relaxed whitespace-pre-wrap font-mono">
                {logContent.content.join('\n')}
              </pre>
            </div>
          ) : (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-600">Failed to load log file content.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function SystemSettings() {
  const [activeTab, setActiveTab] = useState<TabType>('security');

  const tabs: { id: TabType; label: string; icon: React.ReactNode; description: string }[] = [
    {
      id: 'security',
      label: 'Security',
      icon: <User className="h-4 w-4" />,
      description: 'Account settings and password management'
    },
    {
      id: 'monitoring',
      label: 'Monitoring',
      icon: <Clock className="h-4 w-4" />,
      description: 'Stream monitoring and performance settings'
    },
    {
      id: 'logging',
      label: 'Logging',
      icon: <FileText className="h-4 w-4" />,
      description: 'System logging configuration and file management'
    }
  ];

  const renderTabContent = () => {
    switch (activeTab) {
      case 'security':
        return <SecurityTab />;
      case 'monitoring':
        return <MonitoringTab />;
      case 'logging':
        return <LoggingTab />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 flex items-center">
          <Settings className="h-8 w-8 mr-3 text-blue-500" />
          System Settings
        </h1>
        <p className="text-gray-600 mt-2">
          Manage system configurations and account settings
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg border">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {tab.icon}
                <span className="ml-2">{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          <div className="mb-6">
            <p className="text-sm text-gray-600">
              {tabs.find(tab => tab.id === activeTab)?.description}
            </p>
          </div>
          
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
}