"use client";

import { useState } from 'react';
import { 
  FolderOpen, 
  Folder, 
  Video, 
  Star, 
  Download, 
  Trash2, 
  Search,
  Calendar,
  HardDrive,
  Filter,
  Grid3X3,
  List,
  ChevronRight,
  ChevronDown
} from 'lucide-react';
import clsx from 'clsx';
import { formatDate } from '@/lib/utils';

const FileExplorer = () => {
  const [viewMode, setViewMode] = useState<'list' | 'grid'>('list');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFolder, setSelectedFolder] = useState('all');
  const [expandedFolders, setExpandedFolders] = useState<string[]>(['platforms']);

  // Mock data structure
  const folderStructure = {
    platforms: {
      twitch: {
        ninja: ['ninja_2024_01_15.mp4', 'ninja_2024_01_14.mp4'],
        shroud: ['shroud_2024_01_15.mp4', 'shroud_2024_01_13.mp4'],
        xqc: ['xqc_2024_01_16.mp4']
      },
      youtube: {
        pewdiepie: ['pewdiepie_2024_01_15.mkv', 'pewdiepie_2024_01_12.mkv'],
        mrbeast: ['mrbeast_2024_01_14.mkv']
      },
      afreecatv: {
        korean_streamer: ['korean_2024_01_15.ts']
      }
    }
  };

  const mockFiles = [
    {
      id: 1,
      name: 'ninja_2024_01_15.mp4',
      path: 'Twitch/Ninja/',
      size: '2.1 GB',
      duration: '02:15:30',
      quality: '1080p',
      date: '2024-01-15T20:00:00Z',
      platform: 'twitch',
      streamer: 'Ninja',
      isFavorite: true,
      thumbnail: null
    },
    {
      id: 2,
      name: 'pewdiepie_2024_01_15.mkv',
      path: 'YouTube/PewDiePie/',
      size: '1.8 GB',
      duration: '01:45:20',
      quality: '1080p',
      date: '2024-01-15T18:30:00Z',
      platform: 'youtube',
      streamer: 'PewDiePie',
      isFavorite: false,
      thumbnail: null
    },
    {
      id: 3,
      name: 'shroud_2024_01_14.mp4',
      path: 'Twitch/Shroud/',
      size: '3.2 GB',
      duration: '03:20:15',
      quality: '1080p60',
      date: '2024-01-14T21:00:00Z',
      platform: 'twitch',
      streamer: 'Shroud',
      isFavorite: true,
      thumbnail: null
    }
  ];

  const toggleFolder = (folderPath: string) => {
    setExpandedFolders(prev => 
      prev.includes(folderPath) 
        ? prev.filter(path => path !== folderPath)
        : [...prev, folderPath]
    );
  };

  const formatFileSize = (size: string) => size;
  const formatDuration = (duration: string) => duration;

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'twitch': return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'youtube': return 'bg-red-100 text-red-800 border-red-200';
      case 'afreecatv': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'sooplive': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'chzzk': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const filteredFiles = mockFiles.filter(file => 
    file.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    file.streamer.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">File Explorer</h1>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('list')}
            className={clsx('p-2 rounded border', viewMode === 'list' ? 'bg-blue-50 border-blue-200 text-blue-600' : 'border-gray-200 text-gray-600 hover:bg-gray-50')}
          >
            <List className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('grid')}
            className={clsx('p-2 rounded border', viewMode === 'grid' ? 'bg-blue-50 border-blue-200 text-blue-600' : 'border-gray-200 text-gray-600 hover:bg-gray-50')}
          >
            <Grid3X3 className="h-4 w-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Folder Tree */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg border h-fit">
            <div className="p-4 border-b">
              <h3 className="font-semibold text-gray-900 flex items-center">
                <Folder className="h-5 w-5 mr-2 text-blue-500" />
                Folders
              </h3>
            </div>
            <div className="p-4">
              <div className="space-y-2">
                <button
                  onClick={() => setSelectedFolder('all')}
                  className={clsx(
                    'w-full flex items-center space-x-2 px-3 py-2 rounded text-left transition-colors',
                    selectedFolder === 'all' ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'
                  )}
                >
                  <FolderOpen className="h-4 w-4" />
                  <span className="text-sm">All Files</span>
                  <span className="text-xs text-gray-500 ml-auto">({mockFiles.length})</span>
                </button>

                <div>
                  <button
                    onClick={() => toggleFolder('platforms')}
                    className="w-full flex items-center space-x-2 px-3 py-2 rounded text-left transition-colors text-gray-700 hover:bg-gray-50"
                  >
                    {expandedFolders.includes('platforms') ? 
                      <ChevronDown className="h-4 w-4" /> : 
                      <ChevronRight className="h-4 w-4" />
                    }
                    <Folder className="h-4 w-4 text-gray-500" />
                    <span className="text-sm">Platforms</span>
                  </button>
                  
                  {expandedFolders.includes('platforms') && (
                    <div className="ml-4 space-y-1">
                      <button
                        onClick={() => setSelectedFolder('twitch')}
                        className={clsx(
                          'w-full flex items-center space-x-2 px-3 py-2 rounded text-left transition-colors',
                          selectedFolder === 'twitch' ? 'bg-purple-50 text-purple-700' : 'text-gray-600 hover:bg-gray-50'
                        )}
                      >
                        <Folder className="h-4 w-4 text-purple-500" />
                        <span className="text-sm">Twitch</span>
                        <span className="text-xs text-gray-500 ml-auto">(2)</span>
                      </button>
                      <button
                        onClick={() => setSelectedFolder('youtube')}
                        className={clsx(
                          'w-full flex items-center space-x-2 px-3 py-2 rounded text-left transition-colors',
                          selectedFolder === 'youtube' ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:bg-gray-50'
                        )}
                      >
                        <Folder className="h-4 w-4 text-red-500" />
                        <span className="text-sm">YouTube</span>
                        <span className="text-xs text-gray-500 ml-auto">(1)</span>
                      </button>
                    </div>
                  )}
                </div>

                <button
                  onClick={() => setSelectedFolder('favorites')}
                  className={clsx(
                    'w-full flex items-center space-x-2 px-3 py-2 rounded text-left transition-colors',
                    selectedFolder === 'favorites' ? 'bg-yellow-50 text-yellow-700' : 'text-gray-700 hover:bg-gray-50'
                  )}
                >
                  <Star className="h-4 w-4 text-yellow-500" />
                  <span className="text-sm">Favorites</span>
                  <span className="text-xs text-gray-500 ml-auto">(2)</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* File List */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg border">
            <div className="p-4 border-b">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <h3 className="font-semibold text-gray-900">Files</h3>
                  <span className="text-sm text-gray-500">({filteredFiles.length} files)</span>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 border rounded hover:bg-gray-50">
                    <Filter className="h-4 w-4 text-gray-500" />
                  </button>
                  <button className="px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700">
                    + Add Favorite
                  </button>
                </div>
              </div>
              
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search files..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="p-4">
              {viewMode === 'list' ? (
                <div className="space-y-3">
                  {filteredFiles.map((file) => (
                    <div key={file.id} className="flex items-center space-x-4 p-4 border rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-3 flex-1">
                        <Video className="h-8 w-8 text-blue-500 flex-shrink-0" />
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <p className="font-medium text-gray-900 truncate">{file.name}</p>
                            {file.isFavorite && <Star className="h-4 w-4 text-yellow-500 fill-current flex-shrink-0" />}
                          </div>
                          <p className="text-sm text-gray-600 truncate">{file.path}</p>
                          <div className="flex items-center space-x-4 mt-2">
                            <span className={`px-2 py-1 text-xs rounded border ${getPlatformColor(file.platform)}`}>
                              {file.platform.toUpperCase()}
                            </span>
                            <span className="text-xs text-gray-500 flex items-center">
                              <HardDrive className="h-3 w-3 mr-1" />
                              {file.size}
                            </span>
                            <span className="text-xs text-gray-500 flex items-center">
                              <Video className="h-3 w-3 mr-1" />
                              {file.duration}
                            </span>
                            <span className="text-xs text-gray-500 flex items-center">
                              <Calendar className="h-3 w-3 mr-1" />
                              {formatDate(file.date)}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2 flex-shrink-0">
                        <button className="p-2 text-gray-400 hover:text-yellow-500">
                          <Star className={clsx('h-4 w-4', file.isFavorite && 'text-yellow-500 fill-current')} />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-blue-500">
                          <Download className="h-4 w-4" />
                        </button>
                        <button className="p-2 text-gray-400 hover:text-red-500">
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {filteredFiles.map((file) => (
                    <div key={file.id} className="border rounded-lg p-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between mb-3">
                        <Video className="h-8 w-8 text-blue-500" />
                        <div className="flex items-center space-x-1">
                          <button className="p-1 text-gray-400 hover:text-yellow-500">
                            <Star className={clsx('h-4 w-4', file.isFavorite && 'text-yellow-500 fill-current')} />
                          </button>
                          <button className="p-1 text-gray-400 hover:text-blue-500">
                            <Download className="h-4 w-4" />
                          </button>
                          <button className="p-1 text-gray-400 hover:text-red-500">
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                      <p className="font-medium text-gray-900 text-sm mb-2 truncate">{file.name}</p>
                      <div className="space-y-2">
                        <span className={`inline-block px-2 py-1 text-xs rounded border ${getPlatformColor(file.platform)}`}>
                          {file.platform.toUpperCase()}
                        </span>
                        <div className="text-xs text-gray-600 space-y-1">
                          <div>{file.size} • {file.duration}</div>
                          <div>{formatDate(file.date)}</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FileExplorer;