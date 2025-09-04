'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '@/lib/api';
import { 
  PlatformInfo, 
  PlatformListResponse, 
  PlatformUserConfigCreate, 
  PlatformUserConfigUpdate 
} from '@/types/platform';
import { Settings, RefreshCw, Eye, EyeOff, AlertTriangle, CheckCircle, Info, Trash2 } from 'lucide-react';
import { getPlatformIcon } from '@/lib/platformIcons';

export default function PlatformManagement() {
  const [platforms, setPlatforms] = useState<PlatformInfo[]>([]);
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
      const response = await api.platforms.getAll();
      setPlatforms((response.data as PlatformListResponse).platforms);
    } catch (error) {
      console.error('Failed to load platform data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConfigUpdate = async (platformName: string, updates: PlatformUserConfigUpdate) => {
    try {
      setSaving(platformName);
      if (platforms.find(p => p.definition.name === platformName)?.is_configured) {
        // Update existing config
        await api.platforms.updateConfig(platformName, updates);
      } else {
        // Create new config
        await api.platforms.createConfig(platformName, updates);
      }
      await loadData(); // Reload data
    } catch (error) {
      console.error(`Failed to update ${platformName} config:`, error);
    } finally {
      setSaving(null);
    }
  };

  const debouncedUpdate = useCallback((platformName: string, updates: PlatformUserConfigUpdate) => {
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

  const handleFieldUpdate = (platform: PlatformInfo, fieldKey: string, value: string | boolean, section: 'credentials' | 'settings' = 'credentials') => {
    const currentCredentials = platform.user_config?.user_credentials || {};
    const currentSettings = platform.user_config?.custom_settings || {};
    
    // Process value based on type
    const processedValue = typeof value === 'string' ? (value.trim() || undefined) : value;
    
    // Determine which section to update
    const updatedData = section === 'credentials' 
      ? {
          user_credentials: {
            ...currentCredentials,
            [fieldKey]: processedValue,
          },
          custom_settings: currentSettings,
        }
      : {
          user_credentials: currentCredentials,
          custom_settings: {
            ...currentSettings,
            [fieldKey]: processedValue,
          },
        };
    
    // Update local state immediately for UI responsiveness
    setPlatforms(prev => prev.map(p => 
      p.definition.name === platform.definition.name 
        ? { 
            ...p, 
            user_config: p.user_config 
              ? { ...p.user_config, ...updatedData } 
              : {
                  platform_name: p.definition.name,
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                  ...updatedData,
                },
            is_configured: true
          }
        : p
    ));
    
    // Save to server 1 second after last input
    debouncedUpdate(platform.definition.name, updatedData);
  };

  const togglePasswordVisibility = (platformName: string, fieldKey: string) => {
    const key = `${platformName}_${fieldKey}`;
    setShowPasswords(prev => ({
      ...prev,
      [key]: !prev[key],
    }));
  };

  // Generate dynamic form fields from JSON schema
  const renderSchemaField = (platform: PlatformInfo, fieldName: string, fieldSchema: any, section: 'credentials' | 'settings' = 'credentials') => {
    // Get current field value
    const currentValue = section === 'credentials' 
      ? platform.user_config?.user_credentials?.[fieldName] || ''
      : platform.user_config?.custom_settings?.[fieldName] || '';

    // Determine field properties
    const fieldType = fieldSchema.type || 'string';
    const title = fieldSchema.title || fieldName;
    const description = fieldSchema.description || '';
    const isRequired = platform.definition.config_schema.required?.includes(fieldName) || false;
    const defaultValue = fieldSchema.default;
    
    // Detect password fields by name patterns
    const isPassword = fieldName.toLowerCase().includes('password') || fieldName.toLowerCase().includes('secret') || fieldName.toLowerCase().includes('token');
    const visibilityKey = `${platform.definition.name}_${fieldName}`;
    const isVisible = showPasswords[visibilityKey];

    // Handle boolean type fields
    if (fieldType === 'boolean') {
      return (
        <div key={fieldName} className="flex items-center justify-between space-x-3">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-900">
              {title}
              {isRequired && <span className="text-red-500 ml-1">*</span>}
            </label>
            {description && (
              <p className="text-xs text-gray-600 mt-1">{description}</p>
            )}
          </div>
          <button
            type="button"
            onClick={() => handleFieldUpdate(platform, fieldName, !currentValue, section)}
            className={`${
              currentValue ? 'bg-blue-600' : 'bg-gray-200'
            } relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2`}
          >
            <span
              className={`${
                currentValue ? 'translate-x-6' : 'translate-x-1'
              } inline-block h-4 w-4 transform rounded-full bg-white transition-transform`}
            />
          </button>
        </div>
      );
    }

    // Handle string/number type fields
    return (
      <div key={fieldName} className="space-y-2">
        <label className="block text-sm font-medium text-gray-900">
          {title}
          {isRequired && <span className="text-red-500 ml-1">*</span>}
        </label>
        
        <div className="relative">
          <input
            type={isPassword && !isVisible ? 'password' : fieldType === 'integer' || fieldType === 'number' ? 'number' : 'text'}
            value={currentValue}
            onChange={(e) => handleFieldUpdate(platform, fieldName, e.target.value, section)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 pr-10 text-gray-900 bg-white"
            placeholder={defaultValue ? `Default: ${defaultValue}` : `Enter ${title.toLowerCase()}`}
          />
          
          {isPassword && (
            <button
              type="button"
              onClick={() => togglePasswordVisibility(platform.definition.name, fieldName)}
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

        {description && (
          <p className="text-xs text-gray-600">{description}</p>
        )}

        {isRequired && !currentValue && (
          <div className="flex items-center space-x-1 text-orange-600">
            <AlertTriangle className="w-3 h-3" />
            <span className="text-xs">This field is required for proper functionality</span>
          </div>
        )}
      </div>
    );
  };

  // Delete platform configuration
  const handleDeleteConfig = async (platformName: string) => {
    if (!window.confirm(`Are you sure you want to delete the configuration for ${platformName}?`)) {
      return;
    }
    
    try {
      setSaving(platformName);
      await api.platforms.deleteConfig(platformName);
      await loadData();
    } catch (error) {
      console.error(`Failed to delete ${platformName} config:`, error);
    } finally {
      setSaving(null);
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
        
      </div>

      <div className="grid gap-6">
        {platforms.map((platform) => (
          <div key={platform.definition.name} className="bg-white border border-gray-200 rounded-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                {getPlatformIcon(platform.definition.name)}
                <div>
                  <h3 className="text-lg font-medium text-gray-900">{platform.definition.display_name}</h3>
                  <p className="text-sm text-gray-600">{platform.definition.description}</p>
                </div>
                {platform.is_configured && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </div>
              
              <div className="flex items-center space-x-2">
                {saving === platform.definition.name && (
                  <div className="flex items-center space-x-2 text-blue-600">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Saving...</span>
                  </div>
                )}
                
                {platform.is_configured && (
                  <button
                    onClick={() => handleDeleteConfig(platform.definition.name)}
                    className="p-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded"
                    title="Delete configuration"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            </div>

            {/* Platform Requirements Info */}
            <div className="mb-4 p-3 bg-gray-50 rounded-lg text-sm">
              <div className="flex items-start space-x-2">
                <Info className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
                <div className="flex-1 space-y-1">
                  <p className="text-gray-900"><strong>Features:</strong> {[
                    platform.definition.requires_auth && "Authentication Required",
                    platform.definition.supports_chat && "Chat Recording",
                    platform.definition.supports_vod && "VOD Support"
                  ].filter(Boolean).join(", ") || "Basic streaming"}</p>
                  
                  <p className="text-gray-900"><strong>Qualities:</strong> {platform.definition.supported_qualities.join(", ")}</p>
                  
                  {platform.definition.help_text && (
                    <p className="text-gray-700">{platform.definition.help_text}</p>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              {/* Generate form fields from JSON schema */}
              {platform.definition.config_schema.properties && Object.keys(platform.definition.config_schema.properties).length > 0 ? (
                <div className="space-y-4">
                  {Object.entries(platform.definition.config_schema.properties).map(([fieldName, fieldSchema]) => (
                    <div key={fieldName}>
                      {renderSchemaField(platform, fieldName, fieldSchema, 'credentials')}
                    </div>
                  ))}
                  
                  {/* Setup Instructions */}
                  {platform.definition.setup_instructions && !platform.is_configured && (
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Setup Instructions</h4>
                      <div className="text-sm text-blue-800 whitespace-pre-line">
                        {platform.definition.setup_instructions}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-6 text-gray-500">
                  <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>This platform doesn't require any configuration.</p>
                </div>
              )}
            </div>

            {platform.user_config && (
              <div className="mt-4 pt-4 border-t border-gray-200 text-xs text-gray-500">
                <p>Last updated: {new Date(platform.user_config.updated_at).toLocaleString()}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {platforms.length === 0 && (
        <div className="text-center py-8 text-gray-700">
          <Settings className="w-12 h-12 mx-auto mb-4 opacity-50 text-gray-600" />
          <p>No platforms available. Please check your system configuration.</p>
        </div>
      )}
    </div>
  );
}