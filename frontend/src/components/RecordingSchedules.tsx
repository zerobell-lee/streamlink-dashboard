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
      } catch (error: any) {
        console.error('Delete failed:', error);
        alert(error.response?.data?.detail || 'Failed to delete schedule');
      }
    }
  };

  const handleSave = async () => {
    try {
      if (!formData.platform || !formData.streamer_id) {
        alert('Please fill in all required fields');
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
      } else {
        const response = await api.schedules.create(submitData);
        setSchedules([...schedules, response.data]);
      }
      setIsModalOpen(false);
    } catch (error: any) {
      console.error('Save failed:', error);
      alert(error.response?.data?.detail || 'Failed to save schedule');
    }
  };

  const toggleEnabled = async (id: number) => {
    try {
      const response = await api.schedules.toggle(id);
      setSchedules(schedules.map(s => s.id === id ? {
        ...s,
        enabled: response.data.enabled
      } : s));
    } catch (error: any) {
      console.error('Toggle failed:', error);
      alert(error.response?.data?.detail || 'Failed to toggle schedule');
    }
  };


  const getStatusIcon = (enabled: boolean) => {
    return enabled 
      ? <CheckCircle className="h-4 w-4 text-green-500" />
      : <XCircle className="h-4 w-4 text-gray-400" />;
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
            <h1 className="text-3xl font-bold text-gray-900">Recording Schedules</h1>
            <p className="text-gray-600 mt-2">Loading schedules...</p>
          </div>
          <div className="w-32 h-10 bg-gray-200 rounded-lg animate-pulse"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="bg-white rounded-lg border p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
              <div className="h-8 bg-gray-200 rounded w-16"></div>
            </div>
          ))}
        </div>
        <div className="bg-white rounded-lg border p-6">
          <div className="h-6 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="space-y-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-100 rounded animate-pulse"></div>
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
          <h1 className="text-3xl font-bold text-gray-900">Recording Schedules</h1>
          <p className="text-gray-600 mt-2">Manage automatic recording schedules for your favorite streamers</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          <span>Add Schedule</span>
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-400 mr-2" />
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </div>
      )}

      {/* Schedule Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="h-4 w-4 text-blue-500" />
            <span className="text-sm text-gray-600">Total Schedules</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{schedules.length}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Play className="h-4 w-4 text-green-500" />
            <span className="text-sm text-gray-600">Active</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{schedules.filter(s => s.enabled).length}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Pause className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-600">Disabled</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{schedules.filter(s => !s.enabled).length}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <RotateCcw className="h-4 w-4 text-purple-500" />
            <span className="text-sm text-gray-600">With Rotation</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{schedules.filter(s => s.rotation_enabled).length}</p>
        </div>
      </div>

      {/* Schedules List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Schedule List</h2>
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
                    <h3 className="text-lg font-medium text-gray-900 truncate">
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
                  <p className="text-gray-600 mt-1">
                    Streamer ID: {schedule.streamer_id}
                  </p>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
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
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
                <button
                  onClick={() => handleEdit(schedule)}
                  className="p-2 text-gray-400 hover:text-blue-600 rounded"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(schedule.id)}
                  className="p-2 text-gray-400 hover:text-red-600 rounded"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
          {schedules.length === 0 && (
            <div className="p-12 text-center">
              <Clock className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No schedules yet</h3>
              <p className="text-gray-500">Create your first recording schedule to get started</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-6 border-b">
              <h2 className="text-xl font-semibold text-gray-900">
                {editingSchedule ? 'Edit Schedule' : 'Add Schedule'}
              </h2>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Basic Settings */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Basic Settings</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Platform *
                    </label>
                    <select
                      value={formData.platform}
                      onChange={(e) => setFormData({...formData, platform: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                    >
                      <option value="" className="text-gray-500 bg-white">Select platform</option>
                      <option value="twitch" className="text-gray-900 bg-white">Twitch</option>
                      <option value="youtube" className="text-gray-900 bg-white">YouTube</option>
                      <option value="sooplive" className="text-gray-900 bg-white">SoopLive</option>
                      <option value="chzzk" className="text-gray-900 bg-white">Chzzk (치지직)</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Quality
                      <span className="text-xs font-normal text-gray-500 ml-2">
                        (Comma-separated with fallback support)
                      </span>
                    </label>
                    <input
                      type="text"
                      value={formData.quality}
                      onChange={(e) => setFormData({...formData, quality: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white placeholder-gray-400"
                      placeholder="1440p,1080p60,1080p,720p,540p,360p,best,worst"
                    />
                    <p className="text-xs text-gray-600 mt-1">
                      Streamlink will try qualities in order. Examples: "best", "720p", "1440p,1080p,best"
                    </p>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Streamer ID *
                  </label>
                  <input
                    type="text"
                    value={formData.streamer_id}
                    onChange={(e) => setFormData({...formData, streamer_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white placeholder-gray-400"
                    placeholder="Enter streamer ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Streamer Name
                  </label>
                  <input
                    type="text"
                    value={formData.streamer_name}
                    onChange={(e) => setFormData({...formData, streamer_name: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white placeholder-gray-400"
                    placeholder="Display name (optional, defaults to streamer ID)"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Custom Arguments
                  </label>
                  <textarea
                    value={formData.custom_arguments || ''}
                    onChange={(e) => setFormData({...formData, custom_arguments: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white placeholder-gray-400"
                    placeholder="Additional streamlink arguments"
                    rows={2}
                  />
                </div>
              </div>

              {/* Rotation Settings */}
              <div className="space-y-4 border-t pt-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-medium text-gray-900">File Rotation Settings</h3>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.rotation_enabled || false}
                      onChange={(e) => setFormData({...formData, rotation_enabled: e.target.checked})}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                {formData.rotation_enabled && (
                  <div className="space-y-4 bg-gray-50 p-4 rounded-lg">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Rotation Type
                      </label>
                      <select
                        value={formData.rotation_type}
                        onChange={(e) => setFormData({...formData, rotation_type: e.target.value as 'time' | 'count' | 'size'})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                      >
                        <option value="time" className="text-gray-900 bg-white">Time-based (days)</option>
                        <option value="count" className="text-gray-900 bg-white">Count-based (files)</option>
                        <option value="size" className="text-gray-900 bg-white">Size-based (GB)</option>
                      </select>
                    </div>

                    {formData.rotation_type === 'time' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Keep files for (days)
                        </label>
                        <input
                          type="number"
                          value={formData.max_age_days || ''}
                          onChange={(e) => setFormData({...formData, max_age_days: e.target.value === '' ? 0 : parseInt(e.target.value) || 0})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                          min="1"
                        />
                      </div>
                    )}

                    {formData.rotation_type === 'count' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Maximum number of files
                        </label>
                        <input
                          type="number"
                          value={formData.max_count || ''}
                          onChange={(e) => setFormData({...formData, max_count: e.target.value === '' ? 0 : parseInt(e.target.value) || 0})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
                          min="1"
                        />
                      </div>
                    )}

                    {formData.rotation_type === 'size' && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Maximum total size (GB)
                        </label>
                        <input
                          type="number"
                          value={formData.max_size_gb || ''}
                          onChange={(e) => setFormData({...formData, max_size_gb: e.target.value === '' ? 0 : parseInt(e.target.value) || 0})}
                          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-900 bg-white"
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
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">Protect favorite recordings</span>
                      </label>
                      
                      <label className="flex items-center">
                        <input
                          type="checkbox"
                          checked={formData.delete_empty_files}
                          onChange={(e) => setFormData({...formData, delete_empty_files: e.target.checked})}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">Delete empty files</span>
                      </label>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-end space-x-3 p-6 border-t bg-gray-50">
              <button
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
              >
                <Save className="h-4 w-4" />
                <span>{editingSchedule ? 'Update' : 'Create'} Schedule</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecordingSchedules;