"use client";

import { useState, useEffect } from 'react';
import {
  Plus,
  Edit2,
  Trash2,
  Save,
  X,
  Clock,
  Play,
  Pause,
  Calendar,
  Settings,
  AlertTriangle,
  CheckCircle,
  XCircle,
  RotateCcw
} from 'lucide-react';
import { RecordingSchedule, CreateScheduleForm } from '@/types';
import { getPlatformIcon } from '@/lib/platformIcons';
import { api } from '@/lib/api';

const RecordingSchedules = () => {
  const [loading, setLoading] = useState(true);
  const [schedules, setSchedules] = useState<RecordingSchedule[]>([]);
  const [error, setError] = useState<string | null>(null);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSchedule, setEditingSchedule] = useState<RecordingSchedule | null>(null);
  
  // Toast notification state
  const [toast, setToast] = useState<{
    show: boolean;
    message: string;
    type: 'success' | 'error' | 'warning';
  }>({ show: false, message: '', type: 'success' });

  const [formData, setFormData] = useState<CreateScheduleForm>({
    platform: '',
    streamer_id: '',
    streamer_name: '',
    quality: 'best',
    rotation_enabled: false,
    rotation_type: 'time',
    max_age_days: 30,
    max_count: 100,
    max_size_gb: 10,
    protect_favorites: true,
    delete_empty_files: true
  });

  // Toast notification helper
  const showToast = (message: string, type: 'success' | 'error' | 'warning' = 'success') => {
    setToast({ show: true, message, type });
    setTimeout(() => {
      setToast({ show: false, message: '', type: 'success' });
    }, 5000);
  };

  // Fetch data on component mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const schedulesRes = await api.schedules.getAll();
        setSchedules(schedulesRes.data || []);
        setError(null);
      } catch (error: any) {
        console.error('Failed to fetch data:', error);
        setError(error.response?.data?.detail || 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, []);

  const handleCreate = () => {
    setEditingSchedule(null);
    setFormData({
      platform: '',
      streamer_id: '',
      streamer_name: '',
      quality: 'best',
      rotation_enabled: false,
      rotation_type: 'time',
      max_age_days: 30,
      max_count: 100,
      max_size_gb: 10,
      protect_favorites: true,
      delete_empty_files: true
    });
    setIsModalOpen(true);
  };

  const handleEdit = (schedule: RecordingSchedule) => {
    setEditingSchedule(schedule);
    setFormData({
      platform: schedule.platform,
      streamer_id: schedule.streamer_id,
      streamer_name: schedule.streamer_name,
      quality: schedule.quality,
      custom_arguments: schedule.custom_arguments,
      output_format: schedule.output_format,
      filename_template: schedule.filename_template,
      rotation_enabled: schedule.rotation_enabled,
      rotation_type: schedule.rotation_type || 'time',
      max_age_days: schedule.max_age_days || 30,
      max_count: schedule.max_count || 100,
      max_size_gb: schedule.max_size_gb || 10,
      protect_favorites: schedule.protect_favorites,
      delete_empty_files: schedule.delete_empty_files
    });
    setIsModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm('Are you sure you want to delete this recording schedule?')) {
      try {
        await api.schedules.delete(id);
        setSchedules(schedules.filter(s => s.id !== id));
        showToast('Schedule deleted successfully', 'success');
      } catch (error: any) {
        console.error('Delete failed:', error);
        showToast(error.response?.data?.detail || 'Failed to delete schedule', 'error');
      }
    }
  };

  const handleSave = async () => {
    try {
      if (!formData.platform || !formData.streamer_id) {
        showToast('Please fill in all required fields', 'warning');
        return;
      }
      
      // Use streamer_id as streamer_name if streamer_name is empty
      const submitData = {
        ...formData,
        streamer_name: formData.streamer_name?.trim() || formData.streamer_id
      };
      
      if (editingSchedule) {
        const response = await api.schedules.update(editingSchedule.id, submitData);
        setSchedules(schedules.map(s => s.id === editingSchedule.id ? response.data : s));
        showToast('Schedule updated successfully', 'success');
      } else {
        const response = await api.schedules.create(submitData);
        setSchedules([...schedules, response.data]);
        showToast('Schedule created successfully', 'success');
      }
      setIsModalOpen(false);
    } catch (error: any) {
      // Handle validation errors (422 status code)
      if (error.response?.status === 422) {
        console.warn('Validation error:', error.response.data);
        const detail = error.response.data?.detail;
        if (Array.isArray(detail) && detail.length > 0) {
          // Pydantic validation errors are arrays with objects containing 'msg' and 'loc'
          const errorMessages = detail.map((err: any) => {
            const field = err.loc?.length > 0 ? err.loc[err.loc.length - 1] : 'field';
            return `${field}: ${err.msg}`;
          }).join('. ');
          showToast(`Validation Error: ${errorMessages}`, 'error');
        } else if (typeof detail === 'string') {
          showToast(`Validation Error: ${detail}`, 'error');
        } else {
          showToast('Validation error occurred. Please check your input.', 'error');
        }
      } else {
        console.error('Save failed:', error);
        showToast(error.response?.data?.detail || 'Failed to save schedule', 'error');
      }
    }
  };

  const toggleEnabled = async (id: number) => {
    try {
      const response = await api.schedules.toggle(id);
      setSchedules(schedules.map(s => s.id === id ? {
        ...s,
        enabled: response.data.enabled
      } : s));
      showToast(
        response.data.enabled 
          ? 'Schedule enabled successfully' 
          : 'Schedule disabled successfully', 
        'success'
      );
    } catch (error: any) {
      console.error('Toggle failed:', error);
      showToast(error.response?.data?.detail || 'Failed to toggle schedule', 'error');
    }
  };


  const getStatusIcon = (enabled: boolean) => {
    return enabled 
      ? <CheckCircle className="h-4 w-4 text-green-500" />
      : <XCircle className="h-4 w-4 text-muted-foreground" />;
  };


  const formatRotationInfo = (schedule: RecordingSchedule) => {
    if (!schedule.rotation_enabled) {
      return "No rotation";
    }
    
    switch (schedule.rotation_type) {
      case 'time':
        return `Keep ${schedule.max_age_days} days`;
      case 'count':
        return `Keep ${schedule.max_count} files`;
      case 'size':
        return `Keep ${schedule.max_size_gb} GB`;
      default:
        return "Custom rotation";
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground flex items-center">
              <Calendar className="h-8 w-8 mr-3 text-purple-500" />
              Recording Schedules
            </h1>
            <p className="text-muted-foreground mt-2">Loading schedules...</p>
          </div>
          <div className="w-32 h-10 bg-muted rounded-lg animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-card rounded-lg border p-4 animate-pulse">
              <div className="h-4 bg-muted rounded w-20 mb-2"></div>
              <div className="h-8 bg-muted rounded w-16"></div>
            </div>
          ))}
        </div>
        <div className="bg-card rounded-lg border p-6">
          <div className="h-6 bg-muted rounded w-32 mb-4"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-accent rounded animate-pulse"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center">
            <Calendar className="h-8 w-8 mr-3 text-purple-500" />
            Recording Schedules
          </h1>
          <p className="text-muted-foreground mt-2">Manage automatic recording schedules for your favorite streamers</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" />
          <span>Add Schedule</span>
        </button>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-sm text-destructive">{error}</p>
          </div>
        </div>
      )}

      {/* Schedule Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="h-4 w-4 text-blue-500" />
            <span className="text-sm text-muted-foreground">Total Schedules</span>
          </div>
          <p className="text-2xl font-bold text-foreground">{schedules.length}</p>
        </div>
        <div className="bg-card rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Play className="h-4 w-4 text-green-500" />
            <span className="text-sm text-muted-foreground">Active</span>
          </div>
          <p className="text-2xl font-bold text-foreground">{schedules.filter(s => s.enabled).length}</p>
        </div>
        <div className="bg-card rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Pause className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">Disabled</span>
          </div>
          <p className="text-2xl font-bold text-foreground">{schedules.filter(s => !s.enabled).length}</p>
        </div>
        <div className="bg-card rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <RotateCcw className="h-4 w-4 text-purple-500" />
            <span className="text-sm text-muted-foreground">With Rotation</span>
          </div>
          <p className="text-2xl font-bold text-foreground">{schedules.filter(s => s.rotation_enabled).length}</p>
        </div>
      </div>

      {/* Schedules List */}
      <div className="bg-card rounded-lg border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-foreground">Schedule List</h2>
        </div>
        <div className="divide-y">
          {schedules.map((schedule) => (
            <div key={schedule.id} className="p-6 flex items-center justify-between">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 mt-1">
                  {getPlatformIcon(schedule.platform)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-medium text-foreground truncate">
                      {schedule.streamer_name}
                    </h3>
                    {getStatusIcon(schedule.enabled)}
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      {schedule.platform}
                    </span>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {schedule.quality}
                    </span>
                  </div>
                  <p className="text-muted-foreground mt-1">
                    Streamer ID: {schedule.streamer_id}
                  </p>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-muted-foreground">
                    <span className="flex items-center space-x-1">
                      <RotateCcw className="h-3 w-3" />
                      <span>{formatRotationInfo(schedule)}</span>
                    </span>
                    {schedule.custom_arguments && (
                      <span>Custom args: {schedule.custom_arguments}</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={schedule.enabled}
                    onChange={() => toggleEnabled(schedule.id)}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-card after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                </label>
                <button
                  onClick={() => handleEdit(schedule)}
                  className="p-2 text-muted-foreground hover:text-primary rounded"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(schedule.id)}
                  className="p-2 text-muted-foreground hover:text-destructive rounded"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
          {schedules.length === 0 && (
            <div className="p-12 text-center">
              <Clock className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium text-foreground mb-2">No schedules yet</h3>
              <p className="text-muted-foreground">Create your first recording schedule to get started</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-card rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold text-foreground">
                {editingSchedule ? 'Edit Schedule' : 'Add Schedule'}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-muted-foreground hover:text-muted-foreground"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Basic Settings */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-foreground">Basic Settings</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Platform *
                    </label>
                    <select
                      value={formData.platform}
                      onChange={(e) => setFormData({...formData, platform: e.target.value})}
                      className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-foreground bg-background"
                    >
                      <option value="" className="text-muted-foreground bg-card">Select platform</option>
                      <option value="twitch" className="text-foreground bg-card">Twitch</option>
                      <option value="youtube" className="text-foreground bg-card">YouTube</option>
                      <option value="sooplive" className="text-foreground bg-card">SoopLive</option>
                      <option value="chzzk" className="text-foreground bg-card">Chzzk</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Quality
                      <span className="text-xs font-normal text-muted-foreground ml-2">
                        (Comma-separated with fallback support)
                      </span>
                    </label>
                    <input
                      type="text"
                      value={formData.quality}
                      onChange={(e) => setFormData({...formData, quality: e.target.value})}
                      className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-foreground bg-background placeholder:text-muted-foreground"
                      placeholder="1440p,1080p60,1080p,720p,540p,360p,best,worst"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Streamlink will try qualities in order. Examples: "best", "720p", "1440p,1080p,best"
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Streamer ID *
                  </label>
                  <input
                    type="text"
                    value={formData.streamer_id}
                    onChange={(e) => setFormData({...formData, streamer_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-foreground bg-card placeholder-gray-400"
                    placeholder="Enter streamer ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Streamer Name
                  </label>
                  <input
                    type="text"
                    value={formData.streamer_name}
                    onChange={(e) => setFormData({...formData, streamer_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-foreground bg-card placeholder-gray-400"
                    placeholder="Display name (optional, defaults to streamer ID)"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Output Format
                      <span className="text-xs font-normal text-muted-foreground ml-2">
                        (Optional, uses platform default)
                      </span>
                    </label>
                    <select
                      value={formData.output_format || ''}
                      onChange={(e) => setFormData({...formData, output_format: e.target.value || undefined})}
                      className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-foreground bg-background"
                    >
                      <option value="" className="text-muted-foreground bg-card">Use platform default</option>
                      <option value="mp4" className="text-foreground bg-card">MP4 (recommended for most)</option>
                      <option value="ts" className="text-foreground bg-card">TS (Transport Stream)</option>
                      <option value="mkv" className="text-foreground bg-card">MKV</option>
                      <option value="flv" className="text-foreground bg-card">FLV</option>
                    </select>
                    <p className="text-xs text-muted-foreground mt-1">
                      Twitch/CHZZK default: MP4, SoopLive default: TS
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Filename Template
                      <span className="text-xs font-normal text-muted-foreground ml-2">
                        (Optional, uses platform default)
                      </span>
                    </label>
                    <input
                      type="text"
                      value={formData.filename_template || ''}
                      onChange={(e) => setFormData({...formData, filename_template: e.target.value || undefined})}
                      className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-foreground bg-background placeholder:text-muted-foreground"
                      placeholder="{streamer_id}_{yyyyMMdd}_{HHmmss}"
                    />
                    <p className="text-xs text-muted-foreground mt-1">
                      Variables: {"{streamer_id}, {streamer_name}, {platform}, {title}, {quality}, {yyyy}, {MM}, {dd}, {HH}, {mm}, {ss}"}
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Custom Arguments
                  </label>
                  <textarea
                    value={formData.custom_arguments || ''}
                    onChange={(e) => setFormData({...formData, custom_arguments: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-foreground bg-card placeholder-gray-400"
                    placeholder="Additional streamlink arguments"
                    rows={2}
                  />
                </div>
              </div>

              {/* Rotation Settings */}
              <div className="space-y-4 border-t pt-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-foreground">File Rotation Settings</h3>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.rotation_enabled || false}
                      onChange={(e) => setFormData({...formData, rotation_enabled: e.target.checked})}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-card after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                {formData.rotation_enabled && (
                  <div className="space-y-4 bg-accent p-4 rounded-lg">
                    <div>
                      <label className="block text-sm font-medium text-foreground mb-2">
                        Rotation Type
                      </label>
                      <select
                        value={formData.rotation_type}
                        onChange={(e) => setFormData({...formData, rotation_type: e.target.value as 'time' | 'count' | 'size'})}
                        className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-foreground bg-background"
                      >
                        <option value="time" className="text-foreground bg-card">Time-based (days)</option>
                        <option value="count" className="text-foreground bg-card">Count-based (files)</option>
                        <option value="size" className="text-foreground bg-card">Size-based (GB)</option>
                      </select>
                    </div>

                    {formData.rotation_type === 'time' && (
                      <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                          Keep files for (days)
                        </label>
                        <input
                          type="number"
                          value={formData.max_age_days || ''}
                          onChange={(e) => setFormData({...formData, max_age_days: e.target.value === '' ? 0 : parseInt(e.target.value) || 0})}
                          className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-foreground bg-background"
                          min="1"
                        />
                      </div>
                    )}

                    {formData.rotation_type === 'count' && (
                      <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                          Maximum number of files
                        </label>
                        <input
                          type="number"
                          value={formData.max_count || ''}
                          onChange={(e) => setFormData({...formData, max_count: e.target.value === '' ? 0 : parseInt(e.target.value) || 0})}
                          className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-foreground bg-background"
                          min="1"
                        />
                      </div>
                    )}

                    {formData.rotation_type === 'size' && (
                      <div>
                        <label className="block text-sm font-medium text-foreground mb-2">
                          Maximum total size (GB)
                        </label>
                        <input
                          type="number"
                          value={formData.max_size_gb || ''}
                          onChange={(e) => setFormData({...formData, max_size_gb: e.target.value === '' ? 0 : parseInt(e.target.value) || 0})}
                          className="w-full px-3 py-2 border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-foreground bg-background"
                          min="1"
                        />
                      </div>
                    )}

                    <div className="flex items-center space-x-6">
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.protect_favorites}
                          onChange={(e) => setFormData({...formData, protect_favorites: e.target.checked})}
                          className="rounded border-input text-primary focus:ring-ring"
                        />
                        <span className="ml-2 text-sm text-foreground">Protect favorite recordings</span>
                      </label>
                      
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.delete_empty_files}
                          onChange={(e) => setFormData({...formData, delete_empty_files: e.target.checked})}
                          className="rounded border-input text-primary focus:ring-ring"
                        />
                        <span className="ml-2 text-sm text-foreground">Delete empty files</span>
                      </label>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 p-6 border-t bg-accent">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-foreground bg-background border border-input rounded-md hover:bg-accent"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-primary-foreground bg-primary rounded-md hover:bg-primary/90"
              >
                <Save className="h-4 w-4" />
                <span>{editingSchedule ? 'Update' : 'Create'} Schedule</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toast.show && (
        <div className="fixed top-4 right-4 z-50 animate-in slide-in-from-right duration-300">
          <div className={`
            max-w-md w-full bg-card rounded-lg shadow-lg border-l-4 p-4
            ${toast.type === 'success' ? 'border-green-500' : 
              toast.type === 'error' ? 'border-red-500' : 'border-yellow-500'}
          `}>
            <div className="flex items-center">
              <div className="flex-shrink-0">
                {toast.type === 'success' && (
                  <CheckCircle className="h-5 w-5 text-green-500" />
                )}
                {toast.type === 'error' && (
                  <XCircle className="h-5 w-5 text-red-500" />
                )}
                {toast.type === 'warning' && (
                  <AlertTriangle className="h-5 w-5 text-yellow-500" />
                )}
              </div>
              <div className="ml-3 flex-1">
                <p className={`text-sm font-medium 
                  ${toast.type === 'success' ? 'text-green-800' : 
                    toast.type === 'error' ? 'text-red-800' : 'text-yellow-800'}
                `}>
                  {toast.message}
                </p>
              </div>
              <div className="ml-4 flex-shrink-0">
                <button
                  onClick={() => setToast({ show: false, message: '', type: 'success' })}
                  className="text-muted-foreground hover:text-muted-foreground"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecordingSchedules;