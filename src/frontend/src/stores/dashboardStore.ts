import { create } from 'zustand';

interface Event {
  timestamp: string;
  event_id: string;
  event_data: {
    event_name: string;
    station_id?: string;
    customer_id?: string;
    product_sku?: string;
    [key: string]: any;
  };
}

interface DashboardStats {
  total_events: number;
  event_counts: Record<string, number>;
  station_activity: Record<string, number>;
  active_stations: number;
}

interface DashboardState {
  events: Event[];
  stats: DashboardStats;
  addEvent: (event: Event) => void;
  updateStats: (stats: DashboardStats) => void;
  clearEvents: () => void;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  events: [],
  stats: {
    total_events: 0,
    event_counts: {},
    station_activity: {},
    active_stations: 0,
  },
  
  addEvent: (event: Event) => {
    set((state) => ({
      events: [event, ...state.events.slice(0, 99)] // Keep last 100 events
    }));
  },
  
  updateStats: (stats: DashboardStats) => {
    set({ stats });
  },
  
  clearEvents: () => {
    set({ events: [] });
  },
}));