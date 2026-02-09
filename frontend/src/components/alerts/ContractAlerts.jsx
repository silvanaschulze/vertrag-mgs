/**
 * Contract Alerts Component
 * Komponente Vertragsalarme
 * 
 * Lista de alertas relacionados a um contrato específico
 * Liste der Warnungen im Zusammenhang mit einem bestimmten Vertrag
 */

import { useState, useEffect } from 'react';
import { useAuthStore } from '../../store/authStore';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Button
} from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import alertsApi from '../../services/alertsApi';
import CustomAlertForm from './CustomAlertForm';
import {
  ALERT_TYPE_LABELS,
  ALERT_TYPE_COLORS,
  ALERT_STATUS_LABELS,
  ALERT_STATUS_COLORS
} from '../../utils/constants';

/**
 * ContractAlerts Component
 * 
 * @param {Object} props
 * @param {number} props.contractId - ID do contrato
 * @param {string} props.contractTitle - Título do contrato
 */
const ContractAlerts = ({ contractId, contractTitle }) => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [customAlertFormOpen, setCustomAlertFormOpen] = useState(false);
  const userLevel = useAuthStore((state) => state.getUserLevel());
  const [deletingId, setDeletingId] = useState(null);
  // Handler para deletar alerta
  const handleDelete = async (alertId) => {
    if (!window.confirm('Deseja realmente excluir este alerta?')) return;
    setDeletingId(alertId);
    try {
      await alertsApi.deleteAlert(alertId);
      setAlerts((prev) => prev.filter((a) => a.id !== alertId));
    } catch (err) {
      alert('Erro ao excluir alerta');
    } finally {
      setDeletingId(null);
    }
  };

  /**
   * Carrega alertas do contrato
   * Vertragswarnungen laden
   */
  const loadAlerts = async () => {
    if (!contractId) return;

    try {
      setLoading(true);
      console.log(`📤 Carregando alertas do contrato ${contractId}`);
      
      const response = await alertsApi.getAlerts(
        { contract_id: contractId },
        1,
        100 // Pega todos os alertas do contrato
      );

      setAlerts(response.items || []);
    } catch (err) {
      console.error('❌ Erro ao carregar alertas do contrato:', err);
      setError(err.response?.data?.detail || 'Erro ao carregar alertas');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, [contractId]);

  /**
   * Formata data para exibição
   * Datum für Anzeige formatieren
   */
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    try {
      return format(new Date(dateString), 'dd.MM.yyyy HH:mm');
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress size={30} />
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Warnungen laden... / Carregando alertas...
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          Warnungen / Alertas ({alerts.length})
        </Typography>
        <Button
          variant="outlined"
          size="small"
          startIcon={<AddIcon />}
          onClick={() => setCustomAlertFormOpen(true)}
        >
          Benutzerdefiniert / Customizado
        </Button>
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Box sx={{ p: 3 }}>
          <Typography variant="body2" color="error">
            {error}
          </Typography>
        </Box>
      ) : alerts.length === 0 ? (
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Keine Warnungen für diesen Vertrag / Nenhum alerta para este contrato
          </Typography>
        </Box>
      ) : (
        <TableContainer>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Verantwortlicher</TableCell>
                <TableCell>Datum / Data</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Erstellt / Criado</TableCell>
                {userLevel >= 4 && (
                  <TableCell align="right">Aktionen</TableCell>
                )}
              </TableRow>
            </TableHead>

            <TableBody>
              {alerts.map((alert) => (
                <TableRow key={alert.id}>
                  {/* Verantwortlicher (usuário responsável) */}
                  <TableCell>
                    <Typography variant="body2">
                      {alert.responsible_user_name || alert.responsible_user || '-'}
                    </Typography>
                  </TableCell>

                  {/* Data Agendada / Geplantes Datum */}
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(alert.scheduled_for)}
                    </Typography>
                  </TableCell>

                  {/* Status */}
                  <TableCell>
                    <Chip
                      label={ALERT_STATUS_LABELS[alert.status] || alert.status}
                      color={ALERT_STATUS_COLORS[alert.status] || 'default'}
                      size="small"
                    />
                  </TableCell>

                  {/* Criado / Erstellt */}
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {formatDate(alert.created_at)}
                    </Typography>
                  </TableCell>
                  {userLevel >= 4 && (
                    <TableCell align="right">
                      {/* Botão Editar pode ser implementado aqui */}
                      {/* <Button size="small" variant="outlined" color="primary" sx={{ mr: 1 }} disabled>Editar</Button> */}
                      <Button
                        size="small"
                        variant="outlined"
                        color="error"
                        onClick={() => handleDelete(alert.id)}
                        disabled={deletingId === alert.id}
                      >
                        {deletingId === alert.id ? 'Excluindo...' : 'Löschen'}
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Form de alerta customizado */}
      <CustomAlertForm
        open={customAlertFormOpen}
        onClose={() => setCustomAlertFormOpen(false)}
        contractId={contractId}
        contractTitle={contractTitle || `Contrato #${contractId}`}
        onSuccess={() => {
          setCustomAlertFormOpen(false);
          // Recarregar alertas
          loadAlerts();
        }}
      />
    </Paper>
  );
};

export default ContractAlerts;
