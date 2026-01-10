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

  const statusData = stats?.contracts_by_status
    ? Object.entries(stats.contracts_by_status).map(([status, count]) => ({
        name: status,
        value: count
      }))
    : [];

  return (
    <Box sx={{ p: 3 }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 0.5, fontWeight: 600 }}>
            Dashboard do Departamento
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {stats?.department_name && `Departamento: ${stats.department_name}`}
          </Typography>
        </Box>
        <Chip 
          label="Usuário Departamento" 
          color="primary" 
          variant="outlined"
          icon={<DepartmentIcon />}
        />
      </Box>

      {/* Cards de Estatísticas */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Contratos"
            value={stats?.total_contracts}
            subtitle="Departamento"
            icon={ContractIcon}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Contratos Ativos"
            value={stats?.active_contracts}
            subtitle="Em andamento"
            icon={CheckCircle}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expirando 30 Dias"
            value={stats?.expiring_30_days}
            subtitle="Requerem renovação"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Aprovações Pendentes"
            value={stats?.pending_approvals}
            subtitle="Aguardando aprovação"
            icon={ApprovalIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Linha 2 - Alertas e Expirando 90 dias */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Alertas Não Lidos"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} total`}
            icon={AlertIcon}
            color="error"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expirando 90 Dias"
            value={stats?.expiring_90_days}
            subtitle="Monitoramento"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Gráficos */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Status dos Contratos
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
                  Nenhum dado disponível
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card elevation={1} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Suas Permissões
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Visualizar contratos do departamento
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Aprovar contratos do departamento
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Acessar relatórios (sem valores financeiros)
              </Typography>
              <Typography variant="body2" color="text.secondary" paragraph>
                ✅ Criar e gerenciar usuários até nível 3
              </Typography>
            </CardContent>
          </Card>

          <Alert severity="info">
            <strong>Nota:</strong> Você tem acesso a relatórios limitados sem valores financeiros. 
            Para acessar relatórios completos, solicite ao gestor do departamento.
          </Alert>
        </Grid>
      </Grid>
    </Box>
  );
}
