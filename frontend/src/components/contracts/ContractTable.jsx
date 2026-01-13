/**
 * ContractTable - Tabela de Contratos com DataGrid
 * Vertrags-Tabelle mit DataGrid
 * 
 * Lista contratos com paginação, ordenação e ações
 * Listet Verträge mit Paginierung, Sortierung und Aktionen auf
 */
import { useMemo } from 'react';
import { DataGrid } from '@mui/x-data-grid';
import { Box, Chip, IconButton, Tooltip } from '@mui/material';
import { Edit as EditIcon, Delete as DeleteIcon, Visibility as ViewIcon } from '@mui/icons-material';
import { format } from 'date-fns';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import { 
  CONTRACT_STATUS_LABELS, 
  CONTRACT_STATUS_LABELS_EN, 
  CONTRACT_STATUS_COLORS, 
  CONTRACT_TYPE_LABELS,
  CONTRACT_TYPE_LABELS_EN,
  DATE_FORMAT 
} from '../../utils/constants';

/**
 * Formata valor monetário
 * Formatiert Geldwert
 */
const formatCurrency = (value) => {
  if (!value && value !== 0) return '-';
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
  }).format(value);
};

/**
 * Formata data
 * Formatiert Datum
 */
const formatDate = (dateString) => {
  if (!dateString) return '-';
  try {
    return format(new Date(dateString), DATE_FORMAT);
  } catch {
    return dateString;
  }
};

const ContractTable = ({ 
  contracts = [], 
  loading = false, 
  totalRows = 0,
  page = 0,
  pageSize = 25,
  onPageChange,
  onPageSizeChange,
  onSortChange,
  onEdit,
  onDelete,
  onView
}) => {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);

  /**
   * Verifica se usuário pode ver valores financeiros
   * Prüft, ob Benutzer Finanzwerte sehen kann
   * 
   * Level 6 (SYSTEM_ADMIN): NÃO vê valores
   * Level 5 (DIRECTOR): Vê valores
   * Level 4 (DEPARTMENT_ADM): Vê valores
   * Level 3 e abaixo: NÃO vê valores
   */
  const canSeeFinancialValues = useMemo(() => {
    if (!user) return false;
    return user.access_level === 5 || user.access_level === 4;
  }, [user]);

  /**
   * Verifica se pode editar contrato específico
   * Prüft, ob Vertrag bearbeitet werden kann
   */
  const canEditContract = (contract) => {
    if (!user) return false;

    // READ_ONLY não pode editar
    if (user.role === 'READ_ONLY') return false;

    // Level 5 (DIRECTOR): edita tudo
    if (user.access_level >= 5) return true;

    // Level 4 (DEPARTMENT_ADM): edita contratos do departamento
    if (user.access_level >= 4) {
      return contract.department === user.department;
    }

    // Level 3 (DEPARTMENT_USER): edita contratos do departamento
    if (user.access_level >= 3) {
      return contract.department === user.department;
    }

    // Level 2 (TEAM, SYSTEM_ADMIN): edita contratos do time
    if (user.access_level >= 2) {
      return (contract.team === user.team) || (contract.created_by === user.id);
    }

    return false;
  };

  /**
   * Verifica se pode deletar contrato específico
   * Prüft, ob Vertrag gelöscht werden kann
   */
  const canDeleteContract = (contract) => {
    if (!user) return false;

    // Level 5 (DIRECTOR): deleta tudo
    if (user.access_level >= 5) return true;

    // Level 4 (DEPARTMENT_ADM): deleta contratos do departamento
    if (user.access_level >= 4 && user.role === 'DEPARTMENT_ADM') {
      return contract.department === user.department;
    }

    // Outros não podem deletar
    return false;
  };

  /**
   * Definição de colunas do DataGrid
   * DataGrid-Spaltendefinition
   */
  const columns = useMemo(() => {
    const baseColumns = [
      { 
        field: 'id', 
        headerName: 'ID', 
        width: 70,
        sortable: true
      },
      { 
        field: 'title', 
        headerName: 'Titel / Title', 
        flex: 1, 
        minWidth: 200,
        sortable: true
      },
      { 
        field: 'client_name', 
        headerName: 'Partner / Partner', 
        flex: 1, 
        minWidth: 150,
        sortable: true
      },
      { 
        field: 'contract_type', 
        headerName: 'Typ / Type', 
        width: 140,
        sortable: true,
        renderCell: (params) => (
          <Tooltip title={CONTRACT_TYPE_LABELS_EN[params.value] || params.value}>
            <span>{CONTRACT_TYPE_LABELS[params.value] || params.value}</span>
          </Tooltip>
        )
      },
      { 
        field: 'status', 
        headerName: 'Status', 
        width: 180,
        sortable: true,
        renderCell: (params) => (
          <Chip 
            label={CONTRACT_STATUS_LABELS[params.value] || params.value}
            color={CONTRACT_STATUS_COLORS[params.value] || 'default'}
            size="small"
            title={CONTRACT_STATUS_LABELS_EN[params.value] || params.value}
          />
        )
      },
      { 
        field: 'start_date', 
        headerName: 'Start / Start', 
        width: 110,
        sortable: true,
        valueGetter: (value) => value ? formatDate(value) : '-'
      },
      { 
        field: 'end_date', 
        headerName: 'Ende / End', 
        width: 110,
        sortable: true,
        valueGetter: (value) => value ? formatDate(value) : '-'
      }
    ];

    // Adiciona coluna de valor apenas se usuário pode ver
    // Fügt Wertspalte nur hinzu, wenn Benutzer sehen kann
    if (canSeeFinancialValues) {
      baseColumns.push({
        field: 'value',
        headerName: 'Wert / Value',
        width: 130,
        sortable: true,
        valueGetter: (value) => value ? formatCurrency(value) : '-'
      });
    }

    // Coluna de ações
    // Aktionsspalte
    baseColumns.push({
      field: 'actions',
      headerName: 'Aktionen / Actions',
      width: 140,
      sortable: false,
      renderCell: (params) => (
        <Box sx={{ display: 'flex', gap: 0.5 }}>
          <Tooltip title="View Details">
            <IconButton 
              size="small" 
              onClick={() => onView ? onView(params.row) : navigate(`/app/contracts/${params.row.id}`)}
              color="primary"
            >
              <ViewIcon fontSize="small" />
            </IconButton>
          </Tooltip>
          
          {canEditContract(params.row) && (
            <Tooltip title="Edit">
              <IconButton 
                size="small" 
                onClick={() => onEdit ? onEdit(params.row) : navigate(`/app/contracts/${params.row.id}/edit`)}
                color="primary"
              >
                <EditIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
          
          {canDeleteContract(params.row) && (
            <Tooltip title="Delete">
              <IconButton 
                size="small" 
                onClick={() => onDelete && onDelete(params.row)}
                color="error"
              >
                <DeleteIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          )}
        </Box>
      )
    });

    return baseColumns;
  }, [canSeeFinancialValues, user, navigate, onEdit, onDelete, onView]);

  return (
    <Box sx={{ width: '100%', height: 600 }}>
      <DataGrid
        rows={contracts}
        columns={columns}
        rowCount={totalRows}
        loading={loading}
        pagination
        page={page}
        pageSize={pageSize}
        paginationMode="server"
        sortingMode="server"
        onPageChange={onPageChange}
        onPageSizeChange={onPageSizeChange}
        onSortModelChange={onSortChange}
        pageSizeOptions={[10, 25, 50, 100]}
        disableRowSelectionOnClick
        disableColumnMenu
        autoHeight
        sx={{
          '& .MuiDataGrid-cell:focus': {
            outline: 'none'
          },
          '& .MuiDataGrid-row:hover': {
            backgroundColor: 'action.hover'
          }
        }}
      />
    </Box>
  );
};

export default ContractTable;
