"use client";

import { useEffect, useState, useRef } from 'react';
import { BarChart3, Activity, Clock, FolderOpen, Radio, AlertCircle, ArrowRight } from 'lucide-react';
import { api } from '@/lib/api';
import { formatRelativeTime, getServerTime, getServerTimeSync } from '@/lib/utils';
import { getPlatformIcon } from '@/lib/platformIcons';
import Link from 'next/link';

// Real-time duration counter component
const LiveDuration = ({ startTime, initialDuration }: { startTime: string, initialDuration?: number }) => {
  const startTimeRef = useRef(startTime);
  const [duration, setDuration] = useState(() => {
    if (initialDuration && initialDuration > 0) return initialDuration;
    
    try {
      // Use server time-based calculation
      const start = new Date(startTime);
      const now = getServerTimeSync();
      const calculatedDuration = Math.floor((now.getTime() - start.getTime()) / 1000);
      return Math.max(0, calculatedDuration);
    } catch (error) {
      console.warn('Failed to parse startTime:', startTime, error);
      return 0;
    }
  });

  const [serverTimeInitialized, setServerTimeInitialized] = useState(false);

  // Initialize server time on mount
  useEffect(() => {
    getServerTime().then(() => {
      setServerTimeInitialized(true);
    });
  }, []);

  // Update ref if startTime changes (but don't recreate interval)
  useEffect(() => {
    startTimeRef.current = startTime;
  }, [startTime]);

  useEffect(() => {
    if (!serverTimeInitialized) return;
    
    console.log('LiveDuration useEffect - interval created once');
    
    const interval = setInterval(() => {
      try {
        // Use server time for calculation
        const start = new Date(startTimeRef.current);
        const now = getServerTimeSync();
        
        // Validate dates
        if (isNaN(start.getTime()) || isNaN(now.getTime())) {
          console.warn('Invalid date in LiveDuration:', { startTime: startTimeRef.current, start: start.getTime(), now: now.getTime() });
          return;
        }
        
        const currentDuration = Math.floor((now.getTime() - start.getTime()) / 1000);
        setDuration(Math.max(0, currentDuration));
      } catch (error) {
        console.warn('Error calculating duration:', error);
      }
    }, 1000);

    return () => {
      console.log('LiveDuration useEffect - interval cleared');
      clearInterval(interval);
    };
  }, [serverTimeInitialized]); // Depend on server time initialization

  const formatDuration = (seconds: number) => {
    if (isNaN(seconds) || seconds < 0) return '00:00:00';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return <span>{formatDuration(duration)}</span>;
};

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [hasInitialized, setHasInitialized] = useState(false);
  const [data, setData] = useState({
    recordings: [],
    schedules: [],
    schedulerStatus: null,
    totalFilesCount: 0,
    activeRecordings: [],
    error: null
  });

  // Format file size from bytes to human readable
  const formatFileSize = (bytes: number) => {
    if (!bytes) return '0 B';
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };



  // Fetch dashboard data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Only show loading on very first load
        if (!hasInitialized) {
          setLoading(true);
        }
        
        // Fetch each API separately to avoid one failure breaking everything
        let recordingsRes = { data: [] };
        let schedulesRes = { data: [] };
        let allRecordingsRes = { data: [] };

        try {
          recordingsRes = await api.recordings.getAll({ limit: 10 });
        } catch (err) {
          console.warn('Could not fetch recent recordings:', err);
        }

        try {
          schedulesRes = await api.schedules.getAll();
        } catch (err) {
          console.warn('Could not fetch schedules:', err);
        }

        try {
          allRecordingsRes = await api.recordings.getAll({ limit: 1000 });
        } catch (err) {
          console.warn('Could not fetch all recordings:', err);
        }

        // Try to get active recordings separately (might fail)
        let activeRecordingsRes = { data: { active_recordings: [] as any[] } };
        try {
          activeRecordingsRes = await api.scheduler.getActiveRecordings();
        } catch (err) {
          console.warn('Could not fetch active recordings:', err);
        }

        // Try to get scheduler status (might fail if scheduler not running)
        let schedulerStatus = null;
        try {
          const statusRes = await api.scheduler.getStatus();
          schedulerStatus = statusRes.data;
        } catch (err) {
          console.warn('Could not fetch scheduler status:', err);
        }

        // Map active recordings with schedule information
        const activeRecordings = activeRecordingsRes.data?.active_recordings || [];
        const schedules = schedulesRes.data || [];
        // Backend now provides all info directly, no need to enhance
        const enhancedActiveRecordings = activeRecordings as any[];

        setData({
          recordings: recordingsRes.data || [],
          schedules: schedules,
          schedulerStatus,
          totalFilesCount: allRecordingsRes.data?.length || 0,
          activeRecordings: enhancedActiveRecordings as any[],
          error: null
        });
      } catch (error: any) {
        console.error('Dashboard data fetch error:', error);
        setData(prev => ({
          ...prev,
          error: error.response?.data?.detail || 'Failed to load dashboard data'
        }));
      } finally {
        // Set loading false and mark as initialized
        if (!hasInitialized) {
          setLoading(false);
          setHasInitialized(true);
        }
      }
    };

    const fetchFileStats = async () => {
      try {
        // Fetch updated active recordings for real-time file size updates
        const activeRecordingsRes = await api.scheduler.getActiveRecordings();
        const activeRecordings = activeRecordingsRes.data?.active_recordings || [];
        
        // No need to map with schedule info anymore - comes from backend
        const enhancedActiveRecordings = activeRecordings;
        
        setData(prev => ({
          ...prev,
          activeRecordings: enhancedActiveRecordings,
        }));
      } catch (error) {
        console.warn('Could not fetch active recording stats:', error);
      }
    };

    fetchData();
    
    // Only refresh file stats every 10 seconds (for file sizes)
    const fileStatsInterval = setInterval(fetchFileStats, 10000);
    
    return () => {
      clearInterval(fileStatsInterval);
    };
  }, []);

  // Process data for display
  const activeRecordings = data.activeRecordings;
  const recentFiles = data.recordings.filter((r: any) => r.status === 'completed').slice(0, 5);
  const totalSchedules = data.schedules.length;
  const enabledSchedules = data.schedules.filter((s: any) => s.enabled).length;

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <div className="flex items-center space-x-2 text-sm text-gray-500">
            <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
            <span>Loading...</span>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg border p-6 animate-pulse">
              <div className="flex items-center justify-between">
                <div>
                  <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                  <div className="h-8 bg-gray-200 rounded w-16"></div>
                </div>
                <div className="h-8 w-8 bg-gray-200 rounded"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center space-x-2 text-sm text-green-600">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span>System Running</span>
        </div>
      </div>

      {data.error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-sm text-red-600">{data.error}</p>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Schedules</p>
              <p className="text-2xl font-bold text-gray-900">{totalSchedules}</p>
            </div>
            <BarChart3 className="h-8 w-8 text-blue-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">Recording schedules</p>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Enabled Schedules</p>
              <p className="text-2xl font-bold text-gray-900">{enabledSchedules}</p>
            </div>
            <Activity className="h-8 w-8 text-green-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">Currently active</p>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Recordings</p>
              <p className="text-2xl font-bold text-gray-900">{activeRecordings.length}</p>
            </div>
            <Radio className="h-8 w-8 text-red-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">Currently recording</p>
        </div>

        <div className="bg-white rounded-lg border p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Files</p>
              <p className="text-2xl font-bold text-gray-900">{data.totalFilesCount}</p>
            </div>
            <FolderOpen className="h-8 w-8 text-purple-500" />
          </div>
          <p className="text-xs text-gray-500 mt-2">Recorded files</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Active Recordings */}
        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Radio className="h-5 w-5 mr-2 text-red-500" />
              Active Recordings ({activeRecordings.length})
            </h2>
          </div>
          <div className="p-6">
            {activeRecordings.length > 0 ? (
              <div className="space-y-4">
                {activeRecordings.map((recording: any) => (
                  <div key={recording.recording_id || recording.id} className="flex items-center justify-between p-3 bg-red-50 border border-red-200 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                      <div>
                        <p className="font-medium text-gray-900">{recording.streamer_name || recording.streamer_id}</p>
                        <div className="flex items-center space-x-1">
                          {getPlatformIcon(recording.platform, 'sm')}
                          <span className="text-sm text-gray-600">{recording.platform}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">
                        <LiveDuration startTime={recording.start_time} />
                      </p>
                      <p className="text-sm text-gray-600">
                        {recording.file_size ? formatFileSize(recording.file_size) : '...'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No active recordings</p>
            )}
          </div>
        </div>

        {/* Scheduled Recordings */}
        <div className="bg-white rounded-lg border">
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <Clock className="h-5 w-5 mr-2 text-blue-500" />
              Recording Schedules ({enabledSchedules}/{totalSchedules})
            </h2>
          </div>
          <div className="p-6">
            {data.schedules.length > 0 ? (
              <div className="space-y-4">
                {data.schedules.slice(0, 4).map((schedule: any) => (
                  <div key={schedule.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`w-3 h-3 rounded-full ${
                        schedule.enabled ? 'bg-green-500' : 'bg-gray-400'
                      }`}></div>
                      <div>
                        <p className="font-medium text-gray-900">{schedule.streamer_name || schedule.streamer_id}</p>
                        <div className="flex items-center space-x-1">
                          {getPlatformIcon(schedule.platform, 'sm')}
                          <span className="text-sm text-gray-600">{schedule.platform}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium text-gray-900">{schedule.quality || 'best'}</p>
                      <p className={`text-sm capitalize ${
                        schedule.enabled ? 'text-green-600' : 'text-gray-500'
                      }`}>
                        {schedule.enabled ? 'Monitoring' : 'Disabled'}
                      </p>
                    </div>
                  </div>
                ))}
                {data.schedules.length > 4 && (
                  <div className="text-center pt-2">
                    <p className="text-sm text-gray-500">
                      +{data.schedules.length - 4} more schedules
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">No recording schedules configured</p>
            )}
          </div>
        </div>
      </div>

      {/* Recent Files */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-gray-900 flex items-center">
              <FolderOpen className="h-5 w-5 mr-2 text-green-500" />
              Recent Files
            </h2>
            <Link
              href="/recordings"
              className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              View All
              <ArrowRight className="h-4 w-4 ml-1" />
            </Link>
          </div>
        </div>
        <div className="p-6">
          {recentFiles.length > 0 ? (
            <div className="space-y-4">
              {recentFiles.map((file: any) => (
                <div key={file.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <div className="flex items-center space-x-3">
                    <FolderOpen className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="font-medium text-gray-900">{file.file_name}</p>
                      <div className="flex items-center space-x-1 text-sm text-gray-600">
                        <span>{file.streamer_name}</span>
                        <span>•</span>
                        {getPlatformIcon(file.platform, 'sm')}
                        <span>{file.platform}</span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {formatFileSize(file.file_size)}
                    </p>
                    <p className="text-sm text-gray-500">
                      {formatRelativeTime(file.created_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">No recorded files yet</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;