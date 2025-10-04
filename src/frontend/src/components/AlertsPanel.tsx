import React from 'react'
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Chip,
  Box,
  Badge
} from '@mui/material'
import {
  Warning,
  Error,
  Info,
  CheckCircle
} from '@mui/icons-material'
import { formatDistanceToNow } from 'date-fns'

interface Alert {
  id: string
  message: string
  priority: string
  timestamp: string
  data: any
}

interface AlertsPanelProps {
  alerts: Alert[]
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ alerts }) => {
  const getAlertIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return <Error color="error" />
      case 'warning':
        return <Warning color="warning" />
      case 'info':
        return <CheckCircle color="success" />
      default:
        return <Info color="info" />
    }
  }

  const getAlertColor = (priority: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    switch (priority) {
      case 'critical':
        return 'error'
      case 'warning':
        return 'warning'
      case 'info':
        return 'success'
      default:
        return 'info'
    }
  }

  const getPriorityCount = (priority: string) => {
    return alerts.filter(alert => alert.priority === priority).length
  }

  return (
    <Paper sx={{ p: 3, height: '600px', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" component="h3">
          Live Alerts
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Badge badgeContent={getPriorityCount('critical')} color="error">
            <Chip size="small" label="Critical" color="error" variant="outlined" />
          </Badge>
          <Badge badgeContent={getPriorityCount('warning')} color="warning">
            <Chip size="small" label="Warning" color="warning" variant="outlined" />
          </Badge>
        </Box>
      </Box>

      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
        {alerts.length === 0 ? (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <CheckCircle sx={{ fontSize: 48, color: 'success.main', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              All systems operating normally
            </Typography>
          </Box>
        ) : (
          <List sx={{ py: 0 }}>
            {alerts.slice(0, 20).map((alert) => (
              <ListItem
                key={alert.id}
                sx={{
                  mb: 1,
                  border: '1px solid',
                  borderColor: `${getAlertColor(alert.priority)}.main`,
                  borderRadius: 1,
                  backgroundColor: alert.priority === 'critical' ? 'error.light' : 
                                  alert.priority === 'warning' ? 'warning.light' : 
                                  'background.paper',
                  '&:hover': {
                    backgroundColor: alert.priority === 'critical' ? 'error.light' : 
                                    alert.priority === 'warning' ? 'warning.light' : 
                                    'grey.50'
                  }
                }}
              >
                <Box sx={{ mr: 2 }}>
                  {getAlertIcon(alert.priority)}
                </Box>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Typography variant="body2" fontWeight="medium">
                        {alert.message}
                      </Typography>
                      <Chip
                        size="small"
                        label={alert.priority}
                        color={getAlertColor(alert.priority)}
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        {formatDistanceToNow(new Date(alert.timestamp), { addSuffix: true })}
                      </Typography>
                      {alert.data.station_id && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          Station: {alert.data.station_id}
                        </Typography>
                      )}
                      {alert.data.customer_id && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          Customer: {alert.data.customer_id}
                        </Typography>
                      )}
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        )}
      </Box>

      <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          Showing {Math.min(alerts.length, 20)} of {alerts.length} total alerts
        </Typography>
      </Box>
    </Paper>
  )
}

export default AlertsPanel