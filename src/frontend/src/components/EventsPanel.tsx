import React from 'react';
import {
  List,
  ListItem,
  ListItemText,
  Chip,
  Typography,
  Box,
} from '@mui/material';

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

interface EventsPanelProps {
  events: Event[];
}

const EventsPanel: React.FC<EventsPanelProps> = ({ events }) => {
  const getEventColor = (eventName: string) => {
    const dangerEvents = ['Scanner Avoidance', 'Barcode Switching', 'Weight Discrepancies'];
    const warningEvents = ['Long Queue Length', 'Long Wait Time', 'System Crash'];
    
    if (dangerEvents.includes(eventName)) return 'error';
    if (warningEvents.includes(eventName)) return 'warning';
    return 'info';
  };

  if (events.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography color="textSecondary">
          No events detected yet
        </Typography>
      </Box>
    );
  }

  return (
    <List sx={{ width: '100%', maxHeight: '300px', overflow: 'auto' }}>
      {events.slice(0, 20).map((event, index) => (
        <ListItem key={`${event.event_id}-${index}`} sx={{ px: 0 }}>
          <ListItemText
            primary={
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Chip
                  label={event.event_data.event_name}
                  color={getEventColor(event.event_data.event_name) as any}
                  size="small"
                />
                {event.event_data.station_id && (
                  <Chip
                    label={event.event_data.station_id}
                    variant="outlined"
                    size="small"
                  />
                )}
              </Box>
            }
            secondary={
              <Box>
                <Typography variant="caption" display="block">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </Typography>
                {event.event_data.customer_id && (
                  <Typography variant="caption" display="block">
                    Customer: {event.event_data.customer_id}
                  </Typography>
                )}
                {event.event_data.product_sku && (
                  <Typography variant="caption" display="block">
                    Product: {event.event_data.product_sku}
                  </Typography>
                )}
              </Box>
            }
          />
        </ListItem>
      ))}
    </List>
  );
};

export default EventsPanel;