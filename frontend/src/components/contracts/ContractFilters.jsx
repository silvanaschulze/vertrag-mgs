/**
 * ContractFilters - Filtros de Contratos
 * Vertragsfilter
 * 
 * Componente com filtros de status, tipo e busca
 * Komponente mit Status-, Typ- und Suchfiltern
 */
import { Box, TextField, MenuItem, Button, Grid } from '@mui/material';
import { FilterList as FilterIcon, Clear as ClearIcon } from '@mui/icons-material';
import { 
  CONTRACT_STATUS, 
  CONTRACT_STATUS_LABELS,
  CONTRACT_TYPES,
  CONTRACT_TYPE_LABELS
} from '../../utils/constants';

const ContractFilters = ({ 
  filters = {}, 
  onFilterChange,
  onClearFilters 
}) => {
  const handleChange = (field, value) => {
    onFilterChange({ ...filters, [field]: value });
  };

  const handleClear = () => {
    onClearFilters();
  };

  const hasActiveFilters = filters.status || filters.contract_type || filters.search;

  return (
    <Box sx={{ mb: 3 }}>
      <Grid container spacing={2} alignItems="center">
        {/* Status Filter / Statusfilter */}
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            select
            fullWidth
            label="Status"
            value={filters.status || ''}
            onChange={(e) => handleChange('status', e.target.value)}
            size="small"
          >
            <MenuItem value="">
              <em>Alle / All</em>
            </MenuItem>
            {Object.entries(CONTRACT_STATUS).map(([key, value]) => (
              <MenuItem key={value} value={value}>
                {CONTRACT_STATUS_LABELS[value]}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Type Filter / Typfilter */}
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            select
            fullWidth
            label="Typ / Type"
            value={filters.contract_type || ''}
            onChange={(e) => handleChange('contract_type', e.target.value)}
            size="small"
          >
            <MenuItem value="">
              <em>Alle / All</em>
            </MenuItem>
            {Object.entries(CONTRACT_TYPES).map(([key, value]) => (
              <MenuItem key={value} value={value}>
                {CONTRACT_TYPE_LABELS[value]}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Search Filter / Suchfilter */}
        <Grid item xs={12} sm={8} md={4}>
          <TextField
            fullWidth
            label="Suche / Search"
            placeholder="Titel, Partner..."
            value={filters.search || ''}
            onChange={(e) => handleChange('search', e.target.value)}
            size="small"
          />
        </Grid>

        {/* Clear Filters Button / Filter löschen Button */}
        <Grid item xs={12} sm={4} md={2}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={hasActiveFilters ? <ClearIcon /> : <FilterIcon />}
            onClick={handleClear}
            disabled={!hasActiveFilters}
          >
            {hasActiveFilters ? 'Löschen / Clear' : 'Filter'}
          </Button>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ContractFilters;
