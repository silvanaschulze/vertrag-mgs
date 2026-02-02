import React from 'react';
import PropTypes from 'prop-types';
import { Box, TextField, MenuItem, Button, Grid } from '@mui/material';
import { USER_ROLES } from '../../utils/constants';

const UserFilters = ({ filters, onChange, onClear }) => {
  return (
    <Box sx={{ mb: 2 }}>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={3}>
          <TextField
            select
            label="Role"
            value={filters.role || ''}
            onChange={e => onChange({ ...filters, role: e.target.value })}
            fullWidth
            size="small"
          >
            <MenuItem value="">Alle / All</MenuItem>
            {Object.keys(USER_ROLES).map(role => (
              <MenuItem key={role} value={role}>{role}</MenuItem>
            ))}
          </TextField>
        </Grid>
        <Grid item xs={12} sm={3}>
          <TextField
            select
            label="Status"
            value={filters.status || ''}
            onChange={e => onChange({ ...filters, status: e.target.value })}
            fullWidth
            size="small"
          >
            <MenuItem value="">Alle / All</MenuItem>
            <MenuItem value="active">Aktiv / Active</MenuItem>
            <MenuItem value="inactive">Inaktiv / Inactive</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={12} sm={3}>
          <TextField
            label="Abteilung / Department"
            value={filters.department || ''}
            onChange={e => onChange({ ...filters, department: e.target.value })}
            fullWidth
            size="small"
          />
        </Grid>
        <Grid item xs={12} sm={3}>
          <TextField
            label="Suche (Name/E-Mail) / Search"
            value={filters.search || ''}
            onChange={e => onChange({ ...filters, search: e.target.value })}
            fullWidth
            size="small"
          />
        </Grid>
        <Grid item xs={12} sm={12}>
          <Button onClick={onClear} variant="outlined" size="small">Filter zurücksetzen / Clear Filters</Button>
        </Grid>
      </Grid>
    </Box>
  );
};

UserFilters.propTypes = {
  filters: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  onClear: PropTypes.func.isRequired,
};

export default UserFilters;
