/**
 * Dashboard STAFF (Level 1) - Dashboard für Mitarbeiter
 * 
 * Dashboard mais simples:
 * - 3 cards com estatísticas básicas
 * - Apenas contratos próprios
 * - SEM gráficos
 * - SEM valores financeiros
 * 
 * Einfachstes Dashboard:
 * - 3 Karten mit grundlegenden Statistiken
 * - Nur eigene Verträge
 * - KEINE Diagramme
 * - KEINE Finanzwerte
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
 * Componente de Card com Estatística
 * Statistikkarte-Komponente
 */
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

/**
 * Dashboard para STAFF (Level 1)
 * Dashboard für STAFF (Level 1)
 */
export default function DashboardStaff() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  /**
   * Buscar estatísticas do backend
   * Statistiken vom Backend abrufen
   */
  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await dashboardApi.getStats();
        setStats(data);
      } catch (err) {
        console.error('Erro ao carregar estatísticas:', err);
        setError('Erro ao carregar estatísticas do dashboard. Tente novamente mais tarde.');
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
      {/* Cabeçalho / Kopfzeile */}
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 600 }}>
        Meus Contratos
        <Typography component="span" variant="body1" color="text.secondary" sx={{ ml: 2 }}>
          Mitarbeiter Dashboard
        </Typography>
      </Typography>

      {/* Cards de Estatísticas / Statistikkarten */}
      <Grid container spacing={3}>
        {/* Total de Contratos */}
        <Grid item xs={12} md={4}>
          <StatCard
            title="Meus Contratos"
            value={stats?.total_contracts}
            subtitle="Total de contratos onde sou responsável"
            icon={ContractIcon}
            color="primary"
          />
        </Grid>

        {/* Contratos Expirando */}
        <Grid item xs={12} md={4}>
          <StatCard
            title="Expirando em 30 Dias"
            value={stats?.expiring_30_days}
            subtitle="Contratos que vencem em breve"
            icon={WarningIcon}
            color="warning"
          />
        </Grid>

        {/* Alertas */}
        <Grid item xs={12} md={4}>
          <StatCard
            title="Meus Alertas"
            value={stats?.unread_alerts}
            subtitle={`${stats?.total_alerts || 0} alertas no total`}
            icon={AlertIcon}
            color="info"
          />
        </Grid>
      </Grid>

      {/* Informação Adicional / Zusätzliche Informationen */}
      <Box sx={{ mt: 4 }}>
        <Card elevation={1}>
          <CardContent>
            <Typography variant="body2" color="text.secondary">
              <strong>Dica:</strong> Você tem acesso apenas aos contratos onde é responsável. 
              Para criar novos contratos ou acessar relatórios, solicite permissões ao seu gestor.
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              <strong>Tipp:</strong> Sie haben nur Zugriff auf Verträge, für die Sie verantwortlich sind.
              Um neue Verträge zu erstellen oder auf Berichte zuzugreifen, fordern Sie Berechtigungen von Ihrem Manager an.
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
}
