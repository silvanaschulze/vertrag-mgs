/**
 * Dashboard DEPARTMENT ADMIN (Level 4) - Dashboard für Abteilungsadministrator
 * 
 * Dashboard avançado:
 * - Cards completos com estatísticas do departamento
 * - COM valores financeiros
 * - Relatórios completos do departamento
 * - Múltiplos gráficos (status, tipos)
 * - Gerenciamento de usuários do departamento
 * 
 * Erweitertes Dashboard:
 * - Vollständige Karten mit Abteilungsstatistiken
 * - MIT Finanzwerten
 * - Vollständige Abteilungsberichte
 * - Mehrere Diagramme (Status, Typen)
 * - Benutzerverwaltung der Abteilung
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
  AttachMoney as MoneyIcon,
  People as PeopleIcon
} from '@mui/icons-material';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import dashboardApi from '../../services/dashboardApi';

const COLORS = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#6B7280', '#8B5CF6'];

function StatCard({ title, value, subtitle, icon: Icon, color = 'primary', isCurrency = false }) {
  const formattedValue = isCurrency && value !== null && value !== undefined
    ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)
    : value;

  return (
    <Card elevation={3}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 500 }}>
            {title}
          </Typography>
          <Icon sx={{ color: `${color}.main`, fontSize: 40 }} />
        </Box>
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 1, color: `${color}.main`, fontSize: isCurrency ? '1.75rem' : '2.5rem' }}>
          {formattedValue !== null && formattedValue !== undefined ? formattedValue : '-'}
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

export default function DashboardDepartmentAdm() {
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

  const typeData = stats?.contracts_by_type
    ? Object.entries(stats.contracts_by_type).map(([type, count]) => ({
        name: type,
        quantity: count
      }))
    : [];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 0.5, fontWeight: 600 }}>
            Administrative Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {stats?.department_name && `Department: ${stats.department_name}`}
          </Typography>
        </Box>
        <Chip 
          label="Department Admin" 
          color="primary" 
          icon={<PeopleIcon />}
        />
      </Box>

      {/* Statistics Cards - Row 1 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
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
            title="Monthly Value"
            value={stats?.monthly_value}
            subtitle="Active total"
            icon={MoneyIcon}
            color="success"
            isCurrency={true}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Department Users"
            value={stats?.department_users}
            subtitle="Team members"
            icon={PeopleIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Statistics Cards - Row 2 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expiring in 30 Days"
            value={stats?.expiring_30_days}
            subtitle="Action needed"
            icon={WarningIcon}
            color="warning"
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

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Alerts"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} total`}
            icon={AlertIcon}
            color="error"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Approvals"
            value={stats?.pending_approvals}
            subtitle="Waiting"
            icon={ApprovalIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        {/* Status Chart */}
        <Grid item xs={12} md={12} lg={8}>
          <Card elevation={3} sx={{ minHeight: 480, width: '100%', maxWidth: '100%' }}>
            <CardContent sx={{ height: '100%', p: 3, minWidth: 0 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Contracts by Status
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {statusData.length > 0 ? (
                <Box sx={{ width: '100%', minWidth: 0, overflow: 'visible' }}>
                  <ResponsiveContainer width="100%" height={380}>
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
                      <Legend verticalAlign="bottom" height={36} />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">No data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Types Chart */}
        <Grid item xs={12} md={12} lg={8}>
          <Card elevation={3} sx={{ minHeight: 480, width: '100%', maxWidth: '100%' }}>
            <CardContent sx={{ height: '100%', p: 3, minWidth: 0 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Contracts by Type
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {typeData.length > 0 ? (
                <Box sx={{ width: '100%', minWidth: 0, overflow: 'visible' }}>
                  <ResponsiveContainer width="100%" height={380}>
                    <BarChart data={typeData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="name" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="quantity" fill="#2563EB" name="Quantity" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">No data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Additional Information */}
        <Grid item xs={12}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Your Administrative Permissions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ View and edit all department contracts
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Approve department contracts
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Access complete reports with financial values
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Create and manage department users
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Define roles up to level 4
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ❌ Access other departments (request from Board)
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
