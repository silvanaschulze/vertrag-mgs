/**
 * Dashboard DIRECTOR (Level 5) - Dashboard für Geschäftsführung
 * 
 * Dashboard executivo completo:
 * - Visão geral de toda a empresa
 * - Todos valores financeiros
 * - Relatórios executivos completos
 * - Múltiplos gráficos estratégicos
 * - Análise por departamento
 * 
 * Vollständiges Executive Dashboard:
 * - Unternehmensweite Übersicht
 * - Alle Finanzwerte
 * - Vollständige Executive-Berichte
 * - Mehrere strategische Diagramme
 * - Analyse nach Abteilung
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
  People as PeopleIcon,
  Business as BusinessIcon,
  TrendingUp as TrendIcon
} from '@mui/icons-material';
import { 
  PieChart, Pie, Cell, BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend, Tooltip 
} from 'recharts';
import dashboardApi from '../../services/dashboardApi';

const COLORS = ['#2563EB', '#10B981', '#F59E0B', '#EF4444', '#6B7280', '#8B5CF6', '#EC4899'];

function StatCard({ title, value, subtitle, icon: Icon, color = 'primary', isCurrency = false }) {
  const formattedValue = isCurrency && value !== null && value !== undefined
    ? new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(value)
    : value;

  return (
    <Card elevation={3} sx={{ height: '100%' }}>
      <CardContent sx={{ minWidth: 0 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2, minWidth: 0 }}>
          <Typography variant="h6" color="text.secondary" sx={{ fontWeight: 500, fontSize: '0.95rem' }}>
            {title}
          </Typography>
          <Icon sx={{ color: `${color}.main`, fontSize: 36 }} />
        </Box>
        <Typography variant="h3" sx={{ fontWeight: 700, mb: 1, color: `${color}.main`, fontSize: isCurrency ? '1.5rem' : '2.25rem' }}>
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

export default function DashboardDirector() {
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
        console.error('Fehler beim Laden der Statistiken:', err);
        setError('Fehler beim Laden der Dashboard-Statistiken.');
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

  const departmentData = stats?.contracts_by_department
    ? Object.entries(stats.contracts_by_department).map(([dept, count]) => ({
        departamento: dept,
        contracts: count
      }))
    : [];

  return (
    <Box sx={{
      p: 3,
      width: '100%',
      maxWidth: '100%',
      mx: 'auto',
      minHeight: '100vh',
      boxSizing: 'border-box',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'stretch',
      backgroundColor: 'background.default',
    }}>
      {/* Executive Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 0.5, fontWeight: 600 }}>
            Executive Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Company Overview
          </Typography>
        </Box>
        <Chip 
          label="Director" 
          color="primary" 
          icon={<BusinessIcon />}
        />
      </Box>

      {/* Main KPIs - Row 1 */}
      <Grid container spacing={2} sx={{ mb: 5, minWidth: 0 }}>
        <Grid item xs={12} md={6} lg={3} ></Grid>
        <Grid item xs={12}>
          <StatCard
            title="Total Contracts"
            value={stats?.total_contracts}
            subtitle="Across entire company"
            icon={ContractIcon}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Contracts"
            value={stats?.active_contracts}
            subtitle="In progress"
            icon={TrendIcon}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Monthly Value"
            value={stats?.monthly_value}
            subtitle="Recurring revenue"
            icon={MoneyIcon}
            color="success"
            isCurrency={true}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats?.total_users}
            subtitle="On platform"
            icon={PeopleIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Secondary KPIs - Row 2 */}
      <Grid container spacing={2} sx={{ mb: 5, minWidth: 0 }}>
        <Grid item xs={12} md={12} lg={12} ></Grid>
        <Grid item xs={12}>
          <StatCard
            title="Expiring in 30 Days"
            value={stats?.expiring_30_days}
            subtitle="Immediate attention"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} md={12} lg={12} >
          <StatCard
            title="Expiring in 90 Days"
            value={stats?.expiring_90_days}
            subtitle="Planning"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} md={12} lg={12} >
          <StatCard
            title="Pending Alerts"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} total`}
            icon={AlertIcon}
            color="error"
          />
        </Grid>

        <Grid item xs={12} md={12} lg={12} >
          <StatCard
            title="Approvals"
            value={stats?.pending_approvals}
            subtitle="Awaiting decision"
            icon={ApprovalIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Executive Charts */}
      <Grid container spacing={10} sx={{ mb: 12, minWidth: 0 }}>
        <Grid item xs={12} >  </Grid>
        {/* Contracts by Department */}
        <Grid item xs={12} md={12} lg={12} >
          <Card elevation={3} sx={{ width: '130%', minWidth: 0 }}>
            <CardContent>
              <Typography variant="h5" sx={{ mb: 12, fontWeight: 600 }}>
                Contracts by Department
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {departmentData.length > 0 ? (
                <Box sx={{ width: '100%', margin: '0 auto', height: 340, alignSelf: 'center' }}>
                  <ResponsiveContainer width="100%" height={340}>
                    <BarChart data={departmentData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="departamento" angle={-45} textAnchor="end" height={150} />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="contracts" fill="#2563EB" name="Contracts" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">No data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Contracts by Status */}
      
        <Grid item xs={12} md={12} lg={12} >
          <Card elevation={3} sx={{ width: '130%', minWidth: 0 }}>
            <CardContent>
              <Typography variant="h5" sx={{ mb: 12, fontWeight: 600 }}>
                Distribution by Status
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {statusData.length > 0 ? (
                <Box 
                  sx={{ 
                    flexGrow: 1,
                    width: '100%',
                    margin: '0 auto',
                    alignSelf: 'center',
                    height: 340,
                  }}
                >
                  <ResponsiveContainer width="100%" height={340}>
                    <PieChart>
                      <Pie
                        data={statusData}
                        dataKey="value"
                        cx="50%"
                        cy="50%"
                        outerRadius={90}
                        label={false}
                        labelLine={false}
                        fill="#8884d8"
                      >
                        {statusData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                      <Legend verticalAlign="bottom" height={46} />
                    </PieChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">No data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Contracts by Type */}
        <Grid item xs={12} md={12} lg={12} >
          <Card elevation={3} sx={{ width: '180%', minWidth: 0 }}>
            <CardContent>
              <Typography variant="h5" sx={{ mb: 12, fontWeight: 600 }}>
                Contract Types
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {typeData.length > 0 ? (
                <Box sx={{ width: '100%', margin: '0 auto', height: 340, alignSelf: 'center' }}>
                  <ResponsiveContainer width="100%" height={340}>
                    <BarChart data={typeData} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis type="number" />
                      <YAxis dataKey="name" type="category" width={100} />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="quantity" fill="#10B981" name="Quantity" />
                    </BarChart>
                  </ResponsiveContainer>
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">No data available</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Permissions and Information 
        <Grid item xs={12} md={4} lg={4}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Complete Executive Access
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={1}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✔️ View all company contracts
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✔️ Approve strategic contracts
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✔️ Access all reports with financial values
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✔️ Manage users and roles in all sectors
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✔️ Define all access levels (1-5)
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid> */}
      </Grid>
    </Box>
  );
}
