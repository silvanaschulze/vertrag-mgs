import React from 'react';
import PropTypes from 'prop-types';
import { Box, TextField, Grid, Typography } from '@mui/material';

/**
 * ExtractedDataForm
 * Formulário para editar dados extraídos do PDF antes de salvar
 *
 * Props:
 * - data: objeto com campos extraídos (title, client_name, etc)
 * - onChange: (novoObjeto) => void
 * - disabled: boolean
 */
const fields = [
  { name: 'title', label: 'Título do Contrato', required: true },
  { name: 'client_name', label: 'Nome do Cliente', required: true },
  { name: 'client_email', label: 'E-mail do Cliente' },
  { name: 'value', label: 'Valor', type: 'number' },
  { name: 'currency', label: 'Moeda' },
  { name: 'start_date', label: 'Data de Início', type: 'date' },
  { name: 'end_date', label: 'Data de Término', type: 'date' },
  { name: 'renewal_date', label: 'Data de Renovação', type: 'date' },
  { name: 'description', label: 'Descrição' },
];

const ExtractedDataForm = ({ data, onChange, disabled = false }) => {
  const handleFieldChange = (e) => {
    const { name, value } = e.target;
    onChange({ ...data, [name]: value });
  };

  return (
    <Box component="form" autoComplete="off" sx={{ mt: 2 }}>
      <Grid container spacing={2}>
        {fields.map((field) => (
          <Grid item xs={12} sm={field.type === 'date' ? 6 : 12} key={field.name}>
            <TextField
              fullWidth
              label={field.label}
              name={field.name}
              value={data[field.name] || ''}
              onChange={handleFieldChange}
              type={field.type || 'text'}
              required={field.required}
              disabled={disabled}
              InputLabelProps={field.type === 'date' ? { shrink: true } : undefined}
            />
          </Grid>
        ))}
      </Grid>
      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        Revise os dados extraídos antes de salvar. Campos obrigatórios: Título, Cliente.
      </Typography>
    </Box>
  );
};

ExtractedDataForm.propTypes = {
  data: PropTypes.object.isRequired,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

export default ExtractedDataForm;
