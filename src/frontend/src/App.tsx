import React from 'react'
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Chip
} from '@mui/material'
import { useSocket } from './hooks/useSocket'
import Dashboard from './components/Dashboard'
import AlertsPanel from './components/AlertsPanel'
import EventsPanel from './components/EventsPanel'
import StationOverview from './components/StationOverview'
import RealTimeCharts from './components/RealTimeCharts'

const App: React.FC = () => {
  const { isConnected, metrics, events, connectionError, reconnect } = useSocket()

  return (
    <Container maxWidth="xl" className="dashboard-container">
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Project Sentinel - Store Monitor Dashboard
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Chip
            label={isConnected ? 'Connected' : 'Disconnected'}
            color={isConnected ? 'success' : 'error'}
            variant="filled"
          />
          
          {isConnected && (
            <Chip
              label="🔴 LIVE"
              color="error"
              size="small"
              sx={{ 
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': { opacity: 1 },
                  '50%': { opacity: 0.7 },
                  '100%': { opacity: 1 }
                }
              }}
            />
          )}
        </Box>
      </Box>

      {connectionError && (
        <Paper sx={{ p: 2, mb: 3, backgroundColor: '#ffebee' }}>
          <Typography color="error">
            Connection Error: {connectionError}
          </Typography>
          <Typography 
            component="span" 
            sx={{ cursor: 'pointer', textDecoration: 'underline', color: 'primary.main' }}
            onClick={reconnect}
          >
            Click to reconnect
          </Typography>
        </Paper>
      )}

      <Grid container spacing={3}>
        {/* Main Dashboard Metrics */}
        <Grid item xs={12}>
          <Dashboard metrics={metrics} isConnected={isConnected} />
        </Grid>

        {/* Station Overview */}
        <Grid item xs={12} lg={8}>
          <StationOverview 
            stations={metrics.active_stations} 
            queueStats={metrics.queue_stats}
          />
        </Grid>

        {/* Alerts Panel */}
        <Grid item xs={12} lg={4}>
          <AlertsPanel alerts={metrics.alerts} />
        </Grid>

        {/* Real-time Charts */}
        <Grid item xs={12} lg={8}>
          <RealTimeCharts 
            queueStats={metrics.queue_stats}
            events={events}
          />
        </Grid>

        {/* Recent Events */}
        <Grid item xs={12} lg={4}>
          <EventsPanel events={events} />
        </Grid>
      </Grid>

      {/* Footer */}
      <Box sx={{ mt: 4, py: 2, textAlign: 'center', borderTop: '1px solid #e0e0e0' }}>
        <Typography variant="body2" color="text.secondary">
          Project Sentinel Dashboard - Real-time Store Monitoring System
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Total Events: {metrics.total_events} | Active Stations: {metrics.active_stations.length}
        </Typography>
      </Box>
    </Container>
  )
}

export default App