import React from 'react'
import {
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  LinearProgress,
  Chip
} from '@mui/material'
import {
  Store,
  People,
  Timer,
  Warning
} from '@mui/icons-material'

interface QueueStats {
  customer_count: number
  average_dwell_time: number
}

interface StationOverviewProps {
  stations: string[]
  queueStats: Record<string, QueueStats>
}

const StationOverview: React.FC<StationOverviewProps> = ({ stations, queueStats }) => {
  const getStationStatus = (stationId: string) => {
    const stats = queueStats[stationId]
    if (!stats) return 'inactive'
    
    if (stats.customer_count >= 6 || stats.average_dwell_time >= 300) {
      return 'critical'
    }
    if (stats.customer_count >= 4 || stats.average_dwell_time >= 240) {
      return 'warning'
    }
    return 'normal'
  }

  const getStatusColor = (status: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    switch (status) {
      case 'critical': return 'error'
      case 'warning': return 'warning'
      case 'normal': return 'success'
      default: return 'default'
    }
  }

  const getStatusText = (status: string) => {
    switch (status) {
      case 'critical': return 'Critical'
      case 'warning': return 'Warning'
      case 'normal': return 'Normal'
      default: return 'Inactive'
    }
  }

  const getQueueProgress = (count: number) => {
    return Math.min((count / 10) * 100, 100) // Max 10 customers for 100%
  }

  const getDwellProgress = (dwell: number) => {
    return Math.min((dwell / 600) * 100, 100) // Max 10 minutes for 100%
  }

  // Ensure we have some stations to display, even if empty
  const allStations = stations.length > 0 ? stations : ['SCC1', 'SCC2', 'SCC3']

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" component="h3" gutterBottom>
        Station Overview
      </Typography>

      <Grid container spacing={2}>
        {allStations.map((stationId) => {
          const stats = queueStats[stationId] || { customer_count: 0, average_dwell_time: 0 }
          const status = getStationStatus(stationId)
          
          return (
            <Grid item xs={12} sm={6} md={4} key={stationId}>
              <Card 
                sx={{ 
                  height: '100%',
                  border: 2,
                  borderColor: status === 'critical' ? 'error.main' : 
                               status === 'warning' ? 'warning.main' : 
                               status === 'normal' ? 'success.main' : 'grey.300'
                }}
              >
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Store sx={{ mr: 1 }} />
                      <Typography variant="h6" component="h4">
                        {stationId}
                      </Typography>
                    </Box>
                    <Chip
                      label={getStatusText(status)}
                      color={getStatusColor(status)}
                      size="small"
                    />
                  </Box>

                  {/* Customer Count */}
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <People sx={{ mr: 1, fontSize: 20 }} />
                      <Typography variant="body2">
                        Queue Length: {stats.customer_count}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={getQueueProgress(stats.customer_count)}
                      color={stats.customer_count >= 6 ? 'error' : stats.customer_count >= 4 ? 'warning' : 'success'}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  {/* Wait Time */}
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      <Timer sx={{ mr: 1, fontSize: 20 }} />
                      <Typography variant="body2">
                        Wait Time: {Math.round(stats.average_dwell_time)}s
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={getDwellProgress(stats.average_dwell_time)}
                      color={stats.average_dwell_time >= 300 ? 'error' : stats.average_dwell_time >= 240 ? 'warning' : 'success'}
                      sx={{ height: 8, borderRadius: 4 }}
                    />
                  </Box>

                  {/* Status Indicators */}
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
                    {stats.customer_count >= 6 && (
                      <Chip
                        icon={<Warning />}
                        label="Long Queue"
                        color="error"
                        size="small"
                      />
                    )}
                    {stats.average_dwell_time >= 300 && (
                      <Chip
                        icon={<Timer />}
                        label="High Wait Time"
                        color="error"
                        size="small"
                      />
                    )}
                    {status === 'normal' && (
                      <Chip
                        label="Operating Normally"
                        color="success"
                        size="small"
                      />
                    )}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          )
        })}
      </Grid>

      <Box sx={{ mt: 3, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary">
          <strong>Status Legend:</strong> Normal (0-3 customers, &lt;4min wait) | 
          Warning (4-5 customers, 4-5min wait) | 
          Critical (6+ customers, 5+ min wait)
        </Typography>
      </Box>
    </Paper>
  )
}

export default StationOverview