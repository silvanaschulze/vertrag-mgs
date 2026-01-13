/**
 * ContractView - Página de Visualização de Contrato
 * Vertragsansichtsseite
 * 
 * Página para visualizar detalhes de um contrato
 * Seite zur Anzeige von Vertragsdetails
 */
import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Breadcrumbs,
  Link as MuiLink,
  Alert,
  CircularProgress,
  Button,
  ButtonGroup
} from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import {
  NavigateNext as NavigateNextIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ArrowBack as ArrowBackIcon
} from '@mui/icons-material';
import ContractDetail from '../../components/contracts/ContractDetail';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import contractsApi from '../../services/contractsApi';
import { useAuthStore } from '../../store/authStore';

const ContractView = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const user = useAuthStore((state) => state.user);

  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);

  /**
   * Verifica se pode editar contrato
   * Prüft, ob Vertrag bearbeitet werden kann
   */
  const canEdit = useCallback(() => {
    if (!user || !contract) return false;

    if (user.role === 'READ_ONLY') return false;
    if (user.access_level >= 5) return true;
    if (user.access_level >= 4) return contract.department === user.department;
    if (user.access_level >= 3) return contract.department === user.department;
    if (user.access_level >= 2) {
      return (contract.team === user.team) || (contract.created_by === user.id);
    }

    return false;
  }, [user, contract]);

  /**
   * Verifica se pode deletar contrato
   * Prüft, ob Vertrag gelöscht werden kann
   */
  const canDelete = useCallback(() => {
    if (!user || !contract) return false;

    if (user.access_level >= 5) return true;
    if (user.access_level >= 4 && user.role === 'DEPARTMENT_ADM') {
      return contract.department === user.department;
    }

    return false;
  }, [user, contract]);

  /**
   * Carrega contrato
   * Lädt Vertrag
   */
  useEffect(() => {
    const loadContract = async () => {
      try {
        const data = await contractsApi.getContract(id);
        setContract(data);
        setError(null);
      } catch (err) {
        console.error('Error loading contract:', err);
        const errorMessage = err.response?.data?.detail || 'Failed to load contract';
        setError(errorMessage);
        enqueueSnackbar(errorMessage, { variant: 'error' });
      } finally {
        setLoading(false);
      }
    };

    loadContract();
  }, [id, enqueueSnackbar]);

  const handleEdit = () => {
    navigate(`/app/contracts/${id}/edit`);
  };

  const handleDeleteClick = () => {
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    setDeleting(true);
    try {
      await contractsApi.deleteContract(id);
      enqueueSnackbar('Contract deleted successfully', { variant: 'success' });
      navigate('/app/contracts');
    } catch (err) {
      console.error('Error deleting contract:', err);
      const errorMessage = err.response?.data?.detail || 'Failed to delete contract';
      enqueueSnackbar(errorMessage, { variant: 'error' });
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
  };

  const handleBack = () => {
    navigate('/app/contracts');
  };

  if (loading) {
    return (
      <Box sx={{ p: 3, display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error || !contract) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || 'Contract not found'}
        </Alert>
        <Button variant="outlined" startIcon={<ArrowBackIcon />} onClick={handleBack}>
          Zurück / Back
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Breadcrumb */}
      <Breadcrumbs separator={<NavigateNextIcon fontSize="small" />} sx={{ mb: 2 }}>
        <MuiLink
          component="button"
          variant="body1"
          onClick={handleBack}
          sx={{ cursor: 'pointer' }}
        >
          Verträge / Contracts
        </MuiLink>
        <Typography color="text.primary">{contract.title}</Typography>
      </Breadcrumbs>

      {/* Header com ações / Header mit Aktionen */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Vertragsdetails
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Contract Details
          </Typography>
        </Box>

        <ButtonGroup variant="outlined">
          <Button startIcon={<ArrowBackIcon />} onClick={handleBack}>
            Zurück / Back
          </Button>
          {canEdit() && (
            <Button startIcon={<EditIcon />} onClick={handleEdit}>
              Bearbeiten / Edit
            </Button>
          )}
          {canDelete() && (
            <Button color="error" startIcon={<DeleteIcon />} onClick={handleDeleteClick}>
              Löschen / Delete
            </Button>
          )}
        </ButtonGroup>
      </Box>

      {/* Detalhes do Contrato / Vertragsdetails */}
      <ContractDetail contract={contract} />

      {/* Dialog de Confirmação de Delete / Löschbestätigungsdialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Vertrag löschen / Delete Contract"
        message={`Möchten Sie den Vertrag "${contract.title}" wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden. / Are you sure you want to delete contract "${contract.title}"? This action cannot be undone.`}
        confirmText={deleting ? 'Löschen... / Deleting...' : 'Löschen / Delete'}
        cancelText="Abbrechen / Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        severity="error"
      />
    </Box>
  );
};

export default ContractView;
