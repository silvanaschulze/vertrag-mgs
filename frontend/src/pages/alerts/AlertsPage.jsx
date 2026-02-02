/**
 * Alerts Page
 * Seite für Warnungen
 * 
 * Página principal de alertas com listagem, filtros e ações
 * Hauptseite für Warnungen mit Auflistung, Filtern und Aktionen
 */

import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Paper,
  Alert as MuiAlert
} from '@mui/material';
import NotificationsIcon from '@mui/icons-material/Notifications';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useSnackbar } from 'notistack';
import AlertsList from '../../components/alerts/AlertsList';
import AlertFilters from '../../components/alerts/AlertFilters';
import alertsApi from '../../services/alertsApi';
import { ALERT_STATUS } from '../../utils/constants';

/**
 * AlertsPage Component
 * Página de Alertas
 */
const AlertsPage = () => {
  const { enqueueSnackbar } = useSnackbar();

  // Estados / Zustände
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [unreadCount, setUnreadCount] = useState(0);

  // Filtros / Filter
  const [filters, setFilters] = useState({
    alert_type: '',
    status: ALERT_STATUS.ALL,
    search: ''
  });

  // Paginação / Paginierung
  const [page, setPage] = useState(0); // MUI usa 0-based
  const [pageSize, setPageSize] = useState(25);
  const [totalRows, setTotalRows] = useState(0);

  /**
   * Carrega alertas do backend
   * Warnungen vom Backend laden
   */
  const loadAlerts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('📤 Carregando alertas com filtros:', filters, 'página:', page + 1);

      // Mapeia filtros para API
      const apiFilters = {};
      
      if (filters.alert_type) {
        apiFilters.alert_type = filters.alert_type;
      }

      if (filters.status && filters.status !== ALERT_STATUS.ALL) {
        apiFilters.status = filters.status;
      }

      if (filters.search) {
        apiFilters.search = filters.search;
      }

      const response = await alertsApi.getAlerts(
        apiFilters,
        page + 1, // Backend usa 1-based
        pageSize
      );

      console.log('📥 Alertas carregados:', response);

      setAlerts(response.items || []);
      setTotalRows(response.total || 0);
      
    } catch (err) {
      console.error('❌ Erro ao carregar alertas:', err);
      setError(err.response?.data?.detail || 'Erro ao carregar alertas');
      enqueueSnackbar(
        'Fehler beim Laden der Warnungen / Erro ao carregar alertas',
        { variant: 'error' }
      );
    } finally {
      setLoading(false);
    }
  }, [filters, page, pageSize, enqueueSnackbar]);

  /**
   * Carrega contagem de não lidos
   * Anzahl ungelesener laden
   */
  const loadUnreadCount = useCallback(async () => {
    try {
      const count = await alertsApi.getUnreadCount();
      setUnreadCount(count);
    } catch (err) {
      console.error('❌ Erro ao carregar contagem de não lidos:', err);
    }
  }, []);

  /**
   * Efeito inicial - carrega alertas e contador
   * Anfangseffekt - Warnungen und Zähler laden
   */
  useEffect(() => {
    loadAlerts();
    loadUnreadCount();
  }, [loadAlerts, loadUnreadCount]);

  /**
   * Polling para atualizar contador de não lidos a cada 30s
   * Polling zum Aktualisieren des Zählers alle 30s
   */
  useEffect(() => {
    const interval = setInterval(() => {
      loadUnreadCount();
    }, 30000); // 30 segundos

    return () => clearInterval(interval);
  }, [loadUnreadCount]);

  /**
   * Handler quando filtros mudam
   * Handler wenn Filter sich ändern
   */
  const handleFilterChange = (newFilters) => {
    console.log('🔄 Filtros alterados:', newFilters);
    setFilters(newFilters);
    setPage(0); // Volta para primeira página
  };

  /**
   * Limpar todos os filtros
   * Alle Filter löschen
   */
  const handleClearFilters = () => {
    console.log('🧹 Limpando filtros');
    setFilters({
      alert_type: '',
      status: ALERT_STATUS.ALL,
      search: ''
    });
    setPage(0);
  };

  /**
   * Mudança de página
   * Seitenwechsel
   */
  const handlePageChange = (newPage) => {
    console.log('📄 Mudando para página:', newPage + 1);
    setPage(newPage);
  };

  /**
   * Mudança de tamanho de página
   * Änderung der Seitengröße
   */
  const handlePageSizeChange = (newSize) => {
    console.log('📏 Mudando tamanho de página para:', newSize);
    setPageSize(newSize);
    setPage(0); // Volta para primeira página
  };

  /**
   * Callback quando alerta é atualizado
   * Callback wenn Warnung aktualisiert wird
   */
  const handleAlertRead = () => {
    console.log('✅ Alerta atualizado, recarregando lista');
    loadAlerts();
    loadUnreadCount();
  };

  /**
   * Processar todos os alertas pendentes
   * Alle ausstehenden Warnungen verarbeiten
   */
  const handleProcessAlerts = async () => {
    try {
      setLoading(true);
      console.log('🔄 Processando todos os alertas');
      
      const result = await alertsApi.processAllAlerts();
      
      enqueueSnackbar(
        `${result.total_processed} Warnungen verarbeitet / alertas processados`,
        { variant: 'success' }
      );

      // Recarregar lista de alertas
      loadAlerts();
      loadUnreadCount();
    } catch (err) {
      console.error('❌ Erro ao processar alertas:', err);
      enqueueSnackbar(
        'Fehler beim Verarbeiten / Erro ao processar alertas',
        { variant: 'error' }
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header / Kopfzeile */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <NotificationsIcon fontSize="large" color="primary" />
          <div>
            <Typography variant="h4" component="h1">
              Warnungen / Alertas
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Verwaltung von Vertragswarnungen / Gerenciamento de alertas de contratos
            </Typography>
          </div>
        </Box>

        {/* Botões de Ação / Aktionsschaltflächen */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          {/* Botão Processar Alertas */}
          <Button
            variant="contained"
            color="primary"
            startIcon={<RefreshIcon />}
            onClick={handleProcessAlerts}
            disabled={loading}
          >
            Warnungen verarbeiten / Processar Alertas
          </Button>
        </Box>
      </Box>

      {/* Badge de Alertas Não Lidos */}
      {unreadCount > 0 && (
        <MuiAlert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body2">
            <strong>{unreadCount}</strong> ungelesene Warnung(en) / alerta(s) não lido(s)
          </Typography>
        </MuiAlert>
      )}

      {/* Mensagem de Erro */}
      {error && (
        <MuiAlert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </MuiAlert>
      )}

      {/* Filtros / Filter */}
      <AlertFilters
        filters={filters}
        onFilterChange={handleFilterChange}
        onClearFilters={handleClearFilters}
      />

      {/* Informações de Paginação */}
      <Paper sx={{ p: 2, mb: 2, backgroundColor: 'background.default' }}>
        <Typography variant="body2" color="text.secondary">
          {totalRows} Warnung(en) gefunden / alerta(s) encontrado(s)
        </Typography>
      </Paper>

      {/* Lista de Alertas / Warnungsliste */}
      <AlertsList
        alerts={alerts}
        total={totalRows}
        page={page}
        pageSize={pageSize}
        loading={loading}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
        onAlertRead={handleAlertRead}
      />
    </Container>
  );
};

export default AlertsPage;
