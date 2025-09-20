'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { api } from '@/lib/api';
import {
  Search,
  Filter,
  Download,
  Play,
  Pause,
  BarChart3,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Calendar,
  Clock,
  AlertTriangle,
  Activity,
  Eye,
  FileText,
  Trash2
} from 'lucide-react';
import type {
  EnhancedLogFilesResponse,
  PaginatedLogContent,
  LogSearchRequest,
  LogSearchResponse,
  LogAnalytics,
  LogCategoriesResponse,
  LogStreamMessage
} from '@/types';

type LogViewType = 'files' | 'search' | 'analytics' | 'stream';

export default function EnhancedLoggingTab() {

  // State for view mode
  const [activeView, setActiveView] = useState<LogViewType>('files');

  // State for enhanced log files
  const [logFiles, setLogFiles] = useState<EnhancedLogFilesResponse | null>(null);
  const [logFilesLoading, setLogFilesLoading] = useState(false);

  // State for selected file and pagination
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [logContent, setLogContent] = useState<PaginatedLogContent | null>(null);
  const [logContentLoading, setLogContentLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [perPage, setPerPage] = useState(50);

  // State for search
  const [searchRequest, setSearchRequest] = useState<LogSearchRequest>({
    query: '',
    category: '',
    level: '',
    start_time: '',
    end_time: '',
    limit: 1000
  });
  const [searchResponse, setSearchResponse] = useState<LogSearchResponse | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);

  // State for analytics
  const [analytics, setAnalytics] = useState<LogAnalytics | null>(null);
  const [analyticsLoading, setAnalyticsLoading] = useState(false);
  const [analyticsHours, setAnalyticsHours] = useState(24);

  // State for categories
  const [categories, setCategories] = useState<LogCategoriesResponse | null>(null);

  // State for real-time streaming
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamMessages, setStreamMessages] = useState<LogStreamMessage[]>([]);
  const [streamFilters, setStreamFilters] = useState({
    categories: [] as string[],
    levels: [] as string[]
  });
  const wsRef = useRef<WebSocket | null>(null);
  const streamContainerRef = useRef<HTMLDivElement>(null);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      // Load categories
      const categoriesResponse = await api.logs.getCategories();
      console.log('Categories response:', categoriesResponse.data);
      setCategories(categoriesResponse.data);

      // Load log files
      await loadLogFiles();
    } catch (error) {
      console.warn('Failed to load initial logging data:', error);
    }
  };

  const loadLogFiles = async () => {
    setLogFilesLoading(true);
    try {
      const response = await api.logs.getFiles();
      setLogFiles(response.data);
    } catch (error) {
      console.warn('Failed to load log files:', error);
    } finally {
      setLogFilesLoading(false);
    }
  };


  const loadLogFileContent = async (filename: string, page: number = 1) => {
    setLogContentLoading(true);
    try {
      const response = await api.logs.getFileContent(filename, page, perPage, true);
      setLogContent(response.data);
      setCurrentPage(page);
    } catch (error) {
      console.error('Failed to load log file content:', error);
    } finally {
      setLogContentLoading(false);
    }
  };

  const handleFileSelect = (filename: string) => {
    setSelectedFile(filename);
    setCurrentPage(1);
    loadLogFileContent(filename, 1);
  };

  const handlePageChange = (page: number) => {
    if (selectedFile && page !== currentPage) {
      loadLogFileContent(selectedFile, page);
    }
  };

  const handleSearch = async () => {
    setSearchLoading(true);
    try {
      const response = await api.logs.search(searchRequest);
      setSearchResponse(response.data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  const loadAnalytics = async () => {
    setAnalyticsLoading(true);
    try {
      const response = await api.logs.getAnalytics(analyticsHours);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setAnalyticsLoading(false);
    }
  };

  const startLogStream = () => {
    // Use the backend URL for WebSocket connection
    const backendHost = process.env.NEXT_PUBLIC_API_URL?.replace('http://', '').replace('https://', '') || 'localhost:8000';
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${backendHost}/api/v1/logs/stream`;
    const params = new URLSearchParams();

    if (streamFilters.categories.length > 0) {
      params.append('categories', streamFilters.categories.join(','));
    }
    if (streamFilters.levels.length > 0) {
      params.append('levels', streamFilters.levels.join(','));
    }

    const ws = new WebSocket(`${wsUrl}?${params}`);

    ws.onopen = () => {
      setIsStreaming(true);
      setStreamMessages([]);
    };

    ws.onmessage = (event) => {
      try {
        const message: LogStreamMessage = JSON.parse(event.data);
        setStreamMessages(prev => {
          const updated = [message, ...prev];
          return updated.slice(0, 1000); // Keep only latest 1000 messages
        });

        // Auto-scroll to bottom
        if (streamContainerRef.current) {
          streamContainerRef.current.scrollTop = 0;
        }
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      setIsStreaming(false);
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setIsStreaming(false);
    };

    wsRef.current = ws;
  };

  const stopLogStream = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsStreaming(false);
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString();
  };

  const getLevelColor = (level: string) => {
    switch (level.toUpperCase()) {
      case 'DEBUG': return 'text-muted-foreground';
      case 'INFO': return 'text-primary dark:text-blue-400';
      case 'WARNING': return 'text-yellow-600 dark:text-yellow-400 dark:text-yellow-400';
      case 'ERROR': return 'text-destructive dark:text-red-400';
      case 'CRITICAL': return 'text-red-800 dark:text-red-300 font-bold';
      default: return 'text-muted-foreground';
    }
  };

  const getLevelBg = (level: string) => {
    switch (level.toUpperCase()) {
      case 'DEBUG': return 'bg-muted/50';
      case 'INFO': return 'bg-blue-100 dark:bg-blue-900/20';
      case 'WARNING': return 'bg-yellow-100 dark:bg-yellow-900/20';
      case 'ERROR': return 'bg-red-100 dark:bg-red-900/20';
      case 'CRITICAL': return 'bg-red-200 dark:bg-red-900/30';
      default: return 'bg-muted/50';
    }
  };

  const renderTabContent = () => {
    switch (activeView) {
      case 'files':
        return renderFilesView();
      case 'search':
        return renderSearchView();
      case 'analytics':
        return renderAnalyticsView();
      case 'stream':
        return renderStreamView();
      default:
        return null;
    }
  };

  const renderFilesView = () => (
    <div className="space-y-6">
      {/* Files List */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-medium text-foreground">Log Files</h4>
          <button
            onClick={loadLogFiles}
            disabled={logFilesLoading}
            className="flex items-center px-3 py-1 text-sm font-medium text-foreground bg-muted hover:bg-muted/80 rounded-md transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`h-4 w-4 mr-1 ${logFilesLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>

        {logFiles && (
          <div className="grid gap-3">
            {Object.entries(logFiles.log_files).map(([filename, fileInfo]) => (
              <div key={filename} className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
                <div className="flex items-center justify-between">
                  <div>
                    <h5 className="text-sm font-medium text-foreground">{filename}</h5>
                    <div className="text-xs text-muted-foreground space-x-4">
                      <span>Size: {fileInfo.size_mb}MB</span>
                      {fileInfo.line_count && <span>Lines: {fileInfo.line_count.toLocaleString()}</span>}
                      <span>Category: {fileInfo.category}</span>
                      <span>Modified: {formatTimestamp(fileInfo.modified)}</span>
                    </div>
                  </div>
                  <button
                    onClick={() => handleFileSelect(filename)}
                    disabled={!fileInfo.can_search}
                    className="flex items-center px-3 py-1 text-sm font-medium text-primary hover:text-primary/80 transition-colors disabled:opacity-50"
                  >
                    <Eye className="h-4 w-4 mr-1" />
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* File Content Viewer */}
      {selectedFile && (
        <div className="border-t pt-6">
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium text-foreground">
              {selectedFile} Content
            </h4>
            <div className="flex items-center space-x-2">
              <select
                value={perPage}
                onChange={(e) => setPerPage(Number(e.target.value))}
                className="text-sm border border-input rounded px-2 py-1"
              >
                <option value={25}>25 lines</option>
                <option value={50}>50 lines</option>
                <option value={100}>100 lines</option>
                <option value={200}>200 lines</option>
              </select>
              <button
                onClick={() => setSelectedFile(null)}
                className="text-muted-foreground hover:text-muted-foreground transition-colors"
              >
                ✕
              </button>
            </div>
          </div>

          {logContentLoading ? (
            <div className="bg-muted/50 rounded-lg p-8 text-center">
              <div className="inline-flex items-center">
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Loading content...
              </div>
            </div>
          ) : logContent ? (
            <div className="space-y-4">
              {/* Pagination Controls */}
              {logContent.total_pages > 1 && (
                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    Page {logContent.current_page} of {logContent.total_pages}
                    ({logContent.total_lines.toLocaleString()} total lines)
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handlePageChange(logContent.current_page - 1)}
                      disabled={!logContent.has_prev}
                      className="flex items-center px-2 py-1 text-sm font-medium text-foreground bg-muted hover:bg-muted/80 rounded transition-colors disabled:opacity-50"
                    >
                      <ChevronLeft className="h-4 w-4" />
                      Previous
                    </button>
                    <span className="text-sm text-muted-foreground">
                      {logContent.current_page} / {logContent.total_pages}
                    </span>
                    <button
                      onClick={() => handlePageChange(logContent.current_page + 1)}
                      disabled={!logContent.has_next}
                      className="flex items-center px-2 py-1 text-sm font-medium text-foreground bg-muted hover:bg-muted/80 rounded transition-colors disabled:opacity-50"
                    >
                      Next
                      <ChevronRight className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              )}

              {/* Log Content */}
              <div className="bg-muted dark:bg-background text-foreground rounded-lg p-4 max-h-96 overflow-y-auto">
                <pre className="text-xs leading-relaxed whitespace-pre-wrap font-mono">
                  {logContent.content.join('\n')}
                </pre>
              </div>
            </div>
          ) : (
            <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4">
              <p className="text-sm text-destructive">Failed to load log file content.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const renderSearchView = () => (
    <div className="space-y-6">
      {/* Search Form */}
      <div className="bg-muted/50 rounded-lg p-4">
        <h4 className="text-lg font-medium text-foreground mb-4">Search Logs</h4>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Search Query
            </label>
            <input
              type="text"
              value={searchRequest.query}
              onChange={(e) => setSearchRequest(prev => ({ ...prev, query: e.target.value }))}
              placeholder="Enter search terms..."
              className="w-full px-3 py-2 border border-input rounded-md focus:ring-2 focus:ring-primary focus:border-transparent bg-background text-foreground"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Category
            </label>
            <select
              value={searchRequest.category || ''}
              onChange={(e) => setSearchRequest(prev => ({ ...prev, category: e.target.value || undefined }))}
              className="w-full px-3 py-2 border border-input rounded-md focus:ring-2 focus:ring-primary focus:border-transparent bg-background text-foreground"
            >
              <option value="">All categories</option>
              {categories?.categories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Log Level
            </label>
            <select
              value={searchRequest.level || ''}
              onChange={(e) => setSearchRequest(prev => ({ ...prev, level: e.target.value || undefined }))}
              className="w-full px-3 py-2 border border-input rounded-md focus:ring-2 focus:ring-primary focus:border-transparent bg-background text-foreground"
            >
              <option value="">All levels</option>
              <option value="DEBUG">DEBUG</option>
              <option value="INFO">INFO</option>
              <option value="WARNING">WARNING</option>
              <option value="ERROR">ERROR</option>
              <option value="CRITICAL">CRITICAL</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Limit Results
            </label>
            <select
              value={searchRequest.limit}
              onChange={(e) => setSearchRequest(prev => ({ ...prev, limit: Number(e.target.value) }))}
              className="w-full px-3 py-2 border border-input rounded-md focus:ring-2 focus:ring-primary focus:border-transparent bg-background text-foreground"
            >
              <option value={100}>100 results</option>
              <option value={500}>500 results</option>
              <option value={1000}>1000 results</option>
              <option value={5000}>5000 results</option>
            </select>
          </div>
        </div>
        <button
          onClick={handleSearch}
          disabled={searchLoading}
          className="flex items-center px-4 py-2 text-sm font-medium text-primary-foreground bg-primary hover:bg-primary/90 rounded-md transition-colors disabled:opacity-50"
        >
          <Search className={`h-4 w-4 mr-2 ${searchLoading ? 'animate-spin' : ''}`} />
          {searchLoading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {/* Search Results */}
      {searchResponse && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h4 className="text-lg font-medium text-foreground">
              Search Results ({searchResponse.total_found} found)
            </h4>
            {searchResponse.truncated && (
              <span className="text-sm text-yellow-600 dark:text-yellow-400">Results limited to {searchResponse.search_params.limit}</span>
            )}
          </div>

          <div className="space-y-2">
            {searchResponse.results.map((result, index) => (
              <div key={index} className="border border-border rounded-lg p-3 hover:bg-muted/50">
                <div className="flex items-start justify-between mb-2">
                  <div className="text-xs text-muted-foreground">
                    {result.file}:{result.line_number}
                    {result.parsed.timestamp && (
                      <span className="ml-2">{formatTimestamp(result.parsed.timestamp)}</span>
                    )}
                  </div>
                  {result.parsed.level && (
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getLevelBg(result.parsed.level)} ${getLevelColor(result.parsed.level)}`}>
                      {result.parsed.level}
                    </span>
                  )}
                </div>
                <pre className="text-sm text-foreground whitespace-pre-wrap font-mono">
                  {result.content}
                </pre>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderAnalyticsView = () => (
    <div className="space-y-6">
      {/* Analytics Controls */}
      <div className="bg-muted/50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-medium text-foreground">Log Analytics</h4>
          <div className="flex items-center space-x-2">
            <select
              value={analyticsHours}
              onChange={(e) => setAnalyticsHours(Number(e.target.value))}
              className="text-sm text-foreground border border-input rounded px-2 py-1 bg-background focus:ring-2 focus:ring-primary focus:border-transparent"
            >
              <option value={1}>Last 1 hour</option>
              <option value={6}>Last 6 hours</option>
              <option value={24}>Last 24 hours</option>
              <option value={72}>Last 3 days</option>
              <option value={168}>Last week</option>
            </select>
            <button
              onClick={loadAnalytics}
              disabled={analyticsLoading}
              className="flex items-center px-3 py-1 text-sm font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 rounded-md transition-colors disabled:opacity-50"
            >
              <BarChart3 className={`h-4 w-4 mr-1 ${analyticsLoading ? 'animate-spin' : ''}`} />
              {analyticsLoading ? 'Loading...' : 'Generate'}
            </button>
          </div>
        </div>
      </div>

      {/* Analytics Display */}
      {analytics && (
        <div className="grid grid-cols-2 gap-6">
          {/* By Level */}
          <div className="bg-background border border-border rounded-lg p-4">
            <h5 className="text-md font-medium text-foreground mb-3">By Log Level</h5>
            <div className="space-y-2">
              {Object.entries(analytics.by_level).map(([level, count]) => (
                <div key={level} className="flex items-center justify-between">
                  <span className={`text-sm font-medium ${getLevelColor(level)}`}>{level}</span>
                  <span className="text-sm text-muted-foreground">{count.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>

          {/* By Category */}
          <div className="bg-background border border-border rounded-lg p-4">
            <h5 className="text-md font-medium text-foreground mb-3">By Category</h5>
            <div className="space-y-2">
              {Object.entries(analytics.by_category).map(([category, count]) => (
                <div key={category} className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">{category}</span>
                  <span className="text-sm text-muted-foreground">{count.toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Error Patterns */}
          {analytics.error_patterns.length > 0 && (
            <div className="col-span-2 bg-background border border-border rounded-lg p-4">
              <h5 className="text-md font-medium text-foreground mb-3">Recent Error Patterns</h5>
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {analytics.error_patterns.map((error, index) => (
                  <div key={index} className="flex items-start space-x-2 p-2 bg-destructive/10 rounded">
                    <AlertTriangle className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="text-xs text-muted-foreground mb-1">
                        {error.category} • {error.level}
                        {error.timestamp && <span className="ml-2">{formatTimestamp(error.timestamp)}</span>}
                      </div>
                      <p className="text-sm text-foreground truncate">{error.message}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Summary */}
          <div className="col-span-2 bg-primary/10 border border-primary/20 rounded-lg p-4">
            <h5 className="text-md font-medium text-foreground mb-2">Summary</h5>
            <div className="grid grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-foreground">{analytics.total_entries.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">Total Entries</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">{analyticsHours}h</div>
                <div className="text-sm text-muted-foreground">Time Range</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">{Object.keys(analytics.by_category).length}</div>
                <div className="text-sm text-muted-foreground">Categories</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-destructive">{analytics.error_patterns.length}</div>
                <div className="text-sm text-destructive">Error Patterns</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderStreamView = () => (
    <div className="space-y-6">
      {/* Stream Controls */}
      <div className="bg-muted/50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-medium text-foreground">Real-time Log Stream</h4>
          <div className="flex items-center space-x-2">
            {!isStreaming ? (
              <button
                onClick={startLogStream}
                className="flex items-center px-3 py-1 text-sm font-medium text-white bg-green-600 hover:bg-green-700 dark:bg-green-500 dark:hover:bg-green-600 rounded-md transition-colors"
              >
                <Play className="h-4 w-4 mr-1" />
                Start
              </button>
            ) : (
              <button
                onClick={stopLogStream}
                className="flex items-center px-3 py-1 text-sm font-medium text-white bg-destructive hover:bg-destructive/90 rounded-md transition-colors"
              >
                <Pause className="h-4 w-4 mr-1" />
                Stop
              </button>
            )}
            <button
              onClick={() => setStreamMessages([])}
              className="flex items-center px-3 py-1 text-sm font-medium text-foreground bg-muted hover:bg-muted/80 rounded-md transition-colors"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Clear
            </button>
          </div>
        </div>

        {/* Stream Filters */}
        <div className="grid grid-cols-2 gap-4 mt-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Categories Filter
            </label>
            <div className="flex flex-wrap gap-2">
              {(() => {
                console.log('Rendering categories state:', categories);
                return null;
              })()}
              {!categories ? (
                <div className="text-sm text-muted-foreground">Loading categories...</div>
              ) : categories.categories?.length === 0 ? (
                <div className="text-sm text-muted-foreground">No categories available</div>
              ) : (
                categories.categories.map(cat => (
                  <label key={cat} className="flex items-center">
                    <input
                      type="checkbox"
                      checked={streamFilters.categories.includes(cat)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setStreamFilters(prev => ({
                            ...prev,
                            categories: [...prev.categories, cat]
                          }));
                        } else {
                          setStreamFilters(prev => ({
                            ...prev,
                            categories: prev.categories.filter(c => c !== cat)
                          }));
                        }
                      }}
                      className="h-3 w-3 text-primary focus:ring-primary border-input rounded mr-1"
                    />
                    <span className="text-sm text-foreground">{cat}</span>
                  </label>
                ))
              )}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-foreground mb-1">
              Levels Filter
            </label>
            <div className="flex flex-wrap gap-2">
              {['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'].map(level => (
                <label key={level} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={streamFilters.levels.includes(level)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setStreamFilters(prev => ({
                          ...prev,
                          levels: [...prev.levels, level]
                        }));
                      } else {
                        setStreamFilters(prev => ({
                          ...prev,
                          levels: prev.levels.filter(l => l !== level)
                        }));
                      }
                    }}
                    className="h-3 w-3 text-primary focus:ring-primary border-input rounded mr-1"
                  />
                  <span className={`text-sm ${getLevelColor(level)}`}>{level}</span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Stream Messages */}
      <div
        ref={streamContainerRef}
        className="bg-muted dark:bg-background text-foreground rounded-lg p-4 h-96 overflow-y-auto"
      >
        {isStreaming && (
          <div className="flex items-center mb-4 text-green-400 dark:text-green-300">
            <Activity className="h-4 w-4 mr-2 animate-pulse" />
            Live streaming... ({streamMessages.length} messages)
          </div>
        )}

        {streamMessages.length === 0 ? (
          <div className="text-center text-muted-foreground mt-8">
            {isStreaming ? 'Waiting for log messages...' : 'Start streaming to see real-time logs'}
          </div>
        ) : (
          <div className="space-y-1">
            {streamMessages.map((message, index) => (
              <div key={index} className="flex items-start space-x-2 text-xs font-mono">
                <span className="text-muted-foreground shrink-0">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
                <span className={`shrink-0 ${getLevelColor(message.parsed.level)}`}>
                  {message.parsed.level?.padEnd(8) || 'INFO'.padEnd(8)}
                </span>
                <span className="text-muted-foreground shrink-0">
                  {message.category}
                </span>
                <span className="text-foreground break-all">
                  {message.parsed.message || message.content}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="bg-primary/10 border border-primary/20 rounded-md p-4">
          <p className="text-sm text-primary dark:text-primary">
            <strong>Note:</strong> To configure logging settings (log level, retention, categories), visit the{' '}
            <a href="/system" className="text-primary hover:text-primary/80 underline">
              System Settings
            </a>{' '}
            page and go to the Logging tab.
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {/* View Tabs */}
        <div className="mb-6">
          <nav className="flex space-x-8" aria-label="Log Management">
            {[
              { id: 'files', label: 'Files', icon: <FileText className="h-4 w-4" /> },
              { id: 'search', label: 'Search', icon: <Search className="h-4 w-4" /> },
              { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="h-4 w-4" /> },
              { id: 'stream', label: 'Live Stream', icon: <Activity className="h-4 w-4" /> }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveView(tab.id as LogViewType)}
                className={`
                  flex items-center py-2 px-1 border-b-2 font-medium text-sm transition-colors
                  ${activeView === tab.id
                    ? 'border-primary text-primary'
                    : 'border-transparent text-muted-foreground hover:text-foreground hover:border-border'
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
        <div className="min-h-[500px]">
          {renderTabContent()}
        </div>
      </div>
    </div>
  );
}