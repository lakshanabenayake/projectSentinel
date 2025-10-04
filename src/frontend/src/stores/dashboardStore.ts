import { create } from 'zustand'

interface DashboardMetrics {
  total_events: number
  active_stations: string[]
  active_customers: string[]
  alerts: Array<{
    id: string
    message: string
    priority: string
    timestamp: string
    data: any
  }>
  queue_stats: Record<string, {
    customer_count: number
    average_dwell_time: number
  }>
  inventory_alerts: number
}

interface Event {
  timestamp: string
  event_id: string
  event_data: {
    event_name: string
    [key: string]: any
  }
  priority?: string
}

interface DashboardStore {
  // State
  isConnected: boolean
  metrics: DashboardMetrics
  events: Event[]
  connectionError: string | null
  
  // Actions
  setConnected: (connected: boolean) => void
  updateMetrics: (metrics: DashboardMetrics) => void
  addEvent: (event: Event) => void
  setConnectionError: (error: string | null) => void
  clearEvents: () => void
}

export const useDashboardStore = create<DashboardStore>((set, get) => ({
  // Initial state
  isConnected: false,
  metrics: {
    total_events: 0,
    active_stations: [],
    active_customers: [],
    alerts: [],
    queue_stats: {},
    inventory_alerts: 0
  },
  events: [],
  connectionError: null,
  
  // Actions
  setConnected: (connected: boolean) => 
    set({ isConnected: connected }),
    
  updateMetrics: (metrics: DashboardMetrics) => 
    set({ metrics }),
    
  addEvent: (event: Event) => 
    set((state) => ({
      events: [event, ...state.events].slice(0, 100) // Keep last 100 events
    })),
    
  setConnectionError: (error: string | null) => 
    set({ connectionError: error }),
    
  clearEvents: () => 
    set({ events: [] })
}))