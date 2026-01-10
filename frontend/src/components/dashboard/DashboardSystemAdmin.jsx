/**
 * Dashboard SYSTEM ADMIN (Level 6) - Dashboard für Systemadministrator
 * 
 * Dashboard TÉCNICO (NÃO mostra contratos/financeiro):
 * - Métricas técnicas do sistema
 * - Gerenciamento de usuários
 * - Estatísticas de banco de dados
 * - Informações de backup
 * - Sessões ativas
 * - SEM contratos, SEM relatórios, SEM valores financeiros
 * 
 * TECHNISCHES Dashboard (KEINE Verträge/Finanzen):
 * - Technische Systemmetriken
 * - Benutzerverwaltung
 * - Datenbankstatistiken
 * - Backup-Informationen
 * - Aktive Sitzungen
 * - KEINE Verträge, KEINE Berichte, KEINE Finanzwerte
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
  Chip,
  LinearProgress
} from '@mui/material';
import {
  Storage as StorageIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  Backup as BackupIcon,
  Computer as ComputerIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import dashboardApi from '../../services/dashboardApi';

function StatCard({ title, value, subtitle, icon: Icon, color = 'primary', unit = '' }) {
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
          {unit && <Typography component="span" variant="h5" color="text.secondary"> {unit}</Typography>}
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

function MetricCard({ title, value, max, unit, icon: Icon, color = 'primary' }) {
  const percentage = max > 0 ? (value / max) * 100 : 0;
  const barColor = percentage > 80 ? 'error' : percentage > 60 ? 'warning' : 'success';

  return (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Icon sx={{ color: `${color}.main`, fontSize: 32, mr: 2 }} />
          <Typography variant="h6" sx={{ fontWeight: 500 }}>
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          {value !== null && value !== undefined ? value.toFixed(2) : '0.00'} {unit}
        </Typography>
        {max > 0 && (
          <>
            <LinearProgress 
              variant="determinate" 
              value={Math.min(percentage, 100)} 
              color={barColor}
              sx={{ mb: 1, height: 8, borderRadius: 1 }}
            />
            <Typography variant="body2" color="text.secondary">
              {percentage.toFixed(1)}% used
            </Typography>
          </>
        )}
      </CardContent>
    </Card>
  );
}

export default function DashboardSystemAdmin() {
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

  return (
    <Box sx={{ p: 3 }}>
      {/* Technical Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 0.5, fontWeight: 600 }}>
            System Administration Panel
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Technical Information & Management • System Administrator
          </Typography>
        </Box>
        <Chip 
          label="System Admin" 
          color="error" 
          icon={<SecurityIcon />}
        />
      </Box>

      {/* Permissions Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>Technical Access:</strong> You have access only to technical system functions. 
        To access contracts or financial reports, request permissions from the Board.
      </Alert>

      {/* User Statistics */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Users"
            value={stats?.total_users}
            subtitle="Registered in system"
            icon={PeopleIcon}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Sessions"
            value={stats?.active_sessions}
            subtitle="Online users"
            icon={ComputerIcon}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="System Uptime"
            value={stats?.uptime_days}
            subtitle="Days without restart"
            icon={SpeedIcon}
            color="info"
            unit="days"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Last Backup"
            value={stats?.last_backup || 'N/A'}
            subtitle="Backup date"
            icon={BackupIcon}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Storage Metrics */}
      <Typography variant="h5" sx={{ mb: 2, fontWeight: 600 }}>
        Storage and Database
      </Typography>
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <MetricCard
            title="Disk Usage (Uploads)"
            value={stats?.disk_usage_mb || 0}
            max={1024} // 1GB limit example
            unit="MB"
            icon={StorageIcon}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <MetricCard
            title="Database Size"
            value={stats?.total_database_size_mb || 0}
            max={512} // 512MB limit example
            unit="MB"
            icon={StorageIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Administrative Functions */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Your Technical Permissions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Manage all system users
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Define all roles and access levels (1-6)
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Access system configurations
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Manage integrations and APIs
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Access logs and audit
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Manage backups and security
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Access Restrictions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary" paragraph>
                ❌ View department contracts
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ❌ Access financial reports
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ❌ Approve contracts
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ❌ View monetary values
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Alert severity="warning" sx={{ mt: 2 }}>
                <Typography variant="body2">
                  <strong>Note:</strong> To access contracts or financial data, 
                  you must receive additional permissions from the Board or create an account 
                  with an appropriate role (DIRECTOR, DEPARTMENT_ADM, etc).
                </Typography>
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* System Information */}
        <Grid item xs={12}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                System Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600 }}>
                    Version:
                  </Typography>
                  <Typography variant="body1">1.0.0</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600 }}>
                    Environment:
                  </Typography>
                  <Typography variant="body1">Development</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600 }}>
                    Database:
                  </Typography>
                  <Typography variant="body1">SQLite</Typography>
                </Grid>
                <Grid item xs={12} sm={6} md={3}>
                  <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 600 }}>
                    Framework:
                  </Typography>
                  <Typography variant="body1">FastAPI + React</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
