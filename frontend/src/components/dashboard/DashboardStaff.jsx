/**
 * Dashboard STAFF (Level 1) - Employee Dashboard
 * 
 * Simplest dashboard:
 * - 3 cards with basic statistics
 * - Only own contracts
 * - NO charts
 * - NO financial values
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Description as ContractIcon,
  Warning as WarningIcon,
  Notifications as AlertIcon
} from '@mui/icons-material';
import dashboardApi from '../../services/dashboardApi';

/**
 * Statistics Card Component
 */
function StatCard({ title, value, subtitle, icon: Icon, color = 'primary' }) {
  return (
    <Card elevation={3}>
      <CardContent sx={{ minWidth: 0 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2, minWidth: 0 }}>
          <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 500 }}>
            {title}
          </Typography>
          <Icon sx={{ color: `${color}.main`, fontSize: 40 }} />
        </Box>
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 1, color: `${color}.main` }}>
          {value !== null && value !== undefined ? value : '-'}
        </Typography>
        {subtitle && (
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Dashboard for STAFF (Level 1)
 */
export default function DashboardStaff() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Fetch statistics from backend
   */
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await dashboardApi.getStats();
        setStats(data);
      } catch (err) {
        console.error('Error loading statistics:', err);
        setError('Error loading dashboard statistics. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">{error}</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        My Contracts
        <Typography component="span" variant="body1" color="text.secondary" sx={{ ml: 2 }}>
          Employee Dashboard
        </Typography>
      </Typography>

      {/* Statistics Cards */}
      <Grid container spacing={10} sx={{ mb: 5, minWidth: 0 }}  >
        {/* Total Contracts */}
        <Grid item xs={12} md={12} lg={12} ></Grid>
        <Grid item xs={12}>
          <StatCard
            title="My Contracts"
            value={stats?.total_contracts}
            subtitle="Total contracts where I'm responsible"
            icon={ContractIcon}
            color="primary"
          />
        </Grid>

        {/* Expiring Contracts */}
        <Grid item xs={12} md={12} lg={12} >
          <StatCard
            title="Expiring in 30 Days"
            value={stats?.expiring_30_days}
            subtitle="Contracts expiring soon"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        {/* Alerts */}
        <Grid item xs={12} md={12} lg={12} >
          <StatCard
            title="My Alerts"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} total alerts`}
            icon={AlertIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Additional Information */}
      <Box sx={{ mt: 4 }}>
        <Card elevation={1}>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              <strong>Tip:</strong> You only have access to contracts where you are responsible. 
              To create new contracts or access reports, request permissions from your manager.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
