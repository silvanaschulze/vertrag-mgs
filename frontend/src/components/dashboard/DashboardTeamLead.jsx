/**
 * Dashboard TEAM LEAD (Level 2) - Dashboard für Teamleiter
 * 
 * Dashboard intermediário:
 * - 4 cards com estatísticas do time
 * - Pode criar/editar contratos do time
 * - SEM relatórios
 * - SEM valores financeiros
 * - Gráfico simples de status dos contratos
 * 
 * Mittleres Dashboard:
 * - 4 Karten mit Team-Statistiken
 * - Kann Team-Verträge erstellen/bearbeiten
 * - KEINE Berichte
 * - KEINE Finanzwerte
 * - Einfaches Statusdiagramm der Verträge
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
  Divider
} from '@mui/material';
import {
  Description as ContractIcon,
  Warning as WarningIcon,
  Notifications as AlertIcon,
  Groups as TeamIcon
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

export default function DashboardTeamLead() {
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
        console.error('Erro ao carregar estatísticas:', err);
        setError('Erro ao carregar estatísticas do dashboard.');
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

  // Preparar dados para o gráfico de status
  const statusData = stats?.contracts_by_status
    ? Object.entries(stats.contracts_by_status).map(([status, count]) => ({
        name: status,
        value: count
      }))
    : [];

  return (
    <Box sx={{ p: 3 }}>
      {/* Cabeçalho */}
      <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
        Dashboard do Time
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
        {stats?.team_name && `Time: ${stats.team_name}`}
        {stats?.department_name && ` • Departamento: ${stats.department_name}`}
      </Typography>

      {/* Cards de Estatísticas */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Contratos do Time"
            value={stats?.total_contracts}
            subtitle="Total de contratos"
            icon={TeamIcon}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Contratos Ativos"
            value={stats?.active_contracts}
            subtitle="Em andamento"
            icon={ContractIcon}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expirando em 30 Dias"
            value={stats?.expiring_30_days}
            subtitle="Requerem atenção"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Alertas Não Lidos"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} alertas no total`}
            icon={AlertIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Gráfico de Status dos Contratos */}
      {statusData.length > 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Card elevation={3}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Status dos Contratos do Time
                </Typography>
                <Divider sx={{ mb: 2 }} />
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
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={6}>
            <Card elevation={1}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Suas Permissões
                </Typography>
                <Divider sx={{ mb: 2 }} />
                <Typography variant="body2" color="text.secondary" paragraph>
                  ✅ Visualizar contratos do time
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  ✅ Criar e editar contratos do time
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  ❌ Aprovar contratos (solicitar ao gestor do departamento)
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  ❌ Acessar relatórios (solicitar ao gestor do departamento)
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}
