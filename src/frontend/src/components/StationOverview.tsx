import React from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error,
} from '@mui/icons-material';

interface StationOverviewProps {
  stationActivity: Record<string, number>;
}

const StationOverview: React.FC<StationOverviewProps> = ({ stationActivity }) => {
  const getStationStatus = (activity: number) => {
    if (activity >= 10) return 'busy';
    if (activity >= 5) return 'normal';
    if (activity > 0) return 'idle';
    return 'offline';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'busy': return <Warning color="warning" />;
      case 'normal': return <CheckCircle color="success" />;
      case 'idle': return <CheckCircle color="info" />;
      default: return <Error color="error" />;
    }
  };

  const getStatusColor = (status: string): 'error' | 'warning' | 'info' | 'success' => {
    switch (status) {
      case 'busy': return 'warning';
      case 'normal': return 'success';
      case 'idle': return 'info';
      default: return 'error';
    }
  };

  const stations = ['SCC1', 'SCC2', 'SCC3', 'SCC4', 'RC1'];

  return (
    <Grid container spacing={2}>
      {stations.map((stationId) => {
        const activity = stationActivity[stationId] || 0;
        const status = getStationStatus(activity);
        
        return (
          <Grid item xs={12} sm={6} md={4} key={stationId}>
            <Card variant="outlined">
              <CardContent sx={{ p: 2 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  {getStatusIcon(status)}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {stationId}
                  </Typography>
                </Box>
                
                <Chip
                  label={status.toUpperCase()}
                  color={getStatusColor(status)}
                  size="small"
                  sx={{ mb: 1 }}
                />
                
                <Typography variant="body2" color="textSecondary">
                  Activity: {activity} events/10min
                </Typography>
                
                {stationId.startsWith('SCC') && (
                  <Typography variant="caption" display="block">
                    Self-Checkout Counter
                  </Typography>
                )}
                
                {stationId === 'RC1' && (
                  <Typography variant="caption" display="block">
                    Regular Counter
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Grid>
        );
      })}
    </Grid>
  );
};

export default StationOverview;