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

  const typeData = stats?.contracts_by_type
    ? Object.entries(stats.contracts_by_type).map(([type, count]) => ({
        name: type,
        quantidade: count
      }))
    : [];

  return (
    <Box sx={{ p: 3 }}>
      {/* Cabeçalho */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 0.5, fontWeight: 600 }}>
            Dashboard Administrativo
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {stats?.department_name && `Departamento: ${stats.department_name}`}
          </Typography>
        </Box>
        <Chip 
          label="Admin Departamento" 
          color="primary" 
          icon={<PeopleIcon />}
        />
      </Box>

      {/* Cards de Estatísticas - Linha 1 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
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
            title="Valor Mensal"
            value={stats?.monthly_value}
            subtitle="Total ativo"
            icon={MoneyIcon}
            color="success"
            isCurrency={true}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Usuários Depto"
            value={stats?.department_users}
            subtitle="Membros da equipe"
            icon={PeopleIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Cards de Estatísticas - Linha 2 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Expirando 30 Dias"
            value={stats?.expiring_30_days}
            subtitle="Ação necessária"
            icon={WarningIcon}
            color="warning"
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

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Alertas"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} total`}
            icon={AlertIcon}
            color="error"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Aprovações"
            value={stats?.pending_approvals}
            subtitle="Aguardando"
            icon={ApprovalIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Gráficos */}
      <Grid container spacing={3}>
        {/* Gráfico de Status */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Contratos por Status
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
                <Typography variant="body2" color="text.secondary">Nenhum dado disponível</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Gráfico de Tipos */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Contratos por Tipo
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {typeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={typeData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="quantidade" fill="#2563EB" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">Nenhum dado disponível</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Informações Adicionais */}
        <Grid item xs={12}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Suas Permissões Administrativas
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Visualizar e editar todos contratos do departamento
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Aprovar contratos do departamento
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Acessar relatórios completos com valores financeiros
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Criar e gerenciar usuários do departamento
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Definir roles até nível 4
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ❌ Acessar outros departamentos (solicitar à Diretoria)
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
