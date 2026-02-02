import { useState } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  Alert
} from '@mui/material';
import {
  CheckCircle as ApproveIcon,
  Cancel as RejectIcon
} from '@mui/icons-material';
import { approveContract, rejectContract } from '../../services/approvalsApi';
import { useNotification } from '../../hooks/useNotification';

/**
 * Componente para ações de aprovação (aprovar/rejeitar)
 * DE: Komponente für Genehmigungsaktionen (genehmigen/ablehnen)
 * PT: Componente para ações de aprovação (aprovar/rejeitar)
 */
const ApprovalActions = ({ contractId, contractTitle, onSuccess, compact = false }) => {
  const { showSuccess, showError } = useNotification();

  const [approveDialogOpen, setApproveDialogOpen] = useState(false);
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [comments, setComments] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Aprovar contrato
  const handleApprove = async () => {
    setSubmitting(true);
    try {
      await approveContract(contractId, { comments: comments || undefined });
      showSuccess('Vertrag genehmigt / Contrato aprovado');
      setApproveDialogOpen(false);
      setComments('');
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error('Error approving contract:', error);
      showError(
        error.response?.data?.detail || 
        'Fehler beim Genehmigen / Erro ao aprovar'
      );
    } finally {
      setSubmitting(false);
    }
  };

  // Rejeitar contrato
  const handleReject = async () => {
    if (!rejectionReason.trim()) {
      showError('Grund erforderlich / Motivo obrigatório');
      return;
    }

    setSubmitting(true);
    try {
      await rejectContract(contractId, {
        reason: rejectionReason,
        comments: comments || undefined
      });
      showSuccess('Vertrag abgelehnt / Contrato rejeitado');
      setRejectDialogOpen(false);
      setRejectionReason('');
      setComments('');
      if (onSuccess) onSuccess();
    } catch (error) {
      console.error('Error rejecting contract:', error);
      showError(
        error.response?.data?.detail || 
        'Fehler beim Ablehnen / Erro ao rejeitar'
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Box>
      {/* Botões de ação */}
      <Box display="flex" gap={1}>
        <Button
          variant="contained"
          color="success"
          startIcon={<ApproveIcon />}
          onClick={() => setApproveDialogOpen(true)}
          size={compact ? 'small' : 'medium'}
        >
          Genehmigen / Aprovar
        </Button>
        <Button
          variant="outlined"
          color="error"
          startIcon={<RejectIcon />}
          onClick={() => setRejectDialogOpen(true)}
          size={compact ? 'small' : 'medium'}
        >
          Ablehnen / Rejeitar
        </Button>
      </Box>

      {/* Dialog de Aprovação */}
      <Dialog
        open={approveDialogOpen}
        onClose={() => !submitting && setApproveDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Vertrag genehmigen / Aprovar Contrato
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Alert severity="success" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>{contractTitle}</strong>
              </Typography>
              <Typography variant="caption">
                Möchten Sie diesen Vertrag wirklich genehmigen?
                <br />
                Deseja realmente aprovar este contrato?
              </Typography>
            </Alert>

            <TextField
              fullWidth
              multiline
              rows={3}
              label="Kommentare / Comentários (optional)"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Optionale Anmerkungen zur Genehmigung / Observações opcionais sobre a aprovação"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setApproveDialogOpen(false)}
            disabled={submitting}
          >
            Abbrechen / Cancelar
          </Button>
          <Button
            onClick={handleApprove}
            variant="contained"
            color="success"
            disabled={submitting}
          >
            {submitting ? 'Genehmigen... / Aprovando...' : 'Genehmigen / Aprovar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de Rejeição */}
      <Dialog
        open={rejectDialogOpen}
        onClose={() => !submitting && setRejectDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Vertrag ablehnen / Rejeitar Contrato
        </DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Alert severity="error" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <strong>{contractTitle}</strong>
              </Typography>
              <Typography variant="caption">
                Möchten Sie diesen Vertrag wirklich ablehnen?
                <br />
                Deseja realmente rejeitar este contrato?
              </Typography>
            </Alert>

            <TextField
              fullWidth
              required
              label="Ablehnungsgrund / Motivo da Rejeição *"
              value={rejectionReason}
              onChange={(e) => setRejectionReason(e.target.value)}
              placeholder="Geben Sie den Grund für die Ablehnung an / Informe o motivo da rejeição"
              sx={{ mb: 2 }}
              error={!rejectionReason.trim() && rejectDialogOpen}
              helperText={!rejectionReason.trim() && rejectDialogOpen ? 'Grund erforderlich / Motivo obrigatório' : ''}
            />

            <TextField
              fullWidth
              multiline
              rows={3}
              label="Zusätzliche Kommentare / Comentários Adicionais (optional)"
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Optionale zusätzliche Anmerkungen / Observações adicionais opcionais"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button 
            onClick={() => setRejectDialogOpen(false)}
            disabled={submitting}
          >
            Abbrechen / Cancelar
          </Button>
          <Button
            onClick={handleReject}
            variant="contained"
            color="error"
            disabled={submitting || !rejectionReason.trim()}
          >
            {submitting ? 'Ablehnen... / Rejeitando...' : 'Ablehnen / Rejeitar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

ApprovalActions.propTypes = {
  contractId: PropTypes.number.isRequired,
  contractTitle: PropTypes.string.isRequired,
  onSuccess: PropTypes.func,
  compact: PropTypes.bool
};

export default ApprovalActions;
