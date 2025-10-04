import { useEffect, useState, useCallback } from 'react'
import { io, Socket } from 'socket.io-client'

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

export const useSocket = () => {
  const [socket, setSocket] = useState<Socket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    total_events: 0,
    active_stations: [],
    active_customers: [],
    alerts: [],
    queue_stats: {},
    inventory_alerts: 0
  })
  const [events, setEvents] = useState<Event[]>([])
  const [connectionError, setConnectionError] = useState<string | null>(null)

  const connectSocket = useCallback(() => {
    // Try to determine the backend URL dynamically
    const backendUrl = window.location.hostname === '127.0.0.1' 
      ? 'http://127.0.0.1:5000' 
      : 'http://localhost:5000'
    
    console.log(`Connecting to backend at: ${backendUrl}`)
    
    const newSocket = io(backendUrl, {
      transports: ['websocket', 'polling'], // Include polling as fallback
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 5,
      timeout: 20000,
      withCredentials: true, // Include credentials for CORS
      forceNew: true
    })

    newSocket.on('connect', () => {
      console.log('Connected to server')
      setIsConnected(true)
      setConnectionError(null)
      newSocket.emit('request_metrics')
    })

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server')
      setIsConnected(false)
    })

    newSocket.on('connect_error', (error) => {
      console.error('Connection error:', error)
      setConnectionError(error.message)
      setIsConnected(false)
    })

    newSocket.on('new_event', (event: Event) => {
      console.log('New event received:', event)
      setEvents(prevEvents => {
        const newEvents = [event, ...prevEvents]
        // Keep only last 100 events
        return newEvents.slice(0, 100)
      })
    })

    newSocket.on('metrics_update', (newMetrics: DashboardMetrics) => {
      console.log('Metrics updated:', newMetrics)
      setMetrics(newMetrics)
    })

    setSocket(newSocket)

    return newSocket
  }, [])

  useEffect(() => {
    const socketInstance = connectSocket()

    return () => {
      if (socketInstance) {
        socketInstance.disconnect()
      }
    }
  }, [connectSocket])

  const requestMetrics = useCallback(() => {
    if (socket && isConnected) {
      socket.emit('request_metrics')
    }
  }, [socket, isConnected])

  const reconnect = useCallback(() => {
    if (socket) {
      socket.disconnect()
    }
    connectSocket()
  }, [socket, connectSocket])

  return {
    socket,
    isConnected,
    metrics,
    events,
    connectionError,
    requestMetrics,
    reconnect
  }
}