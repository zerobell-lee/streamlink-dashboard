"use client";

import { useState } from 'react';
import { 
  Plus, 
  Edit2, 
  Trash2, 
  Save, 
  X, 
  Settings,
  Clock,
  Hash,
  HardDrive,
  Shield,
  AlertTriangle,
  RotateCcw
} from 'lucide-react';
import { RotationPolicy, CreateRotationPolicyForm } from '@/types';

const RotationPolicies = () => {
  const [policies, setPolicies] = useState<RotationPolicy[]>([
    {
      id: 1,
      name: "Default Time-based Policy",
      policy_type: "time",
      max_age_days: 30,
      enabled: true,
      priority: 1,
      protect_favorites: true,
      delete_empty_files: true,
      created_at: "2024-08-01T00:00:00Z",
      updated_at: "2024-08-01T00:00:00Z"
    },
    {
      id: 2,
      name: "High Priority Storage Limit",
      policy_type: "size",
      max_size_gb: 500,
      enabled: true,
      priority: 2,
      protect_favorites: true,
      delete_empty_files: true,
      created_at: "2024-08-01T00:00:00Z",
      updated_at: "2024-08-01T00:00:00Z"
    }
  ]);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingPolicy, setEditingPolicy] = useState<RotationPolicy | null>(null);
  const [formData, setFormData] = useState<CreateRotationPolicyForm>({
    name: '',
    policy_type: 'time',
    priority: 1,
    protect_favorites: true,
    delete_empty_files: true
  });

  const handleCreate = () => {
    setEditingPolicy(null);
    setFormData({
      name: '',
      policy_type: 'time',
      priority: 1,
      protect_favorites: true,
      delete_empty_files: true
    });
    setIsModalOpen(true);
  };

  const handleEdit = (policy: RotationPolicy) => {
    setEditingPolicy(policy);
    setFormData({
      name: policy.name,
      policy_type: policy.policy_type,
      max_age_days: policy.max_age_days,
      max_count: policy.max_count,
      max_size_gb: policy.max_size_gb,
      priority: policy.priority,
      protect_favorites: policy.protect_favorites,
      delete_empty_files: policy.delete_empty_files,
      min_file_size_mb: policy.min_file_size_mb,
      exclude_patterns: policy.exclude_patterns
    });
    setIsModalOpen(true);
  };

  const handleDelete = (id: number) => {
    if (confirm('Are you sure you want to delete this policy? This may affect schedules using this policy.')) {
      setPolicies(policies.filter(p => p.id !== id));
    }
  };

  const handleSave = () => {
    if (editingPolicy) {
      setPolicies(policies.map(p => p.id === editingPolicy.id ? {
        ...editingPolicy,
        ...formData,
        updated_at: new Date().toISOString()
      } : p));
    } else {
      const newPolicy: RotationPolicy = {
        id: Math.max(...policies.map(p => p.id)) + 1,
        ...formData,
        enabled: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      setPolicies([...policies, newPolicy]);
    }
    setIsModalOpen(false);
  };


  const getPolicyIcon = (type: string) => {
    switch (type) {
      case 'time': return <Clock className="h-5 w-5 text-blue-500" />;
      case 'count': return <Hash className="h-5 w-5 text-green-500" />;
      case 'size': return <HardDrive className="h-5 w-5 text-purple-500" />;
      default: return <Settings className="h-5 w-5 text-gray-500" />;
    }
  };

  const getPolicyDescription = (policy: RotationPolicy) => {
    switch (policy.policy_type) {
      case 'time':
        return `Files older than ${policy.max_age_days} days`;
      case 'count':
        return `Keep only ${policy.max_count} most recent files`;
      case 'size':
        return `Total storage limit: ${policy.max_size_gb} GB`;
      default:
        return 'Unknown policy type';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Rotation Policies</h1>
          <p className="text-gray-600 mt-2">Create and manage file cleanup policies for your recording schedules</p>
        </div>
        <button
          onClick={handleCreate}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="h-4 w-4" />
          <span>Create Policy</span>
        </button>
      </div>

      {/* Policy Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Settings className="h-4 w-4 text-blue-500" />
            <span className="text-sm text-gray-600">Total Policies</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{policies.length}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Hash className="h-4 w-4 text-green-500" />
            <span className="text-sm text-gray-600">Count-based</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{policies.filter(p => p.policy_type === 'count').length}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <Clock className="h-4 w-4 text-blue-500" />
            <span className="text-sm text-gray-600">Time-based</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{policies.filter(p => p.policy_type === 'time').length}</p>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center space-x-2 mb-2">
            <HardDrive className="h-4 w-4 text-purple-500" />
            <span className="text-sm text-gray-600">Size-based</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{policies.filter(p => p.policy_type === 'size').length}</p>
        </div>
      </div>

      {/* Policies List */}
      <div className="bg-white rounded-lg border">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold text-gray-900">Policy List</h2>
        </div>
        <div className="divide-y">
          {policies.map((policy) => (
            <div key={policy.id} className="p-6 flex items-center justify-between">
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0 mt-1">
                  {getPolicyIcon(policy.policy_type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-medium text-gray-900 truncate">
                      {policy.name}
                    </h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Priority {policy.priority}
                    </span>
                  </div>
                  <p className="text-gray-600 mt-1">{getPolicyDescription(policy)}</p>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                    {policy.protect_favorites && (
                      <span className="flex items-center space-x-1">
                        <Shield className="h-3 w-3" />
                        <span>Protect favorites</span>
                      </span>
                    )}
                    {policy.delete_empty_files && (
                      <span className="flex items-center space-x-1">
                        <Trash2 className="h-3 w-3" />
                        <span>Delete empty files</span>
                      </span>
                    )}
                    {policy.min_file_size_mb && (
                      <span>Min size: {policy.min_file_size_mb}MB</span>
                    )}
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleEdit(policy)}
                  className="p-2 text-gray-400 hover:text-blue-600 rounded"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                <button
                  onClick={() => handleDelete(policy.id)}
                  className="p-2 text-gray-400 hover:text-red-600 rounded"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
          {policies.length === 0 && (
            <div className="p-12 text-center">
              <RotateCcw className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No rotation policies created yet</p>
              <button
                onClick={handleCreate}
                className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Create your first policy
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-lg mx-4">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">
                {editingPolicy ? 'Edit Policy' : 'Create New Policy'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="space-y-4">
              {/* Policy Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Policy Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. 30-day Auto Cleanup Policy"
                />
              </div>

              {/* Policy Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Policy Type
                </label>
                <select
                  value={formData.policy_type}
                  onChange={(e) => setFormData({ ...formData, policy_type: e.target.value as 'time' | 'count' | 'size' })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="time">Time-based (days)</option>
                  <option value="count">Count-based (file count)</option>
                  <option value="size">Size-based (GB)</option>
                </select>
              </div>

              {/* Type-specific fields */}
              {formData.policy_type === 'time' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Age (days)
                  </label>
                  <input
                    type="number"
                    value={formData.max_age_days || ''}
                    onChange={(e) => setFormData({ ...formData, max_age_days: parseInt(e.target.value) || undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="30"
                  />
                </div>
              )}

              {formData.policy_type === 'count' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max File Count
                  </label>
                  <input
                    type="number"
                    value={formData.max_count || ''}
                    onChange={(e) => setFormData({ ...formData, max_count: parseInt(e.target.value) || undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="100"
                  />
                </div>
              )}

              {formData.policy_type === 'size' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Max Storage Size (GB)
                  </label>
                  <input
                    type="number"
                    value={formData.max_size_gb || ''}
                    onChange={(e) => setFormData({ ...formData, max_size_gb: parseInt(e.target.value) || undefined })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="500"
                  />
                </div>
              )}

              {/* Priority */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Priority (higher number = higher priority)
                </label>
                <input
                  type="number"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 1 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  min="1"
                />
              </div>

              {/* Advanced Options */}
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Protect Favorites</h4>
                    <p className="text-sm text-gray-600">Never delete files marked as favorites</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.protect_favorites}
                      onChange={(e) => setFormData({ ...formData, protect_favorites: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900">Delete Empty Files</h4>
                    <p className="text-sm text-gray-600">Automatically delete files with 0 bytes</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.delete_empty_files}
                      onChange={(e) => setFormData({ ...formData, delete_empty_files: e.target.checked })}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>

              {/* Optional fields */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Min File Size (MB) - Optional
                </label>
                <input
                  type="number"
                  value={formData.min_file_size_mb || ''}
                  onChange={(e) => setFormData({ ...formData, min_file_size_mb: parseInt(e.target.value) || undefined })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Don't delete files smaller than this"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Exclude Patterns - Optional
                </label>
                <input
                  type="text"
                  value={formData.exclude_patterns || ''}
                  onChange={(e) => setFormData({ ...formData, exclude_patterns: e.target.value || undefined })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g. *.important, backup_*"
                />
                <p className="text-xs text-gray-500 mt-1">Comma-separated file patterns to exclude from policy</p>
              </div>
            </div>

            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setIsModalOpen(false)}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleSave}
                className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                <Save className="h-4 w-4" />
                <span>{editingPolicy ? 'Update' : 'Create'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RotationPolicies;