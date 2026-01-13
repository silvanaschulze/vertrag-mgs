/**
 * Dashboard DEPARTMENT USER (Level 3) - Dashboard für Abteilungsbenutzer
 * 
 * Dashboard intermediário+:
 * - Cards com estatísticas do departamento
 * - Pode aprovar contratos do departamento
 * - Relatórios limitados (SEM valores financeiros)
 * - Gráfico de status dos contratos
 * 
 * Mittleres+ Dashboard:
 * - Karten mit Abteilungsstatistiken
 * - Kann Abteilungsverträge genehmigen
 * - Eingeschränkte Berichte (OHNE Finanzwerte)
 * - Statusdiagramm der Verträge
 */

import { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Divider,
  Chip
} from '@mui/material';
import {
  Description as ContractIcon,
  Warning as WarningIcon,
  Notifications as AlertIcon,
  CheckCircle as ApprovalIcon,
  Business as DepartmentIcon
} from '@mui/icons-material';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import dashboardApi from '../../services/dashboardApi';

const COLORS = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#6B7280'];

function StatCard({ title, value, subtitle, icon: Icon, color = 'primary' }) {
  return (
    <Card elevation={3}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
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

export default function DashboardDepartmentUser() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await dashboardApi.getStats();
        setStats(data);
      } catch (err) {
        console.error('Error loading statistics:', err);
        setError('Error loading dashboard statistics.');
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

  const statusData = stats?.contracts_by_status
    ? Object.entries(stats.contracts_by_status).map(([status, count]) => ({
        name: status,
        value: count
      }))
    : [];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 0.5, fontWeight: 600 }}>
            Department Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {stats?.department_name && `Department: ${stats.department_name}`}
          </Typography>
        </Box>
        <Chip 
          label="Department User" 
          color="primary" 
          variant="outlined"
          icon={<DepartmentIcon />}
        />
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Contracts"
            value={stats?.total_contracts}
            subtitle="Department"
            icon={ContractIcon}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Contracts"
            value={stats?.active_contracts}
            subtitle="In progress"
            icon={CheckCircle}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expiring in 30 Days"
            value={stats?.expiring_30_days}
            subtitle="Require renewal"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Pending Approvals"
            value={stats?.pending_approvals}
            subtitle="Waiting approval"
            icon={ApprovalIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Row 2 - Alerts and Expiring 90 days */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Unread Alerts"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} total`}
            icon={AlertIcon}
            color="error"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expiring in 90 Days"
            value={stats?.expiring_90_days}
            subtitle="Monitoring"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Contract Status
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {statusData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={statusData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {statusData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">
                  No data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={1} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Your Permissions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ View department contracts
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Approve department contracts
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Access reports (without financial values)
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Create and manage users up to level 3
              </Typography>
            </CardContent>
          </Card>

          <Alert severity="info">
            <strong>Note:</strong> You have access to limited reports without financial values. 
            To access complete reports, request from the department manager.
          </Alert>
        </Grid>
      </Grid>
    </Box>
  );
}
