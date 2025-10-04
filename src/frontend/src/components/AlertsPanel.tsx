import React from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Typography,
  Stack,
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

interface AlertsPanelProps {
  events: Event[];
}

const AlertsPanel: React.FC<AlertsPanelProps> = ({ events }) => {
  const getAlertSeverity = (eventName: string): 'error' | 'warning' | 'info' => {
    const errorEvents = ['Scanner Avoidance', 'Barcode Switching', 'Weight Discrepancies'];
    const warningEvents = ['Long Queue Length', 'Long Wait Time', 'System Crash'];
    
    if (errorEvents.includes(eventName)) return 'error';
    if (warningEvents.includes(eventName)) return 'warning';
    return 'info';
  };

  const recentAlerts = events
    .filter(event => {
      const alertEvents = [
        'Scanner Avoidance', 'Barcode Switching', 'Weight Discrepancies',
        'Long Queue Length', 'Long Wait Time', 'System Crash'
      ];
      return alertEvents.includes(event.event_data.event_name);
    })
    .slice(0, 10);

  if (recentAlerts.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 4 }}>
        <Typography color="textSecondary">
          No alerts at this time
        </Typography>
      </Box>
    );
  }

  return (
    <Stack spacing={2}>
      {recentAlerts.map((event, index) => (
        <Alert 
          key={`${event.event_id}-${index}`}
          severity={getAlertSeverity(event.event_data.event_name)}
          variant="outlined"
        >
          <AlertTitle>{event.event_data.event_name}</AlertTitle>
          <Typography variant="body2">
            Station: {event.event_data.station_id || 'Unknown'}
          </Typography>
          {event.event_data.customer_id && (
            <Typography variant="body2">
              Customer: {event.event_data.customer_id}
            </Typography>
          )}
          <Typography variant="caption" color="textSecondary">
            {new Date(event.timestamp).toLocaleString()}
          </Typography>
        </Alert>
      ))}
    </Stack>
  );
};

export default AlertsPanel;