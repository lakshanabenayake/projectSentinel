import React, { useState, useEffect } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Warning,
  Security,
  People,
  ShoppingCart,
} from '@mui/icons-material';
import EventsPanel from './EventsPanel';
import StationOverview from './StationOverview';
import RealTimeCharts from './RealTimeCharts';
import AlertsPanel from './AlertsPanel';
import { useSocket } from '../hooks/useSocket';
import { useDashboardStore } from '../stores/dashboardStore';

const Dashboard: React.FC = () => {
  const { socket, connected } = useSocket();
  const { stats, events, addEvent, updateStats } = useDashboardStore();
  
  useEffect(() => {
    if (socket) {
      // Listen for new events
      socket.on('new_event', (event) => {
        addEvent(event);
      });

      // Listen for data updates
      socket.on('data_update', (data) => {
        console.log('Data update:', data);
      });

      // Fetch initial stats
      fetchStats();
    }

    return () => {
      if (socket) {
        socket.off('new_event');
        socket.off('data_update');
      }
    };
  }, [socket, addEvent]);

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/dashboard/stats');
      const data = await response.json();
      updateStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const connectionStatus = connected ? (
    <Alert severity="success" sx={{ mb: 2 }}>
      Connected to Sentinel Backend
    </Alert>
  ) : (
    <Alert severity="error" sx={{ mb: 2 }}>
      Disconnected from Backend
    </Alert>
  );

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <DashboardIcon sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
        <Typography variant="h3" component="h1" color="primary">
          Project Sentinel Dashboard
        </Typography>
      </Box>

      {connectionStatus}

      {/* Stats Overview */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
              <Warning sx={{ fontSize: 40, mr: 2, color: 'warning.main' }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Total Events
                </Typography>
                <Typography variant="h4">
                  {stats.total_events || 0}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
              <Security sx={{ fontSize: 40, mr: 2, color: 'error.main' }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Security Alerts
                </Typography>
                <Typography variant="h4">
                  {(stats.event_counts?.['Scanner Avoidance'] || 0) +
                   (stats.event_counts?.['Barcode Switching'] || 0) +
                   (stats.event_counts?.['Weight Discrepancies'] || 0)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
              <People sx={{ fontSize: 40, mr: 2, color: 'info.main' }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Active Stations
                </Typography>
                <Typography variant="h4">
                  {stats.active_stations || 0}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent sx={{ display: 'flex', alignItems: 'center' }}>
              <ShoppingCart sx={{ fontSize: 40, mr: 2, color: 'success.main' }} />
              <Box>
                <Typography color="textSecondary" gutterBottom>
                  Queue Issues
                </Typography>
                <Typography variant="h4">
                  {(stats.event_counts?.['Long Queue Length'] || 0) +
                   (stats.event_counts?.['Long Wait Time'] || 0)}
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Main Dashboard Grid */}
      <Grid container spacing={3}>
        {/* Real-time Charts */}
        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 2, height: '400px' }}>
            <Typography variant="h6" gutterBottom>
              Real-time Analytics
            </Typography>
            <RealTimeCharts />
          </Paper>
        </Grid>

        {/* Alerts Panel */}
        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 2, height: '400px', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Recent Alerts
            </Typography>
            <AlertsPanel events={events} />
          </Paper>
        </Grid>

        {/* Station Overview */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '350px' }}>
            <Typography variant="h6" gutterBottom>
              Station Overview
            </Typography>
            <StationOverview stationActivity={stats.station_activity || {}} />
          </Paper>
        </Grid>

        {/* Events Panel */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, height: '350px', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Event Log
            </Typography>
            <EventsPanel events={events} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;