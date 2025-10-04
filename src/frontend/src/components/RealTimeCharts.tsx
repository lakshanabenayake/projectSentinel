import React, { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';
import { Box, Grid, Typography } from '@mui/material';
import { useDashboardStore } from '../stores/dashboardStore';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
);

const RealTimeCharts: React.FC = () => {
  const { events, stats } = useDashboardStore();
  const [eventTrend, setEventTrend] = useState<any>(null);
  const [eventTypeDistribution, setEventTypeDistribution] = useState<any>(null);

  useEffect(() => {
    // Process events for trend chart
    const last30Events = events.slice(0, 30).reverse();
    const trendData = {
      labels: last30Events.map((_, index) => `Event ${index + 1}`),
      datasets: [
        {
          label: 'Events Over Time',
          data: last30Events.map((_, index) => index + 1),
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.2)',
          tension: 0.1,
        },
      ],
    };
    setEventTrend(trendData);

    // Process event type distribution
    const eventCounts = stats.event_counts || {};
    const distributionData = {
      labels: Object.keys(eventCounts),
      datasets: [
        {
          label: 'Event Count',
          data: Object.values(eventCounts),
          backgroundColor: [
            'rgba(255, 99, 132, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 205, 86, 0.8)',
            'rgba(75, 192, 192, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
          ],
          borderColor: [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)',
            'rgba(255, 205, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
            'rgba(255, 159, 64, 1)',
          ],
          borderWidth: 1,
        },
      ],
    };
    setEventTypeDistribution(distributionData);
  }, [events, stats]);

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  if (!eventTrend || !eventTypeDistribution) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <Typography>Loading charts...</Typography>
      </Box>
    );
  }

  return (
    <Grid container spacing={2} sx={{ height: '100%' }}>
      <Grid item xs={12} md={6}>
        <Box sx={{ height: '300px' }}>
          <Typography variant="subtitle2" gutterBottom>
            Event Trend
          </Typography>
          <Line data={eventTrend} options={chartOptions} />
        </Box>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Box sx={{ height: '300px' }}>
          <Typography variant="subtitle2" gutterBottom>
            Event Distribution
          </Typography>
          <Bar data={eventTypeDistribution} options={chartOptions} />
        </Box>
      </Grid>
    </Grid>
  );
};

export default RealTimeCharts;