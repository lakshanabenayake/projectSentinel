import React from 'react'
import {
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Box,
  Chip
} from '@mui/material'
import {
  TrendingUp,
  Warning,
  CheckCircle,
  Error,
  Store,
  People
} from '@mui/icons-material'

interface DashboardProps {
  metrics: {
    total_events: number
    active_stations: string[]
    active_customers: string[]
    alerts: any[]
    inventory_alerts: number
  }
  isConnected: boolean
}

const Dashboard: React.FC<DashboardProps> = ({ metrics, isConnected }) => {
  const criticalAlerts = metrics.alerts.filter(alert => alert.priority === 'critical').length
  const warningAlerts = metrics.alerts.filter(alert => alert.priority === 'warning').length
  const infoAlerts = metrics.alerts.filter(alert => alert.priority === 'info').length

  const MetricCard: React.FC<{
    title: string
    value: number | string
    icon: React.ReactNode
    color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success'
    subtitle?: string
  }> = ({ title, value, icon, color = 'primary', subtitle }) => (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box sx={{ color: `${color}.main`, mr: 1 }}>
            {icon}
          </Box>
          <Typography variant="h6" component="h2" color={`${color}.main`}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" component="div" fontWeight="bold">
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  )

  return (
    <Paper sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" component="h2">
          Store Overview
        </Typography>
        <Chip
          label={isConnected ? 'Live Data' : 'Offline'}
          color={isConnected ? 'success' : 'default'}
          size="small"
        />
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Events"
            value={metrics.total_events}
            icon={<TrendingUp />}
            color="primary"
            subtitle="All detected events"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Stations"
            value={metrics.active_stations.length}
            icon={<Store />}
            color="info"
            subtitle="Currently operational"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Customers"
            value={metrics.active_customers.length}
            icon={<People />}
            color="success"
            subtitle="In checkout process"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Inventory Alerts"
            value={metrics.inventory_alerts}
            icon={<Warning />}
            color="warning"
            subtitle="Stock discrepancies"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Critical Alerts"
            value={criticalAlerts}
            icon={<Error />}
            color="error"
            subtitle="Requires immediate attention"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Warning Alerts"
            value={warningAlerts}
            icon={<Warning />}
            color="warning"
            subtitle="Monitoring required"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={4}>
          <MetricCard
            title="Info Events"
            value={infoAlerts}
            icon={<CheckCircle />}
            color="success"
            subtitle="Normal operations"
          />
        </Grid>
      </Grid>
    </Paper>
  )
}

export default Dashboard