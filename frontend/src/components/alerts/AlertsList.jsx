/**
 * Alerts List Component - VERSÃO COMPLETA
 * Komponente Warnungsliste
 * 
 * Tabela de alertas com paginação, ordenação e ações
 * Tabelle von Warnungen mit Paginierung, Sortierung und Aktionen
 * 
 * AÇÕES:
 * - Ver contrato (todos)
 * - Reprocessar (se failed)
 * - Edit (níveis 4 e 5)
 * - Delete (níveis 4 e 5)
 * - Aprovar contrato (níveis 4 e 5, se PENDING_APPROVAL)
 * - Rejeitar contrato (níveis 4 e 5, se PENDING_APPROVAL)
 */

import { useState, useEffect } from 'react';
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
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField
} from '@mui/material';
import VisibilityIcon from '@mui/icons-material/Visibility';
import ReplayIcon from '@mui/icons-material/Replay';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import { useSnackbar } from 'notistack';
import { useAuthStore } from '../../store/authStore';
import axios from 'axios';

// Interceptor global para enviar o token de autenticação
axios.interceptors.request.use(config => {
  // Busca o token dentro do objeto auth-storage
  const authStorage = localStorage.getItem('auth-storage');
  let token = null;
  if (authStorage) {
    try {
      const parsed = JSON.parse(authStorage);
      token = parsed.state?.token;
    } catch (e) {
      // ignora erro de parse
    }
  }
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
import {
  ALERT_TYPE_LABELS,
  ALERT_TYPE_COLORS,
  ALERT_STATUS_LABELS,
  ALERT_STATUS_COLORS
} from '../../utils/constants';
import alertsApi from '../../services/alertsApi';
import MenuItem from '@mui/material/MenuItem';



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
  const { user } = useAuthStore();
  
  const [reprocessing, setReprocessing] = useState(null);
  const [deleteDialog, setDeleteDialog] = useState({ open: false, alert: null });
  const [approvalDialog, setApprovalDialog] = useState({ open: false, type: null, alert: null });
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [editDialog, setEditDialog] = useState({ open: false, alert: null });
  const [editForm, setEditForm] = useState({ responsible_user_id: '', scheduled_for: '', status: '' });
  const [editSubmitting, setEditSubmitting] = useState(false);
  const [users, setUsers] = useState([]);

  // Buscar usuários ao abrir o modal de edição
  useEffect(() => {
    if (editDialog.open) {
      axios.get('/api/users/') // ajuste o endpoint conforme seu backend
        .then(res => setUsers(res.data))
        .catch(() => setUsers([]));
    }
  }, [editDialog.open]);

  // Verifica se usuário pode editar/deletar (níveis 4 e 5)
  const canManageAlerts = user && (user.access_level === 4 || user.access_level === 5);

  // Handler para abrir modal de edição
const handleEditAlert = (alert) => {
  setEditDialog({ open: true, alert });
  setEditForm({
    responsible_user_id: alert.responsible_user_id || '',
    scheduled_for: alert.scheduled_for ? alert.scheduled_for.slice(0, 10) : '',
    status: alert.status || '',
  });
};

const handleEditConfirm = async () => {
  if (!editDialog.alert) return;
  setEditSubmitting(true);
  try {
    await axios.put(`/api/alerts/${editDialog.alert.id}`, {
      responsible_user_id: editForm.responsible_user_id
        ? String(editForm.responsible_user_id)
        : null,
      scheduled_for: editForm.scheduled_for
        ? `${editForm.scheduled_for}T00:00:00`
        : null,
      status: editForm.status || null,
    });
    enqueueSnackbar('Warnung bearbeitet / Alerta editado', { variant: 'success' });
    setEditDialog({ open: false, alert: null });
    if (onAlertRead) onAlertRead();
  } catch (error) {
    enqueueSnackbar(
      error.response?.data?.detail || 'Fehler beim Bearbeiten / Erro ao editar alerta',
      { variant: 'error' }
    );
  } finally {
    setEditSubmitting(false);
  }
};

  /**
   * Reprocessar alerta falhado
   */
  const handleReprocess = async (alertId, event) => {
    event.stopPropagation();

    try {
      setReprocessing(alertId);
      await alertsApi.reprocessAlert(alertId);
      
      enqueueSnackbar('Warnung erneut verarbeitet / Alerta reprocessado', {
        variant: 'success'
      });

      if (onAlertRead) {
        onAlertRead();
      }
    } catch (error) {
      console.error('❌ Erro ao reprocessar alerta:', error);
      enqueueSnackbar(
        error.response?.data?.detail || 'Fehler beim Neuverarbeiten / Erro ao reprocessar',
        { variant: 'error' }
      );
    } finally {
      setReprocessing(null);
    }
  };

  /**
   * Deletar alerta
   */
  const handleDeleteConfirm = async () => {
    if (!deleteDialog.alert) return;

    try {
      await axios.delete(`/api/alerts/${deleteDialog.alert.id}`);
      
      enqueueSnackbar('Warnung gelöscht / Alerta deletado', {
        variant: 'success'
      });

      setDeleteDialog({ open: false, alert: null });
      
      if (onAlertRead) {
        onAlertRead();
      }
    } catch (error) {
      console.error('❌ Erro ao deletar alerta:', error);
      enqueueSnackbar(
        error.response?.data?.detail || 'Fehler beim Löschen / Erro ao deletar',
        { variant: 'error' }
      );
    }
  };

  /**
   * Aprovar alerta
   */
  const handleApprove = async () => {
    if (!approvalDialog.alert) return;
    try {
      setSubmitting(true);
      await axios.post(`/api/alerts/${approvalDialog.alert.id}/approve`, {
        comment: comment || undefined
      });
      enqueueSnackbar('Warnung genehmigt / Alerta aprovado', {
        variant: 'success'
      });
      setApprovalDialog({ open: false, type: null, alert: null });
      setComment('');
      if (onAlertRead) onAlertRead();
    } catch (error) {
      console.error('❌ Erro ao aprovar alerta:', error);
      enqueueSnackbar(
        error.response?.data?.detail || 'Fehler bei der Genehmigung / Erro ao aprovar alerta',
        { variant: 'error' }
      );
    } finally {
      setSubmitting(false);
    }
  };

  /**
   * Rejeitar alerta
   */
  const handleReject = async () => {
    if (!approvalDialog.alert) return;
    if (!comment.trim()) {
      enqueueSnackbar('Begründung erforderlich / Justificativa obrigatória', {
        variant: 'error'
      });
      return;
    }
    try {
      setSubmitting(true);
      await axios.post(`/api/alerts/${approvalDialog.alert.id}/reject`, {
        comment
      });
      enqueueSnackbar('Warnung abgelehnt / Alerta rejeitado', {
        variant: 'success'
      });
      setApprovalDialog({ open: false, type: null, alert: null });
      setComment('');
      if (onAlertRead) onAlertRead();
    } catch (error) {
      console.error('❌ Erro ao rejeitar alerta:', error);
      enqueueSnackbar(
        error.response?.data?.detail || 'Fehler bei der Ablehnung / Erro ao rejeitar alerta',
        { variant: 'error' }
      );
    } finally {
      setSubmitting(false);
    }
  };

  /**
   * Formata data
   */
  const formatDate = (dateString) => {
    if (!dateString) return '-';
    try {
      return format(new Date(dateString), 'dd.MM.yyyy');
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (!alerts || alerts.length === 0) {
    return (
      <Paper sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Keine Warnungen gefunden / Nenhum alerta encontrado
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
              <TableCell>Firmenname</TableCell>
              <TableCell>Erstellt</TableCell>
              <TableCell>Erstellt von</TableCell>
              <TableCell>Verantwortlicher</TableCell>
              <TableCell>Warnungen Data</TableCell>
              <TableCell align="center">Status</TableCell>
              <TableCell align="center">Aktionen / Ações</TableCell>
            </TableRow>
          </TableHead>

          <TableBody>

            {alerts.map((alert) => {
              const isPendingAlert = alert.status === 'pending';
              return (
                <TableRow key={alert.id} hover>
                  {/* Firmenname */}
                  <TableCell>
                    <Typography variant="body2">
                      {alert.company_name || '-'}
                    </Typography>
                  </TableCell>

                  {/* Erstellt (data de criação do alerta) */}
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(alert.created_at)}
                    </Typography>
                  </TableCell>

                  {/* Erstellt von (nome de quem criou o contrato) */}
                  <TableCell>
                    <Typography variant="body2">
                      {alert.created_by_name || '-'}
                    </Typography>
                  </TableCell>

                  {/* Verantwortlicher (responsável do contrato) */}
                  <TableCell>
                    <Typography variant="body2">
                      {alert.responsible_user_name || '-'}
                    </Typography>
                  </TableCell>

                  {/* Warnungen Data (data agendada do alerta) */}
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(alert.scheduled_for || alert.alert_date)}
                    </Typography>
                  </TableCell>

                  {/* Status */}
                  <TableCell align="center">
                    <Chip 
                      label={ALERT_STATUS_LABELS[alert.status] || alert.status}
                      color={ALERT_STATUS_COLORS[alert.status] || 'default'}
                      size="small"
                    />
                    {isPendingAlert && (
                      <Chip
                        label="PENDING"
                        color="warning"
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </TableCell>

                  {/* Ações */}
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center', flexWrap: 'wrap' }}>
                      {/* Ver Contrato (todos) */}
                      <Tooltip title="Vertrag anzeigen / Ver contrato">
                        <IconButton
                          size="small"
                          color="info"
                          onClick={() => navigate(`/app/contracts/${alert.contract_id}`)}
                        >
                          <VisibilityIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>

                      {/* Reprocessar (se failed) */}
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
                                <ReplayIcon fontSize="small" />
                              )}
                            </IconButton>
                          </span>
                        </Tooltip>
                      )}

                      {/* Editar (níveis 4 e 5) */}
                      {/* Botão de editar só aparece se a funcionalidade existir (exemplo: canEditAlert) */}
                      {canManageAlerts && (
                        <Tooltip title="Bearbeiten / Editar">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => handleEditAlert(alert)}
                            disabled={editSubmitting}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}

                      {/* Deletar (níveis 4 e 5) */}
                      {canManageAlerts && (
                        <Tooltip title="Löschen / Deletar">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => setDeleteDialog({ open: true, alert })}
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}

                      {/* Aprovar (níveis 4 e 5, se ALERTA pendente) */}
                      {canManageAlerts && isPendingAlert && (
                        <Tooltip title="Genehmigen / Aprovar">
                          <IconButton
                            size="small"
                            color="success"
                            onClick={() => setApprovalDialog({ 
                              open: true, 
                              type: 'approve', 
                              alert 
                            })}
                          >
                            <CheckCircleIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}

                      {/* Rejeitar (níveis 4 e 5, se ALERTA pendente) */}
                      {canManageAlerts && isPendingAlert && (
                        <Tooltip title="Ablehnen / Rejeitar">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => setApprovalDialog({ 
                              open: true, 
                              type: 'reject', 
                              alert 
                            })}
                          >
                            <CancelIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Paginação */}
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

       {/* Dialog de Edição de Alerta */}
      <Dialog
        open={editDialog.open}
        onClose={() => setEditDialog({ open: false, alert: null })}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Warnung bearbeiten / Editar alerta</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mt: 1 }}>
            <TextField
              select
              label="Verantwortlicher (User)"
              value={editForm.responsible_user_id}
              onChange={e => setEditForm({ ...editForm, responsible_user_id: e.target.value })}
              fullWidth
            >
              {users.map(user => (
                <MenuItem key={user.id} value={user.id}>
                  {user.name || user.username || user.email}
                </MenuItem>
              ))}
            </TextField>
            <TextField
              label="Geplant für / Agendado para"
              type="date"
              value={editForm.scheduled_for}
              onChange={e => setEditForm({ ...editForm, scheduled_for: e.target.value })}
              InputLabelProps={{ shrink: true }}
              fullWidth
            />
            <TextField
              label="Status"
              select
              value={editForm.status}
              onChange={e => setEditForm({ ...editForm, status: e.target.value })}
              fullWidth
            >
              {Object.entries(ALERT_STATUS_LABELS).map(([key, label]) => (
                <MenuItem key={key} value={key}>
                  {label}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog({ open: false, alert: null })} disabled={editSubmitting}>
            Abbrechen / Cancelar
          </Button>
          <Button
            onClick={handleEditConfirm}
            variant="contained"
            color="primary"
            disabled={editSubmitting}
          >
            {editSubmitting ? <CircularProgress size={20} /> : 'Speichern / Salvar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de Confirmação de Delete */}
      <Dialog
        open={deleteDialog.open}
        onClose={() => setDeleteDialog({ open: false, alert: null })}
      >
        <DialogTitle>Warnung löschen / Deletar alerta</DialogTitle>
        <DialogContent>
          <Typography>
            Möchten Sie diese Warnung wirklich löschen?<br />
            Tem certeza que deseja deletar este alerta?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog({ open: false, alert: null })}>
            Abbrechen / Cancelar
          </Button>
          <Button onClick={handleDeleteConfirm} color="error" variant="contained">
            Löschen / Deletar
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de Aprovação/Rejeição de ALERTA */}
      <Dialog
        open={approvalDialog.open}
        onClose={() => {
          setApprovalDialog({ open: false, type: null, alert: null });
          setComment('');
        }}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          {approvalDialog.type === 'approve'
            ? 'Warnung genehmigen / Aprovar Alerta'
            : 'Warnung ablehnen / Rejeitar Alerta'}
        </DialogTitle>

        <DialogContent>
          {approvalDialog.alert && (
            <>
              <Typography variant="body2" gutterBottom>
                <strong>Alerta:</strong> {ALERT_TYPE_LABELS[approvalDialog.alert.alert_type] || approvalDialog.alert.alert_type}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Contrato:</strong> {approvalDialog.alert.contract?.title || approvalDialog.alert.contract_id}
              </Typography>
              <Typography variant="body2" gutterBottom>
                <strong>Data:</strong> {formatDate(approvalDialog.alert.scheduled_for || approvalDialog.alert.alert_date)}
              </Typography>

              <TextField
                fullWidth
                multiline
                rows={4}
                label={
                  approvalDialog.type === 'approve'
                    ? 'Kommentar (optional) / Comentário (opcional)'
                    : 'Begründung (erforderlich) / Justificativa (obrigatória) *'
                }
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                sx={{ mt: 2 }}
                required={approvalDialog.type === 'reject'}
              />
            </>
          )}
        </DialogContent>

        <DialogActions>
          <Button
            onClick={() => {
              setApprovalDialog({ open: false, type: null, alert: null });
              setComment('');
            }}
            disabled={submitting}
          >
            Abbrechen / Cancelar
          </Button>
          <Button
            onClick={approvalDialog.type === 'approve' ? handleApprove : handleReject}
            variant="contained"
            color={approvalDialog.type === 'approve' ? 'success' : 'error'}
            disabled={submitting}
          >
            {submitting ? (
              <CircularProgress size={20} />
            ) : approvalDialog.type === 'approve' ? (
              'Genehmigen / Aprovar'
            ) : (
              'Ablehnen / Rejeitar'
            )}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default AlertsList;
