/**
 * ContractsList - Página de Listagem de Contratos
 * Vertragslistenseite
 * 
 * Página principal com tabela, filtros e ações de contratos
 * Hauptseite mit Tabelle, Filtern und Vertragsaktionen
 */
import { useState, useEffect, useCallback } from 'react';
import { Box, Button, Typography, Paper, Alert } from '@mui/material';
import { Add as AddIcon } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useSnackbar } from 'notistack';
import { useAuthStore } from '../../store/authStore';
import ContractTable from '../../components/contracts/ContractTable';
import ContractFilters from '../../components/contracts/ContractFilters';
import ConfirmDialog from '../../components/ui/ConfirmDialog';
import contractsApi from '../../services/contractsApi';
import { PAGINATION } from '../../utils/constants';

const ContractsList = () => {
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const user = useAuthStore((state) => state.user);

  // Estado / Zustand
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [totalRows, setTotalRows] = useState(0);
  const [page, setPage] = useState(0); // DataGrid usa 0-based
  const [pageSize, setPageSize] = useState(PAGINATION.DEFAULT_PAGE_SIZE);
  const [filters, setFilters] = useState({
    status: '',
    contract_type: '',
    search: ''
  });
  const [sortModel, setSortModel] = useState([
    { field: 'id', sort: 'asc' } // Ordenação padrão: ID crescente
  ]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [contractToDelete, setContractToDelete] = useState(null);

  /**
   * Verifica se usuário pode criar contratos
   * Prüft, ob Benutzer Verträge erstellen kann
   */
  const canCreateContract = useCallback(() => {
    if (!user) return false;
    // READ_ONLY não pode criar
    if (user.role === 'READ_ONLY') return false;
    // Level 1 (STAFF) não pode criar
    if (user.access_level === 1) return false;
    // Todos outros podem criar
    return true;
  }, [user]);

  /**
   * Carrega contratos do backend
   * Lädt Verträge vom Backend
   */
  const loadContracts = useCallback(async () => {
    console.log('🔄 [PAGINAÇÃO] Iniciando carregamento de contratos...');
    console.log('📊 [PAGINAÇÃO] Estado atual:', {
      page: page,
      pageSize: pageSize,
      filters: filters,
      sortModel: sortModel
    });
    
    setLoading(true);
    setError(null);

    try {
      // Prepara parâmetros para API
      const params = {
        page: page + 1, // API usa 1-based
        page_size: pageSize
      };

      // Adiciona filtros se existirem
      if (filters.status) params.status = filters.status;
      if (filters.contract_type) params.contract_type = filters.contract_type;
      if (filters.search) params.search = filters.search;

      // Adiciona ordenação se existir
      if (sortModel.length > 0) {
        const { field, sort } = sortModel[0];
        params.sort_by = sort === 'desc' ? `-${field}` : field;
        console.log('🔀 [ORDENAÇÃO] Aplicando ordenação:', { field, sort, sort_by: params.sort_by });
      }

      console.log('📤 [PAGINAÇÃO] Parâmetros enviados à API:', params);
      const response = await contractsApi.getContracts(params);
      console.log('📥 [PAGINAÇÃO] Resposta da API:', {
        items_count: response.items?.length || 0,
        total: response.total,
        page: response.page,
        page_size: response.page_size
      });

      setContracts(response.items || []);
      setTotalRows(response.total || 0);
      console.log('✅ [PAGINAÇÃO] Contratos carregados com sucesso');
    } catch (err) {
      console.error('❌ [PAGINAÇÃO] Error loading contracts:', err);
      setError(err.message || 'Failed to load contracts');
      enqueueSnackbar('Error loading contracts', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, filters, sortModel, enqueueSnackbar]);

  /**
   * Effect: Carrega contratos quando parâmetros mudam
   * Effect: Lädt Verträge bei Parameteränderung
   */
  useEffect(() => {
    loadContracts();
  }, [loadContracts]);

  /**
   * Handlers de eventos
   * Event-Handler
   */
  const handlePageChange = (newPage) => {
    console.log('🔄 [PAGINAÇÃO] Mudança de página solicitada:', {
      página_atual: page,
      nova_página: newPage,
      total_registros: totalRows,
      registros_por_página: pageSize
    });
    setPage(newPage);
  };

  const handlePageSizeChange = (newPageSize) => {
    setPageSize(newPageSize);
    setPage(0); // Reset para primeira página
  };

  const handleSortChange = (model) => {
    setSortModel(model);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPage(0); // Reset para primeira página quando filtrar
  };

  const handleClearFilters = () => {
    setFilters({
      status: '',
      contract_type: '',
      search: ''
    });
    setPage(0);
  };

  const handleView = (contract) => {
    navigate(`/app/contracts/${contract.id}`);
  };

  const handleEdit = (contract) => {
    navigate(`/app/contracts/${contract.id}/edit`);
  };

  const handleDelete = (contract) => {
    setContractToDelete(contract);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!contractToDelete) return;

    try {
      await contractsApi.deleteContract(contractToDelete.id);
      enqueueSnackbar('Contract deleted successfully', { variant: 'success' });
      loadContracts(); // Recarrega lista
    } catch (err) {
      console.error('Error deleting contract:', err);
      enqueueSnackbar(
        err.response?.data?.detail || 'Failed to delete contract', 
        { variant: 'error' }
      );
    } finally {
      setDeleteDialogOpen(false);
      setContractToDelete(null);
    }
  };

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false);
    setContractToDelete(null);
  };

  const handleCreateNew = () => {
    navigate('/app/contracts/new');
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header com título e botão novo / Header mit Titel und Neu-Button */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" component="h1" gutterBottom>
            Verträge
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Contracts
          </Typography>
        </Box>
        {canCreateContract() && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleCreateNew}
          >
            Neuer Vertrag / New Contract
          </Button>
        )}
      </Box>

      {/* Erro / Fehler */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Paper com filtros e tabela / Paper mit Filtern und Tabelle */}
      <Paper sx={{ p: 3 }}>
        <ContractFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          onClearFilters={handleClearFilters}
        />

        <ContractTable
          contracts={contracts}
          loading={loading}
          totalRows={totalRows}
          page={page}
          pageSize={pageSize}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          onSortChange={handleSortChange}
          onView={handleView}
          onEdit={handleEdit}
          onDelete={handleDelete}
        />
      </Paper>

      {/* Dialog de Confirmação de Delete / Löschbestätigungsdialog */}
      <ConfirmDialog
        open={deleteDialogOpen}
        title="Vertrag löschen / Delete Contract"
        message={`Möchten Sie den Vertrag "${contractToDelete?.title}" wirklich löschen? / Are you sure you want to delete contract "${contractToDelete?.title}"?`}
        confirmText="Löschen / Delete"
        cancelText="Abbrechen / Cancel"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        severity="error"
      />
    </Box>
  );
};

export default ContractsList;
