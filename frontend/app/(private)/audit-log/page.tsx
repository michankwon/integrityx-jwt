'use client';

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Multiselect, MultiselectBadges, MultiselectOption } from '@/components/ui/multiselect';
import { DateRangePicker } from '@/components/ui/date-range-picker';
import { FilterCardSkeleton, EventCardSkeleton, StatsCardSkeleton } from '@/components/ui/card-skeleton';
import { NoResultsEmptyState } from '@/components/ui/empty-state';
import { Loader2, Search, Filter, Hash, Clock, AlertCircle, RotateCcw, X } from 'lucide-react';
import { DateRange } from 'react-day-picker';
import toast from 'react-hot-toast';

interface Event {
  id: string;
  artifact_id: string;
  event_type: string;
  created_by: string;
  created_at: string;
  payload_json?: string;
  walacor_tx_id?: string;
  artifact_etid?: number;
}

interface EventsResponse {
  events: Event[];
  total: number;
  page: number;
  limit: number;
  has_next: boolean;
  has_prev: boolean;
}

interface ApiResponse<T = any> {
  ok: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
}

const EVENT_TYPE_COLORS = {
  'uploaded': 'bg-blue-100 text-blue-800',
  'verified': 'bg-green-100 text-green-800',
  'sealed': 'bg-purple-100 text-purple-800',
  'verification_failed': 'bg-red-100 text-red-800',
  'tamper_detected': 'bg-red-100 text-red-800',
  'proof_retrieved': 'bg-yellow-100 text-yellow-800',
  'error': 'bg-red-100 text-red-800',
  'failed': 'bg-red-100 text-red-800'
};

const STATUS_MAPPING = {
  'ok': ['verified', 'sealed', 'uploaded', 'proof_retrieved'],
  'tamper': ['verification_failed', 'tamper_detected'],
  'error': ['error', 'failed']
};

// Event type options for multiselect
const EVENT_TYPE_OPTIONS: MultiselectOption[] = [
  { value: 'uploaded', label: 'Uploaded' },
  { value: 'verified', label: 'Verified' },
  { value: 'sealed', label: 'Sealed' },
  { value: 'verification_failed', label: 'Verification Failed' },
  { value: 'tamper_detected', label: 'Tamper Detected' },
  { value: 'proof_retrieved', label: 'Proof Retrieved' },
  { value: 'error', label: 'Error' },
  { value: 'failed', label: 'Failed' }
];

// ETID options for select
const ETID_OPTIONS = [
  { value: '', label: 'All ETIDs' },
  { value: '100001', label: '100001 (Loan Packets)' },
  { value: '100002', label: '100002 (JSON Documents)' },
  { value: '100003', label: '100003 (Appraisals)' },
  { value: '100004', label: '100004 (Credit Reports)' }
];

interface FilterState {
  etid: string;
  eventTypes: string[];
  dateRange: DateRange | undefined;
  result: string;
  searchTerm: string;
}

export default function AuditLogPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  
  // Enhanced filters with URL sync
  const [filters, setFilters] = useState<FilterState>({
    etid: '',
    eventTypes: [],
    dateRange: undefined,
    result: '',
    searchTerm: ''
  });
  
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadingRef = useRef<HTMLDivElement | null>(null);

  // URL synchronization
  const updateURL = useCallback((newFilters: FilterState) => {
    const params = new URLSearchParams();
    
    if (newFilters.etid) params.set('etid', newFilters.etid);
    if (newFilters.eventTypes.length > 0) params.set('eventTypes', newFilters.eventTypes.join(','));
    if (newFilters.dateRange?.from) params.set('startDate', newFilters.dateRange.from.toISOString());
    if (newFilters.dateRange?.to) params.set('endDate', newFilters.dateRange.to.toISOString());
    if (newFilters.result) params.set('result', newFilters.result);
    if (newFilters.searchTerm) params.set('search', newFilters.searchTerm);
    
    const newURL = params.toString() ? `?${params.toString()}` : '';
    router.replace(`/audit-log${newURL}`, { scroll: false });
  }, [router]);

  // Initialize filters from URL
  useEffect(() => {
    const etid = searchParams.get('etid') || '';
    const eventTypes = searchParams.get('eventTypes')?.split(',').filter(Boolean) || [];
    const startDate = searchParams.get('startDate');
    const endDate = searchParams.get('endDate');
    const result = searchParams.get('result') || '';
    const searchTerm = searchParams.get('search') || '';
    
    let dateRange: DateRange | undefined = undefined;
    if (startDate && endDate) {
      dateRange = {
        from: new Date(startDate),
        to: new Date(endDate)
      };
    } else if (startDate) {
      dateRange = {
        from: new Date(startDate),
        to: undefined
      };
    }
    
    const urlFilters: FilterState = {
      etid,
      eventTypes,
      dateRange,
      result,
      searchTerm
    };
    
    setFilters(urlFilters);
  }, [searchParams]);

  const fetchEvents = useCallback(async (page: number = 1, reset: boolean = false) => {
    if (loading) return;
    
    setLoading(true);
    if (page === 1 && reset) {
      setInitialLoading(true);
    }
    
    try {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20'
      });
      
      if (filters.etid) params.append('etid', filters.etid);
      if (filters.eventTypes.length > 0) params.append('eventTypes', filters.eventTypes.join(','));
      if (filters.dateRange?.from) params.append('startDate', filters.dateRange.from.toISOString());
      if (filters.dateRange?.to) params.append('endDate', filters.dateRange.to.toISOString());
      if (filters.result) params.append('status', filters.result);
      if (filters.searchTerm) params.append('search', filters.searchTerm);
      
      const response = await fetch(`/api/events?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch events');
      }
      
      const apiResponse: ApiResponse<EventsResponse> = await response.json();
      
      if (!apiResponse.ok || !apiResponse.data) {
        throw new Error(apiResponse.error?.message || 'Failed to fetch events');
      }
      
      const data = apiResponse.data;
      
      if (reset) {
        setEvents(data.events);
      } else {
        setEvents(prev => [...prev, ...data.events]);
      }
      
      setTotal(data.total);
      setHasMore(data.has_next);
      setCurrentPage(page);
      
    } catch (error) {
      console.error('Error fetching events:', error);
      toast.error('Failed to load events');
    } finally {
      setLoading(false);
      setInitialLoading(false);
    }
  }, [filters, loading]);

  const loadMore = useCallback(() => {
    if (hasMore && !loading) {
      fetchEvents(currentPage + 1, false);
    }
  }, [hasMore, loading, currentPage, fetchEvents]);

  // Filter update handlers
  const updateFilter = useCallback((key: keyof FilterState, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    updateURL(newFilters);
  }, [filters, updateURL]);

  const handleSearch = useCallback(() => {
    setEvents([]);
    setCurrentPage(1);
    setHasMore(true);
    fetchEvents(1, true);
  }, [fetchEvents]);

  const handleReset = useCallback(() => {
    const resetFilters: FilterState = {
      etid: '',
      eventTypes: [],
      dateRange: undefined,
      result: '',
      searchTerm: ''
    };
    
    setFilters(resetFilters);
    updateURL(resetFilters);
    setEvents([]);
    setCurrentPage(1);
    setHasMore(true);
    fetchEvents(1, true);
  }, [updateURL, fetchEvents]);

  // Check if any filters are active
  const hasActiveFilters = useMemo(() => {
    return !!(
      filters.etid ||
      filters.eventTypes.length > 0 ||
      filters.dateRange?.from ||
      filters.result ||
      filters.searchTerm
    );
  }, [filters]);

  // Intersection Observer for infinite scroll
  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (loadingRef.current) {
      observerRef.current.observe(loadingRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [loadMore, hasMore, loading]);

  // Initial load and filter changes
  useEffect(() => {
    fetchEvents(1, true);
  }, [fetchEvents]);

  const getEventTypeColor = (eventType: string) => {
    return EVENT_TYPE_COLORS[eventType as keyof typeof EVENT_TYPE_COLORS] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const parsePayload = (payloadJson?: string) => {
    if (!payloadJson) return null;
    try {
      return JSON.parse(payloadJson);
    } catch {
      return null;
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Audit Log</h1>
        <p className="text-muted-foreground">
          Monitor all system events and document activities with real-time updates.
        </p>
      </div>

      {/* Enhanced Filters */}
      {initialLoading ? (
        <FilterCardSkeleton className="mb-6" />
      ) : (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Filter className="h-5 w-5" />
                Filters
                {hasActiveFilters && (
                  <Badge variant="secondary" className="ml-2">
                    Active
                  </Badge>
                )}
              </div>
              {hasActiveFilters && (
                <Button variant="ghost" size="sm" onClick={handleReset}>
                  <X className="h-4 w-4 mr-1" />
                  Clear All
                </Button>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-4">
            {/* ETID Select */}
            <div className="space-y-2">
              <Label htmlFor="etid">Entity Type ID</Label>
              <Select value={filters.etid} onValueChange={(value) => updateFilter('etid', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select ETID" />
                </SelectTrigger>
                <SelectContent>
                  {ETID_OPTIONS.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            {/* Event Types Multiselect */}
            <div className="space-y-2">
              <Label>Event Types</Label>
              <Multiselect
                options={EVENT_TYPE_OPTIONS}
                value={filters.eventTypes}
                onChange={(value) => updateFilter('eventTypes', value)}
                placeholder="Select event types..."
                maxDisplay={2}
              />
            </div>
            
            {/* Date Range Picker */}
            <div className="space-y-2">
              <Label>Date Range</Label>
              <DateRangePicker
                value={filters.dateRange}
                onChange={(range) => updateFilter('dateRange', range)}
                placeholder="Pick date range"
              />
            </div>
            
            {/* Result Select */}
            <div className="space-y-2">
              <Label htmlFor="result">Result</Label>
              <Select value={filters.result} onValueChange={(value) => updateFilter('result', value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select result" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">All Results</SelectItem>
                  <SelectItem value="ok">OK</SelectItem>
                  <SelectItem value="tamper">Tamper</SelectItem>
                  <SelectItem value="error">Error</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            {/* Search Term */}
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <Input
                id="search"
                value={filters.searchTerm}
                onChange={(e) => updateFilter('searchTerm', e.target.value)}
                placeholder="Search events..."
              />
            </div>
          </div>
          
          {/* Active Filter Badges */}
          {hasActiveFilters && (
            <div className="mb-4 p-3 bg-muted/50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-sm font-medium">Active Filters:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {filters.etid && (
                  <Badge variant="secondary">
                    ETID: {ETID_OPTIONS.find(opt => opt.value === filters.etid)?.label || filters.etid}
                    <button
                      onClick={() => updateFilter('etid', '')}
                      className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {filters.eventTypes.length > 0 && (
                  <MultiselectBadges
                    options={EVENT_TYPE_OPTIONS}
                    value={filters.eventTypes}
                    onRemove={(value) => updateFilter('eventTypes', filters.eventTypes.filter(t => t !== value))}
                    maxDisplay={3}
                  />
                )}
                {filters.dateRange?.from && (
                  <Badge variant="secondary">
                    Date: {filters.dateRange.from.toLocaleDateString()}
                    {filters.dateRange.to && ` - ${filters.dateRange.to.toLocaleDateString()}`}
                    <button
                      onClick={() => updateFilter('dateRange', undefined)}
                      className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {filters.result && (
                  <Badge variant="secondary">
                    Result: {filters.result}
                    <button
                      onClick={() => updateFilter('result', '')}
                      className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
                {filters.searchTerm && (
                  <Badge variant="secondary">
                    Search: {filters.searchTerm}
                    <button
                      onClick={() => updateFilter('searchTerm', '')}
                      className="ml-1 hover:bg-muted-foreground/20 rounded-full p-0.5"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </Badge>
                )}
              </div>
            </div>
          )}
          
          <div className="flex gap-2">
            <Button onClick={handleSearch} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Searching...
                </>
              ) : (
                <>
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </>
              )}
            </Button>
            <Button variant="outline" onClick={handleReset} disabled={loading}>
              <RotateCcw className="h-4 w-4 mr-2" />
              Reset
            </Button>
          </div>
        </CardContent>
        </Card>
      )}

      {/* Stats */}
      {initialLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <StatsCardSkeleton />
          <StatsCardSkeleton />
          <StatsCardSkeleton />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Hash className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Total Events</span>
              </div>
              <p className="text-2xl font-bold">{total.toLocaleString()}</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Current Page</span>
              </div>
              <p className="text-2xl font-bold">{currentPage}</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm font-medium">Loaded Events</span>
              </div>
              <p className="text-2xl font-bold">{events.length.toLocaleString()}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Events Table */}
      <Card>
        <CardHeader>
          <CardTitle>Events</CardTitle>
          <CardDescription>
            Real-time audit trail of all system activities
          </CardDescription>
        </CardHeader>
        <CardContent>
          {initialLoading ? (
            <div className="space-y-4">
              {Array.from({ length: 3 }).map((_, index) => (
                <EventCardSkeleton key={index} />
              ))}
            </div>
          ) : events.length === 0 && !loading ? (
            <NoResultsEmptyState
              action={hasActiveFilters ? {
                label: "Clear Filters",
                onClick: handleReset,
                variant: "outline"
              } : undefined}
            />
          ) : (
            <div className="space-y-4">
              {events.map((event) => {
                const payload = parsePayload(event.payload_json);
                
                return (
                  <div
                    key={event.id}
                    className="border rounded-lg p-4 hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <Badge className={getEventTypeColor(event.event_type)}>
                          {event.event_type}
                        </Badge>
                        {event.artifact_etid && (
                          <Badge variant="outline">
                            ETID: {event.artifact_etid}
                          </Badge>
                        )}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {formatDate(event.created_at)}
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Event ID:</span>
                        <p className="font-mono text-xs break-all">{event.id}</p>
                      </div>
                      
                      <div>
                        <span className="font-medium">Artifact ID:</span>
                        <p className="font-mono text-xs break-all">{event.artifact_id}</p>
                      </div>
                      
                      <div>
                        <span className="font-medium">Created By:</span>
                        <p className="text-xs">{event.created_by}</p>
                      </div>
                      
                      {event.walacor_tx_id && (
                        <div>
                          <span className="font-medium">Walacor TX:</span>
                          <p className="font-mono text-xs break-all">{event.walacor_tx_id}</p>
                        </div>
                      )}
                    </div>
                    
                    {payload && (
                      <div className="mt-3">
                        <span className="font-medium text-sm">Payload:</span>
                        <pre className="text-xs bg-muted p-2 rounded mt-1 overflow-auto max-h-32">
                          {JSON.stringify(payload, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                );
              })}
              
              {/* Loading indicator */}
              <div ref={loadingRef} className="text-center py-4">
                {loading && (
                  <div className="flex items-center justify-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Loading more events...</span>
                  </div>
                )}
                {!hasMore && events.length > 0 && (
                  <p className="text-muted-foreground">No more events to load</p>
                )}
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

