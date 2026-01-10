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
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
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
        quantidade: count
      }))
    : [];

  const departmentData = stats?.contracts_by_department
    ? Object.entries(stats.contracts_by_department).map(([dept, count]) => ({
        departamento: dept,
        contratos: count
      }))
    : [];

  return (
    <Box sx={{ p: 3 }}>
      {/* Cabeçalho Executivo */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 0.5, fontWeight: 600 }}>
            Executive Dashboard
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Unternehmensübersicht • Company Overview
          </Typography>
        </Box>
        <Chip 
          label="Director" 
          color="primary" 
          icon={<BusinessIcon />}
        />
      </Box>

      {/* KPIs Principais - Linha 1 */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Verträge Gesamt"
            value={stats?.total_contracts}
            subtitle="Im gesamten Unternehmen"
            icon={ContractIcon}
            color="primary"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Aktive Verträge"
            value={stats?.active_contracts}
            subtitle="Laufend"
            icon={TrendIcon}
            color="success"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Monatswert Gesamt"
            value={stats?.monthly_value}
            subtitle="Wiederkehrende Einnahmen"
            icon={MoneyIcon}
            color="success"
            isCurrency={true}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Benutzer Gesamt"
            value={stats?.total_users}
            subtitle="Auf der Plattform"
            icon={PeopleIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* KPIs Secundários - Linha 2 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Ablauf 30 Tage"
            value={stats?.expiring_30_days}
            subtitle="Sofortige Aufmerksamkeit"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Ablauf 90 Tage"
            value={stats?.expiring_90_days}
            subtitle="Planung"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Offene Warnungen"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} gesamt`}
            icon={AlertIcon}
            color="error"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Genehmigungen"
            value={stats?.pending_approvals}
            subtitle="Warten auf Entscheidung"
            icon={ApprovalIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Gráficos Executivos */}
      <Grid container spacing={3}>
        {/* Contratos por Departamento */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Verträge nach Abteilung
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {departmentData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={departmentData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="departamento" angle={-15} textAnchor="end" height={80} />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="contratos" fill="#2563EB" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">Keine Daten verfügbar</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Contratos por Status */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Verteilung nach Status
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
                <Typography variant="body2" color="text.secondary">Keine Daten verfügbar</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Contratos por Tipo */}
        <Grid item xs={12} md={6}>
          <Card elevation={3}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Vertragstypen
              </Typography>
              <Divider sx={{ mb: 2 }} />
              {typeData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={typeData} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={100} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="quantidade" fill="#10B981" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary">Keine Daten verfügbar</Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Permissões e Informações */}
        <Grid item xs={12} md={6}>
          <Card elevation={1}>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                Vollständiger Executive-Zugriff
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={1}>
                <Grid item xs={12}>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Alle Verträge des Unternehmens einsehen
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Strategische Verträge genehmigen
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Alle Berichte mit Finanzwerten einsehen
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Benutzer und Rollen in allen Bereichen verwalten
                  </Typography>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    ✅ Alle Zugriffsebenen definieren (1-5)
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
