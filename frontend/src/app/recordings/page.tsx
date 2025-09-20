'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Search,
  Filter,
  Download,
  Trash2,
  Star,
  Grid3X3,
  List,
  Calendar,
  Clock,
  HardDrive,
  Video,
  RefreshCw,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  AlertCircle,
  PlayCircle
} from 'lucide-react';
import clsx from 'clsx';
import DashboardLayout from '@/components/DashboardLayout';
import { api } from '@/lib/api';
import { formatDate, formatDuration, formatFileSize } from '@/lib/utils';
import { getPlatformIcon } from '@/lib/platformIcons';
import ErrorMessageModal from '@/components/ErrorMessageModal';

interface Recording {
  id: number;
  file_name: string;
  file_size: number;
  platform: string;
  streamer_name: string;
  quality: string;
  start_time: string;
  end_time?: string;
  duration: number;
  is_favorite: boolean;
  status: string;
  file_path: string;
  error_message?: string;
}

interface FilterOptions {
  platform: string;
  status: string;
  favorite: boolean | null;
  quality: string;
  dateRange: 'all' | 'today' | 'week' | 'month' | 'year';
}

type ViewMode = 'list' | 'grid';
type SortField = 'name' | 'date' | 'size' | 'duration' | 'streamer';

export default function RecordingsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRecordings, setSelectedRecordings] = useState<Set<number>>(new Set());
  const [sortBy, setSortBy] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [showFilters, setShowFilters] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(15);
  const [filters, setFilters] = useState<FilterOptions>({
    platform: 'all',
    status: 'all',
    favorite: null,
    quality: 'all',
    dateRange: 'all'
  });
  const [errorModalOpen, setErrorModalOpen] = useState(false);
  const [selectedErrorRecording, setSelectedErrorRecording] = useState<Recording | null>(null);

  const queryClient = useQueryClient();

  // Fetch recordings
  const { data: recordings = [], isLoading, error, refetch } = useQuery({
    queryKey: ['recordings'],
    queryFn: async () => {
      const response = await api.recordings.getAll();
      return response.data as Recording[];
    }
  });

  // Toggle favorite mutation
  const toggleFavoriteMutation = useMutation({
    mutationFn: (id: number) => api.recordings.toggleFavorite(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['recordings'] });
    }
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.recordings.delete(id),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: ['recordings'] });
      setSelectedRecordings(prev => {
        const newSet = new Set(prev);
        newSet.delete(deletedId);
        return newSet;
      });
    }
  });

  // Filter and sort recordings
  const filteredAndSortedRecordings = recordings
    .filter(recording => {
      // Search filter
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        if (!recording.file_name.toLowerCase().includes(query) &&
            !recording.streamer_name.toLowerCase().includes(query)) {
          return false;
        }
      }

      // Platform filter
      if (filters.platform !== 'all' && recording.platform !== filters.platform) {
        return false;
      }

      // Status filter
      if (filters.status !== 'all' && recording.status !== filters.status) {
        return false;
      }

      // Favorite filter
      if (filters.favorite !== null && recording.is_favorite !== filters.favorite) {
        return false;
      }

      // Quality filter
      if (filters.quality !== 'all' && recording.quality !== filters.quality) {
        return false;
      }

      // Date range filter
      if (filters.dateRange !== 'all') {
        const recordingDate = new Date(recording.start_time);
        const now = new Date();
        
        switch (filters.dateRange) {
          case 'today':
            if (recordingDate.toDateString() !== now.toDateString()) return false;
            break;
          case 'week':
            const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            if (recordingDate < weekAgo) return false;
            break;
          case 'month':
            const monthAgo = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            if (recordingDate < monthAgo) return false;
            break;
          case 'year':
            const yearAgo = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
            if (recordingDate < yearAgo) return false;
            break;
        }
      }

      return true;
    })
    .sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'name':
          comparison = a.file_name.localeCompare(b.file_name);
          break;
        case 'date':
          comparison = new Date(a.start_time).getTime() - new Date(b.start_time).getTime();
          break;
        case 'size':
          comparison = a.file_size - b.file_size;
          break;
        case 'duration':
          comparison = a.duration - b.duration;
          break;
        case 'streamer':
          comparison = a.streamer_name.localeCompare(b.streamer_name);
          break;
      }
      
      return sortOrder === 'desc' ? -comparison : comparison;
    });

  // Pagination logic
  const totalRecordings = filteredAndSortedRecordings.length;
  const totalPages = Math.ceil(totalRecordings / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const paginatedRecordings = filteredAndSortedRecordings.slice(startIndex, endIndex);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchQuery, filters, sortBy, sortOrder]);

  // Get unique values for filter options
  const platforms = [...new Set(recordings.map(r => r.platform))];
  const statuses = [...new Set(recordings.map(r => r.status))];
  const qualities = [...new Set(recordings.map(r => r.quality))];

  const toggleSelection = (id: number) => {
    const newSelected = new Set(selectedRecordings);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedRecordings(newSelected);
  };

  const selectAll = () => {
    if (selectedRecordings.size === paginatedRecordings.length) {
      setSelectedRecordings(new Set());
    } else {
      setSelectedRecordings(new Set(paginatedRecordings.map(r => r.id)));
    }
  };

  const handleBulkDelete = async () => {
    if (selectedRecordings.size === 0) return;
    
    const confirmMessage = `Delete ${selectedRecordings.size} recordings?`;
    if (window.confirm(confirmMessage)) {
      for (const id of selectedRecordings) {
        await deleteMutation.mutateAsync(id);
      }
      setSelectedRecordings(new Set());
    }
  };

  const handleBulkFavorite = async (favorite: boolean) => {
    if (selectedRecordings.size === 0) return;
    
    for (const id of selectedRecordings) {
      const recording = recordings.find(r => r.id === id);
      if (recording && recording.is_favorite !== favorite) {
        await toggleFavoriteMutation.mutateAsync(id);
      }
    }
  };

  const getPlatformColor = (platform: string): string => {
    const colors: Record<string, string> = {
      'twitch': 'bg-purple-100 text-purple-800 border-purple-200 dark:bg-purple-900/20 dark:text-purple-300 dark:border-purple-800/30',
      'youtube': 'bg-red-100 text-red-800 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800/30',
      'sooplive': 'bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/20 dark:text-orange-300 dark:border-orange-800/30',
      'chzzk': 'bg-green-100 text-green-800 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800/30',
      'default': 'bg-muted text-muted-foreground border-border'
    };
    return colors[platform.toLowerCase()] || colors.default;
  };

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      'completed': 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300',
      'recording': 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300',
      'failed': 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
      'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300',
      'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300',
      'default': 'bg-muted text-muted-foreground'
    };
    return colors[status] || colors.default;
  };

  // Statistics
  const totalSize = recordings.reduce((acc, r) => acc + r.file_size, 0);
  const totalDuration = recordings.reduce((acc, r) => acc + r.duration, 0);
  const favoriteCount = recordings.filter(r => r.is_favorite).length;

  if (error) {
    return (
      <div className="p-6 text-center">
        <div className="text-destructive mb-4">Failed to load recordings</div>
        <button 
          onClick={() => refetch()} 
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <DashboardLayout>
      <div className="p-6">
        <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center">
            <PlayCircle className="h-8 w-8 mr-3 text-red-500" />
            Recordings
          </h1>
          <p className="text-muted-foreground mt-1">
            {totalRecordings} of {recordings.length} recordings
            {totalPages > 1 && (
              <span className="ml-2">
                • Page {currentPage} of {totalPages}
              </span>
            )}
          </p>
        </div>
        
        <button
          onClick={() => refetch()}
          disabled={isLoading}
          className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
        >
          <RefreshCw className={clsx("h-4 w-4", isLoading && "animate-spin")} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card rounded-lg border p-4">
          <div className="flex items-center">
            <Video className="h-5 w-5 text-blue-600 dark:text-blue-400" />
            <span className="ml-2 text-sm font-medium text-foreground">Total</span>
          </div>
          <div className="mt-2 text-2xl font-bold text-foreground">{recordings.length}</div>
        </div>
        
        <div className="bg-card rounded-lg border p-4">
          <div className="flex items-center">
            <Star className="h-5 w-5 text-yellow-500" />
            <span className="ml-2 text-sm font-medium text-foreground">Favorites</span>
          </div>
          <div className="mt-2 text-2xl font-bold text-foreground">{favoriteCount}</div>
        </div>
        
        <div className="bg-card rounded-lg border p-4">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-green-600 dark:text-green-400" />
            <span className="ml-2 text-sm font-medium text-foreground">Total Duration</span>
          </div>
          <div className="mt-2 text-2xl font-bold text-foreground">{formatDuration(totalDuration)}</div>
        </div>
        
        <div className="bg-card rounded-lg border p-4">
          <div className="flex items-center">
            <HardDrive className="h-5 w-5 text-purple-600 dark:text-purple-400" />
            <span className="ml-2 text-sm font-medium text-foreground">Total Size</span>
          </div>
          <div className="mt-2 text-2xl font-bold text-foreground">{formatFileSize(totalSize)}</div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-card rounded-lg border">
        <div className="p-4 border-b">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search recordings..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 bg-background border border-input rounded-md text-foreground focus:ring-2 focus:ring-ring focus:border-input"
              />
            </div>
            
            {/* View Controls */}
            <div className="flex items-center space-x-2">
              <div className="flex bg-muted rounded-md p-1">
                <button
                  onClick={() => setViewMode('list')}
                  className={clsx(
                    "px-3 py-1 rounded text-sm font-medium transition-colors",
                    viewMode === 'list'
                      ? "bg-background text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <List className="h-4 w-4" />
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={clsx(
                    "px-3 py-1 rounded text-sm font-medium transition-colors",
                    viewMode === 'grid'
                      ? "bg-background text-foreground shadow-sm"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <Grid3X3 className="h-4 w-4" />
                </button>
              </div>
              
              <button
                onClick={() => setShowFilters(!showFilters)}
                className={clsx(
                  "flex items-center space-x-2 px-3 py-2 rounded-md border transition-colors",
                  showFilters
                    ? "bg-primary/10 border-primary/20 text-primary"
                    : "border-input text-foreground hover:bg-accent"
                )}
              >
                <Filter className="h-4 w-4" />
                <span>Filters</span>
                <ChevronDown className={clsx("h-4 w-4 transition-transform", showFilters && "rotate-180")} />
              </button>
            </div>
          </div>
          
          {/* Filters Panel */}
          {showFilters && (
            <div className="mt-4 p-4 bg-muted rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Platform</label>
                  <select
                    value={filters.platform}
                    onChange={(e) => setFilters(prev => ({ ...prev, platform: e.target.value }))}
                    className="w-full px-3 py-2 bg-background border border-input rounded-md text-sm text-foreground"
                  >
                    <option value="all">All Platforms</option>
                    {platforms.map(platform => (
                      <option key={platform} value={platform}>{platform}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Status</label>
                  <select
                    value={filters.status}
                    onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
                    className="w-full px-3 py-2 bg-background border border-input rounded-md text-sm text-foreground"
                  >
                    <option value="all">All Status</option>
                    {statuses.map(status => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Quality</label>
                  <select
                    value={filters.quality}
                    onChange={(e) => setFilters(prev => ({ ...prev, quality: e.target.value }))}
                    className="w-full px-3 py-2 bg-background border border-input rounded-md text-sm text-foreground"
                  >
                    <option value="all">All Quality</option>
                    {qualities.map(quality => (
                      <option key={quality} value={quality}>{quality}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Favorites</label>
                  <select
                    value={filters.favorite === null ? 'all' : filters.favorite ? 'true' : 'false'}
                    onChange={(e) => {
                      const value = e.target.value === 'all' ? null : e.target.value === 'true';
                      setFilters(prev => ({ ...prev, favorite: value }));
                    }}
                    className="w-full px-3 py-2 bg-background border border-input rounded-md text-sm text-foreground"
                  >
                    <option value="all">All</option>
                    <option value="true">Favorites Only</option>
                    <option value="false">Non-Favorites</option>
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-foreground mb-1">Date Range</label>
                  <select
                    value={filters.dateRange}
                    onChange={(e) => setFilters(prev => ({ ...prev, dateRange: e.target.value as FilterOptions['dateRange'] }))}
                    className="w-full px-3 py-2 bg-background border border-input rounded-md text-sm text-foreground"
                  >
                    <option value="all">All Time</option>
                    <option value="today">Today</option>
                    <option value="week">This Week</option>
                    <option value="month">This Month</option>
                    <option value="year">This Year</option>
                  </select>
                </div>
              </div>
              
              <div className="mt-4 flex justify-end">
                <button
                  onClick={() => setFilters({
                    platform: 'all',
                    status: 'all',
                    favorite: null,
                    quality: 'all',
                    dateRange: 'all'
                  })}
                  className="px-3 py-1 text-sm text-muted-foreground hover:text-foreground"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>
        
        {/* Toolbar */}
        <div className="px-4 py-3 border-b bg-muted/50 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={selectedRecordings.size > 0 && selectedRecordings.size === paginatedRecordings.length}
                onChange={selectAll}
                className="h-4 w-4 text-primary rounded border-input"
              />
              <span className="text-sm text-foreground">
                {selectedRecordings.size > 0 ? `${selectedRecordings.size} selected` : 'Select all'}
              </span>
            </div>
            
            {selectedRecordings.size > 0 && (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleBulkFavorite(true)}
                  className="flex items-center space-x-1 px-2 py-1 text-sm text-yellow-700 hover:text-yellow-800 hover:bg-yellow-50 dark:text-yellow-400 dark:hover:text-yellow-300 dark:hover:bg-yellow-900/20 rounded"
                >
                  <Star className="h-4 w-4" />
                  <span>Favorite</span>
                </button>
                <button
                  onClick={() => handleBulkFavorite(false)}
                  className="flex items-center space-x-1 px-2 py-1 text-sm text-muted-foreground hover:text-foreground hover:bg-accent rounded"
                >
                  <Star className="h-4 w-4" />
                  <span>Unfavorite</span>
                </button>
                <button
                  onClick={handleBulkDelete}
                  className="flex items-center space-x-1 px-2 py-1 text-sm text-destructive hover:text-destructive/90 hover:bg-destructive/10 rounded"
                >
                  <Trash2 className="h-4 w-4" />
                  <span>Delete</span>
                </button>
              </div>
            )}
          </div>
          
          <div className="flex items-center space-x-2">
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortField)}
              className="px-3 py-1 bg-background border border-input rounded text-sm text-foreground"
            >
              <option value="date">Sort by Date</option>
              <option value="name">Sort by Name</option>
              <option value="size">Sort by Size</option>
              <option value="duration">Sort by Duration</option>
              <option value="streamer">Sort by Streamer</option>
            </select>
            
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="px-2 py-1 bg-background border border-input rounded text-sm text-foreground hover:bg-accent"
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex justify-center items-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : totalRecordings === 0 ? (
        <div className="text-center py-12 bg-card rounded-lg border">
          <Video className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <div className="text-lg font-medium text-foreground mb-2">No recordings found</div>
          <div className="text-muted-foreground">
            {searchQuery || Object.values(filters).some(f => f !== 'all' && f !== null) 
              ? 'Try adjusting your search or filters'
              : 'Recordings will appear here once you start recording streams'
            }
          </div>
        </div>
      ) : (
        <div className="bg-card rounded-lg border">
          {viewMode === 'grid' ? (
            <div className="p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {paginatedRecordings.map((recording) => (
                  <div
                    key={recording.id}
                    className={clsx(
                      "border rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer",
                      selectedRecordings.has(recording.id) && "ring-2 ring-primary bg-primary/10"
                    )}
                    onClick={() => toggleSelection(recording.id)}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center">
                        <Video className="h-6 w-6 text-muted-foreground" />
                      </div>
                      <div className="flex space-x-1">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleFavoriteMutation.mutate(recording.id);
                          }}
                          className={clsx(
                            "p-1 rounded",
                            recording.is_favorite ? "text-yellow-500" : "text-muted-foreground hover:text-yellow-500"
                          )}
                        >
                          <Star className="h-4 w-4" fill={recording.is_favorite ? "currentColor" : "none"} />
                        </button>
                        <button
                          onClick={async (e) => {
                            e.stopPropagation();
                            try {
                              const response = await api.recordings.download(recording.id);
                              const url = window.URL.createObjectURL(response.data);
                              const a = document.createElement('a');
                              a.style.display = 'none';
                              a.href = url;
                              a.download = recording.file_name;
                              document.body.appendChild(a);
                              a.click();
                              window.URL.revokeObjectURL(url);
                              document.body.removeChild(a);
                            } catch (error) {
                              console.error('Download failed:', error);
                              alert('Download failed. Please try again.');
                            }
                          }}
                          className="p-1 text-muted-foreground hover:text-primary rounded"
                        >
                          <Download className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <h3 className="font-medium text-foreground truncate">{recording.file_name}</h3>
                      <p className="text-sm text-muted-foreground">{recording.streamer_name}</p>
                      
                      <div className="flex items-center space-x-2">
                        <div className={clsx("flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border", getPlatformColor(recording.platform))}>
                          {getPlatformIcon(recording.platform, 'sm')}
                          <span>{recording.platform}</span>
                        </div>
                        <span className={clsx("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(recording.status))}>
                          {recording.status}
                        </span>
                      </div>
                      
                      <div className="space-y-1 text-xs text-muted-foreground">
                        <div className="flex items-center space-x-1">
                          <Calendar className="h-3 w-3" />
                          <span>{formatDate(recording.start_time)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock className="h-3 w-3" />
                          <span>{formatDuration(recording.duration)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <HardDrive className="h-3 w-3" />
                          <span>{formatFileSize(recording.file_size)}</span>
                        </div>
                        {recording.status === 'failed' && recording.error_message && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedErrorRecording(recording);
                              setErrorModalOpen(true);
                            }}
                            className="flex items-center space-x-1 text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 px-2 py-1 rounded text-left w-full"
                          >
                            <AlertCircle className="h-3 w-3 flex-shrink-0" />
                            <span className="text-xs">에러 상세 보기</span>
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="divide-y divide-border">
              {paginatedRecordings.map((recording) => (
                <div
                  key={recording.id}
                  className={clsx(
                    "p-4 hover:bg-accent/50 transition-colors cursor-pointer",
                    selectedRecordings.has(recording.id) && "bg-primary/10"
                  )}
                  onClick={() => toggleSelection(recording.id)}
                >
                  <div className="flex items-center space-x-4">
                    <input
                      type="checkbox"
                      checked={selectedRecordings.has(recording.id)}
                      onChange={() => toggleSelection(recording.id)}
                      onClick={(e) => e.stopPropagation()}
                      className="h-4 w-4 text-primary rounded border-input"
                    />
                    
                    <div className="w-10 h-10 bg-muted rounded-lg flex items-center justify-center">
                      <Video className="h-5 w-5 text-muted-foreground" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2">
                        <h3 className="font-medium text-foreground truncate">{recording.file_name}</h3>
                        {recording.is_favorite && (
                          <Star className="h-4 w-4 text-yellow-500" fill="currentColor" />
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{recording.streamer_name}</p>
                      {recording.status === 'failed' && recording.error_message && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedErrorRecording(recording);
                            setErrorModalOpen(true);
                          }}
                          className="flex items-center space-x-1 text-xs text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 hover:bg-red-50 dark:hover:bg-red-900/20 px-2 py-1 rounded mt-1"
                        >
                          <AlertCircle className="h-3 w-3" />
                          <span>에러 상세 보기</span>
                        </button>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <div className={clsx("flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border", getPlatformColor(recording.platform))}>
                        {getPlatformIcon(recording.platform, 'sm')}
                        <span>{recording.platform}</span>
                      </div>
                      <span className={clsx("px-2 py-1 rounded-full text-xs font-medium", getStatusColor(recording.status))}>
                        {recording.status}
                      </span>
                      <span>{recording.quality}</span>
                      <span>{formatDuration(recording.duration)}</span>
                      <span>{formatFileSize(recording.file_size)}</span>
                      <span>{formatDate(recording.start_time)}</span>
                    </div>
                    
                    <div className="flex items-center space-x-1">
                      <button
                        onClick={async (e) => {
                          e.stopPropagation();
                          try {
                            const response = await api.recordings.download(recording.id);
                            const url = window.URL.createObjectURL(response.data);
                            const a = document.createElement('a');
                            a.style.display = 'none';
                            a.href = url;
                            a.download = recording.file_name;
                            document.body.appendChild(a);
                            a.click();
                            window.URL.revokeObjectURL(url);
                            document.body.removeChild(a);
                          } catch (error) {
                            console.error('Download failed:', error);
                            alert('Download failed. Please try again.');
                          }
                        }}
                        className="p-1 text-muted-foreground hover:text-primary rounded"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleFavoriteMutation.mutate(recording.id);
                        }}
                        className={clsx(
                          "p-1 rounded",
                          recording.is_favorite ? "text-yellow-500" : "text-muted-foreground hover:text-yellow-500"
                        )}
                      >
                        <Star className="h-4 w-4" fill={recording.is_favorite ? "currentColor" : "none"} />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          if (window.confirm('Delete this recording?')) {
                            deleteMutation.mutate(recording.id);
                          }
                        }}
                        className="p-1 text-muted-foreground hover:text-destructive rounded"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="bg-card border-t px-6 py-3 flex items-center justify-between">
          <div className="flex items-center text-sm text-foreground">
            <span>
              Showing {startIndex + 1} to {Math.min(endIndex, totalRecordings)} of {totalRecordings} recordings
            </span>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className={clsx(
                "flex items-center px-3 py-2 text-sm font-medium rounded-md",
                currentPage === 1
                  ? "text-muted-foreground cursor-not-allowed"
                  : "text-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              <ChevronLeft className="h-4 w-4 mr-1" />
              Previous
            </button>
            
            <div className="flex items-center space-x-1">
              {/* Page numbers */}
              {(() => {
                const maxVisiblePages = 5;
                const pages = [];
                let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
                const endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
                
                // Adjust if we're near the end
                if (endPage - startPage < maxVisiblePages - 1) {
                  startPage = Math.max(1, endPage - maxVisiblePages + 1);
                }
                
                // Add first page and ellipsis if needed
                if (startPage > 1) {
                  pages.push(
                    <button
                      key={1}
                      onClick={() => setCurrentPage(1)}
                      className="px-3 py-2 text-sm font-medium text-foreground hover:text-foreground hover:bg-accent rounded-md"
                    >
                      1
                    </button>
                  );
                  if (startPage > 2) {
                    pages.push(
                      <span key="start-ellipsis" className="px-2 py-2 text-sm text-muted-foreground">
                        ...
                      </span>
                    );
                  }
                }
                
                // Add visible pages
                for (let i = startPage; i <= endPage; i++) {
                  pages.push(
                    <button
                      key={i}
                      onClick={() => setCurrentPage(i)}
                      className={clsx(
                        "px-3 py-2 text-sm font-medium rounded-md",
                        i === currentPage
                          ? "bg-primary text-primary-foreground"
                          : "text-foreground hover:text-foreground hover:bg-accent"
                      )}
                    >
                      {i}
                    </button>
                  );
                }
                
                // Add last page and ellipsis if needed
                if (endPage < totalPages) {
                  if (endPage < totalPages - 1) {
                    pages.push(
                      <span key="end-ellipsis" className="px-2 py-2 text-sm text-muted-foreground">
                        ...
                      </span>
                    );
                  }
                  pages.push(
                    <button
                      key={totalPages}
                      onClick={() => setCurrentPage(totalPages)}
                      className="px-3 py-2 text-sm font-medium text-foreground hover:text-foreground hover:bg-accent rounded-md"
                    >
                      {totalPages}
                    </button>
                  );
                }
                
                return pages;
              })()}
            </div>
            
            <button
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className={clsx(
                "flex items-center px-3 py-2 text-sm font-medium rounded-md",
                currentPage === totalPages
                  ? "text-muted-foreground cursor-not-allowed"
                  : "text-foreground hover:text-foreground hover:bg-accent"
              )}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>
        </div>
      )}

      {/* Error Message Modal */}
      {selectedErrorRecording && (
        <ErrorMessageModal
          isOpen={errorModalOpen}
          onClose={() => {
            setErrorModalOpen(false);
            setSelectedErrorRecording(null);
          }}
          title="레코딩 에러 상세 정보"
          errorMessage={selectedErrorRecording.error_message || ''}
          recordingInfo={{
            fileName: selectedErrorRecording.file_name,
            streamerName: selectedErrorRecording.streamer_name,
            platform: selectedErrorRecording.platform,
            startTime: formatDate(selectedErrorRecording.start_time)
          }}
        />
      )}
        </div>
      </div>
    </DashboardLayout>
  );
}