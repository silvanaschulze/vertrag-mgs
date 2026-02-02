/**
 * ContractCreate - Página de Criação de Contrato
 * Vertragserstellungsseite
 * 
 * Página para criar novo contrato
 * Seite zum Erstellen eines neuen Vertrags
 */
import { Box, Typography, Breadcrumbs, Link as MuiLink, Alert } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { NavigateNext as NavigateNextIcon } from '@mui/icons-material';
import ContractForm from '../../components/contracts/ContractForm';
import contractsApi from '../../services/contractsApi';
import { useState } from 'react';

const ContractCreate = () => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (data) => {
    setLoading(true);
    try {
      const created = await contractsApi.createContract(data);
      enqueueSnackbar('Contract created successfully', { variant: 'success' });
      navigate(`/app/contracts/${created.id}`);
    } catch (error) {
      console.error('Error creating contract:', error);
      console.error('Error response:', error.response?.data);
      const errorMessage = error.response?.data?.detail || 'Failed to create contract';
      enqueueSnackbar(errorMessage, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/app/contracts');
  };

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
        <Typography color="text.primary">Neuer Vertrag / New Contract</Typography>
      </Breadcrumbs>

      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Neuer Vertrag
        </Typography>
        <Typography variant="body2" color="text.secondary">
          New Contract
        </Typography>
      </Box>

      {/* Informação sobre funcionalidades adicionais */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>Hinweis / Nota:</strong> Mietstaffelungen (Rent Steps) und benutzerdefinierte Warnungen können nach dem Speichern des Vertrags hinzugefügt werden.
        </Typography>
        <Typography variant="caption" display="block" sx={{ mt: 1 }}>
          Rent Steps e alertas customizados podem ser adicionados após salvar o contrato.
        </Typography>
      </Alert>

      {/* Form */}
      <ContractForm
        onSubmit={handleSubmit}
        onCancel={handleCancel}
        loading={loading}
      />
    </Box>
  );
};

export default ContractCreate;
