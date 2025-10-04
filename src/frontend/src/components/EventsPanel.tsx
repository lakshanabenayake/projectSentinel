import React from 'react'
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  Box,
  Chip
} from '@mui/material'
import { formatDistanceToNow } from 'date-fns'

interface Event {
  timestamp: string
  event_id: string
  event_data: {
    event_name: string
    [key: string]: any
  }
  priority?: string
}

interface EventsPanelProps {
  events: Event[]
}

const EventsPanel: React.FC<EventsPanelProps> = ({ events }) => {
  const getEventColor = (eventName: string): "default" | "primary" | "secondary" | "error" | "info" | "success" | "warning" => {
    if (eventName.includes('Scanner Avoidance') || eventName.includes('Barcode Switching')) {
      return 'error'
    }
    if (eventName.includes('Weight Discrepancies') || eventName.includes('Long Queue') || eventName.includes('Long Wait')) {
      return 'warning'
    }
    if (eventName.includes('Success Operation')) {
      return 'success'
    }
    return 'info'
  }

  const getEventIcon = (eventName: string) => {
    if (eventName.includes('Success')) return '✅'
    if (eventName.includes('Scanner Avoidance')) return '🚫'
    if (eventName.includes('Barcode Switching')) return '🔄'
    if (eventName.includes('Weight')) return '⚖️'
    if (eventName.includes('Queue')) return '👥'
    if (eventName.includes('Inventory')) return '📦'
    if (eventName.includes('Staffing')) return '👤'
    if (eventName.includes('Crash')) return '💥'
    return '📋'
  }

  return (
    <Paper sx={{ p: 3, height: '600px', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" component="h3" gutterBottom>
        Recent Events
      </Typography>

      <Box sx={{ flexGrow: 1, overflowY: 'auto' }}>
        {events.length === 0 ? (
          <Box sx={{ textAlign: 'center', mt: 4 }}>
            <Typography variant="body1" color="text.secondary">
              No events detected yet
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Events will appear here in real-time
            </Typography>
          </Box>
        ) : (
          <List sx={{ py: 0 }}>
            {events.slice(0, 50).map((event) => (
              <ListItem
                key={event.event_id}
                sx={{
                  mb: 1,
                  border: '1px solid',
                  borderColor: 'grey.300',
                  borderRadius: 1,
                  backgroundColor: 'background.paper',
                  '&:hover': {
                    backgroundColor: 'grey.50'
                  }
                }}
              >
                <Box sx={{ mr: 2, fontSize: '1.2em' }}>
                  {getEventIcon(event.event_data.event_name)}
                </Box>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Typography variant="body2" fontWeight="medium">
                        {event.event_data.event_name}
                      </Typography>
                      <Chip
                        size="small"
                        label={event.priority || 'info'}
                        color={getEventColor(event.event_data.event_name)}
                        sx={{ ml: 1 }}
                      />
                    </Box>
                  }
                  secondary={
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                      </Typography>
                      <Typography variant="caption" display="block" color="text.secondary">
                        ID: {event.event_id}
                      </Typography>
                      {event.event_data.station_id && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          Station: {event.event_data.station_id}
                        </Typography>
                      )}
                      {event.event_data.customer_id && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          Customer: {event.event_data.customer_id}
                        </Typography>
                      )}
                      {event.event_data.product_sku && (
                        <Typography variant="caption" display="block" color="text.secondary">
                          SKU: {event.event_data.product_sku}
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
          Showing {Math.min(events.length, 50)} of {events.length} total events
        </Typography>
      </Box>
    </Paper>
  )
}

export default EventsPanel