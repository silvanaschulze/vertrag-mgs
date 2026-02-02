import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  Paper
} from '@mui/material';
import { format, parseISO } from 'date-fns';
import { de } from 'date-fns/locale';
import { getContractApprovals } from '../../services/approvalsApi';
import { APPROVAL_STATUS_LABELS, APPROVAL_STATUS_COLORS } from '../../utils/constants';
import { useNotification } from '../../hooks/useNotification';
import ApprovalActions from './ApprovalActions';

/**
 * Lista de aprovações de um contrato
 * DE: Liste der Genehmigungen eines Vertrags
 * PT: Lista de aprovações de um contrato
 */
const ContractApprovals = ({ contractId, contractTitle, contractStatus, onApprovalChange }) => {
  const { showError } = useNotification();

  const [approvals, setApprovals] = useState([]);
  const [loading, setLoading] = useState(true);

  // Verifica se contrato está pendente de aprovação
  const isPendingApproval = contractStatus === 'PENDING_APPROVAL';

  // Carregar aprovações
  const loadApprovals = async () => {
    try {
      setLoading(true);
      const data = await getContractApprovals(contractId);
      // Backend retorna { approvals: [...], total_approvals: ..., ... }
      setApprovals(data?.approvals || []);
    } catch (error) {
      console.error('Error loading approvals:', error);
      // Não mostrar erro se endpoint não existir (404)
      if (error.response?.status !== 404) {
        showError('Fehler beim Laden der Genehmigungen / Erro ao carregar aprovações');
      }
      setApprovals([]); // Garantir que approvals é sempre um array
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (contractId) {
      loadApprovals();
    }
  }, [contractId]);

  // Callback após aprovação/rejeição
  const handleApprovalSuccess = () => {
    loadApprovals();
    if (onApprovalChange) onApprovalChange();
  };

  // Formatar data/hora
  const formatDateTime = (dateStr) => {
    if (!dateStr) return '-';
    try {
      return format(parseISO(dateStr), 'dd.MM.yyyy HH:mm', { locale: de });
    } catch {
      return dateStr;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent>
          <Typography>Lade Genehmigungen... / Carregando aprovações...</Typography>
        </CardContent>
      </Card>
    );
  }

  return (
    <Box>
      {/* Cabeçalho */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h6" gutterBottom>
            Genehmigungen / Aprovações
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Genehmigungs-Historie für diesen Vertrag / Histórico de aprovações para este contrato
          </Typography>
        </Box>
      </Box>

      {/* Ações de aprovação (se pendente) */}
      {isPendingApproval && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="body2" gutterBottom>
            <strong>Genehmigung ausstehend / Aprovação Pendente</strong>
          </Typography>
          <Typography variant="caption" display="block" gutterBottom>
            Dieser Vertrag wartet auf Genehmigung. / Este contrato aguarda aprovação.
          </Typography>
          <Box sx={{ mt: 2 }}>
            <ApprovalActions
              contractId={contractId}
              contractTitle={contractTitle}
              onSuccess={handleApprovalSuccess}
              compact
            />
          </Box>
        </Alert>
      )}

      {/* Tabela de aprovações */}
      {approvals.length === 0 ? (
        <Alert severity="info">
          Keine Genehmigungen vorhanden. / Nenhuma aprovação registrada.
        </Alert>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Genehmiger / Aprovador</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Datum / Data</TableCell>
                <TableCell>Kommentare / Comentários</TableCell>
                <TableCell>Ablehnungsgrund / Motivo da Rejeição</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {approvals.map((approval) => (
                <TableRow key={approval.id}>
                  {/* Aprovador */}
                  <TableCell>
                    <Typography variant="body2">
                      {approval.approver_name || `User #${approval.approver_id}`}
                    </Typography>
                    <Typography variant="caption" color="textSecondary">
                      Level: {approval.required_approval_level || '-'}
                    </Typography>
                  </TableCell>

                  {/* Status */}
                  <TableCell>
                    <Chip
                      label={APPROVAL_STATUS_LABELS[approval.status] || approval.status}
                      color={APPROVAL_STATUS_COLORS[approval.status] || 'default'}
                      size="small"
                    />
                  </TableCell>

                  {/* Data */}
                  <TableCell>
                    {approval.status === 'approved' && (
                      <Typography variant="body2">
                        {formatDateTime(approval.approved_at)}
                      </Typography>
                    )}
                    {approval.status === 'rejected' && (
                      <Typography variant="body2">
                        {formatDateTime(approval.rejected_at)}
                      </Typography>
                    )}
                    {approval.status === 'pending' && (
                      <Typography variant="caption" color="textSecondary">
                        Erstellt: {formatDateTime(approval.created_at)}
                      </Typography>
                    )}
                  </TableCell>

                  {/* Comentários */}
                  <TableCell>
                    <Typography variant="body2">
                      {approval.comments || '-'}
                    </Typography>
                  </TableCell>

                  {/* Motivo da rejeição */}
                  <TableCell>
                    {approval.rejection_reason && (
                      <Typography variant="body2" color="error">
                        {approval.rejection_reason}
                      </Typography>
                    )}
                    {!approval.rejection_reason && '-'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

ContractApprovals.propTypes = {
  contractId: PropTypes.number.isRequired,
  contractTitle: PropTypes.string.isRequired,
  contractStatus: PropTypes.string.isRequired,
  onApprovalChange: PropTypes.func
};

export default ContractApprovals;
