import React, { useEffect, useState } from 'react'
import {
  Paper,
  Typography,
  Box,
  Grid
} from '@mui/material'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  BarElement
} from 'chart.js'
import { Line, Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface QueueStats {
  customer_count: number
  average_dwell_time: number
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

interface RealTimeChartsProps {
  queueStats: Record<string, QueueStats>
  events: Event[]
}

const RealTimeCharts: React.FC<RealTimeChartsProps> = ({ queueStats, events }) => {
  const [queueData, setQueueData] = useState<any>({
    labels: [],
    datasets: []
  })
  
  const [eventData, setEventData] = useState<any>({
    labels: [],
    datasets: []
  })

  useEffect(() => {
    // Update queue stats chart
    const stations = Object.keys(queueStats)
    const customerCounts = stations.map(station => queueStats[station]?.customer_count || 0)
    const waitTimes = stations.map(station => Math.round((queueStats[station]?.average_dwell_time || 0) / 60)) // Convert to minutes

    setQueueData({
      labels: stations,
      datasets: [
        {
          label: 'Queue Length',
          data: customerCounts,
          backgroundColor: 'rgba(54, 162, 235, 0.8)',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        },
        {
          label: 'Wait Time (min)',
          data: waitTimes,
          backgroundColor: 'rgba(255, 99, 132, 0.8)',
          borderColor: 'rgba(255, 99, 132, 1)',
          borderWidth: 1
        }
      ]
    })
  }, [queueStats])

  useEffect(() => {
    // Update events chart - count events by type
    const eventTypes = events.reduce((acc: Record<string, number>, event) => {
      const eventName = event.event_data.event_name
      acc[eventName] = (acc[eventName] || 0) + 1
      return acc
    }, {})

    const labels = Object.keys(eventTypes)
    const data = Object.values(eventTypes)
    const colors = labels.map((label: string) => {
      if (label.includes('Scanner Avoidance') || label.includes('Barcode Switching')) {
        return 'rgba(244, 67, 54, 0.8)'
      }
      if (label.includes('Weight') || label.includes('Queue') || label.includes('Wait')) {
        return 'rgba(255, 152, 0, 0.8)'
      }
      if (label.includes('Success')) {
        return 'rgba(76, 175, 80, 0.8)'
      }
      return 'rgba(33, 150, 243, 0.8)'
    })

    setEventData({
      labels,
      datasets: [
        {
          label: 'Event Count',
          data,
          backgroundColor: colors,
          borderColor: colors.map((color: string) => color.replace('0.8', '1')),
          borderWidth: 1
        }
      ]
    })
  }, [events])

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
        ticks: {
          stepSize: 1
        }
      }
    }
  }

  const eventChartOptions = {
    ...chartOptions,
    indexAxis: 'y' as const,
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      }
    }
  }

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" component="h3" gutterBottom>
        Real-time Analytics
      </Typography>

      <Grid container spacing={3}>
        {/* Queue Stats Chart */}
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <Typography variant="subtitle1" gutterBottom>
              Station Queue Status
            </Typography>
            {Object.keys(queueStats).length > 0 ? (
              <Bar data={queueData} options={chartOptions} />
            ) : (
              <Box sx={{ 
                height: '100%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                backgroundColor: 'grey.50',
                borderRadius: 1
              }}>
                <Typography color="text.secondary">
                  No queue data available
                </Typography>
              </Box>
            )}
          </Box>
        </Grid>

        {/* Events Chart */}
        <Grid item xs={12} md={6}>
          <Box sx={{ height: 300 }}>
            <Typography variant="subtitle1" gutterBottom>
              Event Distribution
            </Typography>
            {events.length > 0 ? (
              <Bar data={eventData} options={eventChartOptions} />
            ) : (
              <Box sx={{ 
                height: '100%', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                backgroundColor: 'grey.50',
                borderRadius: 1
              }}>
                <Typography color="text.secondary">
                  No events detected yet
                </Typography>
              </Box>
            )}
          </Box>
        </Grid>
      </Grid>

      <Box sx={{ mt: 2, p: 2, backgroundColor: 'grey.50', borderRadius: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Charts update automatically as new data arrives. Queue data shows current customer counts and wait times. 
          Event distribution shows the frequency of different event types detected by the system.
        </Typography>
      </Box>
    </Paper>
  )
}

export default RealTimeCharts