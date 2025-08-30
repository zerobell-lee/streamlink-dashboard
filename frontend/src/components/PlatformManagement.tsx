'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Switch } from '@headlessui/react';
import { api } from '@/lib/api';
import { PlatformConfig, PlatformConfigUpdate, SupportedPlatformsResponse, PlatformSchemas, PlatformFieldSchema } from '@/types/platform';
import { Settings, Save, RefreshCw, Eye, EyeOff, ExternalLink, AlertTriangle } from 'lucide-react';
import { getPlatformIcon } from '@/lib/platformIcons';

export default function PlatformManagement() {
  const [platforms, setPlatforms] = useState<PlatformConfig[]>([]);
  const [supportedPlatforms, setSupportedPlatforms] = useState<string[]>([]);
  const [platformSchemas, setPlatformSchemas] = useState<PlatformSchemas>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<string | null>(null);
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});
  const debounceTimers = useRef<Record<string, NodeJS.Timeout>>({});


  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [platformsRes, supportedRes, schemasRes] = await Promise.all([
        api.platforms.getAll(),
        api.platforms.getSupported(),
        api.platforms.getSchemas(),
      ]);
      
      setPlatforms(platformsRes.data);
      setSupportedPlatforms((supportedRes.data as SupportedPlatformsResponse).supported_platforms);
      setPlatformSchemas(schemasRes.data);
    } catch (error) {
      console.error('Failed to load platform data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfigUpdate = async (platformName: string, updates: PlatformConfigUpdate) => {
    try {
      setSaving(platformName);
      await api.platforms.updateConfig(platformName, updates);
      await loadData(); // Reload data
    } catch (error) {
      console.error(`Failed to update ${platformName} config:`, error);
    } finally {
      setSaving(null);
    }
  };

  const debouncedUpdate = useCallback((platformName: string, updates: PlatformConfigUpdate) => {
    const key = `${platformName}`;
    
    // Clear existing timer (restart 1 second countdown from last input)
    if (debounceTimers.current[key]) {
      clearTimeout(debounceTimers.current[key]);
    }
    
    // Set new timer - save 1 second after last input
    debounceTimers.current[key] = setTimeout(() => {
      handleConfigUpdate(platformName, updates);
      delete debounceTimers.current[key];
    }, 1000);
  }, []);



  const handleFieldUpdate = (platform: PlatformConfig, fieldKey: string, value: string) => {
    const updatedSettings = {
      ...platform.additional_settings,
      [fieldKey]: value.trim() || undefined,
    };
    
    // Update local state immediately for UI responsiveness
    setPlatforms(prev => prev.map(p => 
      p.platform === platform.platform 
        ? { ...p, additional_settings: updatedSettings }
        : p
    ));
    
    // Save to server 1 second after last input
    debouncedUpdate(platform.platform, {
      additional_settings: updatedSettings,
    });
  };

  const togglePasswordVisibility = (platformName: string, fieldKey: string) => {
    const key = `${platformName}_${fieldKey}`;
    setShowPasswords(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  const renderPlatformField = (platform: PlatformConfig, field: PlatformFieldSchema) => {
    const value = platform.additional_settings?.[field.key] || '';
    const isPasswordType = field.type === 'password';
    const visibilityKey = `${platform.platform}_${field.key}`;
    const isVisible = showPasswords[visibilityKey];

    return (
      <div key={field.key} className="space-y-2">
        <label className="block text-sm font-medium text-gray-900">
          {field.label}
          {field.required && <span className="text-red-500 ml-1">*</span>}
        </label>
        
        <div className="relative">
          <input
            type={isPasswordType && !isVisible ? 'password' : 'text'}
            value={value}
            onChange={(e) => handleFieldUpdate(platform, field.key, e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10 text-gray-900 bg-white"
            placeholder={field.placeholder}
          />
          
          {isPasswordType && (
            <button
              type="button"
              onClick={() => togglePasswordVisibility(platform.platform, field.key)}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 p-1 hover:bg-gray-100 rounded"
            >
              {isVisible ? (
                <EyeOff className="w-4 h-4 text-gray-500" />
              ) : (
                <Eye className="w-4 h-4 text-gray-500" />
              )}
            </button>
          )}
        </div>

        <div className="flex items-start space-x-2">
          <p className="text-xs text-gray-700 flex-1">
            {field.description}
          </p>
          {field.help_url && (
            <a
              href={field.help_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 flex items-center space-x-1"
            >
              <ExternalLink className="w-3 h-3" />
              <span className="text-xs">Help</span>
            </a>
          )}
        </div>

        {field.required && !value && (
          <div className="flex items-center space-x-1 text-orange-600">
            <AlertTriangle className="w-3 h-3" />
            <span className="text-xs">This field is required for proper functionality</span>
          </div>
        )}
      </div>
    );
  };

  const initializePlatforms = async () => {
    try {
      setLoading(true);
      await api.platforms.initialize();
      await loadData();
    } catch (error) {
      console.error('Failed to initialize platforms:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="w-6 h-6 animate-spin text-gray-700" />
        <span className="ml-2 text-gray-900">Loading platforms...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Settings className="w-6 h-6 text-gray-700" />
          <h2 className="text-xl font-semibold text-gray-900">Platform Management</h2>
        </div>
        
        {platforms.length === 0 && (
          <button
            onClick={initializePlatforms}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Initialize Platforms</span>
          </button>
        )}
      </div>

      <div className="grid gap-6">
        {platforms.map((platform) => (
          <div key={platform.id} className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {getPlatformIcon(platform.platform)}
                <h3 className="text-lg font-medium capitalize text-gray-900">{platform.platform}</h3>
                <Switch
                  checked={platform.enabled}
                  onChange={(enabled) => handleConfigUpdate(platform.platform, { enabled })}
                  className={`${
                    platform.enabled ? 'bg-green-600' : 'bg-gray-200'
                  } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2`}
                >
                  <span
                    className={`${
                      platform.enabled ? 'translate-x-6' : 'translate-x-1'
                    } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
                  />
                </Switch>
              </div>
              
              {saving === platform.platform && (
                <div className="flex items-center space-x-2 text-blue-600">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Saving...</span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 gap-4">

              {/* Dynamic Platform-specific Fields */}
              {platformSchemas[platform.platform] && (
                <>
                  {/* Required Fields */}
                  {platformSchemas[platform.platform].required_fields.map((field) => (
                    <div key={field.key} className="md:col-span-2">
                      {renderPlatformField(platform, field)}
                    </div>
                  ))}
                  
                  {/* Optional Fields */}
                  {platformSchemas[platform.platform].optional_fields.length > 0 && (
                    <div className="md:col-span-2">
                      <details className="group">
                        <summary className="cursor-pointer text-sm font-medium text-gray-800 hover:text-gray-900">
                          Optional Settings ({platformSchemas[platform.platform].optional_fields.length})
                        </summary>
                        <div className="mt-3 space-y-4 pl-4 border-l-2 border-gray-200">
                          {platformSchemas[platform.platform].optional_fields.map((field) => 
                            renderPlatformField(platform, field)
                          )}
                        </div>
                      </details>
                    </div>
                  )}
                </>
              )}

            </div>

            <div className="mt-4 text-xs text-gray-700">
              <p>Updated: {new Date(platform.updated_at).toLocaleString()}</p>
            </div>
          </div>
        ))}
      </div>

      {platforms.length === 0 && (
        <div className="text-center py-8 text-gray-700">
          <Settings className="w-12 h-12 mx-auto mb-4 opacity-50 text-gray-600" />
          <p>No platforms configured. Click "Initialize Platforms" to set up default configurations.</p>
        </div>
      )}
    </div>
  );
}