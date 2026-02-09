/**
 * ContractEdit - Página de Edição de Contrato
 * Vertragsbearbeitungsseite
 * 
 * Página para editar contrato existente
 * Seite zum Bearbeiten eines bestehenden Vertrags
 */
import { useState, useEffect } from 'react';
import { Box, Typography, Breadcrumbs, Link as MuiLink, Alert, CircularProgress } from '@mui/material';
import { useNavigate, useParams } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { NavigateNext as NavigateNextIcon } from '@mui/icons-material';
import ContractForm from '../../components/contracts/ContractForm';
import RentStepsList from '../../components/rent-steps/RentStepsList';
import ContractAlerts from '../../components/alerts/ContractAlerts';
import contractsApi from '../../services/contractsApi';

const ContractEdit = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  
  const [contract, setContract] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Carrega contrato existente
   * Lädt bestehenden Vertrag
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

  const handleSubmit = async (data) => {
    setSaving(true);
    try {
      const updated = await contractsApi.updateContract(id, data);
      enqueueSnackbar('Contract updated successfully', { variant: 'success' });
      navigate(`/app/contracts/${updated.id}`);
    } catch (error) {
      console.error('Error updating contract:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to update contract';
      enqueueSnackbar(errorMessage, { variant: 'error' });
    } finally {
      setSaving(false);
    }
  };

  const handleCancel = () => {
    navigate(`/app/contracts/${id}`);
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
        <Alert severity="error">
          {error || 'Contract not found'}
        </Alert>
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
          onClick={() => navigate('/app/contracts')}
          sx={{ cursor: 'pointer' }}
        >
          Verträge / Contracts
        </MuiLink>
        <MuiLink
          component="button"
          variant="body1"
          onClick={() => navigate(`/app/contracts/${id}`)}
          sx={{ cursor: 'pointer' }}
        >
          {contract.title}
        </MuiLink>
        <Typography color="text.primary">Bearbeiten / Edit</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Vertrag bearbeiten
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Edit Contract: {contract.title}
        </Typography>
      </Box>

      {/* Form */}
      <ContractForm
        initialData={contract}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        loading={saving}
      />

      {/* Alertas do Contrato / Vertragswarnungen */}
      <Box sx={{ mt: 4 }}>
        <ContractAlerts contractId={contract.id} />
      </Box>

      {/* Rent Steps - apenas em edição, contrato já existe */}
      <Box sx={{ mt: 4 }}>
        <RentStepsList 
          contractId={contract.id}
          currentRentAmount={contract.value}
          currentCurrency={contract.currency}
          contractStartDate={contract.start_date}
          contractEndDate={contract.end_date}
          contractInitialValue={contract.value}
        />
      </Box>
    </Box>
  );
};

export default ContractEdit;
