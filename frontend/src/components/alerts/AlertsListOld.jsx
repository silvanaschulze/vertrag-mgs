/**
 * Alerts List Component
 * Komponente Warnungsliste
 * 
 * Tabela de alertas com paginação, ordenação e ações
 * Tabelle von Warnungen mit Paginierung, Sortierung und Aktionen
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import {
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Chip,
  Tooltip,
  Box,
  Typography,
  CircularProgress
} from '@mui/material';
import CircleIcon from '@mui/icons-material/Circle';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ReplayIcon from '@mui/icons-material/Replay';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { useSnackbar } from 'notistack';
import { useAuthStore } from '../../store/authStore';
import axios from 'axios';
import {
  ALERT_TYPE_LABELS,
  ALERT_TYPE_COLORS,
  ALERT_STATUS_LABELS,
  ALERT_STATUS_COLORS
} from '../../utils/constants';
import alertsApi from '../../services/alertsApi';

/**
 * AlertsList Component
 * 
 * @param {Object} props
 * @param {Array} props.alerts - Lista de alertas
 * @param {number} props.total - Total de registros
 * @param {number} props.page - Página atual (0-based para MUI)
 * @param {number} props.pageSize - Itens por página
 * @param {boolean} props.loading - Estado de carregamento
 * @param {Function} props.onPageChange - Callback mudança de página
 * @param {Function} props.onPageSizeChange - Callback mudança de tamanho
 * @param {Function} props.onAlertRead - Callback quando marcar como lido
 */
const AlertsList = ({
  alerts,
  total,
  page,
  pageSize,
  loading,
  onPageChange,
  onPageSizeChange,
  onAlertRead
}) => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [reprocessing, setReprocessing] = useState(null);

  /**
   * Reprocessar alerta falhado
   * Fehlgeschlagene Warnung erneut verarbeiten
   */
  const handleReprocess = async (alertId, event) => {
    event.stopPropagation();

    try {
      setReprocessing(alertId);
      console.log(`🔄 Reprocessando alerta ${alertId}`);
      
      await alertsApi.reprocessAlert(alertId);
      
      enqueueSnackbar('Warnung erneut verarbeitet / Alerta reprocessado', {
        variant: 'success'
      });

      // Notifica pai para atualizar lista
      if (onAlertRead) {
        onAlertRead();
      }
    } catch (error) {
      console.error('❌ Erro ao reprocessar alerta:', error);
      enqueueSnackbar(
        error.response?.data?.detail || 
        'Fehler beim Neuverarbeiten / Erro ao reprocessar',
        { variant: 'error' }
      );
    } finally {
      setReprocessing(null);
    }
  };

  /**
   * Navegar para visualização do contrato
   * Zur Vertragsansicht navigieren
   */
  const handleViewContract = (contractId) => {
    navigate(`/app/contracts/${contractId}`);
  };

  /**
   * Formata data para exibição
   * Datum für Anzeige formatieren
   */
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    try {
      return format(new Date(dateString), 'dd.MM.yyyy');
    } catch {
      return dateString;
    }
  };

  /**
   * Renderiza mensagem vazia
   * Leere Nachricht rendern
   */
  if (!loading && alerts.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h6" color="text.secondary">
          Keine Warnungen gefunden / Nenhum alerta encontrado
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
          Es gibt keine Warnungen mit den ausgewählten Filtern /
          Não há alertas com os filtros selecionados
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper>
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Typ / Tipo</TableCell>
              <TableCell>Vertrag / Contrato</TableCell>
              <TableCell>Datum / Data</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="center">Aktionen / Ações</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            ) : (
              alerts.map((alert) => (
                <TableRow
                  key={alert.id}
                  hover
                  sx={{
                    backgroundColor: alert.status === 'pending' ? 'action.hover' : 'inherit',
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: alert.status === 'pending' 
                        ? 'action.selected' 
                        : 'action.hover'
                    }
                  }}
                  onClick={(e) => handleViewContract(alert.contract_id, alert.id, e)}
                >
                  {/* ID */}
                  <TableCell>
                    <Typography
                      variant="body2"
                      fontWeight={alert.status === 'pending' ? 'bold' : 'normal'}
                    >
                      #{alert.id}
                    </Typography>
                  </TableCell>

                  {/* Tipo / Typ */}
                  <TableCell>
                    <Chip
                      label={ALERT_TYPE_LABELS[alert.alert_type] || alert.alert_type}
                      color={ALERT_TYPE_COLORS[alert.alert_type] || 'default'}
                      size="small"
                    />
                  </TableCell>

                  {/* Título do Contrato / Vertragstitel */}
                  <TableCell>
                    <Typography
                      variant="body2"
                      fontWeight={alert.status === 'pending' ? 'bold' : 'normal'}
                    >
                      {alert.contract?.title || 'N/A'}
                    </Typography>
                    {alert.contract?.partner_name && (
                      <Typography variant="caption" color="text.secondary">
                        {alert.contract.partner_name}
                      </Typography>
                    )}
                  </TableCell>

                  {/* Data do Alerta / Datum der Warnung */}
                  <TableCell>
                    <Typography
                      variant="body2"
                      fontWeight={alert.status === 'pending' ? 'bold' : 'normal'}
                    >
                      {formatDate(alert.scheduled_for || alert.alert_date)}
                    </Typography>
                  </TableCell>

                  {/* Status / Status */}
                  <TableCell align="center">
                    <Chip 
                      label={ALERT_STATUS_LABELS[alert.status] || alert.status}
                      color={ALERT_STATUS_COLORS[alert.status] || 'default'}
                      size="small"
                    />
                  </TableCell>

                  {/* Ações / Aktionen */}
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                      {/* Botão Reprocessar - apenas para failed */}
                      {alert.status === 'failed' && (
                        <Tooltip title="Erneut verarbeiten / Reprocessar">
                          <span>
                            <IconButton
                              size="small"
                              color="warning"
                              onClick={(e) => handleReprocess(alert.id, e)}
                              disabled={reprocessing === alert.id}
                            >
                              {reprocessing === alert.id ? (
                                <CircularProgress size={20} />
                              ) : (
                                <ReplayIcon />
                              )}
                            </IconButton>
                          </span>
                        </Tooltip>
                      )}

                      {/* Botão Ver Contrato */}
                      <Tooltip title="Vertrag anzeigen / Ver contrato">
                        <IconButton
                          size="small"
                          color="info"
                          onClick={(e) => {
                            e.stopPropagation();
                            navigate(`/app/contracts/${alert.contract_id}`);
                          }}
                        >
                          <VisibilityIcon />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Paginação / Paginierung */}
      <TablePagination
        component="div"
        count={total}
        page={page}
        onPageChange={(e, newPage) => onPageChange(newPage)}
        rowsPerPage={pageSize}
        onRowsPerPageChange={(e) => onPageSizeChange(parseInt(e.target.value, 10))}
        rowsPerPageOptions={[10, 25, 50, 100]}
        labelRowsPerPage="Zeilen pro Seite / Linhas por página:"
        labelDisplayedRows={({ from, to, count }) =>
          `${from}-${to} von / de ${count !== -1 ? count : `mehr als / mais de ${to}`}`
        }
      />
    </Paper>
  );
};

export default AlertsList;
