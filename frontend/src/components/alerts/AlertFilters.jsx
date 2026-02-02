/**
 * Alert Filters Component
 * Componente de Filtros de Alertas
 * 
 * Filtros para listagem de alertas (tipo, status de leitura, busca por contrato)
 * Filter für Warnungsliste (Typ, Lesestatus, Suche nach Vertrag)
 */

import { useState } from 'react';
import {
  Box,
  Grid,
  TextField,
  MenuItem,
  Button,
  Paper,
  Typography
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import {
  ALERT_TYPES,
  ALERT_TYPE_LABELS,
  ALERT_STATUS,
  ALERT_STATUS_LABELS
} from '../../utils/constants';

/**
 * AlertFilters Component
 * 
 * @param {Object} props
 * @param {Object} props.filters - Filtros atuais
 * @param {Function} props.onFilterChange - Callback quando filtros mudam
 * @param {Function} props.onClearFilters - Callback para limpar filtros
 */
const AlertFilters = ({ filters, onFilterChange, onClearFilters }) => {
  const [localFilters, setLocalFilters] = useState(filters);

  /**
   * Atualiza filtro local e notifica pai
   * Lokalen Filter aktualisieren und Eltern benachrichtigen
   */
  const handleFilterChange = (field, value) => {
    const newFilters = { ...localFilters, [field]: value };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  /**
   * Limpa todos os filtros
   * Alle Filter löschen
   */
  const handleClear = () => {
    const emptyFilters = {
      alert_type: '',
      status: ALERT_STATUS.ALL,
      search: ''
    };
    setLocalFilters(emptyFilters);
    onClearFilters();
  };

  /**
   * Verifica se há filtros ativos
   * Prüfen, ob Filter aktiv sind
   */
  const hasActiveFilters = () => {
    return (
      localFilters.alert_type ||
      localFilters.status !== ALERT_STATUS.ALL ||
      localFilters.search
    );
  };

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <FilterListIcon sx={{ mr: 1 }} />
        <Typography variant="h6">
          Filter / Filtros
        </Typography>
      </Box>

      <Grid container spacing={2}>
        {/* Tipo de Alerta / Warnungstyp */}
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            select
            fullWidth
            label="Typ / Tipo"
            value={localFilters.alert_type || ''}
            onChange={(e) => handleFilterChange('alert_type', e.target.value)}
            size="small"
          >
            <MenuItem value="">
              <em>Alle / Todos</em>
            </MenuItem>
            {Object.entries(ALERT_TYPE_LABELS).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Status / Status */}
        <Grid item xs={12} sm={6} md={3}>
          <TextField
            select
            fullWidth
            label="Status / Status"
            value={localFilters.status || ALERT_STATUS.ALL}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            size="small"
          >
            {Object.entries(ALERT_STATUS_LABELS).map(([value, label]) => (
              <MenuItem key={value} value={value}>
                {label}
              </MenuItem>
            ))}
          </TextField>
        </Grid>

        {/* Busca por Título do Contrato / Suche nach Vertragstitel */}
        <Grid item xs={12} sm={8} md={4}>
          <TextField
            fullWidth
            label="Suche Vertrag / Buscar Contrato"
            placeholder="Titel des Vertrags... / Título do contrato..."
            value={localFilters.search || ''}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            size="small"
          />
        </Grid>

        {/* Botão Limpar Filtros / Filter löschen Button */}
        <Grid item xs={12} sm={4} md={2} sx={{ display: 'flex', alignItems: 'center' }}>
          <Button
            fullWidth
            variant="outlined"
            color="secondary"
            startIcon={<ClearIcon />}
            onClick={handleClear}
            disabled={!hasActiveFilters()}
            size="small"
          >
            Löschen / Limpar
          </Button>
        </Grid>
      </Grid>

      {/* Indicador de filtros ativos / Aktive Filter Indikator */}
      {hasActiveFilters() && (
        <Box sx={{ mt: 2 }}>
          <Typography variant="caption" color="text.secondary">
            {`Aktive Filter / Filtros ativos: 
              ${localFilters.alert_type ? ALERT_TYPE_LABELS[localFilters.alert_type] : ''} 
              ${localFilters.status !== ALERT_STATUS.ALL ? ALERT_STATUS_LABELS[localFilters.status] : ''} 
              ${localFilters.search ? `"${localFilters.search}"` : ''}`}
          </Typography>
        </Box>
      )}
    </Paper>
  );
};

export default AlertFilters;
